# -*- coding: utf-8 -*-
"""
Step2 阶段1：赛道方案竞选
5 个多维度切入方案 -> 各自在 298 款有效商品上实算指标 -> 6 维加权评分 -> 决出最佳赛道
输入 features.json，输出 track_result.json / track_report.txt
"""
import json, math, os, sys, statistics as st
from collections import Counter

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = []


def p(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    enc = sys.stdout.encoding or "utf-8"
    print(s.encode(enc, errors="replace").decode(enc, errors="replace"))


with open(os.path.join(BASE, "features.json"), "r", encoding="utf-8") as f:
    FEAT = json.load(f)

POOL = [x for x in FEAT if x["median_price"] is not None]
N = len(POOL)
SITE_MEDIAN = st.median([x["median_price"] for x in POOL])
SITE_TOP50 = sum(1 for x in POOL if x["rank"] <= 50) / N * 100


# ---------------- 赛道定义：每个方案都是多维复合筛选 ----------------
def has(x, key, *vals):
    return any(v in x[key] for v in vals)


def thick_in(x, lo, hi):
    t = x["thickness_max"]
    return t is not None and lo <= t < hi


TRACKS = [
    {
        "id": "T1",
        "name": "窄带高势能 · 1500-2000元腰部护脊主力",
        "angle": "价格带稀缺性 × 头部命中率 × 中等SKU矩阵",
        "logic": [
            "价格带 1500~2000 元（全站仅 29 款供给，却是 Top50 命中率最高的价格带 31.0%）",
            "或 厚度 24~28cm 且价格 1400~2400（该厚度段 Top50 率 23.6%）",
            "材质含 弹簧 或 黄麻（黄麻排名中位 136，显著优于椰棕 170）",
            "命中 0胶/无胶 或 可拆洗（两个高势能功能标签，排名中位 128 / 112）",
        ],
        "filter": lambda x: (
            1500 <= x["median_price"] < 2000
            or (thick_in(x, 24, 28) and 1400 <= x["median_price"] < 2400)
        )
        and (has(x, "materials", "弹簧", "黄麻"))
        and (has(x, "funcs", "0胶/无胶", "可拆洗")),
    },
    {
        "id": "T2",
        "name": "低供给溢价 · 天然材质轻奢深睡",
        "angle": "稀缺材质 × 认证背书视觉 × 高客单",
        "logic": [
            "材质含 羊毛/蚕丝 或 记忆棉（羊毛/蚕丝仅 14 款，排名中位 92 为全站最优）",
            "价格 2000 元以上（避开平价绞肉机）",
            "命中 可拆洗 或 透气 或 分区支撑（高端结构性卖点）",
        ],
        "filter": lambda x: has(x, "materials", "羊毛/蚕丝", "记忆棉")
        and x["median_price"] >= 2000
        and has(x, "funcs", "可拆洗", "透气", "分区支撑"),
    },
    {
        "id": "T3",
        "name": "薄垫高周转 · 8-15cm 旧床改造/租房升级",
        "angle": "厚度错位 × 物流成本优势 × 中价带",
        "logic": [
            "厚度 8~15cm（排名中位 94，全厚度段最优，但仅 29 款供给）",
            "价格 600~1600 元（快消决策价格带）",
            "命中 薄垫/褥垫 或 可拆洗 或 透气（卷包压缩发货可行）",
        ],
        "filter": lambda x: thick_in(x, 8, 16)
        and 600 <= x["median_price"] < 1600
        and has(x, "funcs", "薄垫/褥垫", "可拆洗", "透气"),
    },
    {
        "id": "T4",
        "name": "AI智能电动 · 科技溢价赛道",
        "angle": "技术壁垒 × 高溢价 × 首图卖点高转化",
        "logic": [
            "材质/结构含 AI智能（39 款，排名中位 122，Top50 率 28.2%）",
            "或首图卖点命中「AI智能电动调节」（48 款，Top50 率 27.1%）",
            "价格 2000 元以上",
        ],
        "filter": lambda x: (
            has(x, "materials", "AI智能") or has(x, "selling_points", "AI智能电动调节")
        )
        and x["median_price"] >= 2000,
    },
    {
        "id": "T5",
        "name": "平价放量 · 300-800元椰棕走量（对照组）",
        "angle": "大流量池 × 低客单 × 多SKU铺货",
        "logic": [
            "价格 300~800 元（供给最密集的 70 款红海，Top50 率仅 5.7%）",
            "材质含 椰棕 或 3D空气纤维",
            "SKU 数 ≥ 10（铺货型打法）",
        ],
        "filter": lambda x: 300 <= x["median_price"] < 800
        and has(x, "materials", "椰棕", "3D空气纤维")
        and x["sku_count"] >= 10,
    },
]


# ---------------- 赛道级多维评分标准（权重合计 100）----------------
WEIGHTS = {
    "capacity": 15,      # 市场容量：赛道承载的商品数与SKU厚度
    "competition": 20,   # 竞争疏密：供给密度越低越好（反向）
    "momentum": 20,      # 头部势能：Top50/Top100 命中率
    "premium": 15,       # 溢价能力：价格中位 vs 全站中位
    "barrier": 15,       # 壁垒可破性：头部品牌集中度越低越好（反向）
    "feasible": 15,      # 运营可执行性：SKU矩阵健康度 + 价宽比 + 折扣空间
}

DIM_LABEL = {
    "capacity": "市场容量（商品数×SKU厚度）",
    "competition": "竞争疏密（供给密度反向）",
    "momentum": "头部势能（Top50/Top100命中率）",
    "premium": "溢价能力（价格中位/全站中位）",
    "barrier": "壁垒可破性（CR3集中度反向）",
    "feasible": "运营可执行性（SKU矩阵/价宽比/折扣空间）",
}


def clamp(v, lo=0.0, hi=10.0):
    return max(lo, min(hi, v))


def score_track(tr):
    g = [x for x in POOL if tr["filter"](x)]
    if len(g) < 3:
        return None

    n = len(g)
    sku_total = sum(x["sku_count"] for x in g)
    ranks = [x["rank"] for x in g]
    prices = [x["median_price"] for x in g]
    top50 = sum(1 for x in g if x["rank"] <= 50)
    top100 = sum(1 for x in g if x["rank"] <= 100)
    top50r = top50 / n * 100
    top100r = top100 / n * 100
    rank_med = st.median(ranks)
    price_med = st.median(prices)

    brands = Counter(x["brand"] for x in g)
    cr3 = sum(c for _, c in brands.most_common(3)) / n * 100

    sku_med = st.median([x["sku_count"] for x in g])
    spans = [x["price_span_ratio"] for x in g if x["price_span_ratio"]]
    span_med = st.median(spans) if spans else 1.0
    discs = [x["discount_pct"] for x in g if x["discount_pct"]]
    disc_med = st.median(discs) if discs else 100.0

    # 1) 市场容量：饱和曲线而非硬截断，否则红海赛道也会拿满分
    s_cap = clamp(10 * (1 - math.exp(-(n / 18 + sku_total / 600))))

    # 2) 竞争疏密：供给占比越低越好，占比 20% 以上视为红海
    supply_pct = n / N * 100
    s_comp = clamp(10 - supply_pct / 2)

    # 3) 头部势能：Top50 率 40% 为满分锚点（不用全站基线做除数，否则优等赛道全被截断在 10 分）
    s_mom = clamp(top50r / 40 * 6 + top100r / 60 * 4)

    # 4) 溢价：对全站中位的倍数取对数，4 倍中位为满分，避免天价款线性刷分
    s_prem = clamp(10 * math.log(1 + price_med / SITE_MEDIAN) / math.log(4))

    # 5) 壁垒可破性：CR3 越低越易切入
    s_bar = clamp(10 - cr3 / 10)

    # 6) 可执行性：SKU 落在 9~15 最优、价宽比 2.0 最优、折扣率 68% 最优
    sku_fit = 10 - abs(sku_med - 12) * 0.6
    span_fit = 10 - abs(span_med - 2.0) * 2.5
    disc_fit = 10 - abs(disc_med - 68) * 0.25
    s_feas = clamp((clamp(sku_fit) + clamp(span_fit) + clamp(disc_fit)) / 3)

    dims = {
        "capacity": round(s_cap, 2),
        "competition": round(s_comp, 2),
        "momentum": round(s_mom, 2),
        "premium": round(s_prem, 2),
        "barrier": round(s_bar, 2),
        "feasible": round(s_feas, 2),
    }
    total = round(sum(dims[k] / 10 * w for k, w in WEIGHTS.items()), 2)

    return {
        "id": tr["id"],
        "name": tr["name"],
        "angle": tr["angle"],
        "logic": tr["logic"],
        "n": n,
        "sku_total": sku_total,
        "supply_pct": round(supply_pct, 1),
        "rank_median": rank_med,
        "price_median": round(price_med, 0),
        "top50": top50,
        "top50_rate": round(top50r, 1),
        "top100_rate": round(top100r, 1),
        "cr3": round(cr3, 1),
        "top_brands": brands.most_common(5),
        "sku_median": sku_med,
        "span_median": round(span_med, 2),
        "discount_median": round(disc_med, 1),
        "dims": dims,
        "total": total,
        "members": sorted(
            [
                {
                    "rank": x["rank"],
                    "brand": x["brand"],
                    "title": x["title"],
                    "price": x["median_price"],
                    "sku": x["sku_count"],
                    "mats": x["materials"],
                    "funcs": x["funcs"],
                }
                for x in g
            ],
            key=lambda z: z["rank"],
        ),
    }


p("=" * 78)
p("阶段 1 · 赛道方案竞选")
p("=" * 78)
p(f"样本池：{N} 款（剔除 2 款无价格）｜全站价格中位 ¥{SITE_MEDIAN:.0f}｜全站 Top50 基线率 {SITE_TOP50:.1f}%")
p("")
p("评分维度与权重：")
for k, w in WEIGHTS.items():
    p(f"  {DIM_LABEL[k].ljust(34)} 权重 {w}")

results = []
for tr in TRACKS:
    r = score_track(tr)
    if r is None:
        p(f"\n[跳过] {tr['id']} {tr['name']}：命中样本不足 3 款")
        continue
    results.append(r)

p("")
for r in results:
    p("=" * 78)
    p(f"【{r['id']}】{r['name']}    综合得分 {r['total']}")
    p(f"切入角度：{r['angle']}")
    p("筛选逻辑：")
    for l in r["logic"]:
        p(f"    · {l}")
    p(f"命中 {r['n']} 款（占全站 {r['supply_pct']}%）｜SKU 合计 {r['sku_total']} 条")
    p(f"排名中位 {r['rank_median']:.0f}｜价格中位 ¥{r['price_median']:.0f}｜"
      f"Top50 {r['top50']} 款（{r['top50_rate']}%）｜Top100 率 {r['top100_rate']}%")
    p(f"CR3 品牌集中度 {r['cr3']}%｜SKU 中位 {r['sku_median']:.0f}｜"
      f"价宽比中位 {r['span_median']}｜折扣中位 {r['discount_median']}%")
    p(f"主要玩家：{'、'.join(f'{b}({c})' for b, c in r['top_brands'])}")
    p("分项得分：" + "  ".join(f"{k}={v}" for k, v in r["dims"].items()))

p("")
p("=" * 78)
p("竞选排名")
p("=" * 78)
rank_sorted = sorted(results, key=lambda z: -z["total"])
p("名次 方案 " + "".join(k.rjust(12) for k in WEIGHTS) + "      总分")
for i, r in enumerate(rank_sorted, 1):
    p(f"{str(i).rjust(2)}   {r['id']} "
      + "".join(f"{r['dims'][k]:12.2f}" for k in WEIGHTS)
      + f"{r['total']:10.2f}   {r['name']}")

best = rank_sorted[0]
p("")
p(f">>> 最佳赛道：【{best['id']}】{best['name']}（{best['total']} 分）")
p("")
p("该赛道现有玩家明细（按排名）：")
for m in best["members"][:25]:
    p(f"  #{m['rank']:3d} {m['brand'][:10].ljust(11)} ¥{m['price']:7.0f} SKU={m['sku']:3d} "
      f"材={'/'.join(m['mats'][:4])} 功={'/'.join(m['funcs'][:4])}")

with open(os.path.join(BASE, "track_result.json"), "w", encoding="utf-8") as f:
    json.dump(
        {"site": {"n": N, "price_median": SITE_MEDIAN, "top50_baseline": SITE_TOP50},
         "weights": WEIGHTS, "dim_label": DIM_LABEL, "tracks": results, "best": best["id"]},
        f, ensure_ascii=False, indent=1,
    )
with open(os.path.join(BASE, "track_report.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(OUT))
print("\n>>> track_result.json / track_report.txt 已生成")
