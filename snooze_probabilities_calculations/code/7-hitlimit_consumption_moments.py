import pandas as pd
import numpy as np
from pathlib import Path

day_df = pd.read_csv(Path(__file__).parent.parent / "output" / "tables" / "2-day_level_data.csv")
day_df["HLTime"] = pd.to_datetime(day_df["HLTime"], errors="coerce")
day_df["hl_minutes"] = day_df["HLTime"].dt.hour * 60 + day_df["HLTime"].dt.minute

def moments(series: pd.Series) -> dict:
    s = series.dropna()
    return {
        "count": len(s),
        "mean": s.mean(),
        "std": s.std(ddof=1),
        "var": s.var(ddof=1),
        "min": s.min(),
        "p25": s.quantile(0.25),
        "median": s.median(),
        "p75": s.quantile(0.75),
        "max": s.max(),
    }

records = []
for group, g in day_df.groupby("SnoozeGroup"):
    hl_stats = moments(g["hl_minutes"])
    cons_stats = moments(g["CumMins"])
    records.append({
        "SnoozeGroup": group,
        "hl_count": hl_stats["count"],
        "hl_mean_min": hl_stats["mean"],
        "hl_median_min": hl_stats["median"],
        "hl_var": hl_stats["var"],
        "hl_std": hl_stats["std"],
        "hl_p25": hl_stats["p25"],
        "hl_p75": hl_stats["p75"],
        "hl_min": hl_stats["min"],
        "hl_max": hl_stats["max"],
        "cons_count": cons_stats["count"],
        "cons_mean_min": cons_stats["mean"],
        "cons_median_min": cons_stats["median"],
        "cons_var": cons_stats["var"],
        "cons_std": cons_stats["std"],
        "cons_p25": cons_stats["p25"],
        "cons_p75": cons_stats["p75"],
        "cons_min": cons_stats["min"],
        "cons_max": cons_stats["max"],
    })

out_df = pd.DataFrame(records)
out_df = out_df.sort_values("SnoozeGroup")

output_dir = Path(__file__).parent.parent / "output" / "tables"
output_dir.mkdir(parents=True, exist_ok=True)
out_df.to_csv(output_dir / "7-hitlimit_consumption_moments.csv", index=False)




