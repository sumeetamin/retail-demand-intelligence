import argparse
import json
import sqlite3
import joblib
import pandas as pd
from .core import ROOT, demo_data, validate, fit, forecast, backtest
from .sources import online_retail

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv', help='Own daily demand CSV: date,sku,units')
    parser.add_argument('--uci-online-retail', help='Path to UCI Online Retail.xlsx')
    parser.add_argument('--top-skus', type=int, default=12, help='Top qualifying UCI products to model')
    args = parser.parse_args()
    if args.csv and args.uci_online_retail:
        parser.error('Use either --csv or --uci-online-retail, not both.')
    if args.uci_online_retail:
        df = validate(online_retail(args.uci_online_retail, args.top_skus))
        source = f'UCI Online Retail; top {df.sku.nunique()} SKUs by observed sale days; cancellations and non-positive quantities excluded'
    elif args.csv:
        df = validate(pd.read_csv(args.csv))
        source = 'user-provided CSV'
    else:
        df = validate(demo_data())
        source = 'deterministic synthetic retail demand; seed 42'
    for p in ['data', 'artifacts', 'reports']:
        (ROOT/p).mkdir(exist_ok=True)
    df.to_csv(ROOT/'data/sales.csv', index=False)
    with sqlite3.connect(ROOT/'data/warehouse.sqlite') as conn:
        df.to_sql('daily_sales', conn, if_exists='replace', index=False)
        conn.execute('CREATE UNIQUE INDEX IF NOT EXISTS sales_key ON daily_sales(sku,date)')
    metrics, predictions = backtest(df)
    metrics.to_csv(ROOT/'reports/backtest.csv', index=False)
    predictions.to_csv(ROOT/'reports/backtest_predictions.csv', index=False)
    bundle = fit(df, df.date.max()+pd.Timedelta(days=1))
    joblib.dump(bundle, ROOT/'artifacts/model.joblib')
    forecast(bundle, df).to_csv(ROOT/'reports/forecast.csv', index=False)
    summary = dict(data_source=source,
                   rows=len(df), products=df.sku.nunique(), **{k:v for k,v in bundle.items() if k!='model'})
    (ROOT/'reports/model_card.json').write_text(json.dumps(summary, indent=2))
    print(metrics.to_string(index=False))

if __name__ == '__main__':
    main()
