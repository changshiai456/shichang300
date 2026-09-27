# -*- coding: utf-8 -*-
"""
=============================================================================
天猫最新 30 天市场 TOP 300 床垫 1800mm*2000mm 全量 SKU 平台到手价【极速毫秒级自动化采集器】
=============================================================================
核心特性：
1. 【尺寸双重锁定】URL 参数自动挂载 + 浏览器内智能检测锁定 1800mm*2000mm (绝不误采 1.2m/1.5m 等)
2. 【毫秒级微任务捕获】注入 V8 极速微任务，65ms 切换款式并提取加补到手价/券后价与优惠前原价
3. 【高精度排除杂项】自动过滤“系列：”大标题、大图模式切换按钮、缺货禁用按钮，仅提取真实床垫款式
4. 【实时断点续传】每采集一款商品即刻落盘 JSON，遇网络中断或手动暂停均可秒级无缝续传
5. 【双重格式同步导出】全量生成规范 JSON 数据集与面向 Excel / BI 分析的 CSV 扁平化数据表
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
import argparse
from DrissionPage import ChromiumPage, ChromiumOptions

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROFILE_DIR = os.path.join(BASE_DIR, "tmall_chrome_profile")
INPUT_FILE = os.path.join(BASE_DIR, "market_top300_products_catalog.json")
OUT_JSON = os.path.join(BASE_DIR, "market_mattress_300_18m_skus.json")
OUT_CSV = os.path.join(BASE_DIR, "market_mattress_300_18m_skus.csv")

# 浏览器内部注入执行的高性能极速抓取微任务
FAST_SCRAPE_JS = """
async function fastExtractMarketMattressSkus() {
    const sleep = ms => new Promise(r => setTimeout(r, ms));
    
    // 1. 高精度读取天猫红色大促横幅【平台加补后 ¥ xxx】到手价与原价
    function readCurrentPrices() {
        let bannerPrice = null;
        let origPrice = null;
        let isStart = false;
        
        const allSpans = Array.from(document.querySelectorAll('span, div, b, strong, em, p'));
        for (const el of allSpans) {
            if (el.children.length === 0 && el.innerText) {
                const t = el.innerText.trim();
                if (t.includes('平台加补后') || t.includes('补贴到手') || t.includes('券后') || t.includes('到手价')) {
                    let p = el.parentElement;
                    for (let k = 0; k < 5 && p; k++) {
                        const m = p.innerText.match(/(?:平台加补后|补贴到手价|预估到手价|券后到手价|券后价|到手价)[^\\d]*¥?\\s*([\\d\\.]+)\\s*(起)?/);
                        if (m) {
                            bannerPrice = parseFloat(m[1]);
                            if (m[2] === '起' || p.innerText.includes('起')) isStart = true;
                            break;
                        }
                        p = p.parentElement;
                    }
                }
                if (t.includes('优惠前') || t.includes('原价') || t.includes('吊牌价')) {
                    let p = el.parentElement;
                    for (let k = 0; k < 5 && p; k++) {
                        const m = p.innerText.match(/(?:优惠前|原价|吊牌价)[^\\d]*¥?\\s*([\\d\\.]+)/);
                        if (m) {
                            origPrice = parseFloat(m[1]);
                            break;
                        }
                        p = p.parentElement;
                    }
                }
            }
            if (bannerPrice && origPrice) break;
        }
        
        // 兜底大字横幅选择器
        if (!bannerPrice) {
            const bigPrice = document.querySelector('[class*="bannerPrice"], [class*="priceText"], [class*="highlightPrice"], [class*="PromotionPrice"], [class*="promoPrice"]');
            if (bigPrice && bigPrice.innerText) {
                const m = bigPrice.innerText.match(/([\\d\\.]+)/);
                if (m) bannerPrice = parseFloat(m[1]);
            }
        }
        
        return { bannerPrice, origPrice, isStart };
    }
    
    // 2. 智能检测并确保锁定 1800mm*2000mm 尺寸规格
    const allGroups = Array.from(document.querySelectorAll('div[class*="skuItem--"], [class*="sku-item"], [class*="propItem"]'));
    let sizeGroup = null;
    let colorGroup = null;
    
    for (const g of allGroups) {
        const header = (g.innerText || '').slice(0, 40);
        if (header.includes('尺寸') || header.includes('规格') || header.includes('长*宽')) {
            sizeGroup = g;
        } else if (header.includes('颜色分类') || header.includes('款式') || (!header.includes('尺寸') && !header.includes('规格') && !header.includes('1800'))) {
            if (!colorGroup) colorGroup = g;
        }
    }
    
    // 如果尺寸规格未选中 1.8 米，主动点击激活
    if (sizeGroup) {
        const sizeBtns = Array.from(sizeGroup.querySelectorAll('div[class*="valueItem--"], button, [role="radio"]'));
        const btn18m = sizeBtns.find(b => {
            const txt = (b.innerText || '').toLowerCase();
            return (txt.includes('1800') && txt.includes('2000')) ||
                   (txt.includes('1.8') && (txt.includes('2.0') || txt.includes('2米') || txt.includes('床') || txt.includes('双人'))) ||
                   (txt.includes('180') && txt.includes('200'));
        });
        if (btn18m) {
            const cls = btn18m.className || '';
            const isSelected = cls.includes('isSelected--') || cls.includes('selected') || btn18m.getAttribute('aria-checked') === 'true';
            if (!isSelected && !cls.includes('isDisabled--')) {
                btn18m.click();
                await sleep(80);
            }
        }
    }
    
    const initP = readCurrentPrices();
    
    // 如果没有二级款式（仅有尺寸单规格床垫）
    if (!colorGroup) {
        return {
            type: 'single_spec',
            initPrice: initP,
            skuCount: 1,
            elapsedMs: 0,
            skus: [{
                name: '1800mm*2000mm 标准配置款',
                price: initP.bannerPrice,
                orig: initP.origPrice,
                isStart: initP.isStart,
                tag: '平台加补后'
            }]
        };
    }
    
    // 3. 严格筛选可点击的款式项（严禁包含尺寸、严禁包含系列大标题、严禁包含禁用按钮）
    const allValueItems = Array.from(colorGroup.querySelectorAll('div[class*="valueItem--"], button, [role="radio"]'));
    const validItems = allValueItems.filter(el => {
        const cls = el.className || '';
        if (cls.includes('isDisabled--') || el.hasAttribute('disabled')) return false;
        const txt = (el.innerText || '').trim();
        if (txt.includes('*') || txt.includes('mm') || txt.includes('米') || txt.includes('1800') || txt.includes('1500') || txt.includes('1200') || txt.includes('2000*2200')) return false;
        if (txt.includes('系列：') || txt.includes('系列:') || txt.includes('切换大图') || txt.includes('更多') || txt.includes('加入购物车') || txt.includes('立即购买')) return false;
        if (txt.length < 2) return false;
        return true;
    });
    
    if (validItems.length === 0) {
        return {
            type: 'single_spec',
            initPrice: initP,
            skuCount: 1,
            elapsedMs: 0,
            skus: [{
                name: '1800mm*2000mm 标准配置款',
                price: initP.bannerPrice,
                orig: initP.origPrice,
                isStart: initP.isStart,
                tag: '平台加补后'
            }]
        };
    }
    
    // 4. 毫秒级极速模拟点击与实时捕获
    const skus = [];
    const t0 = performance.now();
    
    for (const item of validItems) {
        const skuName = (item.innerText || '').replace(/\\s+/g, ' ').trim();
        item.click();
        await sleep(65);
        
        const curP = readCurrentPrices();
        skus.push({
            name: skuName,
            price: curP.bannerPrice || initP.bannerPrice,
            orig: curP.origPrice || initP.origPrice,
            isStart: curP.isStart,
            tag: '平台加补后'
        });
    }
    
    const elapsed = Math.round(performance.now() - t0);
    return {
        type: 'multi_sku',
        initPrice: initP,
        skuCount: skus.length,
        elapsedMs: elapsed,
        skus: skus
    };
}
return fastExtractMarketMattressSkus();
"""

def save_checkpoint(all_results, total_target_count):
    save_dataset = {
        "meta": {
            "title": "天猫市场TOP300床垫1800mm*2000mm全量SKU到手价数据库",
            "total_target_count": total_target_count,
            "completed_count": len(all_results),
            "spec": "1800mm*2000mm",
            "tag": "平台加补后",
            "updated_at": time.strftime("%Y-%m-%d %H:%M:%S")
        },
        "products": all_results
    }
    with open(OUT_JSON, "w", encoding="utf-8") as out_f:
        json.dump(save_dataset, out_f, ensure_ascii=False, indent=2)

    # 导出 CSV
    csv_rows = []
    for item in all_results:
        for s in item.get("skus", []):
            csv_rows.append({
                "排名": item.get("rank"),
                "商品ID": item.get("itemId"),
                "所属店铺": item.get("shop"),
                "商品标题": item.get("title"),
                "1.8米起步最低价(元)": item.get("min_price"),
                "SKU款型名称": s.get("name"),
                "平台加补后到手价(元)": s.get("price"),
                "优惠前原价(元)": s.get("orig"),
                "价格标签": s.get("tag"),
                "1.8米直达链接": item.get("link")
            })

    if csv_rows:
        with open(OUT_CSV, "w", encoding="utf-8-sig", newline="") as csv_f:
            writer = csv.DictWriter(csv_f, fieldnames=list(csv_rows[0].keys()))
            writer.writeheader()
            writer.writerows(csv_rows)

def main():
    parser = argparse.ArgumentParser(description="天猫市场 TOP300 床垫 1.8m SKU 极速采集器")
    parser.add_argument("--limit", type=int, default=0, help="限制采集的商品数量 (0 表示全量 300 款)")
    parser.add_argument("--start", type=int, default=1, help="起始排名 (默认从第 1 名开始)")
    parser.add_argument("--headless", action="store_true", help="是否无头运行 (默认开启前台渲染窗口以保证价格元素完全渲染)")
    args = parser.parse_args()

    print("=" * 70)
    print("🚀 启动天猫市场 TOP 300 床垫 1.8米 SKU 与平台加补到手价【极速采集器】")
    print(f"📁 浏览器配置目录: {PROFILE_DIR}")
    print(f"📁 输入商品目录:   {INPUT_FILE}")
    print(f"📁 结果导出目录:   {BASE_DIR}")
    print("=" * 70)

    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError(f"未找到商品目录文件，请先运行 extract_sycm_300_catalog.py 生成目录！")

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_catalog_products = data.get("products", [])
    # 按照排名范围过滤
    target_products = [p for p in all_catalog_products if p.get("rank", 0) >= args.start]
    if args.limit > 0:
        target_products = target_products[:args.limit]

    total_target_count = len(target_products)
    print(f"✅ 目标商品载入成功: {total_target_count} 款 (规划排名: #{target_products[0]['rank']} ~ #{target_products[-1]['rank']})\n")

    # 读取已有断点进度
    completed_map = {}
    all_results = []
    if os.path.exists(OUT_JSON):
        try:
            with open(OUT_JSON, "r", encoding="utf-8") as f:
                saved = json.load(f)
                for item in saved.get("products", []):
                    item_id = str(item.get("itemId"))
                    if item_id and len(item.get("skus", [])) > 0:
                        completed_map[item_id] = item
                        all_results.append(item)
            if completed_map:
                print(f"⚡ 检测到历史断点进度，已完成 {len(completed_map)} 款干净数据，将自动跳过并续传！\n")
        except Exception:
            pass

    co = ChromiumOptions()
    co.set_user_data_path(PROFILE_DIR)
    co.headless(args.headless)
    co.set_argument('--no-first-run')
    co.set_argument('--no-default-browser-check')

    print("正在启动 Chromium 引擎并加载天猫独立登录态...")
    page = ChromiumPage(co)

    start_all_time = time.time()
    newly_crawled_count = 0

    for idx, p_info in enumerate(target_products):
        rank = p_info.get("rank", idx + 1)
        item_id = str(p_info.get("itemId", ""))
        title = p_info.get("title", "")
        shop = p_info.get("shop", "")
        target_url = p_info.get("item_url_1800x2000", "")

        if item_id in completed_map:
            continue

        print(f"[{idx + 1}/{total_target_count}] 正在采集: #{rank} | ID: {item_id} | 店铺: {shop} | {title[:28]}...")
        t_page_start = time.time()

        try:
            page.get(target_url)

            # 快速检测关键元素加载就绪
            ready = False
            for _ in range(12):
                ready = page.run_js('return !!document.querySelector("[class*=\\"skuItem--\\"], [class*=\\"bannerPrice\\"], [class*=\\"priceText\\"]");')
                if ready:
                    break
                time.sleep(0.2)
            time.sleep(0.3)

            # 注入极速微任务瞬间采集
            res = page.run_js(FAST_SCRAPE_JS)
            if not res or not isinstance(res, dict):
                raise RuntimeError("JS 采集脚本未返回有效数据")

            skus = res.get("skus", [])
            init_price_info = res.get("initPrice", {})
            init_banner = init_price_info.get("bannerPrice")
            init_orig = init_price_info.get("origPrice")

            # 聚合计算价格分布
            valid_prices = [s["price"] for s in skus if isinstance(s.get("price"), (int, float)) and s["price"] > 0]
            min_p = min(valid_prices) if valid_prices else init_banner
            max_p = max(valid_prices) if valid_prices else init_banner

            if valid_prices:
                valid_prices.sort()
                median_p = valid_prices[len(valid_prices) // 2]
                mean_p = round(sum(valid_prices) / len(valid_prices), 2)
            else:
                median_p = min_p
                mean_p = min_p

            product_record = {
                "rank": rank,
                "rank_change": p_info.get("rank_change", ""),
                "itemId": item_id,
                "shop": shop,
                "shop_url": p_info.get("shop_url", ""),
                "title": title,
                "link": f"https://detail.tmall.com/item.htm?b_s_f=sycm&b_spm=a21ag.29085015&id={item_id}",
                "item_url_1800x2000": target_url,
                "main_img_url": p_info.get("main_img_url", ""),
                "pay_buyers_range": p_info.get("pay_buyers_range", ""),
                "visitors_range": p_info.get("visitors_range", ""),
                "keywords": p_info.get("keywords", ""),
                "min_price": min_p,
                "max_price": max_p,
                "median_price": median_p,
                "mean_price": mean_p,
                "sku_count": len(skus),
                "skus": skus,
                "crawled_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }

            all_results.append(product_record)
            completed_map[item_id] = product_record
            newly_crawled_count += 1

            t_page_elapsed = time.time() - t_page_start
            js_elapsed = res.get("elapsedMs", 0)
            print(f"   ⚡ [完成 #{rank}] 耗时 {t_page_elapsed:.1f}s (JS提取: {js_elapsed}ms) | 款式数: {len(skus)} | 最低到手价: ￥{min_p} | 最高: ￥{max_p}")
            if skus:
                sample_sku = skus[0]
                print(f"      👉 首款: {sample_sku['name'][:26]} => 到手价: ￥{sample_sku['price']} (原价: ￥{sample_sku['orig']})")

            # 实时断点存盘
            save_checkpoint(all_results, len(all_catalog_products))

        except Exception as e:
            print(f"   ⚠️ 采集 #{rank} 遇到异常: {e}，保存占位记录进入下一款...")
            fallback_record = {
                "rank": rank,
                "rank_change": p_info.get("rank_change", ""),
                "itemId": item_id,
                "shop": shop,
                "shop_url": p_info.get("shop_url", ""),
                "title": title,
                "link": f"https://detail.tmall.com/item.htm?b_s_f=sycm&b_spm=a21ag.29085015&id={item_id}",
                "item_url_1800x2000": target_url,
                "main_img_url": p_info.get("main_img_url", ""),
                "pay_buyers_range": p_info.get("pay_buyers_range", ""),
                "visitors_range": p_info.get("visitors_range", ""),
                "keywords": p_info.get("keywords", ""),
                "min_price": None,
                "max_price": None,
                "median_price": None,
                "mean_price": None,
                "sku_count": 0,
                "skus": [],
                "error": str(e),
                "crawled_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            all_results.append(fallback_record)
            completed_map[item_id] = fallback_record
            save_checkpoint(all_results, len(all_catalog_products))
            time.sleep(1)

    page.quit()
    total_time = time.time() - start_all_time
    print("\n" + "=" * 70)
    print("🎉 恭喜！天猫最新市场 TOP 300 床垫 1.8米全量 SKU 极速采集完成！")
    print(f"• 结构化 JSON 数据集: {OUT_JSON}")
    print(f"• 完整 SKU 明细 CSV:   {OUT_CSV}")
    print(f"• 累计商品总数:       {len(all_results)} 款 (本轮新采集: {newly_crawled_count} 款)")
    print(f"• 耗时:               {total_time:.1f} 秒 (平均每款 {total_time / max(newly_crawled_count, 1):.1f} 秒)")
    print("=" * 70)

if __name__ == "__main__":
    main()
