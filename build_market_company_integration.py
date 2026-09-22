# -*- coding: utf-8 -*-
"""
市场300款 + 公司内部95款床垫全域横向对比数据融合与构建引擎
1. 整合天猫大盘300款与公司旗下95款全量数据 (共395款商品，5,877个1.8m SKU)
2. 针对大盘全量SKU执行总高(厚度)正则深度解析，对齐两套数据厚度字段
3. 打通商品ID、来源归属(公司自营 vs 市场大盘)、双向排名体系与主图视觉卖点
4. 输出标准化的 market_company_combined_analysis.json 与 .csv
"""
import json
import re
import os
import math

def extract_height(sku_name, title=''):
    s_text = sku_name or ''
    # 优先从 SKU 名称中匹配所有 cm/CM/厘米/公分/厚 前的数值
    matches = re.findall(r'(\d+(?:\.\d+)?)\s*(?:cm|CM|厘米|公分|厚)', s_text)
    if matches:
        valid_nums = [float(x) for x in matches if 2 <= float(x) <= 55]
        if valid_nums:
            h = max(valid_nums)  # 存在多个cm时取最大数值，如 2cm乳胶+2cm黄麻 24cm 取24
            return int(h) if h.is_integer() else h
    m2 = re.findall(r'(?:厚度|厚|高|总高)\s*[:：]?\s*(\d+(?:\.\d+)?)', s_text)
    if m2:
        valid_nums = [float(x) for x in m2 if 2 <= float(x) <= 55]
        if valid_nums:
            h = max(valid_nums)
            return int(h) if h.is_integer() else h

    # 若 SKU 文本无厚度，回退至商品标题中提取
    t_text = title or ''
    t_matches = re.findall(r'(\d+(?:\.\d+)?)\s*(?:cm|CM|厘米|公分|厚)', t_text)
    if t_matches:
        valid_nums = [float(x) for x in t_matches if 2 <= float(x) <= 55]
        if valid_nums:
            h = max(valid_nums)
            return int(h) if h.is_integer() else h
    t_m2 = re.findall(r'(?:厚度|厚|高|总高)\s*[:：]?\s*(\d+(?:\.\d+)?)', t_text)
    if t_m2:
        valid_nums = [float(x) for x in t_m2 if 2 <= float(x) <= 55]
        if valid_nums:
            h = max(valid_nums)
            return int(h) if h.is_integer() else h
    return None

def format_item_link(item_id=None, original_link=''):
    if not item_id and original_link:
        m = re.search(r'id=(\d+)', str(original_link))
        if m:
            item_id = m.group(1)
    if item_id:
        return f"https://detail.tmall.com/item.htm?b_s_f=sycm&b_spm=a21ag.29085015&id={item_id}"
    return original_link or ""

