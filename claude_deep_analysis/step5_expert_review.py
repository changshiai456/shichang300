# -*- coding: utf-8 -*-
"""
Step5 阶段3：多智能体专家评审
四位专家（数据 / 操盘 / 供应链 / 视觉）各持独立评分维度，对 5 款方案打分。
凡能回到 300 款原始数据验证的指标（标签 Top50 率、价格带势能、赛道 SKU 拥挤度）一律实算；
仅 BOM 成本与工艺复杂度来自设计侧估算，报告中单独标注。
输出 review_result.json / review_report.txt
"""
import json, math, os, sys, statistics as st

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = []


def p(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    enc = sys.stdout.encoding or "utf-8"
    print(s.encode(enc, errors="replace").decode(enc, errors="replace"))


FEAT = json.load(open(os.path.join(BASE, "features.json"), encoding="utf-8"))
DS = json.load(open(os.path.join(BASE, "dataset.json"), encoding="utf-8"))
TR = json.load(open(os.path.join(BASE, "track_result.json"), encoding="utf-8"))
PRODUCTS = json.load(open(os.path.join(BASE, "products.json"), encoding="utf-8"))

POOL = [x for x in FEAT if x["median_price"] is not None]
BEST = [t for t in TR["tracks"] if t["id"] == TR["best"]][0]
TRACK_RANKS = {m["rank"] for m in BEST["members"]}
TRACK = [x for x in POOL if x["rank"] in TRACK_RANKS]
SKUMAP = {d["rank"]: d["skus"] for d in DS["products"]}


def clamp(v, lo=0.0, hi=10.0):
    return max(lo, min(hi, v))


def tag_top50(key, tag):
    """某标签在全站 300 款中的 Top50 命中率（实测）"""
    sub = [x for x in POOL if tag in x[key]]
    if not sub:
        return None, 0
    return sum(1 for x in sub if x["rank"] <= 50) / len(sub) * 100, len(sub)


def track_penetration(key, tag):
    sub = [x for x in TRACK if tag in x[key]]
    return len(sub) / len(TRACK) * 100


def band_top50(price):
    bands = [(0, 300), (300, 800), (800, 1500), (1500, 2000),
             (2000, 3000), (3000, 5000), (5000, 10000), (10000, 9e9)]
    for lo, hi in bands:
        if lo <= price < hi:
            sub = [x for x in POOL if lo <= x["median_price"] < hi]
            return sum(1 for x in sub if x["rank"] <= 50) / len(sub) * 100, f"{lo}-{hi:.0f}"
    return None, "?"


def thickness_top50(t):
    segs = [(0, 8), (8, 15), (15, 20), (20, 24), (24, 28), (28, 99)]
    for lo, hi in segs:
        if lo <= t < hi:
            sub = [x for x in POOL if x["thickness_max"] is not None and lo <= x["thickness_max"] < hi]
            if not sub:
                return None, f"{lo}-{hi}cm"
            return sum(1 for x in sub if x["rank"] <= 50) / len(sub) * 100, f"{lo}-{hi}cm"
    return None, "?"


def track_sku_density(lo, hi):
    """赛道内落在该价格区间的 SKU 条数 —— 越多说明正面撞车越狠"""
    n = 0
    for x in TRACK:
        for s in SKUMAP.get(x["rank"], []):
            v = s.get("price")
            if isinstance(v, (int, float)) and v == v and lo <= v <= hi:
                n += 1
    return n


# ============================ 专家 1：数据分析专家 ============================
def expert_data(pr):
    notes = []
    # 1) 标签势能：所有标签在全站的实测 Top50 率均值（全站基线 16.4%）
    rates = []
    for key, tags in [("selling_points", pr["tags_selling"]),
                      ("marketing_text", pr["tags_marketing"]),
                      ("funcs", pr["tags_funcs"]),
                      ("visual_format", pr["tags_visual"])]:
        for t in tags:
            r, n = tag_top50(key, t)
            if r is not None and n >= 8:
                rates.append(r)
    tag_avg = st.mean(rates) if rates else 0
    s_tag = clamp(tag_avg / 25 * 10)
    notes.append(f"命中标签全站实测 Top50 率均值 {tag_avg:.1f}%（全站基线 16.4%，25% 为满分锚点）")

    # 2) 价格带势能
    br, blabel = band_top50(pr["price_median"])
    s_band = clamp(br / 31 * 10)
    notes.append(f"主力价位落在 ¥{blabel} 带，该带 Top50 率 {br:.1f}%")

    # 3) 厚度段势能
    tr_, tlabel = thickness_top50(pr["thickness"])
    s_thick = clamp(tr_ / 25 * 10) if tr_ else 5.0
    notes.append(f"{pr['thickness']}cm 属 {tlabel} 段，该段 Top50 率 {tr_:.1f}%")

    # 4) SKU 矩阵健康度：全站 9-15 个 SKU 档 Top50 率 26.8% 最优，价宽比 1.5-2.5 最优
    sku_fit = 10 - abs(pr["sku_count"] - 12) * 0.6
    span_fit = 10 - abs(pr["span_ratio"] - 2.0) * 3.0
    s_matrix = clamp((clamp(sku_fit) + clamp(span_fit)) / 2)
    notes.append(f"SKU {pr['sku_count']} 个 / 价宽比 {pr['span_ratio']}（最优区间 9-15 个、1.5-2.5）")

    dims = {"标签势能": round(s_tag, 2), "价格带势能": round(s_band, 2),
            "厚度段势能": round(s_thick, 2), "SKU矩阵健康度": round(s_matrix, 2)}
    w = {"标签势能": 35, "价格带势能": 30, "厚度段势能": 15, "SKU矩阵健康度": 20}
    return dims, w, notes


# ============================ 专家 2：电商操盘专家 ============================
def expert_ops(pr):
    notes = []
    # 1) 引流定价：全站明示主图标价款 Top50 率 25.0%，未标价 15.0%；标价贴近最低SKU 效果最好
    lowest = pr["price_min"]
    ratio = pr["main_image_price"] / lowest * 100
    if 95 <= ratio <= 105:
        s_price = 10.0
        notes.append(f"主图价 ¥{pr['main_image_price']} 紧贴最低 SKU ¥{lowest}（{ratio:.0f}%），属全站排名中位 60 的精准对标策略")
    elif ratio < 95:
        s_price = clamp(10 - (95 - ratio) / 5)
        notes.append(f"主图价低于最低 SKU {100-ratio:.0f}%，属深度补贴引流（全站该策略排名中位 256，落地风险高）")
    else:
        s_price = clamp(10 - (ratio - 105) / 8)
        notes.append(f"主图价高于最低 SKU {ratio-100:.0f}%，属高配锚定（全站该策略排名中位 115）")

    # 2) 钩子效力：营销钩子实测 Top50 率 + 数量
    rates = []
    for t in pr["tags_marketing"]:
        r, n = tag_top50("marketing_text", t)
        if r:
            rates.append(r)
    hook_avg = st.mean(rates) if rates else 0
    cnt_fit = 10 - abs(len(pr["tags_marketing"]) - 4) * 1.5
    s_hook = clamp((clamp(hook_avg / 25 * 10) + clamp(cnt_fit)) / 2)
    notes.append(f"{len(pr['tags_marketing'])} 个钩子，实测 Top50 率均值 {hook_avg:.1f}%")

    # 3) 梯度爬坡：SKU 多时相邻价差天然变小，改按 8% 阈值聚成价格档位，4~6 档为健康升级路径
    ps = sorted(s["price"] for s in pr["ladder"])
    tiers = [ps[0]]
    for v in ps[1:]:
        if v > tiers[-1] * 1.08:
            tiers.append(v)
    nt = len(tiers)
    span_fit = 10 - abs(pr["span_ratio"] - 2.0) * 3.0
    tier_fit = 10 - abs(nt - 5) * 1.6
    s_ladder = clamp((clamp(tier_fit) + clamp(span_fit)) / 2)
    notes.append(f"聚成 {nt} 个价格档位 {'/'.join(f'{v:.0f}' for v in tiers)}"
                 f"，价宽比 {pr['span_ratio']}（健康区间 4~6 档、1.5~2.5 倍）")

    # 4) 撞车规避：赛道内已有 SKU 在本款价格区间的拥挤度
    dens = track_sku_density(pr["price_min"], pr["price_max"])
    s_avoid = clamp(10 - dens / 20)
    notes.append(f"赛道内已有 {dens} 条 SKU 落在 ¥{pr['price_min']}-{pr['price_max']} 区间（越少越好切）")

    dims = {"引流定价策略": round(s_price, 2), "钩子效力": round(s_hook, 2),
            "梯度爬坡合理性": round(s_ladder, 2), "撞车规避度": round(s_avoid, 2)}
    w = {"引流定价策略": 30, "钩子效力": 25, "梯度爬坡合理性": 20, "撞车规避度": 25}
    return dims, w, notes


# ============================ 专家 3：供应链专家 ============================
def expert_supply(pr):
    notes = []
    # 1) 毛利（设计侧 BOM 估算）
    s_margin = clamp((pr["gross_margin"] - 40) / 2.5)
    notes.append(f"毛利率中位 {pr['gross_margin']}%（BOM 为设计估算值，非榜单数据）")

    # 2) BOM 复杂度：材质种类 + 结构层数，越简单越好开模
    layers = pr["construction"].count("→") + 1
    mats = len(pr["tags_materials"])
    s_bom = clamp(10 - (layers - 4) * 0.8 - (mats - 2) * 0.8)
    notes.append(f"{mats} 类主材 / {layers} 层结构")

    # 3) 备货压力：SKU 数越多、跨度越大，滞销尾货风险越高
    s_stock = clamp(10 - (pr["sku_count"] - 3) * 0.8 - (pr["span_ratio"] - 1.5) * 3)
    notes.append(f"{pr['sku_count']} 个 SKU / 价宽比 {pr['span_ratio']}，备货与尾货风险")

    # 4) 物流：厚度直接决定体积重与能否卷包压缩
    t = pr["thickness"]
    if t <= 15:
        s_log = 10.0
        notes.append(f"{t}cm 可卷包压缩，物流成本约为厚垫的 1/3，且无上楼难题")
    else:
        s_log = clamp(10 - (t - 15) * 0.45)
        notes.append(f"{t}cm 需整垫发货，体积重高且存在入户/电梯风险")

    dims = {"毛利空间": round(s_margin, 2), "BOM复杂度": round(s_bom, 2),
            "备货风险": round(s_stock, 2), "物流成本": round(s_log, 2)}
    w = {"毛利空间": 35, "BOM复杂度": 20, "备货风险": 20, "物流成本": 25}
    return dims, w, notes


# ============================ 专家 4：视觉专家 ============================
def expert_visual(pr):
    notes = []
    # 1) 视觉形式实测效力
    rates, pens = [], []
    for t in pr["tags_visual"]:
        r, n = tag_top50("visual_format", t)
        if r:
            rates.append(r)
            pens.append(track_penetration("visual_format", t))
    v_avg = st.mean(rates) if rates else 0
    s_form = clamp(v_avg / 32 * 10)
    notes.append(f"采用「{'/'.join(pr['tags_visual'])}」，全站实测 Top50 率 {v_avg:.1f}%（最高形式为 31.8%）")

    # 2) 赛道差异化：该视觉形式在赛道内渗透越低越显眼
    pen = st.mean(pens) if pens else 50
    s_diff = clamp(10 - pen / 5)
    notes.append(f"该视觉形式在赛道内渗透仅 {pen:.1f}%，视觉辨识度可拉开")

    # 3) 信息密度：主图 3 行卖点最优，利益点 4 条最优
    pt_fit = 10 - abs(len(pr["main_image_points"]) - 3) * 2.0
    bn_fit = 10 - abs(len(pr["benefits"]) - 4) * 1.5
    s_info = clamp((clamp(pt_fit) + clamp(bn_fit)) / 2)
    notes.append(f"{len(pr['main_image_points'])} 行主卖点 + {len(pr['benefits'])} 条利益点")

    # 4) 卖点可验证性：能否在图上落成实物证据（报告/标尺/对比/剖面）
    evidence = ["报告", "标尺", "对比", "剖面", "分解", "数值", "实拍", "透视"]
    hit = sum(1 for e in evidence if e in pr["visual"])
    s_proof = clamp(4 + hit * 2.5)
    notes.append(f"视觉中含 {hit} 类实证元素（检测报告/标尺/对比/剖面等）")

    dims = {"视觉形式效力": round(s_form, 2), "赛道差异化": round(s_diff, 2),
            "信息密度": round(s_info, 2), "卖点可验证性": round(s_proof, 2)}
    w = {"视觉形式效力": 30, "赛道差异化": 25, "信息密度": 20, "卖点可验证性": 25}
    return dims, w, notes


EXPERTS = [
    ("数据分析专家", expert_data, 30),
    ("电商操盘专家", expert_ops, 30),
    ("供应链专家", expert_supply, 20),
    ("视觉专家", expert_visual, 20),
]

p("=" * 78)
p("阶段 3 · 多智能体专家评审")
p("=" * 78)
p(f"评审对象：赛道 {BEST['id']}「{BEST['name']}」下的 5 款方案")
p("专家权重：" + "、".join(f"{n} {w}%" for n, _, w in EXPERTS))
p("口径：标签 Top50 率 / 价格带势能 / 厚度段势能 / 赛道 SKU 拥挤度 均由 298 款榜单实算；")
p("      BOM 成本与工艺层数为设计侧估算，仅供应链专家维度受其影响。")
p("")

results = []
for pr in PRODUCTS:
    p("=" * 78)
    p(f"【{pr['id']}】{pr['name']}")
    p("=" * 78)
    detail, total = {}, 0.0
    for ename, fn, ew in EXPERTS:
        dims, w, notes = fn(pr)
        sub = sum(dims[k] / 10 * w[k] for k in dims)  # 0-100
        total += sub * ew / 100
        detail[ename] = {"dims": dims, "weights": w, "score": round(sub, 2), "notes": notes}
        p(f"\n-- {ename}（权重 {ew}%）得分 {sub:.1f}/100")
        for k, v in dims.items():
            p(f"     {k.ljust(14)} {v:5.2f}/10  ×{w[k]}%")
        for nt in notes:
            p(f"     · {nt}")
    total = round(total, 2)
    p(f"\n>> 综合得分：{total}/100")
    p("")
    results.append({"id": pr["id"], "name": pr["name"], "total": total, "detail": detail})

p("=" * 78)
p("终极选拔结果")
p("=" * 78)
order = sorted(results, key=lambda z: -z["total"])
p("名次  方案  " + "".join(n.rjust(16) for n, _, _ in EXPERTS) + "      综合")
for i, r in enumerate(order, 1):
    p(f"{str(i).rjust(2)}    {r['id']}  "
      + "".join(f"{r['detail'][n]['score']:16.1f}" for n, _, _ in EXPERTS)
      + f"{r['total']:10.2f}   {r['name']}")

champ = order[0]
p("")
p(f">>> 终极爆品方案：【{champ['id']}】{champ['name']}（{champ['total']} 分）")
runner = order[1]
p(f"    次席：【{runner['id']}】{runner['name']}（{runner['total']} 分），差距 {champ['total']-runner['total']:.2f} 分")

with open(os.path.join(BASE, "review_result.json"), "w", encoding="utf-8") as f:
    json.dump({"experts": [{"name": n, "weight": w} for n, _, w in EXPERTS],
               "results": results, "champion": champ["id"]}, f, ensure_ascii=False, indent=1)
with open(os.path.join(BASE, "review_report.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(OUT))
print("\n>>> review_result.json / review_report.txt 已生成")
