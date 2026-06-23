"""
Парсер метаданных тендеров с zakupki.gov.ru (ЕИС).
Собирает названия, заказчиков, номера тендеров по ключевым словам.
Файлы ТЗ недоступны без авторизации, но метаданные дают аналитику.
"""
import requests
import re
import json
import urllib.parse
import time
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter


RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
SOURCE_EIS_DIR = Path(__file__).resolve().parent.parent / "source_eis"

SEARCH_QUERY = "перевозка сотрудников"

# Ключевые слова для фильтрации результатов
INCLUDE_PATTERNS = [
    r"перевоз.*сотрудник", r"фрахт.*транспорт", r"корпорат.*перевоз",
    r"работн.*перевоз", r"перевозк.*работник", r"доставк.*сотрудник",
    r"транспортн.*услуг.*сотрудник", r"автобус.*перевоз",
    r"фрахтовани.*автобус", r"пассажирск.*перевозк",
    r"перевозк.*пассажир", r"автотранспортн.*услуг",
]

# Паттерны исключения
EXCLUDE_PATTERNS = [
    r"авиа", r"авиаперевоз", r"авиабилет", r"воздушн",
    r"железнодорожн", r"груз", r"дет", r"багаж", r"морск",
    r"обуч", r"постав", r"охран", r"подготов", r"продукц",
    r"такс", r"метропол", r"транспорт.*карт", r"страхован",
    r"оспаго", r"оспалате",
]


def match_keywords(text: str) -> bool:
    text_lower = text.lower()
    included = any(re.search(pat, text_lower) for pat in INCLUDE_PATTERNS)
    if not included:
        return False
    return not any(re.search(pat, text_lower) for pat in EXCLUDE_PATTERNS)


def _parse_tenders_from_html(html: str) -> list:
    """Парсит HTML-страницу результатов поиска."""
    blocks = re.split(r'class="row no-gutters registry-entry__form mr-0"', html)
    tenders = []

    for block in blocks[1:]:
        reg = re.search(r'regNumber=(\d+)', block)
        if not reg:
            continue
        reg_number = reg.group(1)

        # Название закупки
        name_match = re.search(
            r'Объект закупки</div>\s*<div[^>]*class="registry-entry__body-value"[^>]*>(.*?)</div>',
            block, re.DOTALL,
        )
        name = ""
        if name_match:
            name = re.sub(r'<[^>]+>', '', name_match.group(1)).strip()

        # Заказчик
        org_match = re.search(r'class="registry-entry__body-value"[^>]*>([^<]+)', block)
        org = org_match.group(1).strip() if org_match else ""

        # Ссылка
        href_match = re.search(r'href="(/epz/order/notice/[^"]+)', block)

        combined = (name + " " + org).lower()

        if match_keywords(combined):
            tenders.append({
                "regNumber": reg_number,
                "name": name,
                "orgName": org,
                "href": "https://zakupki.gov.ru" + href_match.group(1) if href_match else "",
            })

    return tenders


def run():
    SOURCE_EIS_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    print("=== Парсинг ЕИС (zakupki.gov.ru) ===")
    print(f"Поиск: '{SEARCH_QUERY}'")

    all_tenders = []
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
    date_from = (datetime.now() - timedelta(days=60)).strftime("%d.%m.%Y")
    date_to = datetime.now().strftime("%d.%m.%Y")
    search_encoded = urllib.parse.quote(SEARCH_QUERY)

    for page in range(1, 4):
        print(f"\nСтраница {page}:")
        url = (
            "https://zakupki.gov.ru/epz/order/extendedsearch/results.html"
            f"?fz44=on&fz223=on"
            f"&searchString={search_encoded}"
            f"&morphology=on"
            f"&pageNumber={page}"
            f"&sortBy=UPDATE_DATE"
            f"&sortDirection=false"
            f"&recordsPerPage=_50"
            f"&showLotsInfoHidden=false"
            f"&publishDateFrom={date_from}"
            f"&publishDateTo={date_to}"
        )

        try:
            resp = requests.get(url, headers=headers, timeout=30)
            if resp.status_code != 200:
                print(f"  HTTP {resp.status_code}")
                break

            tenders = _parse_tenders_from_html(resp.text)
            if not tenders:
                print("  Нет подходящих тендеров")
                break

            all_tenders.extend(tenders)
            for t in tenders:
                print(f"  [{t['regNumber']}] {t['name'][:80]}")
                print(f"      Заказчик: {t['orgName'][:60]}")

            time.sleep(1)

        except requests.RequestException as e:
            print(f"  Ошибка: {e}")
            break

    # Сохраняем метаданные
    eis_dir = SOURCE_EIS_DIR / f"eis_import_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    eis_dir.mkdir(parents=True, exist_ok=True)

    meta_file = eis_dir / "tenders_meta.json"
    meta_file.write_text(json.dumps(all_tenders, ensure_ascii=False, indent=2))
    print(f"\nМетаданные: {meta_file}")

    # Аналитика
    org_types = Counter()
    regions = Counter()
    for t in all_tenders:
        org = t["orgName"].lower()
        if "муп" in org or "мбУ" in org:
            org_types["МУП/МБУ"] += 1
        elif "фбуз" in org or "фгуп" in org:
            org_types["ФГУП/ФБУЗ"] += 1
        elif "ао" in org or "пао" in org:
            org_types["АО/ПАО"] += 1
        elif "ооо" in org:
            org_types["ООО"] += 1
        elif "администраци" in org or "управление" in org or "департамент" in org:
            org_types["Госорган"] += 1
        else:
            org_types["Прочие"] += 1

    # Отчёт
    report = {
        "date": datetime.now().isoformat(),
        "source": "zakupki.gov.ru",
        "search_query": SEARCH_QUERY,
        "period": f"{date_from} - {date_to}",
        "total_found": len(all_tenders),
        "org_type_distribution": dict(org_types.most_common()),
    }
    report_file = RESULTS_DIR / "eis_fetch_report.json"
    report_file.write_text(json.dumps(report, ensure_ascii=False, indent=2))

    print(f"\n=== Итого ===")
    print(f"Найдено подходящих тендеров: {len(all_tenders)}")
    print(f"Папка: {eis_dir}")
    print(f"Отчёт: {report_file}")
    print(f"\nТипы заказчиков:")
    for ot, count in org_types.most_common():
        print(f"  {ot}: {count}")

    return all_tenders


if __name__ == "__main__":
    run()
