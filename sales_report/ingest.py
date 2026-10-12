"""Discover and read raw sales files (CSV / Excel) from a folder."""
import logging
from pathlib import Path
import pandas as pd

log = logging.getLogger(__name__)


def _norm(s: str) -> str:
    return str(s).strip().lower().replace("_", " ")


def standardise_columns(df: pd.DataFrame, aliases: dict) -> pd.DataFrame:
    """Rename columns to canonical names using the alias map from config."""
    lookup = {_norm(a): canon for canon, al in aliases.items() for a in al}
    return df.rename(columns={c: lookup.get(_norm(c), c) for c in df.columns})


def read_file(path: Path) -> pd.DataFrame:
    """Read one CSV (auto-detecting ; or , separators) or Excel file."""
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path, sep=None, engine="python", dtype=str)
    return pd.read_excel(path, dtype=str)


def ingest_folder(folder: str | Path, cfg: dict) -> pd.DataFrame:
    """Read every matching file, standardise headers and tag rows with their source file."""
    folder = Path(folder)
    files = sorted({f for pat in cfg["file_patterns"] for f in folder.glob(pat)})
    if not files:
        raise FileNotFoundError(f"No input files found in {folder}")
    frames = []
    for f in files:
        try:
            df = standardise_columns(read_file(f), cfg["columns"])
        except Exception as exc:  # corrupt file: log and continue
            log.error("Could not read %s: %s", f.name, exc)
            continue
        missing = set(cfg["required"]) - set(df.columns)
        if missing:
            log.error("Skipping %s: missing columns %s", f.name, sorted(missing))
            continue
        df = df[cfg["required"]].copy()
        df["source_file"] = f.name
        log.info("Read %s (%d rows)", f.name, len(df))
        frames.append(df)
    if not frames:
        raise ValueError("No valid input files")
    return pd.concat(frames, ignore_index=True)
