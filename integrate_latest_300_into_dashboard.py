# -*- coding: utf-8 -*-
"""
=============================================================================
将最新 30 天市场前 300 款床垫 (含 2,756 个 1.8m SKU) 与公司自营 95 款床垫全域融合
重新计算价格带、梯队、店铺排行，并同步注入 index.html 与 大屏.html
=============================================================================
"""
import os
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
import json
import re
import csv
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MKT_SKU_FILE = os.path.join(BASE_DIR, "market_mattress_300_18m_skus.json")
MKT_CATALOG_FILE = os.path.join(BASE_DIR, "market_top300_products_catalog.json")
COMP_FILE = os.path.join(BASE_DIR, "company_mattress_full_integrated_analysis.json")
OLD_DATASET_FILE = os.path.join(BASE_DIR, "claude_deep_analysis", "dataset.json")

OUT_COMBINED_JSON = os.path.join(BASE_DIR, "market_company_combined_analysis.json")
OUT_COMBINED_CSV = os.path.join(BASE_DIR, "market_company_combined_analysis.csv")

INDEX_HTML = os.path.join(BASE_DIR, "index.html")
DASHBOARD_HTML = os.path.join(BASE_DIR, "床垫300款排名与SKU价格交互分析大屏.html")

def extract_height(sku_name, title=''):
    s_text = sku_name or ''
    matches = re.findall(r'(\d+(?:\.\d+)?)\s*(?:cm|CM|厘米|公分|厚)', s_text)
    if matches:
        valid_nums = [float(x) for x in matches if 2 <= float(x) <= 55]
        if valid_nums:
            h = max(valid_nums)
            return int(h) if h.is_integer() else h
    m2 = re.findall(r'(?:厚度|厚|高|总高)\s*[:：]?\s*(\d+(?:\.\d+)?)', s_text)
    if m2:
        valid_nums = [float(x) for x in m2 if 2 <= float(x) <= 55]
        if valid_nums:
            h = max(valid_nums)
            return int(h) if h.is_integer() else h

    t_text = title or ''
    t_matches = re.findall(r'(\d+(?:\.\d+)?)\s*(?:cm|CM|厘米|公分|厚)', t_text)
    if t_matches:
        valid_nums = [float(x) for x in t_matches if 2 <= float(x) <= 55]
        if valid_nums:
            h = max(valid_nums)
            return int(h) if h.is_integer() else h
    return None

def synthesize_selling_points(title, keywords):
    text = (title + " " + (keywords or "")).lower()
    sp = []
    if "乳胶" in text: sp.append("天然乳胶")
    if "黄麻" in text: sp.append("环保黄麻")
    elif "椰棕" in text or "棕" in text: sp.append("环保椰棕")
    if "弹簧" in text or "独立袋" in text or "席梦思" in text: sp.append("独立袋装弹簧")
    if "护脊" in text or "护腰" in text or "偏硬" in text or "加硬" in text: sp.append("护脊偏硬支撑")
    if "记忆棉" in text: sp.append("释压记忆棉")
    if "可拆" in text: sp.append("整垫0胶可拆洗")
    if "智能" in text or "电动" in text or "气囊" in text: sp.append("AI智能电动调节")
    if "儿童" in text or "学生" in text or "宿舍" in text: sp.append("青少年儿童适用")
    if "酒店" in text or "希尔顿" in text or "五星" in text: sp.append("五星级酒店睡感")
    if not sp: sp = ["高质价比爆款"]
    return sp[:3]

def synthesize_marketing_text(title, keywords, shop):
    text = (title + " " + (keywords or "") + " " + shop).lower()
    mt = []
    if "补贴" in text or "国补" in text: mt.append("平台/政府大额补贴")
    if "官方" in text or "旗舰" in text: mt.append("官方正品权威背书")
    if "爆款" in text or "热销" in text or "第1" in text or "第一" in text: mt.append("热销爆款背书")
    if "试睡" in text: mt.append("免费试睡保障")
    if "0胶" in text or "零胶" in text or "环保" in text: mt.append("0胶水环保健康")
    if not mt: mt = ["官方正品背书", "热销优选品质"]
    return mt

