from pathlib import Path
from streamlit.testing.v1 import AppTest

def test_inventory_controls_render():
    app=AppTest.from_file(str(Path(__file__).resolve().parents[1]/'app.py'),default_timeout=30).run()
    assert not app.exception
    app.slider[0].set_value(14).run()
    app.number_input[2].set_value(20.).run()
    assert not app.exception
