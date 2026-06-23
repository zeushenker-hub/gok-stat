"""
Анализ контента тендерных документов:
- извлечение структурированных признаков
- сегментация заказчиков
- схлопывание дублирующихся компаний в один unit
- статистика признаков по сегментам и в целом
"""
from pathlib import Path
from collections import Counter, defaultdict

from scripts.shared import get_all_files, extract_text
from scripts.extractor import (
    extract_features, features_to_csv_row, CSV_HEADER,
    _BOOL_FEATURES, _BOOL_LABELS_SHORT, _NUMERIC_FEATURES,
)
from scripts.segmenter import classify_segment, get_segment_description


_ALL_FEATURES = _BOOL_FEATURES + _NUMERIC_FEATURES

# Полный набор для подсчёта "есть хоть что-то" — включая строковые признаки
_ANY_FEATURE_FIELDS = _ALL_FEATURES + [
    "company_name", "contract_duration", "tender_number",
    "region_city", "work_schedule",
]

_FEAT_DISPLAY = {
    "has_glonass": "ГЛОНАСС/мониторинг",
    "has_conditioner": "Кондиционер",
    "has_medical_check": "Медосмотр",
    "has_security_requirements": "Требования безопасности",
    "has_driver_requirements": "Требования к водителю",
    "employees_count": "Кол-во сотрудников",
    "bus_count": "Кол-во автобусов",
    "route_count": "Кол-во маршрутов",
    "bus_capacity": "Вместимость",
    "any_feature": "Хотя бы один признак",
    "no_feature": "Без единого признака",
}

# Компания определяется по имени папки, в которой лежит файл.
# В source/ у нас одна папка = одна компания.
# Компания определяется по имени папки, в которой лежит файл.
# В source/ у нас одна папка = одна компания.


def _has_value(r, feat):
    if feat in _BOOL_FEATURES:
        return r.get(feat) is True or str(r.get(feat, "")).lower() == "да"
    v = r.get(feat)
    if v is None:
        return False
    s = str(v).strip()
    return bool(s) and s.lower() not in ("", "none", "null")


def _stats_for(rows):
    n = len(rows)
    if n == 0:
        return {}
    stats = {}
    for feat in _ALL_FEATURES:
        cnt = sum(1 for r in rows if _has_value(r, feat))
        stats[feat] = {"count": cnt, "pct": round(cnt / n * 100, 1) if n else 0}
    any_cnt = sum(1 for r in rows if any(_has_value(r, f) for f in _ANY_FEATURE_FIELDS))
    stats["any_feature"] = {"count": any_cnt, "pct": round(any_cnt / n * 100, 1) if n else 0}
    stats["no_feature"] = {"count": n - any_cnt, "pct": round((n - any_cnt) / n * 100, 1) if n else 0}
    return stats


def _get_company_name(filepath):
    """Возвращает название компании = имя папки, в которой лежит файл."""
    # filepath — строка или Path, относительный путь от source_dir
    if isinstance(filepath, str):
        filepath = Path(filepath)
    parts = filepath.parts
    if len(parts) >= 2:
        return parts[-2]  # имя папки
    return filepath.stem  # fallback - файл в корне


def _merge_features(group):
    """Схлопывает группу файлов одной компании в один unit."""
    merged = {}
    base = group[0]
    merged.update(base)
    # название компании — из маппинга
    merged["filename"] = _get_company_name(base.get("filename", ""))
    # булевые: да если хоть у одного да
    for feat in _BOOL_FEATURES:
        merged[feat] = any(_has_value(r, feat) for r in group)
    # числовые: берём максимальное
    for feat in _NUMERIC_FEATURES:
        vals = []
        for r in group:
            v = r.get(feat)
            if v is not None and str(v).strip():
                try:
                    vals.append(int(v))
                except (ValueError, TypeError):
                    pass
        if vals:
            merged[feat] = max(vals)
    # сегмент: тот что у большинства
    segs = Counter(r.get("segment", "") for r in group)
    merged["segment"] = segs.most_common(1)[0][0]
    return merged


