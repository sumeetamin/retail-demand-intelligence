import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from retail.core import demo_data, validate, fit, forecast, inventory, samples
from retail.api import app

def test_data_contract():
    df = demo_data(days=150)
    assert len(validate(df)) == 900
    with pytest.raises(ValueError): validate(pd.concat([df, df.iloc[:1]]))
    with pytest.raises(ValueError): validate(df.drop(index=2))

def test_future_does_not_change_features_or_model():
    df = demo_data(days=160)
    cutoff = pd.Timestamp('2024-05-15')
    a = fit(df, cutoff)
    mutated = df.copy()
    mutated.loc[mutated.date>=cutoff, 'units'] = 100000
    b = fit(mutated, cutoff)
    np.testing.assert_allclose(forecast(a,df).prediction, forecast(b,mutated).prediction)
    assert a['train_target_max'] < a['calibration_origin_min']

def test_feature_origin_and_inventory_monotonicity():
    table = samples(demo_data(days=150))
    assert (table.target_date >= table.origin).all()
    bundle = fit(demo_data(days=150), pd.Timestamp('2024-05-30'))
    pred = forecast(bundle, demo_data(days=150))
    assert (pred.lower<=pred.prediction).all() and (pred.upper>=pred.prediction).all()
    low = inventory(pred, stockout_cost=1)
    high = inventory(pred, stockout_cost=20)
    assert (high.order_quantity>=low.order_quantity).all()

def test_api_validation():
    client = TestClient(app)
    assert client.get('/health').status_code == 200
    assert client.post('/inventory', json={'lead_days':0}).status_code == 422
