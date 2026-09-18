# -*- coding: utf-8 -*-
"""
Step1 特征工程 + 探索性统计
输入 dataset.json，输出 features.json 与 explore_report.txt
"""
import json, re, os, sys, statistics as st
from collections import Counter, defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = []
def p(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    # Windows 控制台为 GBK，emoji 直接 print 会抛 UnicodeEncodeError，落盘仍用 UTF-8
    enc = sys.stdout.encoding or "utf-8"
    print(s.encode(enc, errors="replace").decode(enc, errors="replace"))

with open(os.path.join(BASE, "dataset.json"), "r", encoding="utf-8") as f:
    DS = json.load(f)
prods = DS["products"]

# ---------- 词典 ----------
BRAND_DICT = ["喜临门","慕思","顾家","金可儿","舒达","丝涟","席伊丽","穗宝","晚安","雅兰",
    "斯林百兰","邓禄普","栖作","蓝盒子","菠萝斑马","趣睡","8H","网易严选","京东京造","小米",
    "宜家","林氏","源氏木语","全友","芝华仕","梦百合","admiral","AiSleep睡眠博士","诺伊曼",
    "泰普尔","海丝腾","金橡树","大自然","博洋","富安娜","水星","罗莱","洁丽雅","恒源祥",
    "皖宝","联乐","吉斯","华日","强力","联邦","双虎","天坛","爱依瑞斯","红苹果","曲美",
    "月亮小屋","舒福德","雅兰仕","梦洁","维科","紫罗兰","多喜爱","好眠","觅眠","眠度",
    "睡眠博士","苏纳美","米檬","塔塔猫","眠白","素乐","舒达思","佳佰","京造","造作"]

MATERIAL = {
    "椰棕": ["椰棕","椰梦维","棕垫","山棕","黄麻椰棕"],
    "乳胶": ["乳胶","latex","泰国乳胶","天然乳胶"],
    "弹簧": ["弹簧","席梦思","独立袋","独立筒","spring","袋装弹簧"],
    "记忆棉": ["记忆棉","慢回弹","memory","太空棉"],
    "黄麻": ["黄麻"],
    "海绵": ["海绵","高密度棉","硬质棉"],
    "凝胶": ["凝胶","gel","石墨烯","相变"],
    "3D空气纤维": ["3d","空气纤维","4d"],
    "水凝": ["水凝","水感"],
    "羊毛/蚕丝": ["羊毛","蚕丝","驼绒"],
    # 裸 "ai" 会误命中英文/拼音（family、Plus 系列文案等），必须用限定词
    "AI智能": ["AI智能","ai智能","智能床","智能调节","电动床","电动升降","气囊","零压力","AI 陪"],
}
FEEL = {"偏硬":["偏硬","硬垫","硬感","护脊硬","加硬","硬支撑","硬床垫","偏硬睡感"],
        "偏软":["偏软","软垫","柔软","云感","软感","软床垫","软睡感"],
        "双面双睡感":["双面","双睡感","软硬两用","一垫两用","两面","AB面","ab面"],
        "适中":["适中","中等","软硬适中"]}
FUNC = {
    "可拆洗": ["可拆","拆洗","可洗","水洗","拉链"],
    "0胶/无胶": ["0胶","无胶","零胶","不含胶","0甲醛"],
    "抗菌防螨": ["防螨","抗菌","除螨","抑菌"],
    "分区支撑": ["分区","三区","五区","七区","九区","独立分区"],
    # 注意 "5cm" 会被 "25cm" 包含，薄垫只用语义词，厚薄一律走 thickness_max 数值判定
    "薄垫/褥垫": ["薄垫","褥子","床褥","榻榻米","折叠","卷装","打地铺","可折"],
    "厚垫": ["厚床垫","加厚","超厚"],
    "儿童青少年": ["儿童","青少年","学生","kids","宝宝","婴"],
    "定制尺寸": ["定制","任意尺寸","异形"],
    "透气": ["透气","3d网","散热","凉感"],
    "静音防干扰": ["静音","防干扰","不吵","独立不干扰"],
    "重压/大体重": ["大体重","加硬","承重","胖"],
    "酒店同款": ["酒店","五星","希尔顿","洲际"],
}

def ok(v):
    """价格有效：非 None 且非 NaN（原站两条商品为“页面展示价”缺失）"""
    return v is not None and isinstance(v, (int, float)) and v == v


def num(v):
    return v if ok(v) else None


def hit(text, kws):
    t = text.lower()
    return [k for k in kws if k.lower() in t]

def parse_thickness(text):
    """抽取厚度cm列表"""
    res = []
    for m in re.finditer(r"(\d{1,2}(?:\.\d)?)\s*(?:CM|cm|Cm|厘米)", text):
        v = float(m.group(1))
        if 2 <= v <= 45: res.append(v)
    return res

def is_bundle(name):
    return bool(re.search(r"套餐|\+|枕\*|床笠|送|组合|套购", name))

feat = []
for pr in prods:
    title = pr["title"]
    sku_names = " | ".join(s["name"] for s in pr["skus"])
    mi = pr  # dataset.json 中首图字段为平铺结构
    ocr = mi.get("ocr_raw") or ""
    allbag = f"{title} {sku_names} {ocr}"

    # 品牌
    brand = None
    for b in BRAND_DICT:
        if b.lower() in title.lower() or b.lower() in pr["shop"].lower():
            brand = b; break
    if brand is None:
        # 店铺名前缀兜底
        brand = re.sub(r"(官方)?(旗舰|专卖|专营|自营|企业)?店$", "", pr["shop"]).strip() or pr["shop"]

    mats = [k for k, kws in MATERIAL.items() if hit(allbag, kws)]
    feels = [k for k, kws in FEEL.items() if hit(allbag, kws)]
    funcs = [k for k, kws in FUNC.items() if hit(allbag, kws)]
    th = parse_thickness(allbag)

    disc = None
    pairs = [(s["price"], s["orig"]) for s in pr["skus"]
             if ok(s.get("price")) and ok(s.get("orig")) and s["orig"] > 0]
    if pairs:
        disc = round(st.median([a / b for a, b in pairs]) * 100, 1)

    bundle_n = sum(1 for s in pr["skus"] if is_bundle(s["name"]))
    mn, mx, md, mean = (num(pr[k]) for k in ("min_price", "max_price", "median_price", "mean_price"))

    feat.append({
        "rank": pr["rank"], "shop": pr["shop"], "brand": brand, "title": title,
        "min_price": mn, "max_price": mx,
        "median_price": md, "mean_price": mean,
        "price_valid": md is not None,
        "sku_count": pr["sku_count"],
        "price_span_ratio": round(mx / mn, 2) if (mn and mx) else None,
        "discount_pct": disc,
        "bundle_sku_n": bundle_n,
        "bundle_ratio": round(bundle_n / pr["sku_count"] * 100, 1) if pr["sku_count"] else 0,
        "materials": mats, "feels": feels, "funcs": funcs,
        "thickness_list": sorted(set(th)),
        "thickness_min": min(th) if th else None,
        "thickness_max": max(th) if th else None,
        "selling_points": mi.get("selling_points") or [],
        "marketing_text": mi.get("marketing_text") or [],
        "visual_format": mi.get("visual_format") or [],
        "main_image_price": (mi.get("price_analysis") or {}).get("main_image_price"),
        "attraction_ratio": (mi.get("price_analysis") or {}).get("attraction_ratio"),
        "attraction_level": (mi.get("price_analysis") or {}).get("attraction_level"),
        "has_ocr": bool(ocr),
    })

with open(os.path.join(BASE, "features.json"), "w", encoding="utf-8") as f:
    json.dump(feat, f, ensure_ascii=False, indent=1)

# ================= 探索性统计 =================
# rank 24 / 181 两款顾家商品页面未给出价格(NaN)，统计口径剔除，特征仍保留在 features.json
feat_all = feat
feat = [x for x in feat if x["median_price"] is not None]
p(f"[口径] 全量 {len(feat_all)} 款，有效价格 {len(feat)} 款"
  f"（剔除 rank={[x['rank'] for x in feat_all if x['median_price'] is None]} 无价格）")
p("")

def band(v):
    for lo, hi, lb in [(0,300,"A <300"),(300,800,"B 300-800"),(800,1500,"C 800-1500"),
                       (1500,2000,"D 1500-2000"),(2000,3000,"E 2000-3000"),
                       (3000,5000,"F 3000-5000"),(5000,10000,"G 5000-1w"),(10000,9e9,"H >1w")]:
        if lo <= v < hi: return lb
    return "?"
def tier(r):
    if r <= 10: return "T1 1-10"
    if r <= 30: return "T2 11-30"
    if r <= 50: return "T3 31-50"
    if r <= 100: return "T4 51-100"
    if r <= 200: return "T5 101-200"
    return "T6 201-300"

p("="*70); p("【1】价格带 × 排名梯队 交叉分布（按商品中位价归带，计商品数）"); p("="*70)
cross = defaultdict(Counter)
for f_ in feat: cross[band(f_["median_price"])][tier(f_["rank"])] += 1
tiers = ["T1 1-10","T2 11-30","T3 31-50","T4 51-100","T5 101-200","T6 201-300"]
p("价格带".ljust(14) + "".join(t.rjust(12) for t in tiers) + "   合计")
for b in ["A <300","B 300-800","C 800-1500","D 1500-2000","E 2000-3000","F 3000-5000","G 5000-1w","H >1w"]:
    row = cross[b]
    p(b.ljust(14) + "".join(str(row[t]).rjust(12) for t in tiers) + str(sum(row.values())).rjust(8))

p(""); p("="*70); p("【2】各价格带 头部命中率（Top50占比）与 平均排名"); p("="*70)
for b in ["A <300","B 300-800","C 800-1500","D 1500-2000","E 2000-3000","F 3000-5000","G 5000-1w","H >1w"]:
    g = [f_ for f_ in feat if band(f_["median_price"]) == b]
    if not g: continue
    top50 = sum(1 for x in g if x["rank"] <= 50)
    p(f"{b.ljust(14)} n={len(g):3d}  Top50={top50:2d} ({top50/len(g)*100:5.1f}%)  "
      f"排名中位={st.median([x['rank'] for x in g]):5.0f}  SKU中位={st.median([x['sku_count'] for x in g]):4.0f}  "
      f"折扣中位={st.median([x['discount_pct'] for x in g if x['discount_pct']] or [0]):5.1f}%")

p(""); p("="*70); p("【3】材质组合 出现频次 & 该材质商品的排名/价格表现"); p("="*70)
matc = Counter()
for f_ in feat:
    for m in f_["materials"]: matc[m] += 1
for m, c in matc.most_common():
    g = [f_ for f_ in feat if m in f_["materials"]]
    top50 = sum(1 for x in g if x["rank"] <= 50)
    p(f"{m.ljust(12)} n={c:3d} ({c/len(feat)*100:4.1f}%)  排名中位={st.median([x['rank'] for x in g]):5.0f}  "
      f"价格中位={st.median([x['median_price'] for x in g]):8.0f}  Top50率={top50/c*100:5.1f}%")

p(""); p("="*70); p("【4】功能标签 频次 & 表现（找低供给-高势能缺口）"); p("="*70)
fc = Counter()
for f_ in feat:
    for x in f_["funcs"]: fc[x] += 1
for k, c in fc.most_common():
    g = [f_ for f_ in feat if k in f_["funcs"]]
    top50 = sum(1 for x in g if x["rank"] <= 50)
    p(f"{k.ljust(12)} n={c:3d} ({c/len(feat)*100:4.1f}%)  排名中位={st.median([x['rank'] for x in g]):5.0f}  "
      f"价格中位={st.median([x['median_price'] for x in g]):8.0f}  Top50率={top50/c*100:5.1f}%")

p(""); p("="*70); p("【5】睡感标签"); p("="*70)
flc = Counter()
for f_ in feat:
    for x in f_["feels"]: flc[x] += 1
for k, c in flc.most_common():
    g = [f_ for f_ in feat if k in f_["feels"]]
    top50 = sum(1 for x in g if x["rank"] <= 50)
    p(f"{k.ljust(12)} n={c:3d}  排名中位={st.median([x['rank'] for x in g]):5.0f}  价格中位={st.median([x['median_price'] for x in g]):8.0f}  Top50率={top50/c*100:5.1f}%")

p(""); p("="*70); p("【6】首图营销钩子（marketing_text）频次 & 效果"); p("="*70)
mk = Counter()
for f_ in feat:
    for x in f_["marketing_text"]: mk[x] += 1
for k, c in mk.most_common(30):
    g = [f_ for f_ in feat if k in f_["marketing_text"]]
    top50 = sum(1 for x in g if x["rank"] <= 50)
    p(f"{k.ljust(18)} n={c:3d}  排名中位={st.median([x['rank'] for x in g]):5.0f}  价格中位={st.median([x['median_price'] for x in g]):8.0f}  Top50率={top50/c*100:5.1f}%")

p(""); p("="*70); p("【7】首图卖点（selling_points）频次 & 效果"); p("="*70)
sp = Counter()
for f_ in feat:
    for x in f_["selling_points"]: sp[x] += 1
for k, c in sp.most_common(30):
    g = [f_ for f_ in feat if k in f_["selling_points"]]
    top50 = sum(1 for x in g if x["rank"] <= 50)
    p(f"{k.ljust(20)} n={c:3d}  排名中位={st.median([x['rank'] for x in g]):5.0f}  价格中位={st.median([x['median_price'] for x in g]):8.0f}  Top50率={top50/c*100:5.1f}%")

p(""); p("="*70); p("【8】视觉形式 频次 & 效果"); p("="*70)
vf = Counter()
for f_ in feat:
    for x in f_["visual_format"]: vf[x] += 1
for k, c in vf.most_common():
    g = [f_ for f_ in feat if k in f_["visual_format"]]
    top50 = sum(1 for x in g if x["rank"] <= 50)
    p(f"{k.ljust(22)} n={c:3d}  排名中位={st.median([x['rank'] for x in g]):5.0f}  价格中位={st.median([x['median_price'] for x in g]):8.0f}  Top50率={top50/c*100:5.1f}%")

p(""); p("="*70); p("【9】SKU 策略：SKU数分档 vs 排名"); p("="*70)
for lo, hi, lb in [(1,3,"1-3"),(4,8,"4-8"),(9,15,"9-15"),(16,25,"16-25"),(26,999,"26+")]:
    g = [f_ for f_ in feat if lo <= f_["sku_count"] <= hi]
    if not g: continue
    top50 = sum(1 for x in g if x["rank"] <= 50)
    p(f"SKU {lb.ljust(6)} n={len(g):3d}  排名中位={st.median([x['rank'] for x in g]):5.0f}  Top50率={top50/len(g)*100:5.1f}%  "
      f"价格中位={st.median([x['median_price'] for x in g]):8.0f}  价宽比中位={st.median([x['price_span_ratio'] for x in g if x['price_span_ratio']]):5.2f}")

p(""); p("="*70); p("【10】价格宽度比(max/min) vs 排名"); p("="*70)
for lo, hi, lb in [(1,1.5,"1-1.5"),(1.5,2.5,"1.5-2.5"),(2.5,4,"2.5-4"),(4,99,"4+")]:
    g = [f_ for f_ in feat if f_["price_span_ratio"] and lo <= f_["price_span_ratio"] < hi]
    if not g: continue
    top50 = sum(1 for x in g if x["rank"] <= 50)
    p(f"跨度 {lb.ljust(8)} n={len(g):3d}  排名中位={st.median([x['rank'] for x in g]):5.0f}  Top50率={top50/len(g)*100:5.1f}%")

p(""); p("="*70); p("【11】引流定价度 attraction_level 分布 vs 排名"); p("="*70)
al = Counter(f_["attraction_level"] for f_ in feat if f_["attraction_level"])
for k, c in al.most_common():
    g = [f_ for f_ in feat if f_["attraction_level"] == k]
    p(f"{k[:34].ljust(36)} n={c:3d} 排名中位={st.median([x['rank'] for x in g]):5.0f} 价格中位={st.median([x['median_price'] for x in g]):8.0f}")

p(""); p("="*70); p("【12】店铺/品牌集中度 Top20"); p("="*70)
bc = Counter(f_["brand"] for f_ in feat)
for b, c in bc.most_common(20):
    g = [f_ for f_ in feat if f_["brand"] == b]
    p(f"{b.ljust(14)} 上榜={c:2d}  最好排名={min(x['rank'] for x in g):3d}  价格中位={st.median([x['median_price'] for x in g]):8.0f}")

p(""); p("="*70); p("【13】厚度分布 vs 表现"); p("="*70)
for lo, hi, lb in [(0,8,"<8cm 薄褥垫"),(8,15,"8-15cm"),(15,20,"15-20cm"),(20,24,"20-24cm"),(24,28,"24-28cm"),(28,99,"28cm+")]:
    g = [f_ for f_ in feat if f_["thickness_max"] and lo <= f_["thickness_max"] < hi]
    if not g: continue
    top50 = sum(1 for x in g if x["rank"] <= 50)
    p(f"{lb.ljust(14)} n={len(g):3d}  排名中位={st.median([x['rank'] for x in g]):5.0f}  价格中位={st.median([x['median_price'] for x in g]):8.0f}  Top50率={top50/len(g)*100:5.1f}%")

p(""); p("="*70); p("【14】Top30 商品逐条画像"); p("="*70)
for f_ in sorted(feat, key=lambda x: x["rank"])[:30]:
    p(f"#{f_['rank']:3d} {f_['brand'][:8].ljust(9)} 中位¥{f_['median_price']:7.0f} "
      f"[{f_['min_price']:.0f}-{f_['max_price']:.0f}] SKU={f_['sku_count']:2d} "
      f"套餐{f_['bundle_ratio']:4.0f}% 材={'/'.join(f_['materials'][:4])} 感={'/'.join(f_['feels'][:2])} "
      f"功={'/'.join(f_['funcs'][:4])}")

with open(os.path.join(BASE, "explore_report.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(OUT))
print("\n>>> features.json / explore_report.txt 已生成")
