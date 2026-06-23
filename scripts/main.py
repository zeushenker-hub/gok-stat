import argparse
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description="Tender documents statistics")
    parser.add_argument("--source", type=str, default=None,
                        help="Path to source directory (default: ../source)")
    parser.add_argument("--results", type=str, default=None,
                        help="Path to results directory (default: ../results)")
    parser.add_argument("--skip-basic", action="store_true",
                        help="Skip basic stats, run only content analysis")
    parser.add_argument("--skip-content", action="store_true",
                        help="Skip content analysis, run only basic stats")
    args = parser.parse_args()

    scripts_dir = Path(__file__).resolve().parent
    project_root = scripts_dir.parent

    source_dir = Path(args.source) if args.source else (project_root / "source")
    results_dir = Path(args.results) if args.results else (project_root / "results")

    source_dir = source_dir.resolve()
    results_dir = results_dir.resolve()
    results_dir.mkdir(parents=True, exist_ok=True)

    if not source_dir.is_dir():
        print(f"ERROR: source directory not found: {source_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Source dir:  {source_dir}")
    print(f"Results dir: {results_dir}")
    print()

    if not args.skip_basic:
        from scripts import stats_company, stats_format, stats_wordcloud, stats_geo
        modules = [
            ("company", stats_company),
            ("format", stats_format),
            ("wordcloud", stats_wordcloud),
            ("geo", stats_geo),
        ]
        for name, mod in modules:
            print(f"=== Running {name} ===")
            try:
                mod.run(source_dir, results_dir)
            except Exception as e:
                print(f"  [ERROR] {name} failed: {e}", file=sys.stderr)
            print()

    if not args.skip_content:
        print("=== Running content analysis ===")
        from scripts import analyze_content
        try:
            analyze_content.run(source_dir, results_dir)
        except Exception as e:
            print(f"  [ERROR] content analysis failed: {e}", file=sys.stderr)
        print()

    print("=== Running report ===")
    from scripts import report_html
    try:
        report_html.run(source_dir, results_dir)
    except Exception as e:
        print(f"  [ERROR] report failed: {e}", file=sys.stderr)
    print()

    print("Done. Results in:", results_dir)


if __name__ == "__main__":
    main()
