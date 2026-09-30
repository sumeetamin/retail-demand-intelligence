import pandas as pd
from retail.sources import online_retail


def test_online_retail_adapter_removes_cancellations_and_fills_days(tmp_path):
    dates = pd.date_range('2024-01-01', periods=125, freq='D')
    source = pd.DataFrame({
        'InvoiceNo': [str(i) for i in range(125)] * 2 + ['C999'],
        'StockCode': ['A'] * 125 + ['B'] * 125 + ['A'],
        'Quantity': [1] * 250 + [-2],
        'InvoiceDate': list(dates) + list(dates) + [dates[0]],
    })
    path = tmp_path / 'retail.xlsx'
    source.to_excel(path, index=False)
    result = online_retail(path, top_skus=2)
    assert set(result.sku) == {'A', 'B'}
    assert result.groupby('sku').size().nunique() == 1
    assert result.units.min() >= 0
