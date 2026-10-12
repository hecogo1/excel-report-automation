"""Business aggregations."""
import pandas as pd


def summarise(df: pd.DataFrame, top_n: int = 10) -> dict[str, pd.DataFrame]:
    """Compute KPI, monthly, regional and product summaries."""
    kpi = pd.DataFrame({
        "Metric": ["Total revenue", "Orders", "Units sold", "Average order value", "Regions", "Products"],
        "Value": [df.revenue.sum(), len(df), df.quantity.sum(), df.revenue.mean(),
                  df.region.nunique(), df["product"].nunique()],
    })
    monthly = df.groupby("month", as_index=False).agg(revenue=("revenue", "sum"),
                                                      orders=("revenue", "size"), units=("quantity", "sum"))
    region = (df.groupby("region", as_index=False).agg(revenue=("revenue", "sum"), orders=("revenue", "size"))
              .sort_values("revenue", ascending=False))
    region["share"] = region.revenue / region.revenue.sum()
    product = (df.groupby("product", as_index=False).agg(revenue=("revenue", "sum"), units=("quantity", "sum"))
               .sort_values("revenue", ascending=False).head(top_n))
    pivot = df.pivot_table(index="month", columns="region", values="revenue", aggfunc="sum",
                           fill_value=0).reset_index()
    return {"kpi": kpi, "monthly": monthly, "region": region, "product": product, "pivot": pivot}
