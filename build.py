#!/usr/bin/env python3
import json, urllib.request, urllib.parse, os, re
from datetime import datetime, timezone, timedelta

SHEET_ID = '15PKewFsJYH99OLeC5LvIcHrt9W9tjFBl1067-yVDJAY'
SHEET_NAME = 'ГОК'
DIR = os.path.dirname(__file__)
DATA_FILE = os.path.join(DIR, 'data.json')
HTML_FILE = os.path.join(DIR, 'analytics.html')

def fetch_data():
    url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:json&sheet={urllib.parse.quote(SHEET_NAME)}'
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
    return rows

def build():
    rows = fetch_data()
    now = datetime.now(timezone(timedelta(hours=4))).strftime('%d.%m.%Y, %H:%M:%S')
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        f.write('{"updated":"' + now + '","rows":')
        json.dump(rows, f, ensure_ascii=False)
        f.write('}')
    print(f'data.json: {len(rows)} rows (updated: {now}')

    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        html = f.read()

    marker = '// EMBED'
    data_json = json.dumps(rows, ensure_ascii=False)
    regex = re.compile(r'^(let EMBEDDED_DATA\s*=).*?;(.*)', re.MULTILINE)
    if regex.search(html):
        html = regex.sub(rf'\1 {data_json};\2', html)
    else:
        print('ERROR: let EMBEDDED_DATA = not found in HTML')
        return

    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'analytics.html: embedded {len(rows)} rows')

if __name__ == '__main__':
    build()
