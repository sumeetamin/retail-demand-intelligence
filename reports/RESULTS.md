# Measured results

Results use the UCI Online Retail dataset after removing cancellation invoices and non-positive quantities, completing daily demand with zeros, and selecting 12 SKUs with the most observed sale days. The raw transaction file is not included.

| Measure | Result |
|---|---:|
| Seasonal baseline mean MAE | 101.813 |
| Boosted model mean MAE | 107.825 |
| Relative MAE change | -5.9% |
| Nominal 90% interval observed coverage | 87.3% |

The boosted model improves MAE in two of three temporal folds but fails sharply in the final fold, where it also changes the inventory cost. This honest result is retained: the model is a reproducible demand-forecasting system, not a claim that boosting universally improves retail decisions. The run used 4,488 daily SKU observations and a 492-row calibration set. See the backtest CSV and model card for fold-level details.
