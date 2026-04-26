"""测试 scraper 数据解析逻辑."""
import unittest
from unittest.mock import patch, MagicMock

from src.strategy import parse_institutional_data, build_ranked_list


class TestParseInstitutionalData(unittest.TestCase):
    """测试 T86 原始数据解析."""

    def test_parse_positive_buy_shares(self):
        rows = [
            ["0050", "元大台灣50", "—", "—", "+1,500,000", "0"],
            ["2330", "台積電", "—", "—", "+3,200,000", "0"],
        ]
        results = parse_institutional_data(rows, "2026-04-26")
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["stock_id"], "0050")
        self.assertEqual(results[0]["buy_shares"], 1500)

    def test_parse_negative_buy_shares_filtered(self):
        rows = [
            ["2317", "鴻海", "—", "—", "-500,000", "0"],
            ["2330", "台積電", "—", "—", "+2,000,000", "0"],
        ]
        results = parse_institutional_data(rows, "2026-04-26")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["stock_id"], "2330")

    def test_parse_zero_buy_shares_filtered(self):
        rows = [
            ["1101", "台泥", "—", "—", "0", "0"],
            ["2330", "台積電", "—", "—", "+1,000,000", "0"],
        ]
        results = parse_institutional_data(rows, "2026-04-26")
        self.assertEqual(len(results), 1)

    def test_parse_empty_rows(self):
        results = parse_institutional_data([], "2026-04-26")
        self.assertEqual(len(results), 0)

    def test_parse_malformed_rows(self):
        rows = [
            ["0050"],  # IndexError
            ["2330", "台積電", "—", "—", "not_a_number", "0"],  # ValueError
        ]
        results = parse_institutional_data(rows, "2026-04-26")
        self.assertEqual(len(results), 0)


class TestBuildRankedList(unittest.TestCase):
    """测试排序和过滤逻辑."""

    def test_rank_by_buy_amount(self):
        institutional = [
            {"stock_id": "0050", "stock_name": "元大台灣50", "date": "2026-04-26", "buy_shares": 1500},
            {"stock_id": "2330", "stock_name": "台積電", "date": "2026-04-26", "buy_shares": 3000},
        ]
        prices = {"0050": 50.0, "2330": 600.0}
        volumes = {"0050": 10000, "2330": 50000}

        results = build_ranked_list(institutional, prices, volumes)
        self.assertEqual(len(results), 2)
        # 2330 买超金额更高，应排第一
        self.assertEqual(results[0]["stock_id"], "2330")

    def test_filter_low_price(self):
        institutional = [
            {"stock_id": "9999", "stock_name": "水餃股", "date": "2026-04-26", "buy_shares": 5000},
        ]
        prices = {"9999": 5.0}   # 低于 MIN_CLOSE_PRICE=10
        volumes = {"9999": 100000}

        results = build_ranked_list(institutional, prices, volumes)
        self.assertEqual(len(results), 0)

    def test_filter_low_volume(self):
        institutional = [
            {"stock_id": "1234", "stock_name": "冷門股", "date": "2026-04-26", "buy_shares": 5000},
        ]
        prices = {"1234": 20.0}
        volumes = {"1234": 100}   # 低于 MIN_VOLUME=500

        results = build_ranked_list(institutional, prices, volumes)
        self.assertEqual(len(results), 0)

    def test_limit_to_store_limit(self):
        from src.config import STRATEGY_STORE_LIMIT
        institutional = []
        prices = {}
        volumes = {}
        for i in range(100):
            sid = f"{i:04d}"
            institutional.append({"stock_id": sid, "stock_name": f"股票{i}", "date": "2026-04-26", "buy_shares": (100 - i) * 100})
            prices[sid] = 20.0
            volumes[sid] = 10000

        results = build_ranked_list(institutional, prices, volumes)
        self.assertLessEqual(len(results), STRATEGY_STORE_LIMIT)

    def test_missing_price_or_volume_skipped(self):
        institutional = [
            {"stock_id": "9998", "stock_name": "无价格", "date": "2026-04-26", "buy_shares": 1000},
            {"stock_id": "9999", "stock_name": "无成交量", "date": "2026-04-26", "buy_shares": 1000},
        ]
        prices = {"9999": 30.0}
        volumes = {"9998": 50000}

        results = build_ranked_list(institutional, prices, volumes)
        self.assertEqual(len(results), 0)


class TestTrustEntity(unittest.TestCase):
    """测试投信策略列索引."""

    def test_trust_column_index(self):
        """投信应该取列 6（索引 6），不是外资列 4."""
        rows = [
            ["0050", "元大台灣50", "—", "—", "+9,999,999", "—", "+1,000,000"],
        ]
        import src.config as config
        original_entity = config.STRATEGY_ENTITY
        original_columns = dict(config.ENTITY_COLUMN)
        try:
            config.STRATEGY_ENTITY = "trust"
            config.ENTITY_COLUMN["trust"] = 6
            results = parse_institutional_data(rows, "2026-04-26")
            # 投信买超是 +1,000,000 股 → 1000 张
            self.assertEqual(results[0]["buy_shares"], 1000)
        finally:
            config.STRATEGY_ENTITY = original_entity
            config.ENTITY_COLUMN["trust"] = original_columns["trust"]


if __name__ == "__main__":
    unittest.main()
