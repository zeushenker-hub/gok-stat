import csv
from pathlib import Path
from datetime import datetime
import webbrowser


def _read_csv(path):
    rows = []
    if not path.exists():
        return []
    with open(str(path), "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def _seg_color(seg):
    colors = {
        "Промышленность": "#1565c0",
        "Торговля/Производство": "#e65100",
        "Логистика/Почта": "#2e7d32",
        "IT/Услуги": "#6a1b9a",
        "Госсектор": "#c62828",
        "Строительство": "#00838f",
        "Транспорт/Перевозки": "#4e342e",
        "Не определено": "#78909c",
    }
    for key, col in colors.items():
        if key in seg:
            return col
    return "#78909c"


SORT_JS = """
<script>
function setupSort(tableId) {
  const table = document.getElementById(tableId);
  if (!table) return;
  const headers = table.querySelectorAll('thead th');
  headers.forEach((th, colIdx) => {
    th.style.cursor = 'pointer';
    th.addEventListener('click', () => sortTable(table, colIdx));
  });
}

function sortTable(table, colIdx) {
  const tbody = table.querySelector('tbody');
  if (!tbody) return;
  const rows = Array.from(tbody.querySelectorAll('tr'));
  const dataRows = rows.filter(r => {
    const first = r.querySelector('td');
    return first && !first.textContent.trim().match(/^(Итого|итого)/);
  });
  const footerRows = rows.filter(r => !dataRows.includes(r));

  const isAsc = table.dataset.sortCol == colIdx && table.dataset.sortDir == 'asc';
  const dir = isAsc ? -1 : 1;

  dataRows.sort((a, b) => {
    const aTd = a.querySelectorAll('td')[colIdx];
    const bTd = b.querySelectorAll('td')[colIdx];
    if (!aTd || !bTd) return 0;
    let aText = aTd.textContent.trim();
    let bText = bTd.textContent.trim();

    const aNum = parseFloat(aText.replace(/[^0-9.,]/g, '').replace(',', '.'));
    const bNum = parseFloat(bText.replace(/[^0-9.,]/g, '').replace(',', '.'));
    if (!isNaN(aNum) && !isNaN(bNum)) {
      return (aNum - bNum) * dir;
    }
    return aText.localeCompare(bText, 'ru') * dir;
  });

  dataRows.forEach(r => tbody.appendChild(r));
  footerRows.forEach(r => tbody.appendChild(r));

  table.dataset.sortCol = colIdx;
  table.dataset.sortDir = isAsc ? 'desc' : 'asc';

  headers.forEach((h, i) => {
    const text = h.textContent.replace(/ [▲▼]$/, '');
    h.textContent = text;
  });
  const arrow = isAsc ? ' ▲' : ' ▼';
  headers[colIdx].textContent += arrow;
}

function filterDetailTable() {
  const table = document.getElementById('feat-detail-table');
  const tbody = table.querySelector('tbody');
  const seg = document.getElementById('filter-seg').value;
  const emp = document.getElementById('filter-emp').value;
  const route = document.getElementById('filter-route').value;
  const cap = document.getElementById('filter-cap').value;
  const rows = tbody.querySelectorAll('tr');

  rows.forEach(r => {
    const cells = r.querySelectorAll('td');
    if (!cells.length) { r.style.display = ''; return; }

    // сегмент
    const segBadge = cells[5].querySelector('.badge');
    if (seg && segBadge && segBadge.textContent.trim() !== seg) { r.style.display = 'none'; return; }

    // сотрудники
    if (emp) {
      const v = parseFloat(cells[2].textContent.trim()) || 0;
      const [op, val] = emp.split('|');
      const nv = parseFloat(val);
      if (op === 'gt' && !(v > nv)) { r.style.display = 'none'; return; }
      if (op === 'lt' && !(v < nv)) { r.style.display = 'none'; return; }
      if (op === 'eq' && !(v >= nv && v < nv + 1)) { r.style.display = 'none'; return; }
    }

    // маршруты
    if (route) {
      const v = parseFloat(cells[3].textContent.trim()) || 0;
      const [op, val] = route.split('|');
      const nv = parseFloat(val);
      if (op === 'gt' && !(v > nv)) { r.style.display = 'none'; return; }
      if (op === 'lt' && !(v < nv)) { r.style.display = 'none'; return; }
    }

    // вместимость
    if (cap) {
      const v = parseFloat(cells[4].textContent.trim()) || 0;
      const [op, val] = cap.split('|');
      const nv = parseFloat(val);
      if (op === 'gt' && !(v > nv)) { r.style.display = 'none'; return; }
      if (op === 'lt' && !(v < nv)) { r.style.display = 'none'; return; }
    }

    r.style.display = '';
  });
}
</script>
"""


def _build_segment_table(rows):
    rows_html = ""
    total = sum(int(r["count"]) for r in rows)
    for r in rows:
        seg = r["segment"]
        count = int(r["count"])
        pct = float(r["percentage"])
        bar_w = pct * 2.5
        desc = r.get("description", "")
        files = r.get("files", "")
        if seg == "Не определено" and files:
            desc += " — Компании: " + files
        color = _seg_color(seg)
        rows_html += f"""
        <tr>
            <td><strong style="color:{color}">{seg}</strong></td>
            <td>{count}</td>
            <td>{pct}%</td>
            <td><div class="bar" style="width:{bar_w}px;background:{color}"></div></td>
            <td style="font-size:12px;color:#666">{desc}</td>
        </tr>"""
    rows_html += f"""
        <tr style="font-weight:700;background:#f5f5f5">
            <td>Итого</td><td>{total}</td><td>100%</td><td></td><td></td>
        </tr>"""
    return rows_html, total


def _build_features_table(rows):
    html = ""
    for r in rows:
        seg = r.get("segment", "")
        glonass = "🛰" if r.get("has_glonass") == "да" else ""
        cond = "❄" if r.get("has_conditioner") == "да" else ""
        med = "🏥" if r.get("has_medical_check") == "да" else ""
        sec = "🔒" if r.get("has_security_requirements") == "да" else ""
        driver = "👤" if r.get("has_driver_requirements") == "да" else ""
        icons = f"{glonass}{cond}{med}{sec}{driver}"
        emp = r.get("employees_count", "").strip()
        route = r.get("route_count", "").strip()
        cap = r.get("bus_capacity", "").strip()
        color = _seg_color(seg)
        html += f"""
        <tr>
            <td style="max-width:250px;word-break:break-all">{r.get('filename','')}</td>
            <td style="font-size:16px">{icons}</td>
            <td class="num-col">{emp}</td>
            <td class="num-col">{route}</td>
            <td class="num-col">{cap}</td>
            <td><span class="badge" style="background:{color}15;color:{color};border:1px solid {color}30">{seg}</span></td>
        </tr>"""
    return html


def _build_feature_stats_total(rows):
    html = ""
    for r in rows:
        feat = r["feature"]
        count = r["count"]
        pct = r["pct"]
        bar_w = float(pct) * 2
        if feat == "Хотя бы один признак":
            html += f"""
            <tr style="font-weight:700;background:#e8f5e9">
                <td><strong>{feat}</strong></td>
                <td><strong>{count}</strong></td>
                <td><strong>{pct}%</strong></td>
                <td><div class="bar" style="width:{bar_w}px;background:#2e7d32"></div></td>
            </tr>"""
        elif feat == "Без единого признака":
            html += f"""
            <tr style="font-weight:700;background:#fbe9e7">
                <td><strong>{feat}</strong></td>
                <td><strong>{count}</strong></td>
                <td><strong>{pct}%</strong></td>
                <td><div class="bar" style="width:{bar_w}px;background:#c62828"></div></td>
            </tr>"""
        else:
            html += f"""
            <tr>
                <td>{feat}</td>
                <td>{count}</td>
                <td>{pct}%</td>
                <td><div class="bar" style="width:{bar_w}px;background:#1565c0"></div></td>
            </tr>"""
    return html


def _build_feature_stats_by_segment(rows):
    if not rows:
        return "", ""
    headers = list(rows[0].keys())
    thead = "<tr>"
    for h in headers:
        label = "Сегмент" if h == "segment" else h
        thead += f"<th>{label}</th>"
    thead += "</tr>"
    tbody = ""
    for r in rows:
        tbody += "<tr>"
        for h in headers:
            v = r[h]
            if h == "segment":
                color = _seg_color(v)
                if v == "ИТОГО":
                    tbody += f'<td style="font-weight:700;background:#f5f5f5">{v}</td>'
                else:
                    tbody += f'<td><strong style="color:{color}">{v}</strong></td>'
            else:
                tbody += f"<td>{v}</td>"
        tbody += "</tr>"
    return thead, tbody


def _build_feature_presence_table(rows):
    html = ""
    for r in rows:
        status = r.get("status", "")
        company = r.get("company", "")
        seg = r.get("segment", "")
        color = _seg_color(seg)
        if status == "Есть признаки":
            row_class = ""
            status_display = "✅ Есть признаки"
        else:
            row_class = 'style="background:#fff3f0"'
            status_display = "❌ Нет признаков"
        html += f"""
        <tr {row_class}>
            <td>{status_display}</td>
            <td>{company}</td>
            <td><span class="badge" style="background:{color}15;color:{color};border:1px solid {color}30">{seg}</span></td>
        </tr>"""
    return html


def _build_segment_options(rows):
    segs = sorted(set(r.get("segment", "") for r in rows if r.get("segment")))
    opts = '<option value="">Все сегменты</option>'
    for s in segs:
        opts += f'<option value="{s}">{s}</option>'
    return opts


def run(source_dir, results_dir):
    seg_rows = _read_csv(results_dir / "segmentation.csv") or []
    feat_rows = _read_csv(results_dir / "content_features.csv") or []
    feat_total_rows = _read_csv(results_dir / "feature_stats_total.csv") or []
    feat_by_seg_rows = _read_csv(results_dir / "feature_stats_by_segment.csv") or []
    feat_presence_rows = _read_csv(results_dir / "feature_presence.csv") or []

    seg_table, seg_total = _build_segment_table(seg_rows) or ("<tr><td colspan=5>Нет данных</td></tr>", 0)
    feat_table = _build_features_table(feat_rows) or "<tr><td colspan=6>Нет данных</td></tr>"
    feat_total_html = _build_feature_stats_total(feat_total_rows) or "<tr><td colspan=4>Нет данных</td></tr>"
    feat_by_seg_thead, feat_by_seg_tbody = _build_feature_stats_by_segment(feat_by_seg_rows) or ("<tr><td colspan=6>Нет данных</td></tr>", "")
    seg_options = _build_segment_options(feat_rows)
    feat_presence_table = _build_feature_presence_table(feat_presence_rows) or "<tr><td colspan=3>Нет данных</td></tr>"
    _eis_seg_rows = _read_csv(results_dir / "segmentation.csv") or []
    eis_total = 0
    eis_companies = 0
    eis_with_features = 0
    eis_seg_table = "<tr><td colspan=5>Нет данных. Запустите python3 -m scripts.fetch_eis для загрузки тендеров.</td></tr>"
    eis_feat_thead = ""
    eis_feat_tbody = ""
    eis_feat_by_seg_thead = ""
    eis_feat_by_seg_tbody = ""

    # Если есть отчёт ЕИС — используем его
    _eis_json = results_dir / "eis_fetch_report.json"
    if _eis_json.exists():
        try:
            import json
            _ed = json.loads(_eis_json.read_text(encoding='utf-8'))
            eis_total = _ed.get("total_found", 0)
            eis_companies = eis_total
            eis_with_features = eis_total
            _od = _ed.get("org_type_distribution", {})
            _rows = ""
            for _ot, _cnt in sorted(_od.items(), key=lambda x: -x[1]):
                _pct = round(_cnt / eis_total * 100, 1) if eis_total else 0
                _bw = _pct * 2.5
                _c = {"МУП/МБУ":"#00838f","ФГУП/ФБУЗ":"#c62828","АО/ПАО":"#1565c0","ООО":"#2e7d32","Госорган":"#e65100","Прочие":"#78909c"}.get(_ot,"#78909c")
                _rows += f'<tr><td><strong style="color:{_c}">{_ot}</strong></td><td>{_cnt}</td><td>{_pct}%</td><td><div class="bar" style="width:{_bw}px;background:{_c}"></div></td><td style="font-size:12px;color:#666">Госзакупки</td></tr>'
            _rows += f'<tr style="font-weight:700;background:#f5f5f5"><td>Итого</td><td>{eis_total}</td><td>100%</td><td></td><td></td></tr>'
            eis_seg_table = _rows
        except Exception:
            pass


    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    src_name = source_dir.name

    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Сегментация заказчиков — корпоративные перевозки</title>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f0f2f5; color: #333; padding: 20px; }}
.container {{ max-width: 1400px; margin: 0 auto; }}
h1 {{ font-size: 26px; margin-bottom: 4px; }}
.subtitle {{ color: #666; margin-bottom: 25px; font-size: 14px; }}
.cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; margin-bottom: 30px; }}
.card {{ background: #fff; border-radius: 10px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,.1); }}
.card h3 {{ font-size: 13px; color: #888; text-transform: uppercase; letter-spacing: .5px; }}
.card .value {{ font-size: 30px; font-weight: 700; margin-top: 5px; }}
.section {{ background: #fff; border-radius: 10px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,.1); margin-bottom: 25px; }}
.section h2 {{ font-size: 20px; margin-bottom: 15px; border-bottom: 2px solid #f0f2f5; padding-bottom: 10px; }}
table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
thead th {{ text-align: left; padding: 8px 6px; border-bottom: 2px solid #eee; font-weight: 600; color: #555; white-space: nowrap; user-select: none; position: sticky; top: 0; background: #fff; z-index: 1; }}
thead th:hover {{ background: #e3f2fd; }}
td {{ padding: 6px; border-bottom: 1px solid #f0f2f5; vertical-align: top; }}
tr:hover td {{ background: #f8f9fa; }}
.bar {{ height: 18px; border-radius: 9px; min-width: 4px; }}
.badge {{ display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 600; white-space: nowrap; }}
.scroll {{ max-height: 700px; overflow-y: auto; border: 1px solid #f0f2f5; border-radius: 8px; }}
.seg-desc {{ background: #fafafa; border-left: 4px solid; padding: 12px 16px; margin: 8px 0; border-radius: 0 8px 8px 0; font-size: 13px; line-height: 1.5; }}
.compact td {{ padding: 5px 6px; font-size: 12px; }}
.sort-hint {{ font-size: 11px; color: #999; margin-top: 6px; }}
.filter-row {{ display: flex; align-items: center; gap: 10px; margin-bottom: 12px; flex-wrap: wrap; }}
.filter-row select, .filter-row input {{ padding: 6px 10px; border: 1px solid #ccc; border-radius: 6px; font-size: 13px; background: #fff; }}
.filter-row label {{ font-size: 13px; font-weight: 500; }}
.filter-row .sep {{ color: #ccc; }}

.num-col {{ text-align: center; }}
</style>
{SORT_JS}
</head>
<body onload="setupSort('seg-table');setupSort('feat-total-table');setupSort('feat-by-seg-table');setupSort('feat-detail-table');setupSort('feature-presence-table')">
<div class="container">

<h1>🎯 Сегментация заказчиков корпоративных перевозок</h1>
<p class="subtitle">Сгенерировано: {now} | Источник: {src_name}</p>

<div class="cards">
    <div class="card"><h3>Всего документов</h3><div class="value">{seg_total}</div></div>
    <div class="card"><h3>Сегментов</h3><div class="value">{len(seg_rows)}</div></div>
    <div class="card"><h3>С извлечёнными признаками</h3><div class="value">{len(feat_rows)}</div></div>
</div>

<!-- ========== СЕГМЕНТАЦИЯ ========== -->
<div class="section">
    <h2>📊 Распределение по сегментам</h2>
    <p class="sort-hint">🔄 Кликните на заголовок столбца для сортировки</p>
    <table id="seg-table">
        <thead><tr><th>Сегмент</th><th>Кол-во</th><th>Доля</th><th></th><th>Описание</th></tr></thead>
        <tbody>{seg_table}</tbody>
    </table>
</div>

<!-- ========== ХАРАКТЕРИСТИКА СЕГМЕНТОВ ========== -->
<div class="section">
    <h2>📖 Характеристика сегментов</h2>
    <div class="seg-desc" style="border-left-color:#1565c0">
        <strong style="color:#1565c0">🏭 Промышленность</strong> — Крупные промышленные предприятия и заводы (АвтоВАЗ, РМИ-Сталь, Трубная металлургическая компания, РН-Проектирование). Большое количество сотрудников, строгие требования к безопасности и охране труда. Долгосрочные контракты. Автобусы большой вместимости (от 35 мест). Обязательны медосмотры, ГЛОНАСС, кондиционеры.
    </div>
    <div class="seg-desc" style="border-left-color:#e65100">
        <strong style="color:#e65100">🛒 Торговля/Производство</strong> — Компании сферы торговли и производства продуктов (МАКФА, Метро, Фаберлик, Казанский жировой комбинат, Экоальянс). Доставка на производственные площадки и склады. Сезонность закупок, сменный режим. Требования к комфорту: кондиционеры, состояние салона.
    </div>
    <div class="seg-desc" style="border-left-color:#2e7d32">
        <strong style="color:#2e7d32">📦 Логистика/Почта</strong> — Почтовые и логистические операторы (Почта России, СДЭК). Круглосуточная работа, сортировочные центры, доставка сотрудников к месту работы в любое время суток. Большое количество маршрутов. Требования: мобильная связь для водителей, опрятный внешний вид.
    </div>
    <div class="seg-desc" style="border-left-color:#00838f">
        <strong style="color:#00838f">🏗 Строительство</strong> — Строительные и инфраструктурные компании (Стройтранснефтегаз, Трансинжстрой, Капстрой). Вахтовый метод, удалённые объекты, междугородние перевозки. Повышенные требования к безопасности.
    </div>
    <div class="seg-desc" style="border-left-color:#c62828">
        <strong style="color:#c62828">🏛 Госсектор</strong> — Государственные и унитарные предприятия, госкорпорации (Росатом, ФГУП по ОрВД, Россети). Закупки по 223-ФЗ. Формализованная тендерная документация. Требования к конфиденциальности, безопасности, строгая отчётность.
    </div>
    <div class="seg-desc" style="border-left-color:#4e342e">
        <strong style="color:#4e342e">🚛 Транспорт/Перевозки</strong> — Транспортные компании, участвующие в тендерах как подрядчики (Деловые линии). Сами являются предметом закупки, а не заказчиками.
    </div>
    <div class="seg-desc" style="border-left-color:#6a1b9a">
        <strong style="color:#6a1b9a">💻 IT/Услуги</strong> — IT-компании и сервисные организации (Озон, Эрманн). Доставка офисных сотрудников по стандартным маршрутам. Упор на комфорт и пунктуальность. Стандартная рабочая неделя.
    </div>
</div>

<!-- ========== СВОДКА ПРИЗНАКОВ ========== -->
<div class="section">
    <h2>📈 Какие признаки удалось извлечь (из {seg_total} документов)</h2>
    <p class="sort-hint">🔄 Кликните на заголовок столбца для сортировки</p>
    <table id="feat-total-table">
        <thead><tr><th>Признак</th><th>Кол-во</th><th>Доля</th><th></th></tr></thead>
        <tbody>{feat_total_html}</tbody>
    </table>
</div>

<!-- ========== СПИСОК КОМПАНИЙ С ПРИЗНАКАМИ ========== -->
<div class="section">
    <h2>📋 Компании с признаками и без</h2>
    <p style="font-size:13px;color:#666;margin-bottom:12px">
        Компании, у которых удалось извлечь хотя бы один признак (бинарный или числовой), и компании без единого извлечённого признака.
    </p>
    <p class="sort-hint">🔄 Кликните на заголовок столбца для сортировки</p>
    <table id="feature-presence-table">
        <thead><tr><th>Статус</th><th>Компания</th><th>Сегмент</th></tr></thead>
        <tbody>{feat_presence_table}</tbody>
    </table>
</div>

<!-- ========== СТАТИСТИКА ПО СЕГМЕНТАМ ========== -->
<div class="section">
    <h2>📋 Признаки по сегментам</h2>
    <p class="sort-hint">🔄 Кликните на заголовок столбца для сортировки</p>
    <p style="font-size:13px;color:#666;margin-bottom:12px">
        Сколько документов в каждом сегменте содержат указанный признак.
        <strong>«Хотя бы один»</strong> — документы, где извлечён хотя бы 1 признак.
        <strong>«Без единого»</strong> — документы, где не извлечено ничего (пустой текст, .doc, скриншот pdf).
    </p>
    <div class="scroll">
    <table id="feat-by-seg-table">
        <thead>{feat_by_seg_thead}</thead>
        <tbody>{feat_by_seg_tbody}</tbody>
    </table>
    </div>
</div>

<!-- ========== ПРИЗНАКИ ПО ДОКУМЕНТАМ ========== -->
<div class="section">
    <h2>🔍 Детальные признаки по каждому документу</h2>
    <div class="filter-row">
        <label>Сегмент:</label>
        <select id="filter-seg" onchange="filterDetailTable()">
            {seg_options}
        </select>
        <span class="sep">|</span>
        <label>👥 Сотрудники:</label>
        <select id="filter-emp" onchange="filterDetailTable()">
            <option value="">Любое</option>
            <option value="gt|0">> 0</option>
            <option value="gt|10">> 10</option>
            <option value="gt|50">> 50</option>
            <option value="gt|100">> 100</option>
            <option value="gt|200">> 200</option>
        </select>
        <span class="sep">|</span>
        <label>🛣 Маршруты:</label>
        <select id="filter-route" onchange="filterDetailTable()">
            <option value="">Любое</option>
            <option value="gt|0">> 0</option>
            <option value="gt|1">> 1</option>
            <option value="gt|3">> 3</option>
            <option value="gt|5">> 5</option>
        </select>
        <span class="sep">|</span>
        <label>🚌 Вместимость:</label>
        <select id="filter-cap" onchange="filterDetailTable()">
            <option value="">Любое</option>
            <option value="gt|0">> 0</option>
            <option value="gt|19">> 19</option>
            <option value="gt|35">> 35</option>
            <option value="gt|50">> 50</option>
        </select>
    </div>
    <p class="sort-hint">🔄 Кликните на заголовок столбца для сортировки</p>
    <div class="scroll">
    <table id="feat-detail-table">
        <thead><tr>
            <th>Название компании</th><th>Требования</th><th>👥 Сотр.</th><th>🛣 Маршр.</th><th>🚌 Вмест.</th><th>Сегмент</th>
        </tr></thead>
        <tbody>{feat_table}</tbody>
    </table>
    </div>
    <p style="margin-top:8px;font-size:12px;color:#888">
        🛰 ГЛОНАСС &nbsp;❄ Кондиционер &nbsp;🏥 Медосмотр &nbsp;🔒 Безопасность &nbsp;👤 Требования к водителю
    </p>
</div>

</div>
</body>
</html>"""

    out_path = results_dir / "report.html"
    with open(str(out_path), "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[report] HTML report saved to {out_path}")
    webbrowser.open(f"file://{out_path.resolve()}")
