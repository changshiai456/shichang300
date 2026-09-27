# -*- coding: utf-8 -*-
"""
=============================================================================
从生意参谋报表 Sycm_Report_1790518002796.html 提取最新 30 天市场前 300 款床垫
穿透解析真实商品 ID (itemId) 并生成标准商品目录
=============================================================================
"""
import os
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
import re
import json
import csv
import time
import urllib.request
import concurrent.futures
import bs4

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_HTML = os.path.join(BASE_DIR, "Sycm_Report_1790518002796.html")
OUT_JSON = os.path.join(BASE_DIR, "market_top300_products_catalog.json")
OUT_CSV = os.path.join(BASE_DIR, "market_top300_products_catalog.csv")

def resolve_single_url(target):
    rank, raw_url = target
    for attempt in range(4):
        try:
            req = urllib.request.Request(
                raw_url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
                }
            )
            resp = urllib.request.urlopen(req, timeout=12)
            final_url = resp.geturl()
            m = re.search(r'id=(\d+)', final_url)
            if m:
                return rank, m.group(1), final_url, None
            # If not in final_url, check content for item link
            body = resp.read(2048).decode('utf-8', errors='ignore')
            m2 = re.search(r'id=(\d+)', body)
            if m2:
                return rank, m2.group(1), final_url, None
        except Exception as e:
            if attempt == 3:
                return rank, None, raw_url, str(e)
            time.sleep(1 + attempt * 0.5)
    return rank, None, raw_url, "Unknown failure"

def main():
    print("=" * 70)
    print("🔍 [第一步] 正在解析生意参谋报表 HTML: Sycm_Report_1790518002796.html")
    print("=" * 70)

    if not os.path.exists(REPORT_HTML):
        raise FileNotFoundError(f"未找到报表文件: {REPORT_HTML}")

    with open(REPORT_HTML, "r", encoding="utf-8") as f:
        soup = bs4.BeautifulSoup(f.read(), "html.parser")

    rows = soup.select("#data-table tbody tr")
    print(f"✅ 成功找到表格商品条目: 共 {len(rows)} 行")

    raw_items = []
    url_tasks = []

    for idx, tr in enumerate(rows):
        tds = tr.find_all("td")
        if len(tds) < 7:
            continue
        
        rank_no = int(tds[0].text.strip())
        rank_change = tds[1].text.strip()
        
        # 商品单元格
        item_td = tds[2]
        item_a = item_td.find("a")
        raw_url = item_a["href"] if item_a and "href" in item_a.attrs else ""
        item_img_el = item_td.find("img")
        img_url = item_img_el.get("data-large-src") or item_img_el.get("src") if item_img_el else ""
        
        # 统一转高清图（去掉 _36x36.jpg 等缩略图后缀）
        if img_url:
            img_url = re.sub(r'_\d+x\d+.*$', '', img_url)
            if not img_url.startswith("http"):
                img_url = "https:" + img_url

        title_span = item_td.find("span")
        title = title_span.text.strip() if title_span else item_td.text.strip()

        keywords = tds[3].text.strip()

        # 店铺单元格
        shop_td = tds[4]
        shop_a = shop_td.find("a")
        shop_url = shop_a["href"] if shop_a and "href" in shop_a.attrs else ""
        shop_name_el = shop_td.find("span")
        shop_name = shop_name_el.text.strip() if shop_name_el else shop_td.text.strip()

        pay_buyers = tds[5].text.strip()
        visitors = tds[6].text.strip()

        item_data = {
            "rank": rank_no,
            "rank_change": rank_change,
            "title": title,
            "raw_redirect_url": raw_url,
            "main_img_url": img_url,
            "keywords": keywords,
            "shop": shop_name,
            "shop_url": shop_url,
            "pay_buyers_range": pay_buyers,
            "visitors_range": visitors
        }
        raw_items.append(item_data)
        url_tasks.append((rank_no, raw_url))

    print(f"🚀 开始并发穿透解析 {len(url_tasks)} 个商品的真实天猫/淘宝商品 ID (itemId)...")
    t0 = time.time()
    resolved_map = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        future_to_rank = {executor.submit(resolve_single_url, task): task[0] for task in url_tasks}
        completed = 0
        for future in concurrent.futures.as_completed(future_to_rank):
            rank, item_id, final_url, err = future.result()
            completed += 1
            if item_id:
                resolved_map[rank] = (item_id, final_url)
            else:
                print(f"   ⚠️ #{rank} 解析失败: {err}")
            if completed % 50 == 0 or completed == len(url_tasks):
                print(f"   进度: [{completed}/{len(url_tasks)}] ({completed / len(url_tasks) * 100:.1f}%)")

    t_elapsed = time.time() - t0
    print(f"✨ URL 穿透解析完成！耗时: {t_elapsed:.1f} 秒，成功率: {len(resolved_map)} / {len(url_tasks)}")

    # 组装完整数据集
    products = []
    for item in raw_items:
        r = item["rank"]
        res = resolved_map.get(r)
        if res:
            item_id, final_url = res
        else:
            # 尝试从原始链接兜底提取
            m = re.search(r'id=(\d+)', item.get("raw_redirect_url", ""))
            item_id = m.group(1) if m else f"mkt_{r}"
            final_url = item.get("raw_redirect_url", "")

        standard_url = f"https://detail.tmall.com/item.htm?b_s_f=sycm&b_spm=a21ag.29085015&id={item_id}"
        spec_url = f"https://detail.tmall.com/item.htm?b_s_f=sycm&b_spm=a21ag.29085015&id={item_id}&sku_properties=21433:50753460"

        prod_record = {
            "rank": r,
            "rank_change": item["rank_change"],
            "itemId": str(item_id),
            "shop": item["shop"],
            "shop_url": item["shop_url"],
            "title": item["title"],
            "item_url": standard_url,
            "item_url_1800x2000": spec_url,
            "main_img_url": item["main_img_url"],
            "keywords": item["keywords"],
            "pay_buyers_range": item["pay_buyers_range"],
            "visitors_range": item["visitors_range"],
            "source": "market"
        }
        products.append(prod_record)

    output_dataset = {
        "meta": {
            "title": "天猫床垫最新30天市场TOP300商品目录库",
            "total_products": len(products),
            "source_file": "Sycm_Report_1790518002796.html",
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "spec_standard": "1800mm*2000mm (sku_properties=21433:50753460)"
        },
        "products": products
    }

    # 保存 JSON
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(output_dataset, f, ensure_ascii=False, indent=2)

    # 保存 CSV
    csv_fields = ["rank", "rank_change", "itemId", "shop", "title", "pay_buyers_range", "visitors_range", "keywords", "item_url_1800x2000", "main_img_url"]
    with open(OUT_CSV, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=csv_fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(products)

    print("\n" + "=" * 70)
    print("🎉 恭喜！最新 30 天市场前 300 款床垫基础商品目录生成成功！")
    print(f"• 完整 JSON 数据集: {OUT_JSON}")
    print(f"• 规范 CSV 表格:    {OUT_CSV}")
    print(f"• 成功提取商品总数: {len(products)} 款")
    print("=" * 70)

if __name__ == "__main__":
    main()
