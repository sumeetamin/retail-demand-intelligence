"""Direct multi-horizon forecasting with chronological calibration."""
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import make_pipeline

ROOT = Path(__file__).resolve().parents[1]
FEATURES = ['sku', 'horizon', 'dow', 'month', 'trend', 'last', 'mean7', 'mean28', 'std28', 'seasonal']

def demo_data(seed=42, days=540):
    rng = np.random.default_rng(seed)
    rows = []
    for j, sku in enumerate(['COFFEE', 'TEA', 'RICE', 'OATS', 'SOAP', 'MILK']):
        for t, date in enumerate(pd.date_range('2024-01-01', periods=days)):
            mean = 18 + j * 8 + .025*t + (8+j)*np.sin(2*np.pi*date.dayofweek/7) + 5*np.sin(2*np.pi*t/365)
            units = max(0, round(mean + rng.normal(0, 3+j*.6)))
            rows.append((date, sku, units))
    return pd.DataFrame(rows, columns=['date', 'sku', 'units'])

def validate(frame):
    if not {'date', 'sku', 'units'} <= set(frame):
        raise ValueError('CSV requires date, sku, units columns.')
    df = frame[['date', 'sku', 'units']].copy()
    df['date'] = pd.to_datetime(df.date, errors='raise').dt.normalize()
    df['units'] = pd.to_numeric(df.units, errors='raise')
    if df.isna().any().any() or not np.isfinite(df.units).all() or (df.units < 0).any():
        raise ValueError('Missing, infinite or negative values are not allowed.')
    if df.duplicated(['date', 'sku']).any():
        raise ValueError('Each SKU must have exactly one row per day.')
    for _, g in df.groupby('sku'):
        if len(g) < 120 or g.date.nunique() != (g.date.max()-g.date.min()).days+1:
            raise ValueError('Each SKU needs at least 120 consecutive daily records. Fill missing days explicitly.')
    if df.groupby('sku').date.max().nunique() != 1:
        raise ValueError('All SKUs must end on the same date.')
    return df.sort_values(['sku', 'date']).reset_index(drop=True)

def features(history, sku, target, horizon):
    # History ends before forecast origin; target demand is never a feature.
    values = history.units.to_numpy()
    seasonal = float(values[-7 + (horizon-1) % 7])
    return dict(sku=sku, horizon=horizon, dow=target.dayofweek, month=target.month,
                trend=(target-pd.Timestamp('2024-01-01')).days,
                last=float(values[-1]), mean7=float(values[-7:].mean()),
                mean28=float(values[-28:].mean()), std28=float(values[-28:].std()), seasonal=seasonal)

def samples(df):
    rows = []
    for sku, g in df.groupby('sku'):
        g = g.reset_index(drop=True)
        for origin in range(28, len(g), 7):
            hist = g.iloc[:origin]
            for h in range(1, min(14, len(g)-origin)+1):
                target = g.iloc[origin+h-1]
                row = features(hist, sku, target.date, h)
                row.update(origin=g.iloc[origin].date, target_date=target.date, y=target.units)
                rows.append(row)
    return pd.DataFrame(rows)

def fit(df, cutoff):
    eligible = df[df.date < cutoff]
    table = samples(eligible)
    boundary = pd.Timestamp(cutoff)-pd.Timedelta(days=28)
    train = table[table.target_date < boundary]
    calibration = table[table.origin >= boundary]
    if train.empty or calibration.empty:
        raise ValueError('Not enough training/calibration history.')
    transform = ColumnTransformer([('sku', OneHotEncoder(handle_unknown='ignore', sparse_output=False), ['sku'])], remainder='passthrough')
    model = make_pipeline(transform, HistGradientBoostingRegressor(max_iter=140, max_leaf_nodes=15, l2_regularization=2, random_state=42))
    model.fit(train[FEATURES], train.y)
    residual = np.abs(calibration.y - model.predict(calibration[FEATURES]))
    n = len(residual)
    q = min(1, np.ceil((n+1)*.9)/n)
    radius = float(np.quantile(residual, q, method='higher'))
    return dict(model=model, radius=radius, cutoff=str(pd.Timestamp(cutoff).date()),
                calibration_count=n, train_rows=len(train), skus=sorted(df.sku.unique()),
                train_target_max=str(train.target_date.max().date()), calibration_origin_min=str(calibration.origin.min().date()))

def forecast(bundle, history, horizon=14):
    if not 1 <= horizon <= 14:
        raise ValueError('Horizon must be between 1 and 14 days.')
    cutoff = pd.Timestamp(bundle['cutoff'])
    rows = []
    for sku, g in history[history.date < cutoff].groupby('sku'):
        if sku not in bundle['skus']:
            raise ValueError(f'Unknown SKU: {sku}')
        for h in range(1, horizon+1):
            row = features(g.sort_values('date'), sku, cutoff+pd.Timedelta(days=h-1), h)
            row['date'] = cutoff+pd.Timedelta(days=h-1)
            rows.append(row)
    result = pd.DataFrame(rows)
    result['prediction'] = np.maximum(0, bundle['model'].predict(result[FEATURES]))
    result['lower'] = np.maximum(0, result.prediction-bundle['radius'])
    result['upper'] = result.prediction+bundle['radius']
    return result[['date', 'sku', 'prediction', 'lower', 'upper', 'seasonal']]

def inventory(predictions, on_hand=100, lead_days=7, holding_cost=1., stockout_cost=5.):
    if lead_days < 1 or lead_days > 14 or on_hand < 0 or holding_cost <= 0 or stockout_cost <= 0:
        raise ValueError('Lead time 1–14; stock >= 0; costs > 0 required.')
    from scipy.stats import norm
    # Approximate newsvendor target: independent normal daily errors; explicitly not a service guarantee.
    rows = []
    for sku, g in predictions.groupby('sku'):
        g = g.sort_values('date').head(lead_days)
        mean = float(g.prediction.sum())
        sigma = float(np.sqrt(np.square((g.upper-g.prediction)/1.645).sum()))
        quantile = stockout_cost/(holding_cost+stockout_cost)
        target = max(0, mean+norm.ppf(quantile)*sigma)
        rows.append(dict(sku=sku, expected_demand=round(mean, 1), target_stock=int(np.ceil(target)),
                         on_hand=on_hand, order_quantity=max(0, int(np.ceil(target-on_hand)))))
    return pd.DataFrame(rows)

def backtest(df):
    records, predictions = [], []
    # Three disjoint 14-day test windows, with model selection fixed in advance.
    for offset in [42, 28, 14]:
        cutoff = df.date.max()-pd.Timedelta(days=offset-1)
        bundle = fit(df, cutoff)
        pred = forecast(bundle, df).merge(df, on=['date', 'sku'], validate='one_to_one')
        pred['fold'] = str(cutoff.date())
        predictions.append(pred)
        for name in ['seasonal', 'prediction']:
            error = pred[name]-pred.units
            # At-order-arrival stock simulation; no real operating savings claimed.
            decisions = pred.groupby('sku')[[name, 'units']].sum()
            cost = (np.maximum(decisions[name]-decisions.units, 0) + 5*np.maximum(decisions.units-decisions[name], 0)).sum()
            records.append(dict(fold=str(cutoff.date()), model=name, mae=float(np.abs(error).mean()),
                                wape=float(np.abs(error).sum()/max(1, pred.units.sum())), bias=float(error.mean()),
                                coverage=float(((pred.units>=pred.lower)&(pred.units<=pred.upper)).mean()) if name=='prediction' else None,
                                simulated_cost=float(cost)))
    return pd.DataFrame(records), pd.concat(predictions, ignore_index=True)
