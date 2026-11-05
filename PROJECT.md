# chokepoint-research — 产业链卡点研究方法论 + A股AI基础设施实证

## 这是什么

把「供应链卡点(choke point / bottleneck)投资研究法」本地化落地:
一套可复用的研究流程(skill) + 一份用真实公开数据跑出来的 A 股 AI 基础设施产业链卡点报告。

灵感来源是公开传播的 Serenity(@aleabitoreddit,俗称「白毛股神」)式瓶颈投资思路,以及 GitHub 上几个跟进它的开源 skill 项目。
本项目不复刻任何仓库的文本,规则/模板/数据源/脚本全部自写,并针对本机条件(A股、中文、无付费数据源)做了适配。

## 硬规则(改这个项目时必须守住)

1. **分层标注**:每条信息必须标 `[事实]` / `[观点]` / `[推断]` / `[风险]` / `[未知]`;查不到就写 `[未查到]`,禁止用估算数字冒充查证结果。
2. **证据阶梯**:一手公告/年报/交易所文件 > 行业机构数据 > 权威媒体 > 券商研报 > 社媒/自媒体。社媒只能当线索。
3. **不给综合评分**,只给排序 + 理由;每个结论必须带 ≥3 条反证(失效)条件。
4. **不做单边看多**;必须写「这个逻辑可能怎么错」。
5. 交付物仅作研究辅助,**不构成投资建议**。

## 文件地图

```
chokepoint-research/
├── PROJECT.md                     ← 本文件(接手先读这个)
├── SKILL.md                       ← 方法论主体(已同步安装为 Hermes skill: industry-chokepoint)
├── references/
│   ├── evidence-ladder.md         ← 证据分级细则与判定示例
│   ├── cn-data-sources.md         ← 中国市场的免费一手数据源与检索套路
│   └── output-template.md         ← 报告模板(含分层标注写法)
├── scripts/
│   ├── quote.py                   ← 免登录行情/板块快照(东财公开接口)
│   ├── fetch_fin.py               ← 批量取业绩报表(营收/净利/毛利率)+ 可选现金流
│   ├── fetch_cf_yoy.py            ← 取多期经营现金流做同比
│   ├── check_responsive.py        ← Playwright 响应式回归(320/375/412/768/1280)
│   └── md2html.py                 ← md → 自包含 HTML
└── reports/
    ├── 2026-11-05-A股AI基础设施链卡点.md  ← 最新(2026 三季报口径)
    ├── 2026-11-05-A股AI基础设施链卡点.html
    ├── serenity-guide-2026-09-23.html     ← 面板页(内容已更新到 2026-11-05)
    └── 2026-09-23-*                       ← 上一版存档
```

Hermes skill 安装位置:`%LOCALAPPDATA%/hermes/skills/research/industry-chokepoint/`
GitHub 仓库:`j19031228/chokepoint-research`(私有,可改公开)

## 工具依赖

- 检索:web_search(ddgs 后端)、browser_exec、curl
- 行情:scripts/quote.py,走东方财富公开接口(无需 key);akshare 未安装,不是必需
- 推送:gh CLI(`export PATH="$LOCALAPPDATA/hermes/bin:$PATH"`)

## 踩坑

- 本机 web_extract 后端是 ddgs,只能搜不能抓正文 → 抓页面用 curl 或 browser_exec。
- 中文财经数字没有统一口径(资本开支含不含融资租赁等),引用时必须连口径一起抄。
- 小市值标的的「卡点」叙事最容易失真:主营占比、收入确认时点、客户名单必须回到年报/公告。

## 交接日志

- 2026-09-23 立项:抓取 4 个同类开源仓库做方法比对 → 自写方法论 → 6 路并行证据收集 → 产出实证报告 → 推送 GitHub + 落 Obsidian。
- 2026-11-05 季度重跑:财务全部换成 2026 三季报(东财公开接口,25 家);逐条核验上一版熔断表 11 条(3 已触发 / 6 未触发 / 2 无法确认)。
  - 关键修正:①日东纺"不涨价"被证伪,FY2026 已实施价格改定,电子材料 Q1 营业利润 +70.0%;②"福岛 2026Q4 产能 3 倍"实为 FY2028 口径,2026-12 完工的是处理工程;
    ③中际旭创现金流转正(9M 80.08 亿),但新易盛现金流 −68.4%(新发现);④天孚有源 Q3 恢复产出,"被光芯片卡"风险撤下。
  - 新增脚本:fetch_fin.py / fetch_cf_yoy.py / check_responsive.py。响应式 320–1280 全通过。
