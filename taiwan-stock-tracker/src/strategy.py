import logging
import src.config as config

log = logging.getLogger(__name__)


def parse_institutional_data(rows, target_date):
    """解析 T86 原始数据，按选定的法人类型提取买超."""
    col_index = config.ENTITY_COLUMN.get(config.STRATEGY_ENTITY, config.ENTITY_COLUMN["foreign"])
    entity_name = "外资" if config.STRATEGY_ENTITY == "foreign" else "投信"
    results = []

    for row in rows:
        try:
            stock_id = row[0].strip()
            stock_name = row[1].strip()
            net_shares = int(row[col_index].replace(",", "").replace("+", "").strip())
            if net_shares <= 0:
                continue
            results.append({
                "stock_id": stock_id,
                "stock_name": stock_name,
                "date": target_date,
                "buy_shares": net_shares // 1000,
            })
        except (IndexError, ValueError):
            continue

    log.info(f"{entity_name}买超: {len(results)} 笔")
    return results


def build_ranked_list(institutional, prices, volumes):
    """合并价格/成交量，过滤冷门股，按买超金额排序取前 N."""
    results = []

    for r in institutional:
        close = prices.get(r["stock_id"])
        vol = volumes.get(r["stock_id"], 0)

        if not close or close <= 0:
            continue
        if close < config.MIN_CLOSE_PRICE:
            continue
        if vol < config.MIN_VOLUME:
            continue

        buy_amount = round(r["buy_shares"] * close * 1000 / 10000, 2)
        results.append({**r, "close_price": close, "buy_amount": buy_amount})

    results.sort(key=lambda x: x["buy_amount"], reverse=True)
    top = results[:config.STRATEGY_STORE_LIMIT]
    log.info(f"排序完成，过滤后 {len(top)} 笔（阈值: 价≥{config.MIN_CLOSE_PRICE}元, 量≥{config.MIN_VOLUME}张）")
    return top
