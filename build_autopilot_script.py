# -*- coding: utf-8 -*-
import json, os, sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CATALOG_FILE = os.path.join(BASE_DIR, "market_top300_products_catalog.json")
OUT_JS = os.path.join(BASE_DIR, "market_300_sku_autopilot_collector.js")

with open(CATALOG_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

targets = []
for p in data['products']:
    targets.append({
        'rank': p['rank'],
        'itemId': p['itemId'],
        'shop': p['shop'],
        'title': p['title'],
        'url': p['item_url_1800x2000']
    })

targets_json = json.dumps(targets, ensure_ascii=False, indent=2)

js_content = f"""/**
 * =========================================================================
 * 🚀 天猫市场最新 30 天 TOP 300 床垫 1.8米全量 SKU 平台加补到手价【全自动巡航采集器】
 * =========================================================================
 * 
 * 使用方法：
 * 1. 在天猫任意已登录的商品页面按 F12 打开控制台 (Console)；
 * 2. 粘贴本脚本全部代码并回车；
 * 3. 浏览器将自动巡航采集全部 300 款商品在 1800mm*2000mm 下的所有 SKU 到手价与原价；
 * 4. 采集完毕后自动下载 JSON 与 CSV 文件！
 */
(async function runMarket300AutoPilotSkuCollector() {{
    const STORAGE_KEY = 'MARKET_300_SKU_TASK_DATA';
    const ALL_TARGETS = {targets_json};

    let taskState = null;
    try {{
        const raw = sessionStorage.getItem(STORAGE_KEY);
        if (raw) taskState = JSON.parse(raw);
    }} catch (e) {{}}

    if (!taskState || !taskState.running) {{
        const ok = confirm(`🚀 准备启动天猫最新 30 天市场 TOP 300 床垫 1.8米全量 SKU 自动巡航采集？\\n• 共计目标：${{ALL_TARGETS.length}} 款市场前 300 强床垫\\n• 规格锁定：1800mm*2000mm\\n• 采集项：每个 SKU 款式名称、优惠前原价、平台加补后到手价\\n\\n点击【确定】立即开始自动巡航采集！`);
        if (!ok) return;

        taskState = {{
            running: true,
            currentIndex: 0,
            results: []
        }};
        sessionStorage.setItem(STORAGE_KEY, JSON.stringify(taskState));
    }}

    const sleep = ms => new Promise(r => setTimeout(r, ms));
    const curIdx = taskState.currentIndex;
    const total = ALL_TARGETS.length;

    let hud = document.getElementById('market-300-autopilot-hud');
    if (hud) hud.remove();
    hud = document.createElement('div');
    hud.id = 'market-300-autopilot-hud';
    hud.style.cssText = `
        position: fixed; top: 20px; right: 20px; z-index: 999999999;
        background: rgba(15, 23, 42, 0.95); color: #fff; padding: 18px 22px;
        border-radius: 12px; box-shadow: 0 15px 45px rgba(0,0,0,0.7);
        border: 1px solid rgba(56, 189, 248, 0.7); font-family: sans-serif;
        min-width: 380px; backdrop-filter: blur(10px);
    `;
    hud.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <b style="font-size: 15px; color: #38bdf8;">🏷️ 市场300款 1.8m SKU 巡航采集</b>
            <span style="font-size: 13px; color: #34d399; font-weight: bold;">${{curIdx + 1}} / ${{total}}</span>
        </div>
        <div style="height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px; overflow: hidden; margin-bottom: 10px;">
            <div style="width: ${{Math.round(((curIdx + 1) / total) * 100)}}%; height: 100%; background: linear-gradient(90deg, #38bdf8, #34d399);"></div>
        </div>
        <div style="font-size: 12px; color: #cbd5e1; margin-bottom: 4px;" id="hud-status">正在分析当前商品 SKU 与到手价...</div>
        <div style="font-size: 11px; color: #94a3b8; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">#${{ALL_TARGETS[curIdx] ? ALL_TARGETS[curIdx].rank : ''}} [${{ALL_TARGETS[curIdx] ? ALL_TARGETS[curIdx].shop : ''}}] ${{ALL_TARGETS[curIdx] ? ALL_TARGETS[curIdx].title : ''}}</div>
        <div style="display: flex; gap: 8px; margin-top: 10px;">
            <button id="btn-stop-mkt-task" style="background: #ef4444; color: #fff; border: none; padding: 5px 12px; border-radius: 4px; font-size: 11px; cursor: pointer;">⏹️ 暂停任务并导出已有数据</button>
        </div>
    `;
    document.body.appendChild(hud);

    function readPagePrices() {{
        let bannerPrice = null;
        let origPrice = null;
        let isStart = false;

        const allSpans = Array.from(document.querySelectorAll('span, div, b, strong, em, p'));
        for (const el of allSpans) {{
            if (el.children.length === 0 && el.innerText) {{
                const t = el.innerText.trim();
                if (t.includes('平台加补后') || t.includes('补贴到手') || t.includes('券后') || t.includes('到手价')) {{
                    let p = el.parentElement;
                    for (let k = 0; k < 5 && p; k++) {{
                        const m = p.innerText.match(/(?:平台加补后|补贴到手价|预估到手价|券后到手价|券后价|到手价)[^\\d]*¥?\\s*([\\d\\.]+)\\s*(起)?/);
                        if (m) {{
                            bannerPrice = parseFloat(m[1]);
                            if (m[2] === '起' || p.innerText.includes('起')) isStart = true;
                            break;
                        }}
                        p = p.parentElement;
                    }}
                }}
                if (t.includes('优惠前') || t.includes('原价') || t.includes('吊牌价')) {{
                    let p = el.parentElement;
                    for (let k = 0; k < 5 && p; k++) {{
                        const m = p.innerText.match(/(?:优惠前|原价|吊牌价)[^\\d]*¥?\\s*([\\d\\.]+)/);
                        if (m) {{
                            origPrice = parseFloat(m[1]);
                            break;
                        }}
                        p = p.parentElement;
                    }}
                }}
            }}
            if (bannerPrice && origPrice) break;
        }}

        if (!bannerPrice) {{
            const bigPrice = document.querySelector('[class*="bannerPrice"], [class*="priceText"], [class*="highlightPrice"], [class*="PromotionPrice"], [class*="promoPrice"]');
            if (bigPrice && bigPrice.innerText) {{
                const m = bigPrice.innerText.match(/([\\d\\.]+)/);
                if (m) bannerPrice = parseFloat(m[1]);
            }}
        }}

        return {{ bannerPrice, origPrice, isStart }};
    }}

    function finishAndDownload(results) {{
        const jsonStr = JSON.stringify({{
            meta: {{
                title: '天猫市场TOP300床垫1800mm*2000mm全量SKU到手价数据库',
                total_target_count: ALL_TARGETS.length,
                completed_count: results.length,
                spec: '1800mm*2000mm',
                tag: '平台加补后',
                updated_at: new Date().toISOString()
            }},
            products: results
        }}, null, 2);

        // 下载 JSON
        const blobJson = new Blob([jsonStr], {{ type: 'application/json;charset=utf-8;' }});
        const urlJson = URL.createObjectURL(blobJson);
        const aJson = document.createElement('a');
        aJson.href = urlJson;
        aJson.download = `market_mattress_300_18m_skus_${{new Date().toISOString().slice(0, 10)}}.json`;
        document.body.appendChild(aJson);
        aJson.click();
        document.body.removeChild(aJson);
        URL.revokeObjectURL(urlJson);

        // 下载 CSV
        const csvRows = ['排名,商品ID,所属店铺,商品标题,1.8米起步最低价(元),SKU款型名称,平台加补后到手价(元),优惠前原价(元),价格标签,1.8米直达链接'];
        for (const item of results) {{
            for (const s of (item.skus || [])) {{
                const row = [
                    item.rank,
                    item.itemId,
                    `"${{(item.shop || '').replace(/"/g, '""')}}"`,
                    `"${{(item.title || '').replace(/"/g, '""')}}"`,
                    item.min_price || '',
                    `"${{(s.name || '').replace(/"/g, '""')}}"`,
                    s.price || '',
                    s.orig || '',
                    `"${{(s.tag || '平台加补后').replace(/"/g, '""')}}"`,
                    `"${{(item.link || '').replace(/"/g, '""')}}"`
                ];
                csvRows.push(row.join(','));
            }}
        }}
        const blobCsv = new Blob([csvRows.join('\\r\\n')], {{ type: 'text/csv;charset=utf-8;' }});
        const urlCsv = URL.createObjectURL(blobCsv);
        const aCsv = document.createElement('a');
        aCsv.href = urlCsv;
        aCsv.download = `market_mattress_300_18m_skus_${{new Date().toISOString().slice(0, 10)}}.csv`;
        document.body.appendChild(aCsv);
        aCsv.click();
        document.body.removeChild(aCsv);
        URL.revokeObjectURL(urlCsv);

        alert(`🎉 恭喜！已完成采集，累计提取 ${{results.length}} 款床垫全量 1.8m SKU！\\n数据已自动下载为 JSON 与 CSV 文件！`);
    }}

    document.getElementById('btn-stop-mkt-task').onclick = () => {{
        finishAndDownload(taskState.results);
        sessionStorage.removeItem(STORAGE_KEY);
        hud.remove();
    }};

    await sleep(1500);

    const currentTarget = ALL_TARGETS[curIdx];
    
    // 锁定 1800mm*2000mm 尺寸
    const allGroups = Array.from(document.querySelectorAll('div[class*="skuItem--"], [class*="sku-item"], [class*="propItem"]'));
    let sizeGroup = null;
    let colorGroup = null;
    for (const g of allGroups) {{
        const header = (g.innerText || '').slice(0, 40);
        if (header.includes('尺寸') || header.includes('规格') || header.includes('长*宽')) {{
            sizeGroup = g;
        }} else if (header.includes('颜色分类') || header.includes('款式') || (!header.includes('尺寸') && !header.includes('规格') && !header.includes('1800'))) {{
            if (!colorGroup) colorGroup = g;
        }}
    }}

    if (sizeGroup) {{
        const sizeBtns = Array.from(sizeGroup.querySelectorAll('div[class*="valueItem--"], button, [role="radio"]'));
        const btn18m = sizeBtns.find(b => {{
            const txt = (b.innerText || '').toLowerCase();
            return (txt.includes('1800') && txt.includes('2000')) ||
                   (txt.includes('1.8') && (txt.includes('2.0') || txt.includes('2米') || txt.includes('床') || txt.includes('双人'))) ||
                   (txt.includes('180') && txt.includes('200'));
        }});
        if (btn18m) {{
            const cls = btn18m.className || '';
            const isSelected = cls.includes('isSelected--') || cls.includes('selected') || btn18m.getAttribute('aria-checked') === 'true';
            if (!isSelected && !cls.includes('isDisabled--')) {{
                btn18m.click();
                await sleep(100);
            }}
        }}
    }}

    const initialPrice = readPagePrices();
    const skus = [];

    if (colorGroup) {{
        const allValueItems = Array.from(colorGroup.querySelectorAll('div[class*="valueItem--"], button, [role="radio"]'));
        const validItems = allValueItems.filter(el => {{
            const cls = el.className || '';
            if (cls.includes('isDisabled--') || el.hasAttribute('disabled')) return false;
            const txt = (el.innerText || '').trim();
            if (txt.includes('*') || txt.includes('mm') || txt.includes('米') || txt.includes('1800') || txt.includes('1500') || txt.includes('1200') || txt.includes('2000*2200')) return false;
            if (txt.includes('系列：') || txt.includes('系列:') || txt.includes('切换大图') || txt.includes('更多') || txt.includes('加入购物车') || txt.includes('立即购买')) return false;
            if (txt.length < 2) return false;
            return true;
        }});

        for (const item of validItems) {{
            const skuName = (item.innerText || '').replace(/\\s+/g, ' ').trim();
            try {{
                item.click();
                await sleep(80);
            }} catch (e) {{}}
            const curP = readPagePrices();
            skus.push({{
                name: skuName,
                price: curP.bannerPrice || initialPrice.bannerPrice,
                orig: curP.origPrice || initialPrice.origPrice,
                isStart: curP.isStart,
                tag: '平台加补后'
            }});
        }}
    }}

    if (skus.length === 0 && initialPrice.bannerPrice) {{
        skus.push({{
            name: '1800mm*2000mm 标准配置款',
            price: initialPrice.bannerPrice,
            orig: initialPrice.origPrice,
            isStart: initialPrice.isStart,
            tag: '平台加补后'
        }});
    }}

    const validP = skus.map(s => s.price).filter(p => typeof p === 'number' && !isNaN(p) && p > 0);
    const minPrice = validP.length > 0 ? Math.min(...validP) : (initialPrice.bannerPrice || null);
    const maxPrice = validP.length > 0 ? Math.max(...validP) : (initialPrice.bannerPrice || null);
    validP.sort((a, b) => a - b);
    const medianPrice = validP.length > 0 ? validP[Math.floor(validP.length / 2)] : minPrice;
    const meanPrice = validP.length > 0 ? parseFloat((validP.reduce((a, b) => a + b, 0) / validP.length).toFixed(2)) : minPrice;

    const itemRecord = {{
        rank: currentTarget.rank,
        itemId: currentTarget.itemId,
        shop: currentTarget.shop,
        title: currentTarget.title,
        link: `https://detail.tmall.com/item.htm?b_s_f=sycm&b_spm=a21ag.29085015&id=${{currentTarget.itemId}}`,
        min_price: minPrice,
        max_price: maxPrice,
        median_price: medianPrice,
        mean_price: meanPrice,
        sku_count: skus.length,
        skus: skus
    }};

    taskState.results.push(itemRecord);
    console.log(`✅ [${{curIdx + 1}}/${{total}}] 采集完成:`, itemRecord);

    if (curIdx + 1 >= total) {{
        finishAndDownload(taskState.results);
        sessionStorage.removeItem(STORAGE_KEY);
        hud.remove();
        return;
    }}

    taskState.currentIndex = curIdx + 1;
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(taskState));

    const nextItem = ALL_TARGETS[taskState.currentIndex];
    const nextUrl = nextItem.url;
    document.getElementById('hud-status').innerText = `准备跳转第 ${{curIdx + 2}}/${{total}} 款: #${{nextItem.rank}} ${{nextItem.title.slice(0, 16)}}...`;
    
    await sleep(600);
    window.location.href = nextUrl;
}})();
"""

with open(OUT_JS, 'w', encoding='utf-8') as f:
    f.write(js_content)

print(f"🎉 成功生成 market_300_sku_autopilot_collector.js！包含 {len(targets)} 款商品")
