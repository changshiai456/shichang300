# -*- coding: utf-8 -*-
"""
为 index.html 和 床垫300款排名与SKU价格交互分析大屏.html 注入智能同频对标雷达功能
"""
import os
import re
import shutil
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def upgrade_market_300_dashboard():
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # 1. 注入 CSS 样式
    radar_css = """
        /* 🎯 SKU 智能同频对标雷达控制面板 */
        .sku-anchor-radar-box {
            display: none;
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.98), rgba(30, 41, 59, 0.98));
            border: 2px solid #ef4444;
            border-radius: 12px;
            padding: 16px 20px;
            margin-bottom: 20px;
            box-shadow: 0 15px 45px rgba(239, 68, 68, 0.25);
            backdrop-filter: blur(10px);
            animation: fadeIn 0.3s ease;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-8px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .radar-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(239, 68, 68, 0.3);
        }
        .radar-title {
            display: flex;
            align-items: center;
            gap: 12px;
            flex-wrap: wrap;
        }
        .radar-pulse {
            display: inline-block;
            width: 10px;
            height: 10px;
            background: #ef4444;
            border-radius: 50%;
            box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7);
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
            70% { box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }
            100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
        }
        .radar-target-pill {
            background: rgba(239, 68, 68, 0.15);
            border: 1px solid rgba(239, 68, 68, 0.4);
            color: #f87171;
            padding: 3px 10px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 600;
        }
        .radar-badge {
            background: #1e293b;
            color: #38bdf8;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 12px;
        }
        .radar-close-btn {
            background: #334155;
            border: 1px solid #475569;
            color: #fff;
            padding: 5px 12px;
            border-radius: 6px;
            font-size: 12px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .radar-close-btn:hover { background: #ef4444; border-color: #ef4444; }

        .radar-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 14px;
            margin-bottom: 12px;
        }
        .radar-item {
            background: rgba(15, 23, 42, 0.7);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 10px 14px;
        }
        .radar-item-title {
            font-size: 12px;
            color: var(--text-sub);
            margin-bottom: 6px;
            font-weight: 600;
            display: flex;
            justify-content: space-between;
        }
        .delta-btn-group {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            align-items: center;
        }
        .delta-btn {
            background: #1e293b;
            border: 1px solid #334155;
            color: #cbd5e1;
            padding: 3px 9px;
            border-radius: 4px;
            font-size: 12px;
            cursor: pointer;
            transition: all 0.15s;
        }
        .delta-btn:hover { border-color: #f87171; color: #fff; }
        .delta-btn.active {
            background: #ef4444;
            border-color: #ef4444;
            color: #fff;
            font-weight: 700;
        }
        .radar-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            padding-top: 10px;
            font-size: 13px;
        }
        .sku-price-anchor-btn {
            background: rgba(239, 68, 68, 0.12);
            border: 1px solid rgba(239, 68, 68, 0.35);
            color: #f87171;
            padding: 2px 7px;
            border-radius: 4px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.15s;
            display: inline-flex;
            align-items: center;
            gap: 5px;
        }
        .sku-price-anchor-btn:hover {
            background: #ef4444;
            color: #fff;
            box-shadow: 0 0 10px rgba(239, 68, 68, 0.5);
            transform: scale(1.02);
        }
        .sku-anchor-tag {
            background: rgba(0,0,0,0.35);
            color: #fca5a5;
            font-size: 10px;
            padding: 1px 4px;
            border-radius: 3px;
        }
        .sku-price-anchor-btn:hover .sku-anchor-tag {
            background: #fff;
            color: #ef4444;
            font-weight: bold;
        }
    """

    if ".sku-anchor-radar-box" not in html:
        html = html.replace("</style>", radar_css + "\n    </style>")

    # 2. 注入雷达 HTML 控制面板（放在 tab-filter 下方）
    radar_html = """
        <!-- 🎯 SKU 智能同频对标雷达控制面板 -->
        <div id="sku-anchor-radar" class="sku-anchor-radar-box">
            <div class="radar-header">
                <div class="radar-title">
                    <span class="radar-pulse"></span>
                    <b style="color: #fff; font-size: 15px;">🎯 SKU 智能同频对标雷达</b>
                    <span class="radar-target-pill" id="radar-target-name">已锁定基准 SKU</span>
                    <span class="radar-badge" id="radar-target-shop">品牌店铺</span>
                    <span class="radar-badge" style="color: #f87171; font-weight: 700;" id="radar-target-price">基准到手价: ￥1,268.20</span>
                    <span class="radar-badge" style="color: #fbbf24;" id="radar-target-height">基准厚度: 21cm</span>
                </div>
                <button class="radar-close-btn" onclick="exitSkuAnchorMode()">✕ 退出对标模式</button>
            </div>
            <div class="radar-grid">
                <!-- 价格公差控制 (正负任意元) -->
                <div class="radar-item">
                    <div class="radar-item-title">
                        <span>💰 价格公差范围 (正负任意元)</span>
                        <span style="color: #34d399; font-weight: 700;" id="radar-price-range-lbl">￥1168.2 ~ ￥1368.2</span>
                    </div>
                    <div class="delta-btn-group">
                        <button class="delta-btn" onclick="setAnchorDelta(50)">±50元</button>
                        <button class="delta-btn active" id="delta-btn-100" onclick="setAnchorDelta(100)">±100元 (默认)</button>
                        <button class="delta-btn" onclick="setAnchorDelta(150)">±150元</button>
                        <button class="delta-btn" onclick="setAnchorDelta(200)">±200元</button>
                        <button class="delta-btn" onclick="setAnchorDelta(300)">±300元</button>
                        <div style="display: flex; align-items: center; gap: 4px; margin-left: 6px;">
                            <span style="color: var(--text-dim); font-size: 11px;">自定义±:</span>
                            <input type="number" id="radar-custom-delta" value="100" class="input-box" style="width: 70px; padding: 2px 6px; height: 26px;" oninput="onCustomDeltaInput(this.value)">
                            <span style="color: var(--text-dim); font-size: 11px;">元</span>
                        </div>
                    </div>
                </div>

                <!-- 床垫总高 (厚度) 筛选 -->
                <div class="radar-item">
                    <div class="radar-item-title">
                        <span>📐 床垫总高 (厚度) 筛选模式</span>
                        <span style="color: #fbbf24;" id="radar-height-desc">锁定本SKU厚度</span>
                    </div>
                    <div style="display: flex; flex-wrap: wrap; gap: 10px; align-items: center; font-size: 12px;">
                        <label style="cursor: pointer; display: flex; align-items: center; gap: 4px;">
                            <input type="radio" name="radar-h-mode" value="exact" checked onchange="onRadarHeightModeChange()">
                            <span>精确匹配 (<b id="radar-h-exact-val" style="color: #fbbf24;">21</b>cm)</span>
                        </label>
                        <label style="cursor: pointer; display: flex; align-items: center; gap: 4px;">
                            <input type="radio" name="radar-h-mode" value="range" onchange="onRadarHeightModeChange()">
                            <span>相近厚度 (±2cm: <span id="radar-h-near-val">19~23cm</span>)</span>
                        </label>
                        <label style="cursor: pointer; display: flex; align-items: center; gap: 4px;">
                            <input type="radio" name="radar-h-mode" value="all" onchange="onRadarHeightModeChange()">
                            <span>不限厚度</span>
                        </label>
                        <div style="display: flex; align-items: center; gap: 4px; margin-left: auto;">
                            <span style="color: var(--text-dim); font-size: 11px;">指定:</span>
                            <input type="number" id="radar-custom-height-input" value="21" class="input-box" style="width: 55px; padding: 2px 6px; height: 26px;" oninput="onCustomHeightInput(this.value)">
                            <span style="color: var(--text-dim); font-size: 11px;">cm</span>
                        </div>
                    </div>
                </div>

                <!-- 关键词联动过滤 -->
                <div class="radar-item">
                    <div class="radar-item-title">
                        <span>🔤 关键词/材质微调过滤</span>
                        <span style="color: var(--text-dim); font-size: 11px;">支持搜索同频材质/工艺</span>
                    </div>
                    <div style="display: flex; gap: 8px; align-items: center;">
                        <input type="text" id="radar-kw-input" class="input-box" style="width: 100%; padding: 3px 8px; height: 26px;" placeholder="可输入如：黄麻、乳胶、独立袋、偏硬..." oninput="onRadarKwInput(this.value)">
                        <button class="btn btn-sm btn-outline" onclick="clearRadarKw()" style="padding: 3px 8px;">清除</button>
                    </div>
                </div>
            </div>
            <div class="radar-footer">
                <div>
                    <span>⚡ 实时对标状态：已锁定同频检索条件，下方列表即刻呈现符合条件的竞品款式！</span>
                </div>
                <div style="display: flex; gap: 8px;">
                    <button class="btn btn-sm btn-outline" onclick="copyRadarFilteredLinks()">📋 复制对标商品直达链接</button>
                </div>
            </div>
        </div>
    """

    if 'id="sku-anchor-radar"' not in html:
        # 插入到 tab-filter 的起始位置
        html = html.replace('<div id="tab-filter" class="tab-content active">', '<div id="tab-filter" class="tab-content active">\n' + radar_html)

    # 3. 替换 SKU 价格为可点击对标按钮
    old_sku_price_pattern = r'<td><span class="sku-price">￥\${s\.price !== null \? s\.price : \'无标价\'}</span></td>'
    new_sku_price_btn = """<td>
        <button class="sku-price-anchor-btn" onclick="activateSkuRadar('${escapeJs(s.name)}', ${s.price}, ${s.height || 'null'}, '${escapeJs(p.shop)}', '${escapeJs(p.title)}')" title="点击以此价格自动对标同频竞品 (正负任意元 & 厚度)">
            ￥${s.price !== null ? s.price : '无标价'} <span class="sku-anchor-tag">🎯对标</span>
        </button>
    </td>"""

    html = re.sub(old_sku_price_pattern, new_sku_price_btn, html)

    # 4. 注入 JavaScript 逻辑
    radar_js = """
        // ==========================================
        // 🎯 智能同频对标雷达核心动作 (300款大盘)
        // ==========================================
        let anchorTarget = null;
        let anchorDelta = 100;
        let anchorHeightMode = 'exact';
        let anchorCustomHeight = null;
        let anchorKeyword = '';

        function escapeJs(str) {
            if (!str) return '';
            return String(str).replace(/'/g, "\\\\'").replace(/"/g, '&quot;');
        }

        function activateSkuRadar(skuName, price, height, shop, title) {
            if (price === null || isNaN(price) || price <= 0) return alert('该SKU暂无有效价格');

            anchorTarget = {
                skuName: skuName,
                price: parseFloat(price),
                height: (height !== null && !isNaN(height)) ? parseFloat(height) : null,
                shop: shop,
                title: title
            };

            anchorDelta = 100;
            anchorHeightMode = anchorTarget.height ? 'exact' : 'all';
            anchorCustomHeight = anchorTarget.height;
            anchorKeyword = '';

            document.getElementById('radar-target-name').innerText = anchorTarget.skuName;
            document.getElementById('radar-target-shop').innerText = anchorTarget.shop;
            document.getElementById('radar-target-price').innerText = `基准到手价: ￥${anchorTarget.price.toFixed(2)}`;
            document.getElementById('radar-target-height').innerText = `基准厚度: ${anchorTarget.height ? anchorTarget.height + 'cm' : '未标明'}`;

            updateRadarControlsUI();

            const radarBox = document.getElementById('sku-anchor-radar');
            if (radarBox) {
                radarBox.style.display = 'block';
                switchNav('tab-filter');
                radarBox.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }

            syncRadarToFilters();
        }

        function updateRadarControlsUI() {
            if (!anchorTarget) return;
            const minP = Math.max(0, anchorTarget.price - anchorDelta).toFixed(2);
            const maxP = (anchorTarget.price + anchorDelta).toFixed(2);
            document.getElementById('radar-price-range-lbl').innerText = `￥${minP} ~ ￥${maxP} (±${anchorDelta}元)`;
            document.getElementById('radar-custom-delta').value = anchorDelta;

            document.querySelectorAll('.delta-btn').forEach(btn => {
                const txt = btn.innerText;
                btn.classList.toggle('active', txt.includes(`±${anchorDelta}元`));
            });

            const h = anchorCustomHeight;
            document.getElementById('radar-h-exact-val').innerText = h !== null ? h : '-';
            document.getElementById('radar-h-near-val').innerText = h !== null ? `${Math.max(1, h-2)}~${h+2}cm` : '-';
            document.getElementById('radar-custom-height-input').value = h !== null ? h : '';

            const radios = document.getElementsByName('radar-h-mode');
            radios.forEach(r => {
                r.checked = (r.value === anchorHeightMode);
            });

            let hDesc = '不限厚度';
            if (anchorHeightMode === 'exact') hDesc = `锁定精确 ${h}cm`;
            else if (anchorHeightMode === 'range') hDesc = `相近厚度 ±2cm (${Math.max(1, h-2)}~${h+2}cm)`;
            document.getElementById('radar-height-desc').innerText = hDesc;

            document.getElementById('radar-kw-input').value = anchorKeyword;
        }

        function setAnchorDelta(val) {
            anchorDelta = parseFloat(val) || 100;
            updateRadarControlsUI();
            syncRadarToFilters();
        }

        function onCustomDeltaInput(val) {
            const num = parseFloat(val);
            if (!isNaN(num) && num >= 0) {
                anchorDelta = num;
                document.querySelectorAll('.delta-btn').forEach(b => b.classList.remove('active'));
                updateRadarControlsUI();
                syncRadarToFilters();
            }
        }

        function onRadarHeightModeChange() {
            const radios = document.getElementsByName('radar-h-mode');
            for (let r of radios) {
                if (r.checked) {
                    anchorHeightMode = r.value;
                    break;
                }
            }
            updateRadarControlsUI();
            syncRadarToFilters();
        }

        function onCustomHeightInput(val) {
            const num = parseFloat(val);
            if (!isNaN(num) && num > 0) {
                anchorCustomHeight = num;
                anchorHeightMode = 'exact';
                updateRadarControlsUI();
                syncRadarToFilters();
            }
        }

        function onRadarKwInput(val) {
            anchorKeyword = (val || '').trim();
            syncRadarToFilters();
        }

        function clearRadarKw() {
            anchorKeyword = '';
            document.getElementById('radar-kw-input').value = '';
            syncRadarToFilters();
        }

        function exitSkuAnchorMode() {
            anchorTarget = null;
            const radarBox = document.getElementById('sku-anchor-radar');
            if (radarBox) radarBox.style.display = 'none';

            document.getElementById('cust-min-price').value = '';
            document.getElementById('cust-max-price').value = '';
            document.getElementById('cust-min-height').value = '';
            document.getElementById('cust-max-height').value = '';
            document.getElementById('cust-keyword').value = '';
            runCustomFilter();
        }

        function syncRadarToFilters() {
            if (!anchorTarget) return;
            const minP = Math.max(0, anchorTarget.price - anchorDelta);
            const maxP = anchorTarget.price + anchorDelta;
            document.getElementById('cust-min-price').value = minP;
            document.getElementById('cust-max-price').value = maxP;

            if (anchorHeightMode === 'exact' && anchorCustomHeight !== null) {
                document.getElementById('cust-min-height').value = anchorCustomHeight;
                document.getElementById('cust-max-height').value = anchorCustomHeight;
            } else if (anchorHeightMode === 'range' && anchorCustomHeight !== null) {
                document.getElementById('cust-min-height').value = Math.max(1, anchorCustomHeight - 2);
                document.getElementById('cust-max-height').value = anchorCustomHeight + 2;
            } else {
                document.getElementById('cust-min-height').value = '';
                document.getElementById('cust-max-height').value = '';
            }

            document.getElementById('cust-keyword').value = anchorKeyword;
            runCustomFilter();
        }

        function copyRadarFilteredLinks() {
            if (!anchorTarget) return;
            const links = [];
            document.querySelectorAll('#filter-results-list .product-card').forEach(card => {
                const titleEl = card.querySelector('.product-title');
                const linkEl = card.querySelector('a[href*="detail.tmall.com"], a[href*="item.taobao.com"]');
                if (linkEl) {
                    links.push((titleEl ? titleEl.innerText.trim() : '') + ' => ' + linkEl.href);
                }
            });
            navigator.clipboard.writeText(links.join('\\n')).then(() => {
                alert(`📋 已成功复制 ${links.length} 款同频对标商品链接至剪贴板！`);
            });
        }
    """

    if "activateSkuRadar" not in html:
        html = html.replace("</script>", radar_js + "\n    </script>")

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    with open("床垫300款排名与SKU价格交互分析大屏.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("🎉 成功为 index.html 和 床垫300款排名与SKU价格交互分析大屏.html 注入智能同频对标雷达！")

if __name__ == "__main__":
    upgrade_market_300_dashboard()
