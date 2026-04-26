import logging
import time

from src.config import (
    TWSE_REQUEST_DELAY, STRATEGY_ENTITY,
    STRATEGY_STORE_LIMIT, STRATEGY_NOTIFY_LIMIT,
)
from src.scraper import get_target_date, fetch_twse_institutional, fetch_twse_close_prices_and_volume
from src.strategy import parse_institutional_data, build_ranked_list
from src.notion import check_duplicate_records, write_to_notion
from src.notifier import send_line_message

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)


def main():
    log.info("=" * 50)
    entity_name = "外资" if STRATEGY_ENTITY == "foreign" else "投信"
    log.info(f"台湾{entity_name}买超监控（数据源: TWSE）")
    log.info("=" * 50)

    # 反向探测非交易日
    for target_date in get_target_date():
        log.info(f"尝试目标日期: {target_date}")
        raw_rows = fetch_twse_institutional(target_date)
        if raw_rows:
            break
    else:
        log.warning("连续 5 天无数据，退出。")
        return

    # 解析
    institutional = parse_institutional_data(raw_rows, target_date)
    if not institutional:
        log.warning("买超名单为空，退出。")
        return

    # 拉取价格/成交量
    time.sleep(TWSE_REQUEST_DELAY)
    prices, volumes = fetch_twse_close_prices_and_volume(target_date)

    # 排序 + 过滤
    ranked = build_ranked_list(institutional, prices, volumes)
    if not ranked:
        log.warning("过滤后排名为空，退出。")
        return

    # 去重检查
    if check_duplicate_records(target_date):
        log.info(f"Notion 已有 {target_date} 的记录，跳过写入")
        return

    # 写入 Notion + LINE 推送
    success = write_to_notion(ranked)
    sent = send_line_message(ranked, target_date)

    status = "完成 ✅" if sent else "完成 ⚠️ LINE 推送失败"
    log.info(f"[汇总] 日期: {target_date} | 筛选: {len(ranked)} 笔 | Notion: {success}/{len(ranked)} | LINE: {'OK' if sent else 'FAIL'}")
    log.info(status)


if __name__ == "__main__":
    main()
