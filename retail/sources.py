"""Dataset adapters. Raw source files stay in ignored data/private/."""
from pathlib import Path
import pandas as pd


def online_retail(path: str | Path, top_skus: int = 12) -> pd.DataFrame:
    """Convert UCI Online Retail transactions into complete daily SKU demand series.

    Cancellations and non-positive quantities are excluded. Zeros are inserted for
    dates with no observed sale, which is appropriate for a unit-demand series but
    does not recover demand lost to stockouts.
    """
    raw = pd.read_excel(path)
    required = {'InvoiceNo', 'StockCode', 'Quantity', 'InvoiceDate'}
    if not required <= set(raw):
        raise ValueError(f'UCI file is missing columns: {required - set(raw)}')
    invoice = raw['InvoiceNo'].astype(str).str.strip()
    frame = raw.loc[(~invoice.str.startswith('C')) & (raw['Quantity'] > 0)].copy()
    frame['date'] = pd.to_datetime(frame['InvoiceDate'], format='mixed', errors='coerce').dt.normalize()
    frame['sku'] = frame['StockCode'].astype(str).str.strip().str.replace(r'\.0$', '', regex=True)
    frame = frame.dropna(subset=['date']).loc[lambda x: x['sku'].ne('')]
    observed_days = frame.groupby('sku')['date'].nunique().sort_values(ascending=False)
    candidates = observed_days[observed_days >= 120].head(top_skus).index
    if len(candidates) < 2:
        raise ValueError('Fewer than two SKUs have 120 observed sale days after cleaning.')
    frame = frame[frame['sku'].isin(candidates)]
    daily = frame.groupby(['date', 'sku'], as_index=False)['Quantity'].sum().rename(columns={'Quantity': 'units'})
    dates = pd.date_range(daily.date.min(), daily.date.max(), freq='D')
    grid = pd.MultiIndex.from_product([dates, sorted(candidates)], names=['date', 'sku']).to_frame(index=False)
    return grid.merge(daily, on=['date', 'sku'], how='left').fillna({'units': 0}).sort_values(['sku', 'date']).reset_index(drop=True)
