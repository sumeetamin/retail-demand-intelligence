# Measured results

Deterministic synthetic data; seed 42. Six products, 540 daily observations each. Results are from three fixed 14-day test windows, not a real retailer benchmark.

| Measure | Result |
|---|---:|
| Seasonal baseline mean MAE | 4.841 |
| Boosted model mean MAE | 4.082 |
| Relative MAE improvement | 15.7% |
| Nominal 90% interval observed coverage | 86.9% |

The model beats the baseline on MAE in each fold. Its fixed-window inventory cost is worse in the final fold, illustrating that improved forecast error does not always improve a decision metric. Observed interval coverage is below the 90% target. These shortcomings are retained in the report.

Run `python -m retail.train` to reproduce; exact values can differ with dependency/platform versions. Raw predictions, fold metrics and the temporal split metadata are included beside this file.
