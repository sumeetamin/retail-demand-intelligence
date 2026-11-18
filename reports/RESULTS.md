# Leakage-safe retail backtest

Run against the official UCI Online Retail workbook after selecting the 12 products by observed sale days in only the first 120 calendar days. The later test windows do not influence cohort selection. The 12 products were held fixed across all folds.

| Test window | Model | MAE | WAPE | Realized 7-day policy cost |
|---|---|---:|---:|---:|
| 2011-10-29 | Seasonal baseline | 72.524 | 0.920 | 11,043 |
| 2011-10-29 | Gradient boosting | 60.036 | 0.762 | 10,630 |
| 2011-11-12 | Seasonal baseline | 70.804 | 1.036 | 5,652 |
| 2011-11-12 | Gradient boosting | 52.774 | 0.772 | 11,773 |
| 2011-11-26 | Seasonal baseline | 54.327 | 0.839 | 3,860 |
| 2011-11-26 | Gradient boosting | 48.681 | 0.751 | 3,904 |

Across the three windows, gradient boosting lowered mean MAE from **65.885 to 53.830** (18.3%) and achieved mean nominal 90% interval coverage of **88.5%**. Its aggregate realized 7-day policy cost was **26,307**, compared with **20,555** for the seasonal baseline, a 28.0% increase. The model was more accurate on units but did not minimize this simple inventory-cost measure. For this cost setup, the dashboard selects the lower mean lead-window policy-cost forecast across these three windows; this choice is specific to the assumed initial stock, lead time and costs.

The current cost simulation now runs the same seven-day lead-time reorder function used by the dashboard, with 100 starting units per SKU and the stated 1:5 holding-to-stockout penalty. It evaluates realized demand over the lead window. This remains a simplified one-cycle policy simulation, not an operating-savings estimate; it omits replenishment arrivals after the first cycle, supplier constraints, stockouts that censor observed demand, and business-calibrated costs. The intervals do not guarantee future coverage. Three short windows on one retailer dataset do not establish generalization.

The benchmark is reproducible from the included aggregate daily sales file used by CI. To regenerate the data outputs, run:

```bash
python -m retail.train --csv data/sales.csv
```

The raw workbook is not included. Dataset source: [UCI Online Retail](https://archive.ics.uci.edu/dataset/352/online+retail), CC BY 4.0.
