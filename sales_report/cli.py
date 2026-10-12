"""Command-line entry point.

Example:
    python -m sales_report.cli --input sample_data/input --output output/sales_report.xlsx
"""
import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

from .aggregate import summarise
from .clean import clean
from .config import load_config
from .ingest import ingest_folder
from .report import write_report


def setup_logging(log_dir: Path) -> Path:
    """Log to console and to a timestamped file."""
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"run_{datetime.now():%Y%m%d_%H%M%S}.log"
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
                        handlers=[logging.FileHandler(log_file, encoding="utf-8"), logging.StreamHandler()])
    return log_file


def run(input_dir, output, config="config.yaml", log_dir="logs") -> Path:
    """Full pipeline: ingest -> clean/validate -> aggregate -> Excel report."""
    log = logging.getLogger("sales_report")
    cfg = load_config(config)
    raw = ingest_folder(input_dir, cfg)
    good, bad = clean(raw, cfg)
    tables = summarise(good, cfg["report"]["top_n_products"])
    out = write_report(tables, good, bad, Path(output), cfg)
    log.info("Report written to %s (revenue %.2f, %d clean rows, %d rejected)",
             out, good.revenue.sum(), len(good), len(bad))
    return out


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Build a formatted Excel sales report from a folder of messy files.")
    p.add_argument("--input", "-i", required=True, help="Folder with .csv/.xlsx files")
    p.add_argument("--output", "-o", default="output/sales_report.xlsx")
    p.add_argument("--config", "-c", default="config.yaml")
    p.add_argument("--log-dir", default="logs")
    a = p.parse_args(argv)
    lf = setup_logging(Path(a.log_dir))
    try:
        run(a.input, a.output, a.config, a.log_dir)
    except Exception as exc:
        logging.getLogger("sales_report").exception("Run failed: %s", exc)
        return 1
    logging.getLogger("sales_report").info("Log saved to %s", lf)
    return 0


if __name__ == "__main__":
    sys.exit(main())