def run(source_dir: Path, results_dir: Path) -> None:
    files = get_all_files()
    doc_files = [f for f in files if f.is_file() and f.suffix.lower() in
                 (".docx", ".pdf", ".xlsx", ".doc")]

    all_rows = []

    for fp in doc_files:
        rel = fp.relative_to(source_dir)
        company_name = _get_company_name(rel)
        print(f"  [{company_name}] {fp.name}")
        text = extract_text(fp)
        features = extract_features(text, filename=str(rel))
        segment = classify_segment(features, text)
        features["segment"] = segment
        features["any_feature"] = any(_has_value(features, f) for f in _ANY_FEATURE_FIELDS)
        features["filename"] = company_name  # заменяем filename на имя компании
        all_rows.append(features)

    # Группируем по компаниям (все файлы одной папки уже имеют одинаковое имя)
    groups = defaultdict(list)
    for r in all_rows:
        company = r["filename"]
        groups[company].append(r)

    merged_rows = []
    for key, grp in groups.items():
        if len(grp) > 1:
            merged = _merge_features(grp)
            merged_rows.append(merged)
        else:
            merged_rows.append(dict(grp[0]))

    total = len(merged_rows)

    # Сегментация
    segment_counter: Counter = Counter()
    segment_files: dict = {}
    by_segment: dict = defaultdict(list)

    for r in merged_rows:
        seg = r["segment"]
        segment_counter[seg] += 1
        by_segment[seg].append(r)
        if seg not in segment_files:
            segment_files[seg] = []
        segment_files[seg].append(r["filename"])

    # 1. CSV с признаками
    out_features = results_dir / "content_features.csv"
    with open(str(out_features), "w", encoding="utf-8") as f:
        f.write(CSV_HEADER + ',"segment"\n')
        for feat in merged_rows:
            row = features_to_csv_row(feat)
            seg = _csv_safe(feat.get("segment", "Не определено"))
            f.write(f'{row},"{seg}"\n')
    print(f"[content] Wrote {len(merged_rows)} feature rows (merged from {len(all_rows)} files) to {out_features}")

    # 2. Статистика признаков — общая
    total_stats = _stats_for(merged_rows)
    out_tot = results_dir / "feature_stats_total.csv"
    display_order = ["any_feature", "no_feature"] + _ALL_FEATURES
    with open(str(out_tot), "w", encoding="utf-8") as f:
        f.write("feature,type,count,pct\n")
        for feat in display_order:
            s = total_stats.get(feat, {"count": 0, "pct": 0})
            label = _FEAT_DISPLAY.get(feat, feat)
            f.write(f'"{label}",boolean,{s["count"]},{s["pct"]}\n')
    print(f"[content] Wrote total feature stats to {out_tot}")

    # 3. Статистика по сегментам
    out_seg = results_dir / "feature_stats_by_segment.csv"
    with open(str(out_seg), "w", encoding="utf-8") as f:
        header_parts = ["segment"]
        display_feats = _ALL_FEATURES + ["any_feature"]
        for feat in display_feats:
            header_parts.append(_FEAT_DISPLAY.get(feat, feat))
        header_parts.append("Без единого признака")
        f.write(",".join(f'"{h}"' for h in header_parts) + "\n")

        all_segs_sort = sorted(segment_counter.keys(), key=lambda s: -segment_counter[s])
        for seg in all_segs_sort:
            seg_rows = by_segment.get(seg, [])
            seg_stats = _stats_for(seg_rows)
            row_parts = [seg]
            for feat in display_feats:
                s = seg_stats.get(feat, {"count": 0, "pct": 0})
                row_parts.append(f'{s["count"]} ({s["pct"]}%)')
            s = seg_stats.get("no_feature", {"count": 0, "pct": 0})
            row_parts.append(f'{s["count"]} ({s["pct"]}%)')
            f.write(",".join(row_parts) + "\n")

        row_parts = ["ИТОГО"]
        for feat in display_feats:
            s = total_stats.get(feat, {"count": 0, "pct": 0})
            row_parts.append(f'{s["count"]} ({s["pct"]}%)')
        s = total_stats.get("no_feature", {"count": 0, "pct": 0})
        row_parts.append(f'{s["count"]} ({s["pct"]}%)')
        f.write(",".join(row_parts) + "\n")

    print(f"[content] Wrote per-segment feature stats to {out_seg}")

    # 4. Сегментация
    out_seg_sum = results_dir / "segmentation.csv"
    with open(str(out_seg_sum), "w", encoding="utf-8") as f:
        f.write("segment,count,percentage,description,files\n")
        for seg, count in sorted(segment_counter.items(), key=lambda x: -x[1]):
            pct = round(count / total * 100, 1)
            desc = get_segment_description(seg)
            files_list = "; ".join(segment_files.get(seg, []))
            f.write(f'"{seg}",{count},{pct},"{desc}","{files_list}"\n')
    print(f"[content] Segmented {total} units into {len(segment_counter)} segments -> {out_seg_sum}")


    # 5. Компании с признаками и без
    out_feature_list = results_dir / "feature_presence.csv"
    has_features = []
    no_features = []
    for r in merged_rows:
        company = r.get("filename", "")
        seg = r.get("segment", "")
        has_any = r.get("any_feature", False)
        row = (company, seg)
        if has_any:
            has_features.append(row)
        else:
            no_features.append(row)
    
    with open(str(out_feature_list), "w", encoding="utf-8") as f:
        f.write("status,company,segment\n")
        for company, seg in sorted(has_features, key=lambda x: x[0].lower()):
            f.write('"Есть признаки","' + company + '","' + seg + '"\n')
        for company, seg in sorted(no_features, key=lambda x: x[0].lower()):
            f.write('"Нет признаков","' + company + '","' + seg + '"\n')
    print(f"[content] Wrote feature presence list to {out_feature_list}")

    # 5. Вывод
    print()
    print(f"=== ИТОГОВАЯ СЕГМЕНТАЦИЯ ({total} юнитов, схлопнуто из {len(all_rows)} файлов) ===")
    for seg, count in sorted(segment_counter.items(), key=lambda x: -x[1]):
        pct = round(count / total * 100, 1)
        print(f"  {seg}: {count} ({pct}%)")
        for fn in segment_files.get(seg, []):
            print(f"    - {fn}")

    print()
    print("=== СТАТИСТИКА ПРИЗНАКОВ (ОБЩАЯ) ===")
    for feat in display_order:
        s = total_stats.get(feat, {"count": 0, "pct": 0})
        label = _FEAT_DISPLAY.get(feat, feat)
        print(f"  {label}: {s['count']}/{total} ({s['pct']}%)")

    return merged_rows, segment_counter


def _csv_safe(v):
    if v is None:
        return ""
    s = str(v).replace('"', '""').replace("\n", " ").replace("\r", " ")
    return s
