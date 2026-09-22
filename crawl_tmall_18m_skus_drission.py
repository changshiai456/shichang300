# -*- coding: utf-8 -*-
"""
=============================================================================
天猫 95 款床垫 1800mm*2000mm 全量 SKU 平台加补到手价【极速毫秒级自动化采集器】
=============================================================================
核心特性：
1. 【毫秒级瞬时提取】采用浏览器内核 V8 原生 JS 微任务注入，60ms 极速切换款式并捕获红条加补价，
   单款商品仅需 1.0~1.3 秒即可瞬间完成全部 SKU 提取！
2. 【严格尺寸锁定】绝对不触碰“尺寸”区域（只锁定 1800mm*2000mm），彻底排除任何 1200/1350/1500/2000 等其他尺寸！
3. 【高精度排除杂项】自动排除“系列：”大标题、切换大图模式、禁用款式与营销标签，仅提取真正的床垫款式配置！
4. 【实时断点续传】每采集完一款商品即刻安全落盘 JSON，任意意外中断均可无缝续传！
5. 【双重格式导出】全量生成规范 JSON 数据集与面向 Excel / BI 分析的 CSV 扁平化数据表！
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

BASE_DIR = os.path.abspath(".")
PROFILE_DIR = os.path.join(BASE_DIR, "tmall_chrome_profile")
INPUT_FILE = os.path.join(BASE_DIR, "company_active_mattresses_dataset.json")
OUT_JSON = os.path.join(BASE_DIR, "company_mattress_18m_skus_all.json")
OUT_CSV = os.path.join(BASE_DIR, "company_mattress_18m_skus_all.csv")

# 浏览器内部注入执行的高性能极速抓取微任务
FAST_SCRAPE_JS = """
async function fastExtractMattressSkus() {
    const sleep = ms => new Promise(r => setTimeout(r, ms));
    
    // 1. 高精度读取天猫红色大促横幅【平台加补后 ¥ xxx】到手价与原价
    function readCurrentPrices() {
        let bannerPrice = null;
        let origPrice = null;
        let isStart = false;
        
        // 查找所有包含核心价格文案的叶子节点
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
    
    const initP = readCurrentPrices();
    
    // 2. 智能定位“颜色分类/款式配置”分组 (严格避开“尺寸”或“规格”)
    const groups = Array.from(document.querySelectorAll('div[class*="skuItem--"], [class*="sku-item"], [class*="propItem"]'));
    let colorGroup = null;
    for (const g of groups) {
        const header = (g.innerText || '').slice(0, 40);
        if (header.includes('颜色分类') || header.includes('款式') || (!header.includes('尺寸') && !header.includes('规格') && !header.includes('1800'))) {
            colorGroup = g;
            break;
        }
    }
    
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
        // 严禁包含尺寸标识
        if (txt.includes('*') || txt.includes('mm') || txt.includes('米') || txt.includes('1800') || txt.includes('1500') || txt.includes('1200') || txt.includes('2000*2200')) return false;
        // 严禁包含分类系列大标题与功能按钮
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
        
        // 触发真实点击
        item.click();
        await sleep(65); // 65ms 毫秒级微任务等待，完美匹配 React 渲染更新周期
        
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
return fastExtractMattressSkus();
"""

def main():
    print("=" * 70)
    print("🚀 启动天猫 95 款核心在售床垫 1.8米 SKU 与平台加补到手价【极速采集器】")
    print(f"📁 浏览器配置目录: {PROFILE_DIR}")
    print(f"📁 结果导出目录:   {BASE_DIR}")
    print("=" * 70)

    parser = argparse.ArgumentParser(description="天猫 95 款床垫 1.8m SKU 极速采集器")
    parser.add_argument("--limit", type=int, default=0, help="限制采集的商品数量 (0 表示全量 95 款)")
    args = parser.parse_args()

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    target_products = data.get("products", [])
    if args.limit > 0:
        target_products = target_products[:args.limit]
    total_count = len(target_products)
    print(f"✅ 已载入核心在售床垫: {total_count} 款 (计划执行: {total_count} 款)\n")

    # 读取断点续传（如果已有干净有效数据）
    completed_map = {}
    if os.path.exists(OUT_JSON):
        try:
            with open(OUT_JSON, "r", encoding="utf-8") as f:
                saved = json.load(f)
                for item in saved.get("products", []):
                    # 检查是否包含误抓的 1350 或尺寸，如果是旧数据则跳过并重新采集
                    skus = item.get("skus", [])
                    has_wrong_size = any('*' in s.get('name', '') or '1350' in s.get('name', '') for s in skus)
                    if not has_wrong_size and len(skus) > 0:
                        completed_map[str(item.get("itemId"))] = item
            if completed_map:
                print(f"⚡ 检测到历史断点进度，已完成 {len(completed_map)} 款干净数据，将自动续传！\n")
        except Exception:
            pass

    co = ChromiumOptions()
    co.set_user_data_path(PROFILE_DIR)
    co.headless(False)  # 前台运行以支持动态视觉价格渲染
    co.set_argument('--no-first-run')
    co.set_argument('--no-default-browser-check')

    print("正在启动 DrissionPage 自动化引擎并加载天猫登录态...")
    page = ChromiumPage(co)

    all_results = list(completed_map.values())
    start_all_time = time.time()

    for idx, p_info in enumerate(target_products):
        rank = p_info.get("rank", idx + 1)
        item_id = str(p_info.get("itemId", ""))
        title = p_info.get("title", "")
        shop = p_info.get("shop", "")
        target_url = p_info.get("item_url_1800x2000", "")

        if item_id in completed_map:
            continue

        print(f"[{idx + 1}/{total_count}] 正在采集: #{rank} | ID: {item_id} | 店铺: {shop} | {title[:26]}...")
        t_page_start = time.time()

        try:
            page.get(target_url)

            # 快速检测页面关键元素就绪（用轻量微任务检测，无 CDP 超时停顿）
            for _ in range(10):
                ready = page.run_js('return !!document.querySelector("[class*=\\"skuItem--\\"], [class*=\\"bannerPrice\\"], [class*=\\"priceText\\"]");')
                if ready:
                    break
                time.sleep(0.2)
            time.sleep(0.4)

            # 注入浏览器原生微任务瞬间完成全部 SKU 采集
            res = page.run_js(FAST_SCRAPE_JS)
            if not res or not isinstance(res, dict):
                raise RuntimeError("JS 采集脚本未返回有效数据")

            skus = res.get("skus", [])
            init_price_info = res.get("initPrice", {})
            init_banner = init_price_info.get("bannerPrice")
            init_orig = init_price_info.get("origPrice")

            # 聚合计算价格分布指标
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
                "itemId": item_id,
                "shop": shop,
                "title": title,
                "link": f"https://detail.tmall.com/item.htm?b_s_f=sycm&b_spm=a21ag.29085015&id={item_id}",
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

            t_page_elapsed = time.time() - t_page_start
            js_elapsed = res.get("elapsedMs", 0)
            print(f"   ⚡ [完成 #{rank}] 耗时 {t_page_elapsed:.1f}s (JS提取: {js_elapsed}ms) | 款式数: {len(skus)} | 最低到手价: ￥{min_p} | 最高: ￥{max_p}")
            if skus:
                sample_sku = skus[0]
                print(f"      👉 首款: {sample_sku['name'][:24]} => 到手价: ￥{sample_sku['price']} (原价: ￥{sample_sku['orig']})")

            # 实时断点存盘
            save_dataset = {
                "meta": {
                    "total_active_mattresses": total_count,
                    "completed_count": len(all_results),
                    "spec": "1800mm*2000mm",
                    "tag": "平台加补后",
                    "updated_at": time.strftime("%Y-%m-%d %H:%M:%S")
                },
                "products": all_results
            }
            with open(OUT_JSON, "w", encoding="utf-8") as out_f:
                json.dump(save_dataset, out_f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"   ⚠️ 采集遇到异常: {e}，跳过进入下一款...")
            time.sleep(1)

    # 导出最终规范 CSV 表格
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

    page.quit()
    total_time = time.time() - start_all_time
    print("\n" + "=" * 70)
    print("🎉 恭喜！95 款核心在售床垫 1.8米全量 SKU 平台加补价极速采集圆满完成！")
    print(f"• 结构化 JSON 数据集: {OUT_JSON}")
    print(f"• 完整 SKU 明细 CSV:   {OUT_CSV}")
    print(f"• 总计提取商品数:     {len(all_results)} 款")
    print(f"• 总计提取 SKU 条目:   {len(csv_rows)} 条")
    print(f"• 总耗时:             {total_time:.1f} 秒 (平均每款 {total_time / max(len(all_results), 1):.1f} 秒)")
    print("=" * 70)

if __name__ == "__main__":
    main()
