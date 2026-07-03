import urllib.request, json, urllib.parse
from datetime import datetime, timezone, timedelta

SHEET_ID = '15PKewFsJYH99OLeC5LvIcHrt9W9tjFBl1067-yVDJAY'
TZ = timezone(timedelta(hours=4))

def fetch_sheet(sheet_name, column_map):
    url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:json&sheet={urllib.parse.quote(sheet_name)}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as r:
        raw = r.read().decode('utf-8')
    start = raw.index('{')
    end = raw.rindex('}') + 1
    data = json.loads(raw[start:end])
    rows = []
    for r in data['table']['rows']:
        c = r.get('c') or []
        row = {}
        for idx, key in column_map.items():
            if idx < len(c) and c[idx] and c[idx].get('v') is not None:
                v = c[idx]['v']
                row[key] = str(v) if isinstance(v, (int, float)) else v
            else:
                row[key] = None
        rows.append(row)
    return rows

GOK_COLUMNS = {
    0: 'company', 1: 'inn', 2: 'okved', 3: 'gendir',
    5: 'tel1', 6: 'tel2', 7: 'responsible',
    8: 'call1', 9: 'afterNdz', 10: 'lpr', 11: 'comment'
}

GRAD_COLUMNS = {
    0: 'company', 1: 'inn', 2: 'okved',
    3: 'region', 4: 'city', 5: 'gendir', 6: 'innGendir',
    7: 'tel1', 8: 'tel2', 9: 'responsible',
    10: 'call1', 11: 'afterNdz', 12: 'lpr',
    13: 'refusalReason', 14: 'meetingAppointed', 15: 'comment'
}

INTEGRATOR_COLUMNS = {
    0: 'integrator', 1: 'company', 2: 'inn', 3: 'okved',
    4: 'gendir', 5: 'innGendir', 6: 'tel1', 7: 'tel2',
    8: 'responsible', 9: 'call1', 10: 'afterNdz', 11: 'lpr',
    12: 'refusalReason', 13: 'meetingAppointed', 14: 'comment'
}

now = datetime.now(TZ).strftime('%d.%m.%Y, %H:%M:%S')

gok_rows = fetch_sheet('ГОК', GOK_COLUMNS)
grad_rows = fetch_sheet('Град', GRAD_COLUMNS)
integrator_rows = fetch_sheet('Интегратор', INTEGRATOR_COLUMNS)

with open('data.json', 'w', encoding='utf-8') as f:
    f.write('{"updated":"' + now + '","rows_gok":')
    json.dump(gok_rows, f, ensure_ascii=False)
    f.write(',"rows_grad":')
    json.dump(grad_rows, f, ensure_ascii=False)
    f.write(',"rows_integrator":')
    json.dump(integrator_rows, f, ensure_ascii=False)
    f.write('}')

print(f'OK: ГОК={len(gok_rows)}, Град={len(grad_rows)}, Интегратор={len(integrator_rows)}')
