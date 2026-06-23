import re
from pathlib import Path
from typing import List, Tuple

from scripts.shared import get_all_files, extract_text


COMPANY_PATTERNS = [
    re.compile(r'(?:"([^"]+)"|«([^»]+)»|\(([^)]+)\))'),
]


def extract_company_name(filepath: Path) -> str:
    stem = filepath.stem
    for pattern in COMPANY_PATTERNS:
        match = pattern.search(stem)
        if match:
            return match.group(1) or match.group(2) or match.group(3)
    clean = re.sub(r'[«»"()]', "", stem)
    parts = clean.replace("_", " ").replace("-", " ").split()
    return " ".join(parts[:5])


def run(source_dir: Path, results_dir: Path) -> None:
    files = get_all_files()
    rows = []
    for fp in files:
        if not fp.is_file():
            continue
        company = extract_company_name(fp)
        text = extract_text(fp)
        text_preview = text[:1000].replace("\n", " ") if text else ""
        if not company or company.strip() == fp.stem.strip():
            if text_preview:
                fallback = text_preview[:80].strip()
                if fallback:
                    company = fallback
        rows.append((fp.name, company, len(text), fp.suffix.lower()))

    out_path = results_dir / "company_stats.csv"
    with open(str(out_path), "w", encoding="utf-8") as f:
        f.write("filename,company,char_count,format\n")
        for name, comp, cc, ext in rows:
            safe_name = name.replace('"', '""')
            safe_comp = comp.replace('"', '""')
            f.write(f'"{safe_name}","{safe_comp}",{cc},"{ext}"\n')
    print(f"[company] Wrote {len(rows)} rows to {out_path}")
