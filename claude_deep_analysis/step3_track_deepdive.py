# -*- coding: utf-8 -*-
"""
Step3 最佳赛道(T1)内部深挖：找卖点缺口 / 价格断层 / SKU命名套路 / 视觉与钩子空白
输入 features.json + track_result.json，输出 deepdive_report.txt
"""
import json, os, re, sys, statistics as st
from collections import Counter

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = []


def p(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    enc = sys.stdout.encoding or "utf-8"
    print(s.encode(enc, errors="replace").decode(enc, errors="replace"))


FEAT = json.load(open(os.path.join(BASE, "features.json"), encoding="utf-8"))
TR = json.load(open(os.path.join(BASE, "track_result.json"), encoding="utf-8"))
DS = json.load(open(os.path.join(BASE, "dataset.json"), encoding="utf-8"))

best = [t for t in TR["tracks"] if t["id"] == TR["best"]][0]
ranks = {m["rank"] for m in best["members"]}
G = [x for x in FEAT if x["rank"] in ranks]
POOL = [x for x in FEAT if x["median_price"] is not None]
SKUMAP = {d["rank"]: d["skus"] for d in DS["products"]}

p("=" * 78)
p(f"最佳赛道深挖：【{best['id']}】{best['name']}")
p("=" * 78)
p(f"赛道内 {len(G)} 款｜排名中位 {best['rank_median']:.0f}｜价格中位 ¥{best['price_median']:.0f}")
p("")

# ---------- 1. 赛道内 头部(Top50) vs 尾部(100+) 的差异 ----------
head = [x for x in G if x["rank"] <= 50]
tail = [x for x in G if x["rank"] > 100]
p("=" * 78)
p("【1】赛道内头尾对比：赢家做对了什么")
p("=" * 78)


def prof(name, g):
    if not g:
        return
    p(f"\n-- {name}（{len(g)} 款）")
    p(f"   价格中位 ¥{st.median([x['median_price'] for x in g]):.0f}｜"
      f"SKU 中位 {st.median([x['sku_count'] for x in g]):.0f}｜"
      f"价宽比中位 {st.median([x['price_span_ratio'] for x in g if x['price_span_ratio']] or [0]):.2f}｜"
      f"套餐SKU占比中位 {st.median([x['bundle_ratio'] for x in g]):.0f}%")
    for key, label in [("materials", "材质"), ("funcs", "功能"), ("feels", "睡感"),
                       ("selling_points", "首图卖点"), ("marketing_text", "营销钩子"),
                       ("visual_format", "视觉形式")]:
        c = Counter()
        for x in g:
            for v in x[key]:
                c[v] += 1
        items = "、".join(f"{k}{v}/{len(g)}" for k, v in c.most_common(6))
        p(f"   {label}：{items or '（无）'}")


prof("头部 Top50", head)
prof("尾部 100名后", tail)

# ---------- 2. 卖点缺口：全站高效但赛道内低渗透 ----------
p("")
p("=" * 78)
p("【2】卖点/钩子缺口：全站高势能，但本赛道渗透不足 → 可差异化抢占")
p("=" * 78)
for key, label in [("selling_points", "首图卖点"), ("marketing_text", "营销钩子"),
                   ("visual_format", "视觉形式"), ("funcs", "功能标签")]:
    p(f"\n-- {label}")
    allc = Counter()
    for x in POOL:
        for v in x[key]:
            allc[v] += 1
    gc = Counter()
    for x in G:
        for v in x[key]:
            gc[v] += 1
    rows = []
    for k, c in allc.items():
        if c < 8:
            continue
        sub = [x for x in POOL if k in x[key]]
        eff = sum(1 for x in sub if x["rank"] <= 50) / len(sub) * 100
        pen = gc[k] / len(G) * 100
        rows.append((k, c, eff, pen, eff - pen))
    for k, c, eff, pen, gap in sorted(rows, key=lambda z: -z[4]):
        flag = "  <== 缺口" if eff >= 18 and pen <= 30 else ""
        p(f"   {k.ljust(16)} 全站{c:3d}款 Top50率{eff:5.1f}%｜本赛道渗透{pen:5.1f}%{flag}")

# ---------- 3. 价格断层：赛道内 1400-2400 的价格点分布 ----------
p("")
p("=" * 78)
p("【3】价格断层扫描：赛道内所有 SKU 落点（每 100 元一格）")
p("=" * 78)
buckets = Counter()
for x in G:
    for s in SKUMAP.get(x["rank"], []):
        v = s.get("price")
        if isinstance(v, (int, float)) and v == v and 800 <= v <= 3200:
            buckets[int(v // 100) * 100] += 1
for b in range(800, 3200, 100):
    n = buckets.get(b, 0)
    bar = "█" * n
    mark = "  <== 空档" if n <= 2 else ""
    p(f"   ¥{b:5d}-{b+99:<5d} {n:3d} {bar}{mark}")

# ---------- 4. SKU 命名套路 ----------
p("")
p("=" * 78)
p("【4】赛道内 SKU 命名套路拆解（头部款优先）")
p("=" * 78)
for x in sorted(G, key=lambda z: z["rank"])[:8]:
    p(f"\n-- #{x['rank']} {x['brand']}  ¥{x['median_price']:.0f}  SKU={x['sku_count']}")
    p(f"   标题：{x['title'][:60]}")
    for s in SKUMAP.get(x["rank"], [])[:6]:
        pr = s.get("price")
        pr = f"¥{pr:.0f}" if isinstance(pr, (int, float)) and pr == pr else "—"
        p(f"     {pr.ljust(8)} {s['name'][:52]}")

# 命名结构件频次
p("")
p("-- SKU 名称高频结构件（赛道内全量）")
pat = Counter()
for x in G:
    for s in SKUMAP.get(x["rank"], []):
        for seg in re.findall(r"[【（(]([^】）)]{2,12})[】）)]", s["name"]):
            pat[seg] += 1
for k, c in pat.most_common(25):
    p(f"   {k.ljust(18)} {c}")

# ---------- 5. 主图标价行为 ----------
p("")
p("=" * 78)
p("【5】主图标价与引流度（赛道内）")
p("=" * 78)
priced = [x for x in G if x["main_image_price"]]
p(f"   赛道内明示主图标价 {len(priced)}/{len(G)} 款")
for x in sorted(priced, key=lambda z: z["rank"]):
    p(f"   #{x['rank']:3d} {x['brand'][:10].ljust(11)} 主图¥{x['main_image_price']:.0f}｜"
      f"SKU区间 ¥{x['min_price']:.0f}-{x['max_price']:.0f}｜{x['attraction_level'] or ''}")
allp = [x for x in POOL if x["main_image_price"]]
p(f"\n   全站明示标价 {len(allp)} 款，其 Top50 率 "
  f"{sum(1 for x in allp if x['rank']<=50)/len(allp)*100:.1f}%，"
  f"未标价款 Top50 率 "
  f"{sum(1 for x in POOL if not x['main_image_price'] and x['rank']<=50)/len([x for x in POOL if not x['main_image_price']])*100:.1f}%")

# ---------- 6. 厚度与睡感组合空白 ----------
p("")
p("=" * 78)
p("【6】厚度 × 睡感 组合覆盖（赛道内，找空白格）")
p("=" * 78)
feels = ["偏硬", "适中", "偏软", "双面双睡感"]
rows = {}
for x in G:
    t = x["thickness_max"]
    tb = "未标" if t is None else ("<20cm" if t < 20 else "20-24cm" if t < 24 else "24-28cm" if t < 28 else "28cm+")
    for f_ in (x["feels"] or ["未标"]):
        rows.setdefault(tb, Counter())[f_] += 1
p("   厚度段".ljust(12) + "".join(f.rjust(12) for f in feels))
for tb in ["<20cm", "20-24cm", "24-28cm", "28cm+", "未标"]:
    c = rows.get(tb, Counter())
    p(f"   {tb.ljust(10)}" + "".join(str(c.get(f_, 0)).rjust(12) for f_ in feels))

with open(os.path.join(BASE, "deepdive_report.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(OUT))
print("\n>>> deepdive_report.txt 已生成")
