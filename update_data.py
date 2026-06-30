import urllib.request, json, urllib.parse, os
from datetime import datetime, timezone, timedelta

SHEET_ID = '15PKewFsJYH99OLeC5LvIcHrt9W9tjFBl1067-yVDJAY'
TZ = timezone(timedelta(hours=4))
DIR = os.path.dirname(__file__)

SHEETS = [
    ('ГОК', os.path.join(DIR, 'data.json')),
    ('Град', os.path.join(DIR, 'data_grad.json')),
]

def fetch_sheet(sheet_name, output_path):
    url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:json&sheet={urllib.parse.quote(sheet_name)}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as r:
        raw = r.read().decode('utf-8')

    start = raw.index('{')
    end = raw.rindex('}') + 1
    data = json.loads(raw[start:end])

    cols = data['table']['cols']
    rows = []

    if sheet_name == 'ГОК':
        for r in data['table']['rows']:
            c = r.get('c') or []
            row = {}
            if len(c) > 0: row['company'] = c[0]['v'] if c[0] else ''
            if len(c) > 1: row['inn'] = str(c[1]['v']) if c[1] else ''
            if len(c) > 2: row['okved'] = str(c[2]['v']) if c[2] else ''
            if len(c) > 3: row['gendir'] = c[3]['v'] if c[3] else ''
            if len(c) > 5: row['tel1'] = str(c[5]['v']) if c[5] else ''
            if len(c) > 6: row['tel2'] = str(c[6]['v']) if c[6] else ''
            if len(c) > 7: row['responsible'] = c[7]['v'] if c[7] else None
            if len(c) > 8: row['call1'] = c[8]['v'] if c[8] else None
            if len(c) > 9: row['afterNdz'] = c[9]['v'] if c[9] else None
            if len(c) > 10: row['lpr'] = c[10]['v'] if c[10] else None
            if len(c) > 11: row['comment'] = c[11]['v'] if c[11] else None
            rows.append(row)
    elif sheet_name == 'Град':
        for r in data['table']['rows']:
            c = r.get('c') or []
            row = {}
            if len(c) > 0: row['company'] = c[0]['v'] if c[0] else ''
            if len(c) > 1: row['inn'] = str(c[1]['v']) if c[1] else ''
            if len(c) > 2: row['okved'] = str(c[2]['v']) if c[2] else ''
            if len(c) > 3: row['region'] = c[3]['v'] if c[3] else ''
            if len(c) > 4: row['city'] = c[4]['v'] if c[4] else ''
            if len(c) > 5: row['gendir'] = c[5]['v'] if c[5] else ''
            if len(c) > 6: row['innGendir'] = str(c[6]['v']) if c[6] else ''
            if len(c) > 7: row['tel1'] = str(c[7]['v']) if c[7] else ''
            if len(c) > 8: row['tel2'] = str(c[8]['v']) if c[8] else ''
            if len(c) > 9: row['responsible'] = c[9]['v'] if c[9] else None
            if len(c) > 10: row['call1'] = c[10]['v'] if c[10] else None
            if len(c) > 11: row['afterNdz'] = c[11]['v'] if c[11] else None
            if len(c) > 12: row['lpr'] = c[12]['v'] if c[12] else None
            if len(c) > 13: row['reason'] = c[13]['v'] if c[13] else None
            if len(c) > 14: row['meeting'] = c[14]['v'] if c[14] else None
            if len(c) > 15: row['comment'] = c[15]['v'] if c[15] else None
            rows.append(row)

    now = datetime.now(TZ).strftime('%d.%m.%Y, %H:%M:%S')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('{"updated":"' + now + '","rows":')
        json.dump(rows, f, ensure_ascii=False)
        f.write('}')
    print(f'{sheet_name}: {len(rows)} rows -> {output_path} (updated: {now})')

for name, path in SHEETS:
    fetch_sheet(name, path)
