"""Dataset adapters. Raw source files stay in ignored data/private/."""
from pathlib import Path
import pandas as pd


def online_retail(path: str | Path, top_skus: int = 12) -> pd.DataFrame:
    """Build daily series for products selected from the first 120 calendar days.

    Selecting the cohort from the opening period avoids using future sales to decide
    which products appear in later backtest windows. Cancellations and non-positive
    quantities are excluded. Missing product-days become zero, which does not recover
    demand lost to stockouts.
    """
    if top_skus < 2:
        raise ValueError("top_skus must be at least 2.")
    raw = pd.read_excel(path)
    required = {"InvoiceNo", "StockCode", "Quantity", "InvoiceDate"}
    if not required <= set(raw):
        raise ValueError(f"UCI file is missing columns: {required - set(raw)}")
    invoice = raw["InvoiceNo"].astype(str).str.strip()
    frame = raw.loc[(~invoice.str.startswith("C")) & (raw["Quantity"] > 0)].copy()
    frame["date"] = pd.to_datetime(frame["InvoiceDate"], format="mixed", errors="coerce").dt.normalize()
    frame["sku"] = raw.loc[frame.index, "StockCode"].astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
    frame = frame.dropna(subset=["date"]).loc[lambda x: x["sku"].ne("")]
    first_date = frame["date"].min()
    selection_end = first_date + pd.Timedelta(days=120)
    selection_period = frame.loc[frame["date"] < selection_end]
    observed_days = selection_period.groupby("sku")["date"].nunique().sort_values(ascending=False)
    candidates = observed_days[observed_days >= 30].head(top_skus).index
    if len(candidates) < 2:
        raise ValueError("Fewer than two SKUs have 30 observed sale days in the first 120 calendar days.")
    frame = frame[frame["sku"].isin(candidates)]
    daily = frame.groupby(["date", "sku"], as_index=False)["Quantity"].sum().rename(columns={"Quantity": "units"})
    dates = pd.date_range(daily.date.min(), daily.date.max(), freq="D")
    grid = pd.MultiIndex.from_product([dates, sorted(candidates)], names=["date", "sku"]).to_frame(index=False)
    return grid.merge(daily, on=["date", "sku"], how="left").fillna({"units": 0}).sort_values(["sku", "date"]).reset_index(drop=True)
