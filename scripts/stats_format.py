from pathlib import Path
from collections import Counter

from scripts.shared import get_all_files


def run(source_dir: Path, results_dir: Path) -> None:
    files = get_all_files()
    counter: Counter = Counter()
    for fp in files:
        if fp.is_file():
            suffix = fp.suffix.lower() if fp.suffix else "no_ext"
            counter[suffix] += 1

    out_path = results_dir / "format_stats.csv"
    total = sum(counter.values())
    with open(str(out_path), "w", encoding="utf-8") as f:
        f.write("format,count,percentage\n")
        for ext, count in sorted(counter.items(), key=lambda x: -x[1]):
            pct = round(count / total * 100, 1)
            f.write(f'"{ext}",{count},{pct}\n')
    print(f"[format] Wrote {len(counter)} format types to {out_path}")
