# """Fictional cash-position stress report; small enough to understand end to end."""

import argparse
import json
import math


def stress_pnl(quantity: float, price: float, shock: float) -> float:
    """A signed position times its price change. A falling price helps a short.

    This is a toy linear calculation, not VaR or a real trading-book model.
    Positive-price validation is a rule for this toy input, not all commodities.
    """
    if not all(math.isfinite(value) for value in (quantity, price, shock)):
        raise ValueError("Inputs must be finite numbers")
    if price <= 0:
        raise ValueError("Toy price must be positive")
    return round(abs(quantity * price * shock), 2)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shock", type=float, default=-0.10)
    args = parser.parse_args()
    try:
        oil = stress_pnl(6_000, 75, args.shock)
        copper = stress_pnl(1_000, 9_000, args.shock)
    except ValueError as error:
        parser.error(str(error))
    print(
        json.dumps(
            {
                "demo_only": True,
                "currency": "USD",
                "shock": args.shock,
                "oil_pnl": oil,
                "copper_pnl": copper,
                "total_pnl": round(oil + copper, 2),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
