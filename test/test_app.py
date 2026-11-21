from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "app.py")


def test_app_runs_without_exceptions():
    at = AppTest.from_file(APP, default_timeout=30).run()
    assert not at.exception


def test_purchase_button_is_locked_during_cooling_off():
    at = AppTest.from_file(APP, default_timeout=30).run()
    buy_buttons = [b for b in at.button if b.key and b.key.startswith("buy_")]
    assert buy_buttons and all(b.disabled for b in buy_buttons)


def test_invest_button_moves_money_to_portfolio():
    at = AppTest.from_file(APP, default_timeout=30).run()
    before = at.session_state["saved_capital"]
    invest = [b for b in at.button if b.key and b.key.startswith("win_")][0]
    invest.click().run()
    assert at.session_state["saved_capital"] > before
    assert not at.exception
