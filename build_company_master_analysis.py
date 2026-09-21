# -*- coding: utf-8 -*-
"""
=============================================================================
构建公司 95 款床垫全量 1.8m SKU 与主图分析交互大屏及综合数据表
=============================================================================
"""
import os
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
import json
import csv
import re

BASE_DIR = os.path.abspath(".")
SKU_JSON = os.path.join(BASE_DIR, "company_mattress_18m_skus_all.json")
OCR_JSON = os.path.join(BASE_DIR, "company_active_mattresses_images_analysis.json")
SYCM_JSON = os.path.join(BASE_DIR, "company_active_mattresses_dataset.json")

OUT_MASTER_JSON = os.path.join(BASE_DIR, "company_mattress_full_integrated_analysis.json")
OUT_MASTER_CSV = os.path.join(BASE_DIR, "company_mattress_full_integrated_analysis.csv")
OUT_HTML = os.path.join(BASE_DIR, "公司旗下床垫95款全量SKU与主图分析交互大屏.html")

def main():
    print("=" * 70)
    print("🚀 正在整合公司旗下 95 款床垫全量 1.8m SKU、主图视觉与销售数据...")
    print("=" * 70)

    with open(SKU_JSON, "r", encoding="utf-8") as f:
        sku_data = json.load(f)
    with open(OCR_JSON, "r", encoding="utf-8") as f:
        ocr_data = json.load(f)
    with open(SYCM_JSON, "r", encoding="utf-8") as f:
        sycm_data = json.load(f)

    # 建立映射
    sycm_map = {str(p["itemId"]): p for p in sycm_data["products"]}
    ocr_map = {}
    for k, v in ocr_data.items():
        ocr_map[str(v.get("itemId"))] = v

    integrated_products = []
    all_sku_flat_rows = []

    all_prices = []
    
    for p in sku_data["products"]:
        item_id = str(p.get("itemId"))
        rank = p.get("rank")
        shop = p.get("shop")
        title = p.get("title")
        link = p.get("link")
        
        # 补充生意参谋指标
        s_info = sycm_map.get(item_id, {})
        sales_amt = s_info.get("pay_amount", 0.0)
        sales_qty = s_info.get("pay_item_qty", 0)
        buyers = s_info.get("pay_buyer_qty", 0)
        unit_price = s_info.get("customer_unit_price", 0.0)
        pay_rate = s_info.get("pay_rate", "0%")
        
        # 补充主图与 OCR 指标
        o_info = ocr_map.get(item_id, {})
        main_img_url = o_info.get("main_img_url", s_info.get("img_url", ""))
        img_file = o_info.get("image_file", f"{item_id}.jpg")
        local_img_path = f"company_analysis/images/{img_file}"
        
        ocr_raw = o_info.get("ocr_raw", "")
        ocr_lines = o_info.get("ocr_lines", [])
        selling_points = o_info.get("selling_points", [])
        marketing_text = o_info.get("marketing_text", [])
        visual_format = o_info.get("visual_format", [])
        
        skus = p.get("skus", [])
        min_p = p.get("min_price")
        max_p = p.get("max_price")
        median_p = p.get("median_price")
        mean_p = p.get("mean_price")
        
        for s in skus:
            if isinstance(s.get("price"), (int, float)) and s["price"] > 1:
                all_prices.append(s["price"])
                
            all_sku_flat_rows.append({
                "排名": rank,
                "商品ID": item_id,
                "店铺": shop,
                "商品标题": title,
                "1.8米起步最低加补价(元)": min_p,
                "1.8米最高加补价(元)": max_p,
                "1.8米款式中位价(元)": median_p,
                "款式总数": len(skus),
                "SKU款型名称": s.get("name"),
                "平台加补后到手价(元)": s.get("price"),
                "优惠前原价(元)": s.get("orig"),
                "价格标签": s.get("tag", "平台加补后"),
                "支付金额(元)": sales_amt,
                "支付件数": sales_qty,
                "支付买家数": buyers,
                "客单价(元)": unit_price,
                "支付转化率": pay_rate,
                "主图卖点标签": " / ".join(selling_points) if selling_points else "",
                "主图营销标签": " / ".join(marketing_text) if marketing_text else "",
                "主图OCR文本摘要": ocr_raw[:80].replace("\n", " "),
                "1.8米直达链接": link,
                "主图链接": main_img_url,
                "本地主图路径": local_img_path
            })

        prod_record = {
            "rank": rank,
            "itemId": item_id,
            "shop": shop,
            "title": title,
            "link": link,
            "main_img_url": main_img_url,
            "image_file": img_file,
            "local_img_path": local_img_path,
            "sales_amount": sales_amt,
            "sales_qty": sales_qty,
            "buyers": buyers,
            "unit_price": unit_price,
            "pay_rate": pay_rate,
            "min_price": min_p,
            "max_price": max_p,
            "median_price": median_p,
            "mean_price": mean_p,
            "sku_count": len(skus),
            "skus": skus,
            "ocr_raw": ocr_raw,
            "ocr_lines": ocr_lines,
            "selling_points": selling_points,
            "marketing_text": marketing_text,
            "visual_format": visual_format
        }
        integrated_products.append(prod_record)

    all_prices.sort()
    overall_median = all_prices[len(all_prices)//2] if all_prices else 0
    overall_mean = round(sum(all_prices)/len(all_prices), 2) if all_prices else 0

    # 价格带统计
    BANDS = [
        {"id": "band_under_300", "label": "300元以下", "sub": "学生宿舍/简易薄垫/低客单", "min": 0, "max": 299.99},
        {"id": "band_300_600", "label": "300-600元", "sub": "入门级薄款黄麻/折叠榻榻米", "min": 300, "max": 599.99},
        {"id": "band_600_1000", "label": "600-1000元", "sub": "主打薄垫/全拆黄麻/静音弹簧", "min": 600, "max": 999.99},
        {"id": "band_1000_1500", "label": "1000-1500元", "sub": "主力放量级/五星酒店款/双面睡感", "min": 1000, "max": 1499.99},
        {"id": "band_1500_2000", "label": "1500-2000元", "sub": "品质升级款/轻奢护腰/尊耀全拆", "min": 1500, "max": 1999.99},
        {"id": "band_above_2000", "label": "2000元以上", "sub": "高端奢华/大体重加粗/多功能全拆", "min": 2000, "max": 999999},
    ]

    price_bands_stats = []
    total_skus_count = len(all_prices)
    for b in BANDS:
        matched_skus = [p for p in all_prices if b["min"] <= p <= b["max"]]
        matched_prods = [p for p in integrated_products if p["min_price"] is not None and b["min"] <= p["min_price"] <= b["max"]]
        price_bands_stats.append({
            "id": b["id"],
            "label": b["label"],
            "sub": b["sub"],
            "min": b["min"],
            "max": b["max"],
            "sku_count": len(matched_skus),
            "sku_pct": round(len(matched_skus) / max(total_skus_count, 1) * 100, 1),
            "prod_count": len(matched_prods),
            "prod_pct": round(len(matched_prods) / max(len(integrated_products), 1) * 100, 1),
            "median": matched_skus[len(matched_skus)//2] if matched_skus else 0,
            "mean": round(sum(matched_skus)/len(matched_skus), 2) if matched_skus else 0
        })

    # 排名梯队统计
    RANK_TIERS = [
        {"id": "tier_top10", "label": "Top 1-10 核心爆款", "start": 1, "end": 10},
        {"id": "tier_11_30", "label": "Top 11-30 潜力放量款", "start": 11, "end": 30},
        {"id": "tier_31_60", "label": "Top 31-60 腰部基石款", "start": 31, "end": 60},
        {"id": "tier_61_95", "label": "Top 61-95 长尾补齐款", "start": 61, "end": 95},
    ]
    rank_tiers_stats = []
    for r_def in RANK_TIERS:
        t_prods = [p for p in integrated_products if r_def["start"] <= p["rank"] <= r_def["end"]]
        t_skus = []
        for p in t_prods:
            for s in p["skus"]:
                if isinstance(s.get("price"), (int, float)) and s["price"] > 1:
                    t_skus.append(s["price"])
        t_skus.sort()
        t_amt = sum(p["sales_amount"] for p in t_prods)
        rank_tiers_stats.append({
            "id": r_def["id"],
            "label": r_def["label"],
            "prod_count": len(t_prods),
            "sku_count": len(t_skus),
            "sales_amount": round(t_amt, 2),
            "median_price": t_skus[len(t_skus)//2] if t_skus else 0,
            "mean_price": round(sum(t_skus)/len(t_skus), 2) if t_skus else 0,
            "min_start_price": min([p["min_price"] for p in t_prods if p["min_price"] and p["min_price"] > 1] or [0]),
            "max_start_price": max([p["min_price"] for p in t_prods if p["min_price"] and p["min_price"] > 1] or [0])
        })

    # 店铺矩阵统计
    shop_groups = {}
    for p in integrated_products:
        s = p["shop"]
        shop_groups.setdefault(s, []).append(p)
        
    top_shops_stats = []
    for s_name, p_list in sorted(shop_groups.items(), key=lambda x: len(x[1]), reverse=True):
        s_skus = []
        for p in p_list:
            for s in p["skus"]:
                if isinstance(s.get("price"), (int, float)) and s["price"] > 1:
                    s_skus.append(s["price"])
        s_skus.sort()
        s_amt = sum(p["sales_amount"] for p in p_list)
        s_qty = sum(p["sales_qty"] for p in p_list)
        top_shops_stats.append({
            "shop": s_name,
            "prod_count": len(p_list),
            "sku_count": len(s_skus),
            "sales_amount": round(s_amt, 2),
            "sales_qty": s_qty,
            "min_price": min([p["min_price"] for p in p_list if p["min_price"] and p["min_price"] > 1] or [0]),
            "max_price": max([p["max_price"] for p in p_list if p["max_price"] and p["max_price"] > 1] or [0]),
            "median_price": s_skus[len(s_skus)//2] if s_skus else 0,
            "mean_price": round(sum(s_skus)/len(s_skus), 2) if s_skus else 0
        })

    master_dataset = {
        "meta": {
            "title": "公司旗下在售床垫 95 款 1800mm*2000mm 全量 SKU 与主图深度统计分析",
            "total_products": len(integrated_products),
            "total_skus": len(all_sku_flat_rows),
            "overall_price_median": overall_median,
            "overall_price_mean": overall_mean,
            "updated_at": sku_data.get("meta", {}).get("updated_at")
        },
        "price_bands_stats": price_bands_stats,
        "rank_tiers_stats": rank_tiers_stats,
        "top_shops_stats": top_shops_stats,
        "products": integrated_products
    }

    # 导出全景 JSON
    with open(OUT_MASTER_JSON, "w", encoding="utf-8") as f:
        json.dump(master_dataset, f, ensure_ascii=False, indent=2)
    print(f"✅ 全景主数据集已导出: {OUT_MASTER_JSON}")

    # 导出全景 CSV
    if all_sku_flat_rows:
        with open(OUT_MASTER_CSV, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(all_sku_flat_rows[0].keys()))
            writer.writeheader()
            writer.writerows(all_sku_flat_rows)
        print(f"✅ 全景扁平化 CSV 已导出: {OUT_MASTER_CSV} (共 {len(all_sku_flat_rows)} 条 SKU)")

    return master_dataset

if __name__ == "__main__":
    main()
