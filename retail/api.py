import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from .core import ROOT, forecast, inventory

app = FastAPI(title='Retail Demand Intelligence', version='1.0.0')

class PlanRequest(BaseModel):
    on_hand: int = Field(default=100, ge=0)
    lead_days: int = Field(default=7, ge=1, le=14)
    holding_cost: float = Field(default=1, gt=0, allow_inf_nan=False)
    stockout_cost: float = Field(default=5, gt=0, allow_inf_nan=False)

def predictions():
    if not (ROOT/'artifacts/model.joblib').exists():
        raise HTTPException(503, 'Run python -m retail.train first.')
    bundle = joblib.load(ROOT/'artifacts/model.joblib')
    history = pd.read_csv(ROOT/'data/sales.csv', parse_dates=['date'])
    return forecast(bundle, history)

@app.get('/health')
def health():
    return {'status': 'ready' if (ROOT/'artifacts/model.joblib').exists() else 'untrained'}

@app.get('/forecast')
def get_forecast():
    result = predictions()
    result['date'] = result.date.dt.strftime('%Y-%m-%d')
    return result.to_dict('records')

@app.post('/inventory')
def plan(request: PlanRequest):
    return inventory(predictions(), **request.model_dump()).to_dict('records')
