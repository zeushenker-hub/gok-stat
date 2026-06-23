from pathlib import Path
from typing import List, Tuple
import re

from scripts.shared import SOURCE_DIR


CITY_KEYWORDS = {
    "москв": "Москва",
    "московск": "Московская область",
    "питер": "Санкт-Петербург",
    "санкт": "Санкт-Петербург",
    "ленинградск": "Ленинградская область",
    "казан": "Татарстан",
    "татарстан": "Татарстан",
    "екатеринбург": "Свердловская область",
    "екат": "Свердловская область",
    "новосиб": "Новосибирская область",
    "краснояр": "Красноярский край",
    "самар": "Самарская область",
    "тольятти": "Самарская область",
    "автоваз": "Самарская область",
    "нижн": "Нижегородская область",
    "ростов": "Ростовская область",
    "уф": "Республика Башкортостан",
    "башкортостан": "Республика Башкортостан",
    "перм": "Пермский край",
    "челяб": "Челябинская область",
    "краснодар": "Краснодарский край",
    "воронеж": "Воронежская область",
    "владимир": "Владимирская область",
    "твер": "Тверская область",
    "тул": "Тульская область",
    "калуж": "Калужская область",
    "рязан": "Рязанская область",
    "ярослав": "Ярославская область",
    "иванов": "Ивановская область",
    "костром": "Костромская область",
    "псков": "Псковская область",
    "новгород": "Новгородская область",
    "вологод": "Вологодская область",
    "архангел": "Архангельская область",
    "мурман": "Мурманская область",
    "петрозавод": "Республика Карелия",
    "карели": "Республика Карелия",
    "сыктывкар": "Республика Коми",
    "киров": "Кировская область",
    "марий": "Республика Марий Эл",
    "саран": "Республика Мордовия",
    "пенз": "Пензенская область",
    "саратов": "Саратовская область",
    "ульянов": "Ульяновская область",
    "чуваш": "Чувашская Республика",
    "чебоксар": "Чувашская Республика",
    "оренбург": "Оренбургская область",
    "удмурт": "Удмуртская Республика",
    "ижевск": "Удмуртская Республика",
    "курган": "Курганская область",
    "тюмен": "Тюменская область",
    "ханты": "Ханты-Мансийский АО",
    "ямал": "Ямало-Ненецкий АО",
    "сургут": "Ханты-Мансийский АО",
    "томск": "Томская область",
    "кемеров": "Кемеровская область",
    "иркут": "Иркутская область",
    "бурят": "Республика Бурятия",
    "забайкал": "Забайкальский край",
    "амур": "Амурская область",
    "хабаров": "Хабаровский край",
    "примор": "Приморский край",
    "владивосток": "Приморский край",
}


def classify_region(filepath: Path) -> str:
    rel = filepath.relative_to(SOURCE_DIR)
    text = str(rel).lower()
    for keyword, region in CITY_KEYWORDS.items():
        if keyword in text:
            return region
    return "Не определено"


def run(source_dir: Path, results_dir: Path) -> None:
    from scripts.shared import get_all_files

    files = get_all_files()
    from collections import Counter
    region_counter: Counter = Counter()
    details = []
    for fp in files:
        if not fp.is_file():
            continue
        region = classify_region(fp)
        region_counter[region] += 1
        details.append((fp.name, region))

    out_path = results_dir / "geo_stats.csv"
    total = sum(region_counter.values())
    with open(str(out_path), "w", encoding="utf-8") as f:
        f.write("region,count,percentage\n")
        for region, count in sorted(region_counter.items(), key=lambda x: -x[1]):
            pct = round(count / total * 100, 1)
            f.write(f'"{region}",{count},{pct}\n')

    details_path = results_dir / "geo_details.csv"
    with open(str(details_path), "w", encoding="utf-8") as f:
        f.write("filename,region\n")
        for name, region in details:
            safe_name = name.replace('"', '""')
            safe_region = region.replace('"', '""')
            f.write(f'"{safe_name}","{safe_region}"\n')

    print(f"[geo] Classified {len(details)} files into {len(region_counter)} regions")
    print(f"[geo] Wrote summary to {out_path}, details to {details_path}")
