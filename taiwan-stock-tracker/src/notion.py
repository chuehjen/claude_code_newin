import logging
import requests
import time
from src.config import (
    NOTION_TOKEN, NOTION_DB_ID, NOTION_API_VERSION, NOTION_DB_URL,
    MAX_RETRIES, RETRY_BACKOFF,
)

log = logging.getLogger(__name__)


def _headers():
    return {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_API_VERSION,
    }


def check_duplicate_records(target_date):
    """查询 Notion 当天是否已有记录."""
    payload = {
        "filter": {"property": "日期", "date": {"equals": target_date}},
        "page_size": 1,
    }
    try:
        resp = requests.post(
            f"https://api.notion.com/v1/databases/{NOTION_DB_ID}/query",
            headers=_headers(), json=payload, timeout=15,
        )
        resp.raise_for_status()
        results = resp.json().get("results", [])
        return len(results) > 0
    except requests.RequestException as e:
        log.warning(f"Notion 去重查询失败: {e}，将继续写入")
        return False


def write_to_notion(records):
    """写入记录到 Notion，每条间隔避免限速."""
    headers = _headers()
    success = 0
    skipped = 0

    for rank, r in enumerate(records, start=1):
        payload = {
            "parent": {"database_id": NOTION_DB_ID},
            "properties": {
                "名稱": {"title": [{"text": {"content": r["stock_name"]}}]},
                "日期": {"date": {"start": r["date"]}},
                "代碼": {"rich_text": [{"text": {"content": r["stock_id"]}}]},
                "買超金額萬元": {"number": r["buy_amount"]},
                "收盤價": {"number": r["close_price"]},
                "買超張數": {"number": r["buy_shares"]},
                "排名": {"number": rank},
            },
        }

        for attempt, delay in enumerate(RETRY_BACKOFF, start=1):
            try:
                resp = requests.post(
                    "https://api.notion.com/v1/pages",
                    headers=headers, json=payload, timeout=15,
                )
                if resp.status_code in (200, 201):
                    success += 1
                    break
                else:
                    log.warning(f"Notion 写入失败 ({r['stock_id']}): HTTP {resp.status_code}")
                    if attempt < MAX_RETRIES:
                        time.sleep(delay)
                    else:
                        skipped += 1
            except requests.RequestException as e:
                log.warning(f"Notion 写入异常 ({r['stock_id']}): {e}")
                if attempt < MAX_RETRIES:
                    time.sleep(delay)
                else:
                    skipped += 1

    log.info(f"Notion 写入: 成功 {success}/{len(records)}, 失败 {skipped}")
    return success
