# -*- coding: utf-8 -*-
"""
完整构建与升级全域横向对比交互大屏:
打通天猫市场300款 + 公司内部95款 (共395款商品，5,877个1.8m SKU)
精确注入每一个对比组件与交互逻辑
"""
import json
import re
import os
import shutil

def main():
    print("[1/5] 读取融合主数据集...")
    with open('market_company_combined_analysis.json', 'r', encoding='utf-8') as f:
        combined_db = json.load(f)

    db_json_str = json.dumps(combined_db, ensure_ascii=False)
    print(f"  - 融合主库: {len(combined_db['products'])} 款商品, {combined_db['meta']['total_skus']} 个SKU")

    print("[2/5] 读取原始 index.html 并解析模块...")
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. 注入 CSS
    extra_css = """
        /* =================== 全域横向对比与数据源切换组件样式 =================== */
        .source-filter-bar {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.95));
            border: 1px solid #3b82f6;
            border-radius: 10px;
            padding: 10px 16px;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        }
        .source-pills {
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
        }
        .source-pill-btn {
            background: rgba(15, 23, 42, 0.8);
            border: 1px solid #475569;
            color: #94a3b8;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }
        .source-pill-btn:hover {
            color: #fff;
            border-color: #60a5fa;
            background: rgba(59, 130, 246, 0.15);
        }
        .source-pill-btn.active {
            background: linear-gradient(135deg, #2563eb, #1d4ed8);
            border-color: #60a5fa;
            color: #fff;
            box-shadow: 0 0 12px rgba(37, 99, 235, 0.5);
        }
        .source-pill-btn.btn-company.active {
            background: linear-gradient(135deg, #9333ea, #7e22ce);
            border-color: #c084fc;
            box-shadow: 0 0 12px rgba(147, 51, 234, 0.5);
        }
        .source-pill-btn.btn-market.active {
            background: linear-gradient(135deg, #0284c7, #0369a1);
            border-color: #38bdf8;
            box-shadow: 0 0 12px rgba(2, 132, 199, 0.5);
        }

        /* 身份标识徽章 */
        .badge-company {
            background: linear-gradient(135deg, rgba(168, 85, 247, 0.25), rgba(126, 34, 206, 0.35));
            border: 1px solid #a855f7;
            color: #e9d5ff;
            font-size: 11px;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 4px;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }
        .badge-market {
            background: rgba(56, 189, 248, 0.15);
            border: 1px solid rgba(56, 189, 248, 0.4);
            color: #38bdf8;
            font-size: 11px;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 4px;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }
        .badge-cross {
            background: rgba(245, 158, 11, 0.18);
            border: 1px solid rgba(245, 158, 11, 0.45);
            color: #fbbf24;
            font-size: 11px;
            font-weight: 600;
            padding: 2px 8px;
            border-radius: 4px;
        }
        .product-card.is-company-card {
            border-left: 4px solid #a855f7 !important;
            background: linear-gradient(90deg, rgba(168, 85, 247, 0.04) 0%, rgba(22, 32, 50, 0.8) 100%);
        }

        /* 单品横向对比操作按钮 */
        .btn-compare-add {
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid #475569;
            color: #cbd5e1;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 12px;
            cursor: pointer;
            transition: all 0.15s;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }
        .btn-compare-add:hover {
            border-color: #38bdf8;
            color: #fff;
            background: rgba(56, 189, 248, 0.15);
        }
        .btn-compare-add.active {
            background: rgba(16, 185, 129, 0.2);
            border-color: #10b981;
            color: #34d399;
            font-weight: 700;
        }

        /* 底部常驻横向对比浮动栏 */
        .compare-dock-container {
            position: fixed;
            bottom: 24px;
            right: 24px;
            background: linear-gradient(135deg, rgba(17, 24, 39, 0.98), rgba(30, 41, 59, 0.98));
            border: 2px solid #38bdf8;
            border-radius: 12px;
            padding: 12px 18px;
            z-index: 9998;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.6);
            backdrop-filter: blur(10px);
            display: flex;
            align-items: center;
            gap: 16px;
            max-width: 90vw;
            animation: slideUp 0.3s ease;
        }
        @keyframes slideUp {
            from { transform: translateY(50px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        .dock-items-wrapper {
            display: flex;
            gap: 8px;
            align-items: center;
            max-width: 580px;
            overflow-x: auto;
            padding: 4px 0;
        }
        .dock-pill {
            background: rgba(15, 23, 42, 0.9);
            border: 1px solid #475569;
            border-radius: 6px;
            padding: 4px 8px;
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 12px;
            color: #e2e8f0;
            white-space: nowrap;
        }
        .dock-pill-del {
            cursor: pointer;
            color: #94a3b8;
            font-weight: bold;
            font-size: 14px;
        }
        .dock-pill-del:hover { color: #ef4444; }

        /* 左右并列深度横向对比模态框 */
        .side-modal-overlay {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0, 0, 0, 0.85);
            backdrop-filter: blur(6px);
            z-index: 10000;
            display: none;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .side-modal-box {
            background: #0f172a;
            border: 2px solid #38bdf8;
            border-radius: 14px;
            width: 95%;
            max-width: 1400px;
            height: 90vh;
            display: flex;
            flex-direction: column;
            box-shadow: 0 25px 60px rgba(0, 0, 0, 0.8);
            overflow: hidden;
        }
        .side-modal-header {
            padding: 16px 24px;
            background: #1e293b;
            border-bottom: 1px solid #334155;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .side-modal-body {
            flex: 1;
            overflow: auto;
            padding: 20px;
        }
        .side-compare-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }
        .side-compare-table th, .side-compare-table td {
            border: 1px solid #334155;
            padding: 12px 14px;
            vertical-align: top;
        }
        .side-compare-table th.side-prop-col {
            width: 160px;
            background: #1e293b;
            color: #94a3b8;
            font-weight: 700;
            position: sticky;
            left: 0;
            z-index: 2;
        }
        .side-compare-table td.side-prod-col {
            min-width: 260px;
            max-width: 320px;
            background: rgba(15, 23, 42, 0.6);
        }
        .side-compare-table td.side-prod-col.is-comp {
            background: rgba(168, 85, 247, 0.05);
            border-top: 3px solid #a855f7;
        }
        .side-compare-table td.side-prod-col.is-mkt {
            background: rgba(56, 189, 248, 0.05);
            border-top: 3px solid #38bdf8;
        }

        /* 雷达跨库选择按钮 */
        .radar-scope-btn {
            background: #1e293b;
            border: 1px solid #475569;
            color: #cbd5e1;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
            cursor: pointer;
            transition: all 0.15s;
        }
        .radar-scope-btn:hover { border-color: #f87171; color: #fff; }
        .radar-scope-btn.active {
            background: #ef4444;
            border-color: #ef4444;
            color: #fff;
            font-weight: bold;
        }

        .sku-radar-hit-badge {
            display: inline-block;
            background: rgba(16, 185, 129, 0.2);
            border: 1px solid #10b981;
            color: #34d399;
            padding: 1px 6px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            margin-left: 6px;
        }
    """
    if ".source-filter-bar" not in html:
        html = html.replace("</style>", extra_css + "\n    </style>")

    # 2. 注入全局数据源切换栏 (HTML)
    source_bar_html = """
    <!-- 🌐 对比数据源全局切换栏 -->
    <div class="source-filter-bar">
        <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
            <span style="font-size: 13px; font-weight: 700; color: #cbd5e1; display: flex; align-items: center; gap: 6px;">
                <span>🌐 全局数据源视角:</span>
            </span>
            <div class="source-pills">
                <button class="source-pill-btn active" id="src-btn-all" onclick="setSourceFilter('all')">
                    <span>🌟 全部床垫 (395款 / 5,877 SKU)</span>
                </button>
                <button class="source-pill-btn btn-company" id="src-btn-comp" onclick="setSourceFilter('company')">
                    <span>🏢 仅看公司内部产品 (95款 / 1,283 SKU)</span>
                </button>
                <button class="source-pill-btn btn-market" id="src-btn-mkt" onclick="setSourceFilter('market')">
                    <span>🌐 仅看天猫大盘竞品 (300款 / 4,594 SKU)</span>
                </button>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 10px;">
            <button class="btn btn-sm" onclick="openSideBySideModal()" style="background: linear-gradient(135deg, #0284c7, #2563eb); border: none; color: #fff; font-weight: 700; padding: 6px 14px; border-radius: 6px; box-shadow: 0 0 10px rgba(56,189,248,0.4); cursor: pointer;">
                <span>⚖️ 打开横向对比工作台 (<span id="dock-btn-badge">0</span>/5)</span>
            </button>
        </div>
    </div>
    """
    if 'class="source-filter-bar"' not in html:
        html = html.replace('<div class="nav-tabs">', source_bar_html + '\n    <div class="nav-tabs">')

    # 3. 注入雷达控制面板 (HTML)
    radar_box_html = """
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
                    <!-- 跨库对标范围选择 -->
                    <div style="display: flex; gap: 4px; align-items: center; margin-left: 8px;">
                        <span style="font-size: 11px; color: var(--text-dim);">对标范围:</span>
                        <button class="radar-scope-btn active" id="radar-scope-all" onclick="setRadarScope('all')">跨库395款</button>
                        <button class="radar-scope-btn" id="radar-scope-mkt" onclick="setRadarScope('market')">仅大盘竞品</button>
                        <button class="radar-scope-btn" id="radar-scope-comp" onclick="setRadarScope('company')">仅公司自营</button>
                    </div>
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
                    <span>⚡ 跨库实时对标状态：已锁定同频检索条件，下方列表即刻呈现符合条件的竞品款式！</span>
                </div>
                <div style="display: flex; gap: 8px;">
                    <button class="btn btn-sm btn-outline" onclick="copyRadarFilteredLinks()">📋 复制对标商品直达链接</button>
                </div>
            </div>
        </div>
    """
    if 'id="sku-anchor-radar"' not in html:
        target_marker = '<div id="tab-custom" class="tab-content active">'
        if target_marker in html:
            html = html.replace(target_marker, target_marker + '\n' + radar_box_html)

    # 4. 升级 Tab 5 预设对比按钮栏
    new_preset_block = """        <!-- 快捷场景横向对比模版 (支持跨库) -->
        <div class="compare-preset-bar">
            <div class="preset-title">⚡ 快捷场景横向对比模版:</div>
            <button class="preset-btn" onclick="applyComparePreset('company_vs_market')" style="border-color: rgba(168, 85, 247, 0.7); color: #c084fc; background: rgba(168, 85, 247, 0.12); font-weight: 700;">🏢 公司自营 95 款 vs 🌐 天猫大盘 300 款全景 PK</button>
            <button class="preset-btn" onclick="applyComparePreset('waist_battle')" style="border-color: rgba(56, 189, 248, 0.6); color: #38bdf8;">💰 公司主力(800-1500元) vs 头部大牌同价位款</button>
            <button class="preset-btn" onclick="applyComparePreset('material_duel')">🌿 公司黄麻/0胶 vs 大盘黄麻/0胶竞品</button>
            <button class="preset-btn" onclick="applyComparePreset('price_levels')">💰 四阶价格带PK (低端/中端/高端/高奢)</button>
            <button class="preset-btn" onclick="applyComparePreset('height_tiers')">📏 厚度规格PK (薄垫≤10cm vs 主流 vs 加厚)</button>
            <button class="preset-btn" onclick="applyComparePreset('brands')">🏬 头部大牌PK (喜临门 vs 蓝盒子 vs 源氏木语 vs 梦百合)</button>
            <button class="preset-btn" onclick="applyComparePreset('favorites')" style="border-color: rgba(251, 191, 36, 0.6); color: #fbbf24; background: rgba(251, 191, 36, 0.08);">⭐ 已收藏商品专属PK</button>
            <button class="preset-btn" onclick="applyComparePreset('custom_init')">🔄 恢复默认对比</button>
        </div>"""
    
    html = re.sub(r'<!-- 快捷场景预设栏 -->\s*<div class="compare-preset-bar">.*?</div>', new_preset_block, html, flags=re.DOTALL)

    # 5. 升级 Tab 5 条件卡片输入项：增加数据来源选择
    old_cg_rank = """                        <!-- 排名区间 -->
                        <div class="group-field-row">
                            <span class="group-field-lbl">排名范围:</span>"""
    new_cg_source = """                        <!-- 数据来源选择 -->
                        <div class="group-field-row">
                            <span class="group-field-lbl">数据来源:</span>
                            <select id="cg-source-${g.id}" class="group-input-box" style="flex: 1; padding: 4px 6px; font-size: 11px; background: #0f172a; border-color: #475569;" onchange="onGroupConditionChange(${g.id})">
                                <option value="all" ${(!g.source || g.source === 'all') ? 'selected' : ''}>🌟 全部床垫 (跨库395款)</option>
                                <option value="company" ${g.source === 'company' ? 'selected' : ''}>🏢 仅限公司自营 (95款)</option>
                                <option value="market" ${g.source === 'market' ? 'selected' : ''}>🌐 仅限天猫大盘 (300款)</option>
                            </select>
                        </div>

                        <!-- 排名区间 -->
                        <div class="group-field-row">
                            <span class="group-field-lbl">排名范围:</span>"""
    if 'id="cg-source-${g.id}"' not in html and old_cg_rank in html:
        html = html.replace(old_cg_rank, new_cg_source)

    # 6. 升级 syncCompareInputsToData 读取 source
    old_sync = "const nameEl = document.getElementById(`cg-name-${g.id}`);"
    new_sync = """const nameEl = document.getElementById(`cg-name-${g.id}`);
                const srcEl = document.getElementById(`cg-source-${g.id}`);
                if (srcEl) g.source = srcEl.value;"""
    if "const srcEl = document.getElementById(`cg-source-${g.id}`);" not in html and old_sync in html:
        html = html.replace(old_sync, new_sync)

    # 7. 升级 runComparisonAnalysis 中按数据源过滤
    old_cg_prod_filter = "candidateProducts.forEach(p => {\n                    if (p.rank < minR || p.rank > maxR) return;"
    new_cg_prod_filter = """candidateProducts.forEach(p => {
                    if (g.source === 'company' && !p.is_company) return;
                    if (g.source === 'market' && p.is_company) return;
                    if (minR !== null && maxR !== null) {
                        if (p.rank < minR || p.rank > maxR) return;
                    }"""
    if old_cg_prod_filter in html:
        html = html.replace(old_cg_prod_filter, new_cg_prod_filter)

    # 8. 升级常驻对比栏与并列模态框 (HTML)
    dock_and_modal_html = """
    <!-- ⚖️ 底部常驻横向对比浮动栏 -->
    <div id="compare-floating-dock" class="compare-dock-container" style="display: none;">
        <div style="font-weight: 700; color: #38bdf8; font-size: 13px; display: flex; align-items: center; gap: 6px;">
            <span>⚖️ 横向对比池</span>
            <span id="dock-counter-badge" style="background: #0284c7; color: #fff; border-radius: 9999px; padding: 1px 7px; font-size: 11px;">0/5</span>
        </div>
        <div class="dock-items-wrapper" id="dock-items-list">
            <!-- 动态填充对比商品标签 -->
        </div>
        <div style="display: flex; gap: 8px; align-items: center;">
            <button class="btn btn-sm btn-outline" onclick="clearComparedProducts()" style="padding: 4px 10px; font-size: 11px;">清空</button>
            <button class="btn btn-sm" onclick="openSideBySideModal()" style="background: linear-gradient(135deg, #10b981, #059669); border: none; color: #fff; font-weight: 700; padding: 5px 14px; font-size: 12px; box-shadow: 0 0 10px rgba(16,185,129,0.4); cursor: pointer;">
                🚀 开始横向PK
            </button>
        </div>
    </div>

    <!-- ⚖️ 左右并列深度横向对比全屏模态框 -->
    <div id="side-by-side-modal" class="side-modal-overlay" onclick="if(event.target === this) closeSideBySideModal()">
        <div class="side-modal-box">
            <div class="side-modal-header">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span style="font-size: 20px;">⚖️</span>
                    <div>
                        <h2 style="font-size: 17px; font-weight: 700; color: #fff; margin: 0;">多商品左右并列深度横向对比工作台</h2>
                        <p style="font-size: 12px; color: #94a3b8; margin: 2px 0 0 0;">并列透视商品基本面、1.8米全量SKU价格阶梯、厚度区间与主图核心卖点</p>
                    </div>
                </div>
                <div style="display: flex; gap: 10px; align-items: center;">
                    <button onclick="exportSideBySideCSV()" class="btn btn-sm btn-outline" style="border-color: #38bdf8; color: #38bdf8;">📥 导出对比报告 (CSV)</button>
                    <button onclick="closeSideBySideModal()" style="background: none; border: none; font-size: 24px; color: #94a3b8; cursor: pointer; padding: 2px 8px;">✕</button>
                </div>
            </div>
            <div class="side-modal-body" id="side-modal-body-content">
                <!-- 动态表格 -->
            </div>
        </div>
    </div>
    """
    if 'id="compare-floating-dock"' not in html:
        html = html.replace('</body>', dock_and_modal_html + '\n</body>')

    # 9. 替换数据库
    print("[3/5] 写入 395 款全量数据库...")
    html = re.sub(r'const DB = \{.*?\};\s*(?:const|let|var|\n)', f'const DB = {db_json_str};\n', html, count=1, flags=re.DOTALL)

    # 10. 保存与同步
    print("[4/5] 保存 index.html 并同步...")
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"  - index.html 写入完成 ({os.path.getsize('index.html')//1024} KB)")

    backup_name = '床垫300款排名与SKU价格交互分析大屏.html'
    shutil.copyfile('index.html', backup_name)
    print(f"  - 同步更新副本: {backup_name} ({os.path.getsize(backup_name)//1024} KB)")

if __name__ == '__main__':
    main()
