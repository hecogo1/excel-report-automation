"""Cleaning and validation rules."""
import logging
import pandas as pd

log = logging.getLogger(__name__)


def parse_number(s: pd.Series) -> pd.Series:
    """Parse numbers written as '1.234,50', '1,234.50', '€ 12,5' or '12.5'."""
    s = s.astype(str).str.replace(r"[^\d,.\-]", "", regex=True)
    both = s.str.contains(",") & s.str.contains(".", regex=False)
    eu = both & (s.str.rfind(",") > s.str.rfind("."))
    s = s.where(~eu, s.str.replace(".", "", regex=False))
    s = s.where(~(both & ~eu), s.str.replace(",", "", regex=False))
    s = s.str.replace(",", ".", regex=False)
    return pd.to_numeric(s, errors="coerce")


def parse_dates(s: pd.Series) -> pd.Series:
    """Parse ISO dates, day-first dates (dd/mm/yyyy) and Excel datetimes."""
    iso = pd.to_datetime(s, format="%Y-%m-%d", errors="coerce")
    iso = iso.fillna(pd.to_datetime(s, format="%Y-%m-%d %H:%M:%S", errors="coerce"))
    return iso.fillna(pd.to_datetime(s, dayfirst=True, errors="coerce", format="mixed"))


def clean(df: pd.DataFrame, cfg: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (clean_rows, rejected_rows_with_reason)."""
    v = cfg["validation"]
    df = df.copy()
    df["region"] = df["region"].astype(str).str.strip().str.title()
    df["product"] = df["product"].astype(str).str.strip().str.title()
    df["date"] = parse_dates(df["date"])
    df["quantity"] = parse_number(df["quantity"])
    df["unit_price"] = parse_number(df["unit_price"])

    reason = pd.Series("", index=df.index)
    reason[df["date"].isna()] += "invalid date;"
    reason[df["quantity"].isna()] += "invalid quantity;"
    reason[df["unit_price"].isna()] += "invalid price;"
    reason[df["region"].isin(["", "Nan", "None"])] += "missing region;"
    reason[df["product"].isin(["", "Nan", "None"])] += "missing product;"
    q_bad = df["quantity"].notna() & ~df["quantity"].between(v["min_quantity"], v["max_quantity"])
    reason[q_bad] += "quantity out of range;"
    reason[df["unit_price"].notna() & (df["unit_price"] < v["min_price"])] += "price below minimum;"

    rejected = df[reason != ""].assign(reason=reason[reason != ""])
    ok = df[reason == ""].copy()
    n_before = len(ok)
    ok = ok.drop_duplicates(subset=["date", "region", "product", "quantity", "unit_price"])
    dups = n_before - len(ok)
    ok["revenue"] = (ok["quantity"] * ok["unit_price"]).round(2)
    ok["month"] = ok["date"].dt.to_period("M").astype(str)
    log.info("Clean rows: %d | rejected: %d | duplicates removed: %d", len(ok), len(rejected), dups)
    return ok.reset_index(drop=True), rejected.reset_index(drop=True)
