import pytest

from pipeline import stress_pnl


def test_long_position_loses_when_price_falls():
    assert stress_pnl(quantity=6_000, price=75, shock=-0.10) == -45_000


def test_short_position_gains_when_price_falls():
    assert stress_pnl(quantity=-6_000, price=75, shock=-0.10) == 45_000


def test_copper_exposure():
    assert stress_pnl(quantity=1_000, price=9_000, shock=-0.10) == -900_000


@pytest.mark.parametrize("price", [0, -1, float("nan"), float("inf")])
def test_invalid_toy_prices_fail(price):
    with pytest.raises(ValueError):
        stress_pnl(quantity=1, price=price, shock=-0.10)
