import time
import logging
import requests
from src.config import TWSE_HEADERS, TWSE_REQUEST_DELAY, MAX_RETRIES, RETRY_BACKOFF

log = logging.getLogger(__name__)


def _retry_request(url, params=None, headers=None, timeout=30):
    """带指数退避重试的 HTTP GET."""
    for attempt, delay in enumerate(RETRY_BACKOFF, start=1):
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=timeout)
            resp.raise_for_status()
            return resp
        except requests.RequestException as e:
            log.warning(f"请求失败 (尝试 {attempt}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES:
                log.info(f"等待 {delay} 秒后重试...")
                time.sleep(delay)
            else:
                raise
    return None


def get_target_date():
    """反向探测非交易日：当天往前试，最多 5 天."""
    from datetime import date, timedelta
    today = date.today()
    for delta in range(5):
        d = today - timedelta(days=delta)
        yield d.isoformat()


def fetch_twse_institutional(target_date):
    """抓取 T86 三大法人买卖超数据."""
    date_str = target_date.replace("-", "")
    url = "https://www.twse.com.tw/rwd/zh/fund/T86"
    params = {"date": date_str, "selectType": "ALL", "response": "json"}
    log.info(f"正在拉取 TWSE 三大法人数据，日期: {target_date}")

    try:
        resp = _retry_request(url, params=params, headers=TWSE_HEADERS, timeout=30)
    except requests.RequestException as e:
        log.error(f"TWSE T86 请求彻底失败: {e}")
        return []

    data = resp.json()
    if data.get("stat") != "OK":
        log.warning(f"TWSE 非交易日或无数据: {data.get('stat')}")
        return []

    rows = data.get("data", [])
    log.info(f"TWSE T86 原始数据: {len(rows)} 笔")
    return rows


def fetch_twse_close_prices_and_volume(target_date):
    """抓取 MI_INDEX 收盘价和成交量."""
    date_str = target_date.replace("-", "")
    url = "https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX"
    params = {"date": date_str, "type": "ALLBUT0999", "response": "json"}
    log.info("正在拉取收盘价和成交量...")

    try:
        resp = _retry_request(url, params=params, headers=TWSE_HEADERS, timeout=30)
    except requests.RequestException as e:
        log.error(f"TWSE MI_INDEX 请求彻底失败: {e}")
        return {}, {}

    data = resp.json()
    prices = {}
    volumes = {}

    for table in data.get("tables", []):
        fields = table.get("fields", [])
        rows = table.get("data", [])
        if not rows or len(fields) < 10:
            continue

        try:
            close_idx = next(i for i, f in enumerate(fields) if "收盤" in f)
            volume_idx = next(i for i, f in enumerate(fields) if "成交股數" in f)
            id_idx = next(i for i, f in enumerate(fields) if "代號" in f or "代碼" in f)
        except StopIteration:
            continue

        for row in rows:
            try:
                stock_id = row[id_idx].strip()
                prices[stock_id] = float(row[close_idx].replace(",", ""))
                volumes[stock_id] = int(float(row[volume_idx].replace(",", "")))
            except (ValueError, IndexError, KeyError):
                continue

        if prices and volumes:
            break

    log.info(f"收盘价: {len(prices)} 只 | 成交量: {len(volumes)} 只")
    return prices, volumes
