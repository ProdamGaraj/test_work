import asyncio
import unittest
from decimal import Decimal

from starter import recommend_price, sample_fetch_offers


def offers_source(*offers):
    async def fetch():
        return {"status": "success", "offers": list(offers)}
    return fetch


def run(coro):
    return asyncio.run(coro)


class RecommendPriceTest(unittest.TestCase):
    def test_normal_calculation(self):
        result = run(recommend_price(
            sample_fetch_offers,
            current_price=Decimal("4900.00"),
            min_price=Decimal("4500.00"),
        ))
        self.assertEqual(result["price"], Decimal("4728.00"))
        self.assertEqual(result["decision"], "APPLY")

    def test_timeout_returns_hold(self):
        async def slow_source():
            await asyncio.sleep(1)

        result = run(recommend_price(
            slow_source,
            current_price=Decimal("4900.00"),
            min_price=Decimal("4500.00"),
            timeout_s=0.05,
        ))
        self.assertEqual(result["price"], Decimal("4900.00"))
        self.assertEqual(result["decision"], "HOLD")

    def test_exactly_30_percent_is_apply_above_is_review(self):
        # 710.66 * 0.985 = 700.0001 -> 700.00, exactly -30% of 1000
        exact = run(recommend_price(
            offers_source({"seller": "A", "price": Decimal("710.66"), "delivery_days": 1}),
            current_price=Decimal("1000.00"),
            min_price=Decimal("100.00"),
        ))
        self.assertEqual(exact["price"], Decimal("700.00"))
        self.assertEqual(exact["decision"], "APPLY")

        # 710.65 * 0.985 = 699.99025 -> 699.99, just over 30%
        over = run(recommend_price(
            offers_source({"seller": "A", "price": Decimal("710.65"), "delivery_days": 1}),
            current_price=Decimal("1000.00"),
            min_price=Decimal("100.00"),
        ))
        self.assertEqual(over["price"], Decimal("699.99"))
        self.assertEqual(over["decision"], "REVIEW")


if __name__ == "__main__":
    unittest.main()
