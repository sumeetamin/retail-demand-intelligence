import json
import pandas as pd
import streamlit as st
from retail.core import ROOT, inventory

st.set_page_config(page_title='Demand Intelligence', page_icon='📦', layout='wide')
st.caption('OPERATIONS LAB / DATA SCIENCE')
st.title('Demand Intelligence')
st.write('Forecast demand. Understand uncertainty. Plan the next order.')
if not (ROOT/'reports/forecast.csv').exists():
    st.info('Run `python -m retail.train` to generate the model and reports.')
    st.stop()
card = json.loads((ROOT/'reports/model_card.json').read_text())
st.info('Dataset: '+card['data_source']+'. Inventory costs are simulated, not measured business savings.')
sales = pd.read_csv(ROOT/'data/sales.csv', parse_dates=['date'])
pred = pd.read_csv(ROOT/'reports/forecast.csv', parse_dates=['date'])
metrics = pd.read_csv(ROOT/'reports/backtest.csv')
selected = st.sidebar.selectbox('Product', sorted(sales.sku.unique()))
lead = st.sidebar.slider('Lead time (days)', 1, 14, 7)
stock = st.sidebar.number_input('On hand per product', min_value=0, value=100)
holding = st.sidebar.number_input('Overstock cost per unit', min_value=.1, value=1.)
shortage = st.sidebar.number_input('Stockout cost per unit', min_value=.1, value=5.)
model = metrics[metrics.model=='prediction']
a,b,c = st.columns(3)
a.metric('Backtest MAE', f'{model.mae.mean():.2f} units')
b.metric('90% interval coverage', f'{model.coverage.mean():.1%}')
c.metric('Products', sales.sku.nunique())
tabs = st.tabs(['Forecast & stock', 'Evaluation', 'Data contract'])
with tabs[0]:
    historical = sales[sales.sku==selected].tail(56).set_index('date')[['units']]
    future = pred[pred.sku==selected].set_index('date')[['prediction', 'lower', 'upper']]
    st.line_chart(pd.concat([historical, future]))
    st.caption('Intervals use held-out chronological residuals; coverage under distribution shift is not guaranteed.')
    plan = inventory(pred, stock, lead, holding, shortage)
    st.subheader('Suggested replenishment')
    st.dataframe(plan, hide_index=True, width='stretch')
    st.download_button('Download order plan', plan.to_csv(index=False), 'inventory-plan.csv', 'text/csv')
    st.caption('Approximate newsvendor policy assumes independent daily errors and one replenishment cycle.')
with tabs[1]:
    st.dataframe(metrics, hide_index=True, width='stretch')
    st.bar_chart(metrics.groupby('model')[['mae']].mean())
    st.write('Three disjoint test windows. Each fold trains on earlier dates and calibrates on a separate 28-day window.')
with tabs[2]:
    st.code('date,sku,units\n2024-01-01,COFFEE,25\n2024-01-02,COFFEE,28', language='csv')
    st.write('Use daily demand, at least 120 consecutive days per SKU, common end date, no duplicates or missing values. Sales censored by stockouts underestimate demand.')
    st.code('python -m retail.train --csv path/to/demand.csv')
