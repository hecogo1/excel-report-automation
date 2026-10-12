# Usage guide

## Installation
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Running
```bash
python -m sales_report.cli --input <folder> [--output output/sales_report.xlsx] [--config config.yaml] [--log-dir logs]
```
| Option | Default | Description |
|---|---|---|
| `--input`, `-i` | required | Folder containing `.csv`, `.xlsx`, `.xls` files |
| `--output`, `-o` | `output/sales_report.xlsx` | Path of the generated report |
| `--config`, `-c` | `config.yaml` | Configuration file |
| `--log-dir` | `logs` | Where run logs are written |

Exit code is `0` on success and `1` on failure (details in the log), so it can be scheduled with cron, Windows Task Scheduler or Airflow.

## Input requirements
Each file needs these columns (any alias in `config.yaml` works, case-insensitive):
`date`, `region`, `product`, `quantity`, `unit_price`. Extra columns are ignored.

## Configuration (`config.yaml`)
- `columns`: add the header names your systems use, e.g. add `"sales zone"` under `region`.
- `validation`: allowed quantity range and minimum price.
- `report`: title, currency format (Excel number format) and number of top products.
- `file_patterns`: which files to pick up.

## Output workbook
| Sheet | Contents |
|---|---|
| Summary | KPIs + monthly line chart, regional pie chart, top-products bar chart |
| Monthly | revenue, orders and units per month |
| By Region | revenue, orders, share |
| Top Products | top N products by revenue |
| Month x Region | pivot table |
| Clean Data | all validated rows with computed revenue |
| Rejected Rows | invalid rows with the rejection reason |

## Validation rules
A row is rejected when: the date can't be parsed (e.g. `31/02/2026`), quantity or price is not numeric, quantity is outside `[min_quantity, max_quantity]`, price < `min_price`, or region/product is blank. Exact duplicates are removed (count is logged).

## Regenerating the sample data
```bash
python scripts/make_sample_data.py     # synthetic, seeded
python scripts/preview_charts.py       # README images
```

## Tests
```bash
pytest -q
```
Covers number/date parsing, header mapping, every validation rule, de-duplication, aggregations and an end-to-end run, including the check that the 3 charts exist.
