import os

# ── 必需的环境变量 ──────────────────────────────────────
NOTION_TOKEN      = os.environ.get("NOTION_TOKEN", "")
NOTION_DB_ID      = os.environ.get("NOTION_DB_ID", "")
LINE_ACCESS_TOKEN = os.environ.get("LINE_ACCESS_TOKEN", "")

# ── Notion ──────────────────────────────────────────────
NOTION_DB_URL     = f"https://www.notion.so/{NOTION_DB_ID.replace('-', '')}"
NOTION_API_VERSION = "2022-06-28"

# ── LINE ────────────────────────────────────────────────
LINE_API_URL      = "https://api.line.me/v2/bot/message/broadcast"

# ── TWSE ────────────────────────────────────────────────
TWSE_HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
TWSE_REQUEST_DELAY = 2  # 两次请求间隔秒数

# ── 策略参数 ────────────────────────────────────────────
STRATEGY_STORE_LIMIT    = 50   # 写入 Notion 数量
STRATEGY_NOTIFY_LIMIT   = 20   # LINE 推送数量
STRATEGY_ENTITY         = "foreign"  # "foreign" | "trust"

# T86 接口列索引：外资本日买卖超 / 投信本日买卖超
ENTITY_COLUMN = {
    "foreign": 4,   # 外资买卖超股数
    "trust":   5,   # 投信买卖超股数
}

# 流动性过滤阈值
MIN_CLOSE_PRICE = 10    # 收盘价 ≥ 10 元
MIN_VOLUME      = 500   # 成交量 ≥ 500 张

# ── 重试配置 ────────────────────────────────────────────
MAX_RETRIES     = 3
RETRY_BACKOFF   = [2, 4, 8]  # 秒
