"""
Извлечение структурированных признаков из текста тендерных документов
для последующей сегментации заказчиков корпоративных перевозок.
"""
import re
from pathlib import Path
from typing import Dict, List, Optional, Any


# Паттерны для извлечения ключевых признаков из ТЗ
PATTERNS = {
    "company_name": re.compile(
        r'(?:ООО|АО|ПАО|ФГУП|ГК|ЗАО)\s[«"]?([А-ЯЁ][^«»"()]+?)[»"]?',
        re.IGNORECASE,
    ),
    "employees_count": re.compile(
        r'(?:количеств[оа]\s+(?:человек|работников|сотрудников|персонала)\s*(?:в\s+количестве|:)?\s*)?(\d{2,5})\s*(?:чел|человек|работник|сотрудник)',
        re.IGNORECASE,
    ),
    "bus_count": re.compile(
        r'(\d+)\s*(?:единиц|автобус(?:а|ов)|транспортных\s+средств|машин)',
        re.IGNORECASE,
    ),
    "route_count": re.compile(
        r'(\d+)\s*(?:маршрут(?:а|ов)|направлени(?:й|я))',
        re.IGNORECASE,
    ),
    "contract_duration": re.compile(
        r'(?:срок|период|длительность|действие)\s+(?:оказания|действия|договора)?\s*[:\s]+(.{10,60}?(?:дн|месяц|год|лет|календарны))',
        re.IGNORECASE,
    ),
    "tender_number": re.compile(
        r'(?:тендер|закупк|№|номер)\s*[:\s]*(\d{5,})',
        re.IGNORECASE,
    ),
    "region_city": re.compile(
        r'(?:г\.\s*|город\s*|в\s+г\.|г\s+)([А-ЯЁ][а-яё]+(?:[-\s][А-ЯЁ][а-яё]+)*)',
    ),
    "bus_capacity": re.compile(
        r'(?:вместимость(?:ю|)|количеств[оа]\s+мест|пассажировместимость)[\s:]*\(?(\d{2,3})\s*(?:мест|чел|пассажир)',
        re.IGNORECASE,
    ),
    "work_schedule": re.compile(
        r'(?:режим\s+работы|график|смен[а-я]{1,3}|понедельника\s+по\s+(?:пятницу|воскресенье)|(?:ежедневн[а-я]{2,3}|круглосуточн[а-я]{1,3}))',
        re.IGNORECASE,
    ),
    "has_glonass": re.compile(r'(?:эра[- ]?глонасс|глонасс|систем[а-я]{2,5}\s+мониторинг)', re.IGNORECASE),
    "has_conditioner": re.compile(r'кондиционер', re.IGNORECASE),
    "has_medical_check": re.compile(r'(?:предрейсов[а-я]{2,5}\s+медицинск|медосмотр)', re.IGNORECASE),
    "has_security_requirements": re.compile(
        r'(?:требовани[яе]\s+(?:к\s+)?безопасност|безопасность\s+перевозок|охран)',
        re.IGNORECASE,
    ),
    "has_driver_requirements": re.compile(
        r'(?:требовани[яе]\s+к\s+водител|стаж\s+работы\s+водител|водител[ья]\s+должн)',
        re.IGNORECASE,
    ),
}


def _csv_safe(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, bool):
        return "да" if v else ""
    s = str(v)
    s = s.replace("\n", " ").replace("\r", " ").replace('"', '""')
    return s


def extract_features(text: str, filename: str = "") -> Dict[str, Any]:
    """
    Извлекает структурированные признаки из текста ТЗ.
    Возвращает словарь с найденными характеристиками.
    """
    features: Dict[str, Any] = {
        "filename": filename,
        "company_name": "",
        "employees_count": None,
        "bus_count": None,
        "route_count": None,
        "contract_duration": "",
        "tender_number": "",
        "region_city": "",
        "bus_capacity": None,
        "work_schedule": "",
        "has_glonass": False,
        "has_conditioner": False,
        "has_medical_check": False,
        "has_security_requirements": False,
        "has_driver_requirements": False,
        "text_preview": text[:200].replace("\n", " ").replace("\r", " ").strip(),
    }

    for key, pattern in PATTERNS.items():
        if key == "company_name":
            match = pattern.search(text[:5000])
        else:
            match = pattern.search(text)
        if match:
            if key in ("has_glonass", "has_conditioner", "has_medical_check",
                       "has_security_requirements", "has_driver_requirements"):
                features[key] = True
            elif key in ("employees_count", "bus_count", "route_count", "bus_capacity"):
                features[key] = int(match.group(1))
            elif key == "contract_duration":
                features[key] = match.group(1).strip()[:100]
            elif key == "tender_number":
                features[key] = match.group(1)
            elif key == "region_city":
                features[key] = match.group(1).strip()
            elif key == "work_schedule":
                features[key] = match.group(0).strip()[:80]
            else:
                features[key] = match.group(0).strip()[:100]

    return features


def features_to_csv_row(features: Dict[str, Any]) -> str:
    """Преобразует словарь признаков в строку CSV."""
    vals = []
    for key in _CSV_COLUMNS:
        sv = _csv_safe(features.get(key, ""))
        vals.append(f'"{sv}"')
    return ",".join(vals)


_BOOL_FEATURES = [
    "has_glonass", "has_conditioner", "has_medical_check",
    "has_security_requirements", "has_driver_requirements",
]

_BOOL_LABELS_SHORT = {
    "has_glonass": "ГЛОНАСС",
    "has_conditioner": "Кондиционер",
    "has_medical_check": "Медосмотр",
    "has_security_requirements": "Безопасность",
    "has_driver_requirements": "Требования к водителю",
}

_BOOL_LABELS_ICON = {
    "has_glonass": "🛰 ГЛОНАСС",
    "has_conditioner": "❄ Кондиционер",
    "has_medical_check": "🏥 Медосмотр",
    "has_security_requirements": "🔒 Безопасность",
    "has_driver_requirements": "👤 Треб. к водителю",
}

_NUMERIC_FEATURES = [
    "employees_count", "bus_count", "route_count", "bus_capacity",
]


_CSV_COLUMNS = [
    "filename",
    "company_name",
    "employees_count",
    "bus_count",
    "route_count",
    "contract_duration",
    "tender_number",
    "region_city",
    "bus_capacity",
    "work_schedule",
    "has_glonass",
    "has_conditioner",
    "has_medical_check",
    "has_security_requirements",
    "has_driver_requirements",
    "text_preview",
]


CSV_HEADER = ",".join(f'"{c}"' for c in _CSV_COLUMNS)
