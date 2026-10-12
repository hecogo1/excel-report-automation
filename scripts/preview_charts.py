"""Render PNG previews of the report contents for the README."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

x = pd.read_excel("output/sales_report.xlsx", sheet_name=None)
fig, ax = plt.subplots(1, 3, figsize=(16, 4.5))
m = x["Monthly"]; ax[0].plot(m.month, m.revenue / 1e3, marker="o", color="#1F4E78")
ax[0].set_title("Monthly revenue (k€)"); ax[0].grid(alpha=.3)
r = x["By Region"]; ax[1].pie(r.revenue, labels=r.region, autopct="%1.0f%%"); ax[1].set_title("Revenue share by region")
p = x["Top Products"].iloc[::-1]; ax[2].barh(p["product"], p.revenue / 1e3, color="#2E75B6")
ax[2].set_title("Top products (k€)")
fig.tight_layout(); fig.savefig("images/report_preview.png", dpi=110)
rej = x["Rejected Rows"].reason.str.rstrip(";").value_counts()
fig, ax = plt.subplots(figsize=(6, 3)); rej.plot.barh(ax=ax, color="#C44E52")
ax.set_title("Rows rejected by validation"); fig.tight_layout(); fig.savefig("images/validation.png", dpi=110)
