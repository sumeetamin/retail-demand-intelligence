# Historical results requiring rerun

The numbers below came from an earlier run in which products were selected by observed sale-day counts over the full dataset. That selection used information from periods later than some backtest origins, so these metrics are retained only as historical output and must not be used as valid out-of-time performance evidence.

The data adapter now selects the product cohort from only the first 120 calendar days, before the later backtest windows. Re-run the real-data pipeline and regenerate this report, the backtest CSV, predictions, and model card before citing any forecast or inventory-cost result.

| Earlier metric | Historical value (not valid for current comparison) |
|---|---:|
| Seasonal baseline mean MAE | 101.813 |
| Boosted model mean MAE | 107.825 |
| Relative MAE change | -5.9% |
| Nominal 90% interval observed coverage | 87.3% |

The earlier run used 4,488 daily SKU observations and a 492-row calibration set. Those counts and scores describe the old full-period-selected cohort. Do not infer current model performance from them.