def main():
    print("[1/5] 读取两大数据源...")
    with open('company_mattress_full_integrated_analysis.json', 'r', encoding='utf-8') as f:
        comp_data = json.load(f)
    
    with open('claude_deep_analysis/dataset.json', 'r', encoding='utf-8') as f:
        mkt_data = json.load(f)

    comp_products = comp_data.get('products', [])
    mkt_products = mkt_data.get('products', [])
    print(f"  - 公司内部商品数: {len(comp_products)}")
    print(f"  - 市场大盘商品数: {len(mkt_products)}")

    # 建立商品ID映射以识别双重身份 (在公司旗下且打入大盘300强)
    comp_item_map = {}
    for p in comp_products:
        item_id = str(p.get('itemId', ''))
        if item_id:
            comp_item_map[item_id] = p

    mkt_item_map = {}
    for p in mkt_products:
        m = re.search(r'id=(\d+)', p.get('link', ''))
        item_id = m.group(1) if m else ''
        if item_id:
            mkt_item_map[item_id] = p

    print(f"[2/5] 交叉比对与厚度深度清洗...")
    # 处理市场大盘300款
    processed_mkt = []
    for p in mkt_products:
        m = re.search(r'id=(\d+)', p.get('link', ''))
        item_id = m.group(1) if m else f"mkt_{p['rank']}"
        is_also_comp = item_id in comp_item_map
        comp_counterpart = comp_item_map.get(item_id)

        # SKU 处理与厚度提取
        skus = []
        for s in p.get('skus', []):
            h = extract_height(s.get('name', ''), p.get('title', ''))
            skus.append({
                'name': s.get('name', ''),
                'price': float(s.get('price', 0.0)),
                'orig': float(s['orig']) if s.get('orig') is not None else None,
                'tag': s.get('tag', ''),
                'height': h,
                'isStart': s.get('isStart', False)
            })

        heights = sorted(list(set(s['height'] for s in skus if s['height'] is not None)))
        h_min = min(heights) if heights else None
        h_max = max(heights) if heights else None
        if h_min is not None and h_max is not None:
            h_disp = f"{h_min}cm" if h_min == h_max else f"{h_min}~{h_max}cm"
        else:
            h_disp = "未标注"

        prod_dict = {
            'unique_id': f"mkt_{p['rank']}_{item_id}",
            'itemId': item_id,
            'source': 'market',
            'source_name': '天猫大盘',
            'is_company': False,
            'is_market': True,
            'is_cross_listed': is_also_comp,
            'rank': p['rank'],
            'market_rank': p['rank'],
            'company_rank': comp_counterpart['rank'] if is_also_comp else None,
            'display_rank': f"大盘 #{p['rank']}",
            'source_badge': '🌐 天猫大盘爆品',
            'cross_badge': f"🏢 关联公司自营 #{comp_counterpart['rank']}" if is_also_comp else None,
            'shop': p.get('shop', ''),
            'title': p.get('title', ''),
            'link': format_item_link(item_id, p.get('link', '')),
            'min_price': float(p.get('min_price', 0.0)),
            'max_price': float(p.get('max_price', 0.0)),
            'median_price': float(p.get('median_price', 0.0)),
            'mean_price': float(p.get('mean_price', 0.0)),
            'sku_count': len(skus),
            'heights': heights,
            'height_min': h_min,
            'height_max': h_max,
            'height_display': h_disp,
            'skus': skus,
            'ocr_lines': p.get('ocr_lines', []),
            'selling_points': p.get('selling_points', []),
            'marketing_text': p.get('marketing_text', ''),
            'visual_format': p.get('visual_format', ''),
            'main_img_url': comp_counterpart.get('main_img_url', '') if is_also_comp else f"https://img.alicdn.com/bao/uploaded/i2/item_pic.jpg",
            'image_file': comp_counterpart.get('image_file', '') if is_also_comp else f"{item_id}.jpg",
            'local_img_path': comp_counterpart.get('local_img_path', '') if is_also_comp else ''
        }
        processed_mkt.append(prod_dict)

    # 处理公司自营95款
    processed_comp = []
    for p in comp_products:
        item_id = str(p.get('itemId', ''))
        is_also_mkt = item_id in mkt_item_map
        mkt_counterpart = mkt_item_map.get(item_id)

        skus = []
        for s in p.get('skus', []):
            h = extract_height(s.get('name', ''), p.get('title', ''))
            if h is None and s.get('height') is not None:
                h = s.get('height')
            skus.append({
                'name': s.get('name', ''),
                'price': float(s.get('price', 0.0)),
                'orig': float(s['orig']) if s.get('orig') is not None else None,
                'tag': s.get('tag', ''),
                'height': h,
                'isStart': s.get('isStart', False)
            })

        heights = sorted(list(set(s['height'] for s in skus if s['height'] is not None)))
        h_min = min(heights) if heights else None
        h_max = max(heights) if heights else None
        if h_min is not None and h_max is not None:
            h_disp = f"{h_min}cm" if h_min == h_max else f"{h_min}~{h_max}cm"
        else:
            h_disp = "未标注"

        prod_dict = {
            'unique_id': f"comp_{p['rank']}_{item_id}",
            'itemId': item_id,
            'source': 'company',
            'source_name': '公司自营',
            'is_company': True,
            'is_market': is_also_mkt,
            'is_cross_listed': is_also_mkt,
            'rank': p['rank'],
            'company_rank': p['rank'],
            'market_rank': mkt_counterpart['rank'] if is_also_mkt else None,
            'display_rank': f"自营 #{p['rank']}",
            'source_badge': '🏢 公司自营款',
            'cross_badge': f"🔥 斩获大盘 #{mkt_counterpart['rank']}" if is_also_mkt else None,
            'shop': p.get('shop', ''),
            'title': p.get('title', ''),
            'link': format_item_link(item_id, p.get('link', '')),
            'sales_amount': p.get('sales_amount', 0.0),
            'sales_qty': p.get('sales_qty', 0),
            'buyers': p.get('buyers', 0),
            'pay_rate': p.get('pay_rate', '0%'),
            'min_price': float(p.get('min_price', 0.0)),
            'max_price': float(p.get('max_price', 0.0)),
            'median_price': float(p.get('median_price', 0.0)),
            'mean_price': float(p.get('mean_price', 0.0)),
            'sku_count': len(skus),
            'heights': heights,
            'height_min': h_min,
            'height_max': h_max,
            'height_display': h_disp,
            'skus': skus,
            'ocr_lines': p.get('ocr_lines', []),
            'selling_points': p.get('selling_points', []),
            'marketing_text': p.get('marketing_text', ''),
            'visual_format': p.get('visual_format', ''),
            'main_img_url': p.get('main_img_url', ''),
            'image_file': p.get('image_file', ''),
            'local_img_path': p.get('local_img_path', '')
        }
        processed_comp.append(prod_dict)

    all_products = processed_mkt + processed_comp
    print(f"  - 全量合并商品总数: {len(all_products)} 款")
    all_skus = [s for p in all_products for s in p['skus']]
    print(f"  - 全量合并SKU总数: {len(all_skus)} 个")
    resolved_skus = [s for s in all_skus if s['height'] is not None]
    print(f"  - 厚度成功识别SKU数: {len(resolved_skus)} 个 ({len(resolved_skus)/len(all_skus)*100:.1f}%)")

    print("[3/5] 计算综合统计指标 (价格带、厚度梯队、来源对比)...")
    all_prices = [s['price'] for s in all_skus if s['price'] > 0]
    all_prices.sort()
    med_price = all_prices[len(all_prices)//2] if all_prices else 0
    mean_price = round(sum(all_prices)/len(all_prices), 2) if all_prices else 0

    # 价格带统计
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

    # 排名梯队统计 (按大盘300款排名梯队划分)
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

    # 店铺品牌排行 (含完整兼容字段)
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

    combined_db = {
        'meta': {
            'title': '天猫市场300款与公司内部床垫全域横向对比综合数据库',
            'updated_at': '2026-09-21',
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

    print("[4/5] 保存全量结构化 JSON 文件...")
    json_path = 'market_company_combined_analysis.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(combined_db, f, ensure_ascii=False, indent=2)
    print(f"  - 已输出 JSON: {json_path} ({os.path.getsize(json_path)//1024} KB)")

    print("[5/5] 生成横向对比平面 CSV 文件...")
    import csv
    csv_path = 'market_company_combined_analysis.csv'
    with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
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
    print(f"  - 已输出 CSV: {csv_path} ({os.path.getsize(csv_path)//1024} KB)")
    print("全域融合数据集生成完毕！")

if __name__ == '__main__':
    main()
