"""Generate SYNTHETIC messy sales files for the demo (seeded, reproducible).

Messiness injected on purpose: different header names per file, ';' vs ','
separators, European number formats, mixed date formats, stray whitespace,
inconsistent casing, duplicates, negative/zero quantities, blank cells.
"""
import random
from pathlib import Path
import pandas as pd

random.seed(7)
OUT = Path(__file__).resolve().parents[1] / "sample_data" / "input"
REGIONS = ["North", "South", "East", "West", "Central"]
PRODUCTS = {"Laptop Pro": 1199, "Laptop Air": 899, "Monitor 27": 279, "Keyboard": 49, "Mouse": 25,
            "Docking Station": 159, "Headset": 89, "Webcam": 69, "Tablet": 449, "Printer": 199}


def rows(month, n):
    out = []
    for _ in range(n):
        p = random.choice(list(PRODUCTS))
        d = pd.Timestamp(2026, month, random.randint(1, 28))
        out.append([d, random.choice(REGIONS), p, random.randint(1, 20),
                    round(PRODUCTS[p] * random.uniform(.9, 1.05), 2)])
    return out


def messify(r):
    d, reg, p, q, pr = r
    x = random.random()
    reg = random.choice([reg, reg.upper(), f" {reg.lower()} "])
    p = random.choice([p, p.lower(), p + " "])
    if x < .02: q = -q
    elif x < .03: q = ""
    elif x < .04: d = "31/02/2026"
    elif x < .045: reg = ""
    return [d, reg, p, q, pr]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for f in OUT.glob("*"): f.unlink()
    # 1) Jan-Feb: clean-ish Excel
    r = rows(1, 180) + rows(2, 170)
    pd.DataFrame([messify(x) for x in r], columns=["Date", "Region", "Product", "Quantity", "Unit Price"]) \
        .to_excel(OUT / "sales_2026_Q1_part1.xlsx", index=False)
    # 2) March: European CSV ; with dd/mm/yyyy and 1.234,50
    r = [messify(x) for x in rows(3, 200)]
    r += r[:8]  # duplicates
    df = pd.DataFrame(r, columns=["fecha", "zone", "item", "qty", "price"])
    df["fecha"] = [d.strftime("%d/%m/%Y") if isinstance(d, pd.Timestamp) else d for d in df.fecha]
    df["price"] = [f"{p:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") for p in df.price]
    df.to_csv(OUT / "ventas_marzo.csv", sep=";", index=False)
    # 3) April-May: US CSV with currency symbols
    r = [messify(x) for x in rows(4, 190) + rows(5, 210)]
    df = pd.DataFrame(r, columns=["Order Date", "AREA", "Product Name", "Units", "unit_price"])
    df["Order Date"] = [d.strftime("%Y-%m-%d") if isinstance(d, pd.Timestamp) else d for d in df["Order Date"]]
    df["unit_price"] = [f"€ {p:,.2f}" for p in df.unit_price]
    df.to_csv(OUT / "sales_apr_may.csv", index=False)
    # 4) June: Excel
    pd.DataFrame([messify(x) for x in rows(6, 220)], columns=["order_date", "region", "product", "qty", "price"]) \
        .to_excel(OUT / "sales_june.xlsx", index=False)
    # 5) A broken file missing required columns (should be skipped & logged)
    pd.DataFrame({"Date": ["2026-06-01"], "Notes": ["export error"]}).to_csv(OUT / "broken_export.csv", index=False)
    print("Sample files written to", OUT)


if __name__ == "__main__":
    main()
