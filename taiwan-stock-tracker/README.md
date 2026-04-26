# 台股外资买超自动监控

每日自动抓取 TWSE 三大法人买卖超数据，筛选后写入 Notion，并通过 LINE Broadcast 推送摘要。

## 文件结构

```
├── main.py                          # 编排入口（thin runner）
├── requirements.txt                 # 依赖
├── src/
│   ├── __init__.py
│   ├── config.py                    # 环境变量 + 策略常量
│   ├── scraper.py                   # TWSE 数据抓取（含重试）
│   ├── strategy.py                  # 筛选逻辑（排序、过滤、去重）
│   ├── notion.py                    # Notion 写入 + 重复检测
│   └── notifier.py                  # LINE Broadcast 推送
├── tests/
│   ├── __init__.py
│   └── test_scraper.py              # 单元测试
└── .github/workflows/
    └── daily_stock.yml              # GitHub Actions 定时任务
```

## 快速开始

### 第一步：建立 Notion Database

在 Notion 新建一个 Database，添加以下 **7 个字段**（类型必须匹配）：

| 字段名       | 类型        |
|------------|-----------|
| 名稱         | Title     |
| 日期         | Date      |
| 代碼         | Rich Text |
| 買超金額萬元    | Number    |
| 收盤價        | Number    |
| 買超張數      | Number    |
| 排名         | Number    |

> ⚠️ 创建完后，把你的 Notion Integration **Invite** 进这个 Database。

### 第二步：在 GitHub 添加 3 个 Secrets

进入仓库 → Settings → Secrets and variables → Actions → New repository secret

| Secret 名称         | 来源                                      |
|--------------------|------------------------------------------|
| `NOTION_TOKEN`     | Notion Integration → Internal Token      |
| `NOTION_DB_ID`     | Notion DB URL 中间的32位字符串              |
| `LINE_ACCESS_TOKEN`| LINE Developers → Channel access token   |

> **注意**：LINE 推送使用 **Broadcast** 模式，所有关注官方账号的用户都会收到。不需要 `LINE_USER_ID`。
> LINE Official Account 需要为 **verified** 状态才能使用 Broadcast。

### 第三步：推送代码到私有仓库

```bash
git remote add origin https://github.com/你的用户名/仓库名.git
git push -u origin main
```

### 第四步：测试运行

进入仓库 → Actions → 台股外資買超日報 → Run workflow（手动触发一次）

---

## 策略参数调整

打开 `src/config.py`，修改顶部的策略常量：

```python
STRATEGY_STORE_LIMIT    = 50   # 写入 Notion 数量
STRATEGY_NOTIFY_LIMIT   = 20   # LINE 推送数量
STRATEGY_ENTITY         = "foreign"  # "foreign" | "trust"

# 流动性过滤阈值
MIN_CLOSE_PRICE = 10    # 收盘价 ≥ 10 元（过滤水饺股）
MIN_VOLUME      = 500   # 成交量 ≥ 500 张（过滤冷门股）

# TWSE 请求间隔（秒）
TWSE_REQUEST_DELAY = 2
```

### 切换投信策略

将 `STRATEGY_ENTITY` 改为 `"trust"` 即可追踪投信买卖超。

### 流动性过滤

默认过滤收盘价低于 10 元、成交量低于 500 张的股票，避免推荐冷门股/地雷股。
如需调整，修改 `MIN_CLOSE_PRICE` 和 `MIN_VOLUME` 即可。

## 运行时间

- 自动运行：每个交易日（周一至周五）台北时间 **16:05**
- 手动运行：GitHub Actions → Run workflow

## 功能特性

- **反向探测非交易日**：自动回推找最近交易日，不依赖周几推算
- **流动性过滤**：过滤水饺股和冷门股，提升推荐质量
- **Notion 去重**：同一天重复运行不会重复写入
- **HTTP 重试**：所有请求使用指数退避重试（最多 3 次）
- **LINE Broadcast**：所有关注官方账号的用户都能收到推送
- **可切换法人类型**：外资 / 投信一键切换

## 本地测试

```bash
python -m unittest tests/test_scraper.py -v
```