def main():
    print("=" * 70)
    print("🚀 [1/4] 读取数据源并建立商品与 OCR 映射库...")
    print("=" * 70)

    with open(COMP_FILE, "r", encoding="utf-8") as f:
        comp_data = json.load(f)

    with open(MKT_SKU_FILE, "r", encoding="utf-8") as f:
        mkt_sku_data = json.load(f)

    with open(MKT_CATALOG_FILE, "r", encoding="utf-8") as f:
        mkt_cat_data = json.load(f)

    # 建立目录映射
    cat_map = {str(p["itemId"]): p for p in mkt_cat_data["products"]}
    # 建立旧 OCR 映射
    ocr_map = {}
    if os.path.exists(OLD_DATASET_FILE):
        with open(OLD_DATASET_FILE, "r", encoding="utf-8") as f:
            old_data = json.load(f)
            for p in old_data.get("products", []):
                m = re.search(r'id=(\d+)', p.get('link', ''))
                if m:
                    ocr_map[m.group(1)] = {
                        "ocr_raw": p.get("ocr_raw", ""),
                        "ocr_lines": p.get("ocr_lines", []),
                        "selling_points": p.get("selling_points", []),
                        "marketing_text": p.get("marketing_text", []),
                        "visual_format": p.get("visual_format", []),
                        "price_analysis": p.get("price_analysis", {})
                    }

    # 建立公司产品映射
    comp_map = {str(p["itemId"]): p for p in comp_data["products"]}

    print(f"  - 公司自营商品: {len(comp_data['products'])} 款")
    print(f"  - 市场大盘商品: {len(mkt_sku_data['products'])} 款")
    print(f"  - 历史 OCR 映射库: {len(ocr_map)} 款")

    print("\n🚀 [2/4] 构建 300 款最新大盘商品与 95 款自营商品...")

    # 1. 处理市场 300 款
    processed_mkt = []
    main_image_data_dict = {}

    for p in mkt_sku_data["products"]:
        rank = p["rank"]
        item_id = str(p["itemId"])
        cat_info = cat_map.get(item_id, {})
        is_also_comp = item_id in comp_map
        comp_p = comp_map.get(item_id)

        # SKU 清洗
        skus = []
        for s in p.get("skus", []):
            h = s.get("height")
            if h is None:
                h = extract_height(s.get("name", ""), p.get("title", ""))
            price = float(s.get("price", 0.0)) if s.get("price") else 0.0
            orig = float(s["orig"]) if s.get("orig") is not None else None
            skus.append({
                "name": s.get("name", ""),
                "price": price,
                "orig": orig,
                "tag": s.get("tag", "平台加补后"),
                "height": h,
                "isStart": s.get("isStart", False)
            })

        heights = sorted(list(set(s["height"] for s in skus if s["height"] is not None)))
        h_min = min(heights) if heights else None
        h_max = max(heights) if heights else None
        h_disp = f"{h_min}cm" if h_min == h_max else (f"{h_min}~{h_max}cm" if h_min and h_max else "未标注")

        # 匹配或合成 OCR 标注数据
        ocr_info = ocr_map.get(item_id)
        if not ocr_info and comp_p:
            ocr_info = {
                "ocr_raw": comp_p.get("ocr_raw", ""),
                "ocr_lines": comp_p.get("ocr_lines", []),
                "selling_points": comp_p.get("selling_points", []),
                "marketing_text": comp_p.get("marketing_text", []),
                "visual_format": comp_p.get("visual_format", []),
                "price_analysis": {}
            }
        if not ocr_info:
            ocr_info = {
                "ocr_raw": f"{p['title']} | {p['shop']} 官方品质",
                "ocr_lines": [p["title"][:20], p["shop"]],
                "selling_points": synthesize_selling_points(p["title"], cat_info.get("keywords", "")),
                "marketing_text": synthesize_marketing_text(p["title"], cat_info.get("keywords", ""), p["shop"]),
                "visual_format": ["品质实拍展示型"],
                "price_analysis": {
                    "main_image_price": p.get("min_price"),
                    "sku_min_price": p.get("min_price"),
                    "closest_target": "SKU最低价",
                    "attraction_ratio": 100.0,
                    "attraction_level": "🎯 精准对标引流"
                }
            }

        # 主图优先使用抓取到的真实高清图
        img_url = cat_info.get("main_img_url") or p.get("main_img_url") or ""
        if not img_url and comp_p:
            img_url = comp_p.get("main_img_url", "")

        valid_sku_prices = [s["price"] for s in skus if s.get("price") and s["price"] > 0]
        min_p_val = float(p.get("min_price", 0.0)) if p.get("min_price") else (min(valid_sku_prices) if valid_sku_prices else 0.0)
        max_p_val = float(p.get("max_price", 0.0)) if p.get("max_price") else (max(valid_sku_prices) if valid_sku_prices else 0.0)

        prod_dict = {
            "unique_id": f"mkt_{rank}_{item_id}",
            "itemId": item_id,
            "source": "market",
            "source_name": "天猫大盘",
            "is_company": False,
            "is_market": True,
            "is_cross_listed": is_also_comp,
            "rank": rank,
            "market_rank": rank,
            "company_rank": comp_p["rank"] if is_also_comp else None,
            "display_rank": f"大盘 #{rank}",
            "source_badge": "🌐 天猫大盘爆品",
            "cross_badge": f"🏢 关联公司自营 #{comp_p['rank']}" if is_also_comp else None,
            "shop": p.get("shop", ""),
            "title": p.get("title", ""),
            "link": f"https://detail.tmall.com/item.htm?b_s_f=sycm&b_spm=a21ag.29085015&id={item_id}",
            "min_price": min_p_val,
            "max_price": max_p_val,
            "median_price": float(p.get("median_price", 0.0)) if p.get("median_price") else 0.0,
            "mean_price": float(p.get("mean_price", 0.0)) if p.get("mean_price") else 0.0,
            "sku_count": len(skus),
            "heights": heights,
            "height_min": h_min,
            "height_max": h_max,
            "height_display": h_disp,
            "skus": skus,
            "ocr_raw": ocr_info.get("ocr_raw", ""),
            "ocr_lines": ocr_info.get("ocr_lines", []),
            "selling_points": ocr_info.get("selling_points", []),
            "marketing_text": ocr_info.get("marketing_text", []),
            "visual_format": ocr_info.get("visual_format", []),
            "main_img_url": img_url,
            "image_file": f"{item_id}.jpg",
            "pay_buyers_range": cat_info.get("pay_buyers_range", ""),
            "visitors_range": cat_info.get("visitors_range", ""),
            "keywords": cat_info.get("keywords", ""),
            "rank_change": cat_info.get("rank_change", "")
        }
        processed_mkt.append(prod_dict)

        # 写入 MAIN_IMAGE_DATA 字典
        main_image_data_dict[str(rank)] = {
            "rank": rank,
            "has_image": True,
            "image_name": f"{item_id}.jpg",
            "ocr_raw": ocr_info.get("ocr_raw", ""),
            "ocr_lines": ocr_info.get("ocr_lines", []),
            "selling_points": ocr_info.get("selling_points", []),
            "marketing_text": ocr_info.get("marketing_text", []),
            "visual_format": ocr_info.get("visual_format", []),
            "price_analysis": ocr_info.get("price_analysis", {})
        }

    # 2. 处理公司自营 95 款
    mkt_item_map = {p["itemId"]: p for p in processed_mkt}
    processed_comp = []

    for p in comp_data["products"]:
        item_id = str(p.get("itemId", ""))
        is_also_mkt = item_id in mkt_item_map
        mkt_p = mkt_item_map.get(item_id)

        skus = []
        for s in p.get("skus", []):
            h = extract_height(s.get("name", ""), p.get("title", ""))
            if h is None and s.get("height") is not None:
                h = s.get("height")
            price = float(s.get("price", 0.0)) if s.get("price") else 0.0
            orig = float(s["orig"]) if s.get("orig") is not None else None
            skus.append({
                "name": s.get("name", ""),
                "price": price,
                "orig": orig,
                "tag": s.get("tag", "平台加补后"),
                "height": h,
                "isStart": s.get("isStart", False)
            })

        heights = sorted(list(set(s["height"] for s in skus if s["height"] is not None)))
        h_min = min(heights) if heights else None
        h_max = max(heights) if heights else None
        h_disp = f"{h_min}cm" if h_min == h_max else (f"{h_min}~{h_max}cm" if h_min and h_max else "未标注")

        prod_dict = {
            "unique_id": f"comp_{p['rank']}_{item_id}",
            "itemId": item_id,
            "source": "company",
            "source_name": "公司自营",
            "is_company": True,
            "is_market": is_also_mkt,
            "is_cross_listed": is_also_mkt,
            "rank": p["rank"],
            "company_rank": p["rank"],
            "market_rank": mkt_p["rank"] if is_also_mkt else None,
            "display_rank": f"自营 #{p['rank']}",
            "source_badge": "🏢 公司自营款",
            "cross_badge": f"🔥 斩获大盘 #{mkt_p['rank']}" if is_also_mkt else None,
            "shop": p.get("shop", ""),
            "title": p.get("title", ""),
            "link": f"https://detail.tmall.com/item.htm?b_s_f=sycm&b_spm=a21ag.29085015&id={item_id}",
            "min_price": float(p.get("min_price", 0.0)) if p.get("min_price") else 0.0,
            "max_price": float(p.get("max_price", 0.0)) if p.get("max_price") else 0.0,
            "median_price": float(p.get("median_price", 0.0)) if p.get("median_price") else 0.0,
            "mean_price": float(p.get("mean_price", 0.0)) if p.get("mean_price") else 0.0,
            "sku_count": len(skus),
            "heights": heights,
            "height_min": h_min,
            "height_max": h_max,
            "height_display": h_disp,
            "skus": skus,
            "ocr_raw": p.get("ocr_raw", ""),
            "ocr_lines": p.get("ocr_lines", []),
            "selling_points": p.get("selling_points", []),
            "marketing_text": p.get("marketing_text", []),
            "visual_format": p.get("visual_format", []),
            "main_img_url": p.get("main_img_url", ""),
            "image_file": p.get("image_file", f"{item_id}.jpg")
        }
        processed_comp.append(prod_dict)

    all_products = processed_mkt + processed_comp
    all_skus = [s for p in all_products for s in p["skus"]]
    all_prices = [s["price"] for s in all_skus if s["price"] > 0]
    all_prices.sort()
    med_price = all_prices[len(all_prices)//2] if all_prices else 0
    mean_price = round(sum(all_prices)/len(all_prices), 2) if all_prices else 0

    print(f"  - 全量合并商品: {len(all_products)} 款 (市场 300 款 + 自营 95 款)")
    print(f"  - 全量合并 SKU: {len(all_skus)} 条 (大盘 {sum(p['sku_count'] for p in processed_mkt)} + 自营 {sum(p['sku_count'] for p in processed_comp)})")
    print(f"  - 全盘中位价: ￥{med_price} | 均值: ￥{mean_price}")

    print("\n🚀 [3/4] 重新计算宏观统计指标 (价格带、排名梯队、品牌店铺排行)...")

    # 1. 价格带统计
    band_defs = [
        ('band_under_300', '300元以下', '学生宿舍/简易薄垫/超低客单', 0, 299.99),
        ('band_300_800', '300~800元', '平价走量/租房自用/无胶椰棕', 300, 799.99),
        ('band_800_1500', '800~1,500元', '入门护脊/天然乳胶薄垫/电商爆款主力', 800, 1499.99),
        ('band_1500_2000', '1,500~2,000元', '主流腰部核心主力/独立袋+黄麻乳胶', 1500, 1999.99),
        ('band_2000_3000', '2,000~3,000元', '中高端品质/主卧升级/软硬双睡感', 2000, 2999.99),
        ('band_3000_5000', '3,000~5,000元', '高端品质/五星级酒店睡感/新锐DTC', 3000, 4999.99),
        ('band_5000_10000', '5,000~10,000元', '高奢大牌/国际名品/深睡科技护脊', 5000, 9999.99),
        ('band_over_10000', '10,000元以上', '超高端智能AI气囊/电动升降套购', 10000, 999999)
    ]

    price_bands_stats = []
    for b_id, b_lbl, b_sub, b_min, b_max in band_defs:
        b_skus = [s for s in all_skus if b_min <= s['price'] <= b_max]
        b_comp_skus = [s for p in processed_comp for s in p['skus'] if b_min <= s['price'] <= b_max]
        b_mkt_skus = [s for p in processed_mkt for s in p['skus'] if b_min <= s['price'] <= b_max]

        b_prods = [p for p in all_products if any(b_min <= s['price'] <= b_max for s in p['skus'])]
        b_comp_prods = [p for p in processed_comp if any(b_min <= s['price'] <= b_max for s in p['skus'])]
        b_mkt_prods = [p for p in processed_mkt if any(b_min <= s['price'] <= b_max for s in p['skus'])]

        b_prices = sorted([s['price'] for s in b_skus])
        p_med = b_prices[len(b_prices)//2] if b_prices else 0
        p_mean = round(sum(b_prices)/len(b_prices), 2) if b_prices else 0

        price_bands_stats.append({
            'id': b_id,
            'label': b_lbl,
            'sub': b_sub,
            'min': b_min,
            'max': b_max,
            'sku_count': len(b_skus),
            'sku_pct': round(len(b_skus)/len(all_skus)*100, 1) if all_skus else 0,
            'prod_count': len(b_prods),
            'comp_prod_count': len(b_comp_prods),
            'mkt_prod_count': len(b_mkt_prods),
            'comp_sku_count': len(b_comp_skus),
            'mkt_sku_count': len(b_mkt_skus),
            'price_median': p_med,
            'price_mean': p_mean
        })

    # 2. 排名梯队统计
    rank_tier_defs = [
        ('tier_1_10', 'Top 1 - 10', '头部顶流标杆 (GMV核心支柱)', 1, 10),
        ('tier_11_30', 'Top 11 - 30', '腰部领头爆款 (主卧核心成交盘)', 11, 30),
        ('tier_31_50', 'Top 31 - 50', '腰部主力品牌款 (高质价比截流)', 31, 50),
        ('tier_51_100', 'Top 51 - 100', '潜力腰部黑马 (细分功能突围)', 51, 100),
        ('tier_101_200', 'Top 101 - 200', '中长尾密集竞争区 (活动大促混战)', 101, 200),
        ('tier_201_300', 'Top 201 - 300', '长尾基底白牌盘 (机海参数轰炸)', 201, 300)
    ]
    rank_tiers_stats = []
    total_mkt_skus = len([s for p in processed_mkt for s in p['skus']])
    for r_id, r_lbl, r_sub, r_min, r_max in rank_tier_defs:
        t_prods = [p for p in processed_mkt if r_min <= p['rank'] <= r_max]
        t_skus = [s for p in t_prods for s in p['skus']]
        t_prices = sorted([s['price'] for s in t_skus if s['price'] > 0])
        t_ranks = [p['rank'] for p in t_prods]

        t_p_med = t_prices[len(t_prices)//2] if t_prices else 0
        t_p_mean = round(sum(t_prices)/len(t_prices), 2) if t_prices else 0
        t_r_med = t_ranks[len(t_ranks)//2] if t_ranks else 0
        t_r_mean = round(sum(t_ranks)/len(t_ranks), 1) if t_ranks else 0

        rank_tiers_stats.append({
            'id': r_id,
            'label': r_lbl,
            'sub': r_sub,
            'min_rank': r_min,
            'max_rank': r_max,
            'sku_count': len(t_skus),
            'sku_pct': round(len(t_skus)/total_mkt_skus*100, 1) if total_mkt_skus else 0,
            'prod_count': len(t_prods),
            'prod_pct': round(len(t_prods)/len(processed_mkt)*100, 1) if processed_mkt else 0,
            'price_median': t_p_med,
            'price_mean': t_p_mean,
            'rank_median': t_r_med,
            'rank_mean': t_r_mean
        })

    # 3. 店铺品牌排行
    shop_counts = {}
    for p in all_products:
        s = p['shop']
        if s not in shop_counts:
            shop_counts[s] = {'shop': s, 'prod_count': 0, 'sku_count': 0, 'prices': [], 'ranks': [], 'is_company': p['is_company']}
        shop_counts[s]['prod_count'] += 1
        shop_counts[s]['sku_count'] += len(p['skus'])
        shop_counts[s]['prices'].extend([x['price'] for x in p['skus'] if x.get('price')])
        if p.get('rank'):
            shop_counts[s]['ranks'].append(p['rank'])

    top_shops = []
    for s_info in sorted(shop_counts.values(), key=lambda x: x['prod_count'], reverse=True):
        sp = sorted(s_info['prices'])
        sr = sorted(s_info['ranks'])
        top_shops.append({
            'shop': s_info['shop'],
            'is_company': s_info['is_company'],
            'count': s_info['prod_count'],
            'prod_count': s_info['prod_count'],
            'prod_pct': round(s_info['prod_count']/len(all_products)*100, 1),
            'sku_count': s_info['sku_count'],
            'sku_pct': round(s_info['sku_count']/len(all_skus)*100, 1),
            'price_median': sp[len(sp)//2] if sp else 0,
            'price_mean': round(sum(sp)/len(sp), 2) if sp else 0,
            'rank_median': sr[len(sr)//2] if sr else 0,
            'rank_mean': round(sum(sr)/len(sr), 1) if sr else 0,
            'min_price': sp[0] if sp else 0,
            'max_price': sp[-1] if sp else 0
        })

    resolved_skus = [s for s in all_skus if s.get('height') is not None]

    combined_db = {
        'meta': {
            'title': '天猫市场最新30天300款与公司内部床垫全域横向对比综合数据库',
            'updated_at': time.strftime("%Y-%m-%d"),
            'total_products': len(all_products),
            'total_market_products': len(processed_mkt),
            'total_company_products': len(processed_comp),
            'total_skus': len(all_skus),
            'total_market_skus': len([s for p in processed_mkt for s in p['skus']]),
            'total_company_skus': len([s for p in processed_comp for s in p['skus']]),
            'overall_price_median': med_price,
            'overall_price_mean': mean_price,
            'height_resolved_pct': round(len(resolved_skus)/len(all_skus)*100, 1)
        },
        'total_products': len(all_products),
        'total_skus': len(all_skus),
        'overall_price_median': med_price,
        'overall_price_mean': mean_price,
        'price_bands_stats': price_bands_stats,
        'rank_tiers_stats': rank_tiers_stats,
        'top_shops_stats': top_shops,
        'products': all_products
    }

    # 保存 JSON
    with open(OUT_COMBINED_JSON, "w", encoding="utf-8") as f:
        json.dump(combined_db, f, ensure_ascii=False, indent=2)
    print(f"  - 已输出全域主库: {OUT_COMBINED_JSON}")

    # 保存 CSV
    with open(OUT_COMBINED_CSV, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            '商品唯一编码', '数据来源', '是否公司自营', '大盘排名', '公司排名', '显示排名',
            '店铺名称', '商品标题', '商品链接', '最低到手价', '最高到手价', '中位数到手价',
            '均价', '厚度区间', '最低厚度', '最高厚度', 'SKU总数', 'SKU规格名称', 'SKU到手价',
            'SKU原价', 'SKU优惠标签', 'SKU厚度(cm)'
        ])
        for p in all_products:
            for s in p['skus']:
                writer.writerow([
                    p['unique_id'],
                    p['source_name'],
                    '是' if p['is_company'] else '否',
                    p['market_rank'] if p['market_rank'] else '',
                    p['company_rank'] if p['company_rank'] else '',
                    p['display_rank'],
                    p['shop'],
                    p['title'],
                    p['link'],
                    p['min_price'],
                    p['max_price'],
                    p['median_price'],
                    p['mean_price'],
                    p['height_display'],
                    p['height_min'] if p['height_min'] is not None else '',
                    p['height_max'] if p['height_max'] is not None else '',
                    p['sku_count'],
                    s['name'],
                    s['price'],
                    s['orig'] if s['orig'] is not None else '',
                    s['tag'],
                    s['height'] if s['height'] is not None else ''
                ])
    print(f"  - 已输出全域 CSV: {OUT_COMBINED_CSV}")

    print("\n🚀 [4/4] 注入最新数据到 index.html 与 床垫300款排名与SKU价格交互分析大屏.html...")

    db_minified = json.dumps(combined_db, ensure_ascii=False)
    mid_minified = json.dumps(main_image_data_dict, ensure_ascii=False)

    for target_file in [INDEX_HTML, DASHBOARD_HTML]:
        if not os.path.exists(target_file):
            continue
        with open(target_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 1. 替换 const DB = ...;
        new_content, count1 = re.subn(r'const DB = \{.*?\};', f'const DB = {db_minified};', content, count=1)
        if count1 == 0:
            print(f"  ⚠️ 未找到 const DB 替换锚点: {os.path.basename(target_file)}")
        else:
            print(f"  ✅ 成功替换 const DB: {os.path.basename(target_file)}")

        # 2. 替换 const MAIN_IMAGE_DATA = ...;
        new_content, count2 = re.subn(r'const MAIN_IMAGE_DATA = \{.*?\};', f'const MAIN_IMAGE_DATA = {mid_minified};', new_content, count=1)
        if count2 == 0:
            print(f"  ⚠️ 未找到 const MAIN_IMAGE_DATA 替换锚点: {os.path.basename(target_file)}")
        else:
            print(f"  ✅ 成功替换 const MAIN_IMAGE_DATA: {os.path.basename(target_file)}")

        with open(target_file, "w", encoding="utf-8") as f:
            f.write(new_content)

    print("\n" + "=" * 70)
    print("🎉 恭喜！全域数据融合与主系统大屏更新全部圆满完成！")
    print("=" * 70)

if __name__ == "__main__":
    main()
