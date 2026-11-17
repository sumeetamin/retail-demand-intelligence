# Leakage-safe retail backtest

Run against the official UCI Online Retail workbook after selecting the 12 products by observed sale days in only the first 120 calendar days. The later test windows do not influence cohort selection. The 12 products were held fixed across all folds.

| Test window | Model | MAE | WAPE | Simulated inventory cost |
|---|---|---:|---:|---:|
| 2011-10-29 | Seasonal baseline | 72.524 | 0.920 | 38,624 |
| 2011-10-29 | Gradient boosting | 60.036 | 0.762 | 29,653 |
| 2011-11-12 | Seasonal baseline | 70.804 | 1.036 | 15,425 |
| 2011-11-12 | Gradient boosting | 52.774 | 0.772 | 19,458 |
| 2011-11-26 | Seasonal baseline | 54.327 | 0.839 | 12,201 |
| 2011-11-26 | Gradient boosting | 48.681 | 0.751 | 23,211 |

Across the three windows, gradient boosting lowered mean MAE from **65.885 to 53.830** (18.3%) and achieved mean nominal 90% interval coverage of **88.5%**. Its aggregate simulated inventory cost was **72,322**, compared with **66,250** for the seasonal baseline, a 9.2% increase. The model was more accurate on units but did not minimize this simple inventory-cost measure. For this cost setup, choose the seasonal baseline until the replenishment policy is tuned and evaluated against business-calibrated costs.

The simulated cost sums fixed-window overage and shortage penalties. It is not an operating-savings estimate or a complete inventory simulation. The intervals do not guarantee future coverage. Three short windows on one retailer dataset do not establish generalization.

Reproduce the run by downloading the UCI Online Retail workbook into `data/private/` and running:

```bash
python -m retail.train --uci-online-retail data/private/Online_Retail.xlsx --top-skus 12
```

The raw workbook is not included. Dataset source: [UCI Online Retail](https://archive.ics.uci.edu/dataset/352/online+retail), CC BY 4.0.
