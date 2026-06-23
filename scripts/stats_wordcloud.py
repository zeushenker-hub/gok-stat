from pathlib import Path
from collections import Counter
import re

from scripts.shared import get_all_files, extract_text


STOPWORDS = {
    "и", "в", "на", "с", "по", "от", "для", "о", "об", "не", "no",
    "а", "но", "да", "к", "до", "за", "из", "у", "при", "что",
    "это", "так", "как", "или", "то", "же", "бы", "если",
    "чтобы", "все", "еще", "уже", "когда", "где", "там",
    "настоящим", "настоящего", "также", "может", "должен",
    "the", "and", "for", "with", "from", "that", "this",
}


def extract_words(text: str) -> list:
    words = re.findall(r"[а-яёa-z]{4,}", text.lower())
    return [w for w in words if w not in STOPWORDS]


def run(source_dir: Path, results_dir: Path) -> None:
    files = get_all_files()
    counter: Counter = Counter()
    total_text_len = 0
    for fp in files:
        if not fp.is_file():
            continue
        text = extract_text(fp)
        total_text_len += len(text)
        words = extract_words(text)
        counter.update(words)

    top_words = counter.most_common(100)

    out_path = results_dir / "wordcloud_top100.csv"
    with open(str(out_path), "w", encoding="utf-8") as f:
        f.write("word,count\n")
        for word, count in top_words:
            f.write(f'"{word}",{count}\n')

    print(f"[wordcloud] Total text chars: {total_text_len}")
    print(f"[wordcloud] Unique words: {len(counter)}")
    print(f"[wordcloud] Top-5: {[w for w, _ in top_words[:5]]}")
    print(f"[wordcloud] Wrote {len(top_words)} rows to {out_path}")
