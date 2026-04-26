import logging
import requests
import time
from src.config import (
    LINE_ACCESS_TOKEN, LINE_API_URL, NOTION_DB_URL,
    STRATEGY_STORE_LIMIT, STRATEGY_NOTIFY_LIMIT,
    MAX_RETRIES, RETRY_BACKOFF,
)

log = logging.getLogger(__name__)


def send_line_message(records, target_date):
    """通过 LINE Broadcast 推送前 N 名摘要."""
    top = records[:STRATEGY_NOTIFY_LIMIT]
    lines = [
        f"🏦 外資買超日報 {target_date}",
        "─" * 24,
        f"📊 今日前 {STRATEGY_NOTIFY_LIMIT} 名（完整前{STRATEGY_STORE_LIMIT}名已存 Notion）\n",
    ]

    for rank, r in enumerate(top, start=1):
        lines.append(
            f"{rank:>2}. {r['stock_name']}（{r['stock_id']}）\n"
            f"    買超 {r['buy_shares']:,} 張｜收盤 {r['close_price']} 元\n"
            f"    💰 金額約 {r['buy_amount']:,.0f} 萬元"
        )

    lines += [
        "\n" + "─" * 24,
        f"📋 完整前{STRATEGY_STORE_LIMIT}名 → Notion：",
        NOTION_DB_URL,
    ]

    message = "\n".join(lines)
    headers = {
        "Authorization": f"Bearer {LINE_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    for attempt, delay in enumerate(RETRY_BACKOFF, start=1):
        try:
            resp = requests.post(
                LINE_API_URL,
                headers=headers,
                json={"messages": [{"type": "text", "text": message}]},
                timeout=15,
            )
            if resp.status_code == 200:
                log.info("LINE Broadcast 推送成功")
                return True
            else:
                log.error(f"LINE 失败: HTTP {resp.status_code} {resp.text}")
                if attempt < MAX_RETRIES:
                    time.sleep(delay)
                else:
                    return False
        except requests.RequestException as e:
            log.error(f"LINE 推送异常: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(delay)
            else:
                return False

    return False
