import argparse
import json
import sqlite3
import joblib
import pandas as pd
from .core import ROOT, demo_data, validate, fit, forecast, backtest

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv', help='Own daily demand CSV: date,sku,units')
    args = parser.parse_args()
    df = validate(pd.read_csv(args.csv) if args.csv else demo_data())
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
    summary = dict(data_source='user-provided CSV' if args.csv else 'deterministic synthetic retail demand; seed 42',
                   rows=len(df), products=df.sku.nunique(), **{k:v for k,v in bundle.items() if k!='model'})
    (ROOT/'reports/model_card.json').write_text(json.dumps(summary, indent=2))
    print(metrics.to_string(index=False))

if __name__ == '__main__':
    main()
