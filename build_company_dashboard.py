# -*- coding: utf-8 -*-
"""
生成公司旗下 95 款床垫全量 1.8m SKU 与主图视觉交互分析大屏
"""
import os
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
import json

BASE_DIR = os.path.abspath(".")
MASTER_JSON = os.path.join(BASE_DIR, "company_mattress_full_integrated_analysis.json")
OUT_HTML = os.path.join(BASE_DIR, "公司旗下床垫95款全量SKU与主图分析交互大屏.html")

def build_dashboard():
    with open(MASTER_JSON, "r", encoding="utf-8") as f:
        master_data = json.load(f)

    db_json_str = json.dumps(master_data, ensure_ascii=False)

    html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>公司旗下床垫95款1.8米全量SKU到手价与主图视觉深度统计分析大屏</title>
    <style>
        :root {{
            --bg: #090d16;
            --surface: #111827;
            --surface-card: #162032;
            --surface-hover: #1e293b;
            --border: #2d3748;
            --border-highlight: #ef4444;
            --primary: #3b82f6;
            --primary-light: rgba(59, 130, 246, 0.15);
            --danger: #ef4444;
            --danger-light: rgba(239, 68, 68, 0.15);
            --warning: #f59e0b;
            --warning-light: rgba(245, 158, 11, 0.15);
            --success: #10b981;
            --success-light: rgba(16, 185, 129, 0.15);
            --text-main: #f8fafc;
            --text-sub: #94a3b8;
            --text-dim: #64748b;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Microsoft YaHei", sans-serif;
            background-color: var(--bg);
            color: var(--text-main);
            line-height: 1.5;
            padding: 20px 24px;
        }}

        /* 顶部导航与总览 */
        .app-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
            padding-bottom: 16px;
            margin-bottom: 20px;
        }}
        .header-title h1 {{ font-size: 22px; font-weight: 700; color: #fff; display: flex; align-items: center; gap: 10px; }}
        .header-title p {{ font-size: 13px; color: var(--text-sub); margin-top: 4px; }}
        .header-stats {{
            display: flex;
            gap: 12px;
        }}
        .stat-badge {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 8px 14px;
            text-align: right;
        }}
        .stat-badge .num {{ font-size: 16px; font-weight: 700; color: #f87171; }}
        .stat-badge .lbl {{ font-size: 11px; color: var(--text-sub); }}

        /* Tab 导航 */
        .nav-tabs {{
            display: flex;
            gap: 8px;
            border-bottom: 1px solid var(--border);
            margin-bottom: 20px;
            overflow-x: auto;
        }}
        .tab-btn {{
            background: none;
            border: none;
            color: var(--text-sub);
            padding: 12px 18px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 8px;
            white-space: nowrap;
        }}
        .tab-btn:hover {{ color: #fff; }}
        .tab-btn.active {{
            color: #f87171;
            border-bottom-color: #f87171;
            background: var(--danger-light);
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
        }}

        /* Tab 内容区 */
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}

        /* 筛选面板 */
        .filter-panel {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        .filter-row {{
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 16px;
            margin-bottom: 14px;
        }}
        .filter-row:last-child {{ margin-bottom: 0; }}
        .filter-label {{
            font-size: 13px;
            font-weight: 600;
            color: var(--text-sub);
            min-width: 80px;
        }}
        .filter-input {{
            background: var(--bg);
            border: 1px solid var(--border);
            color: #fff;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 13px;
            outline: none;
        }}
        .filter-input:focus {{ border-color: #f87171; }}
        .pill-group {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }}
        .pill {{
            background: var(--surface-card);
            border: 1px solid var(--border);
            color: var(--text-sub);
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 12px;
            cursor: pointer;
            transition: all 0.15s;
            user-select: none;
        }}
        .pill:hover {{ border-color: #64748b; color: #fff; }}
        .pill.active {{
            background: #ef4444;
            border-color: #ef4444;
            color: #fff;
            font-weight: 600;
        }}

        /* KPI 汇总卡片 */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 14px;
            margin-bottom: 20px;
        }}
        .kpi-card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 14px 16px;
        }}
        .kpi-card .val {{ font-size: 22px; font-weight: 700; color: #fff; }}
        .kpi-card .val.red {{ color: #f87171; }}
        .kpi-card .val.blue {{ color: #60a5fa; }}
        .kpi-card .val.green {{ color: #34d399; }}
        .kpi-card .val.amber {{ color: #fbbf24; }}
        .kpi-card .lbl {{ font-size: 12px; color: var(--text-sub); margin-top: 2px; }}

        /* 数据表格与卡片 */
        .table-wrap {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            overflow: hidden;
            margin-bottom: 25px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }}
        th {{
            background: #1e293b;
            color: #cbd5e1;
            padding: 12px 14px;
            text-align: left;
            font-weight: 600;
            border-bottom: 1px solid var(--border);
            white-space: nowrap;
        }}
        td {{
            padding: 12px 14px;
            border-bottom: 1px solid #1e293b;
            color: #e2e8f0;
            vertical-align: middle;
        }}
        tr:hover td {{ background: var(--surface-hover); }}

        .rank-badge {{
            display: inline-block;
            width: 28px;
            height: 28px;
            line-height: 28px;
            text-align: center;
            border-radius: 6px;
            font-weight: 700;
            font-size: 12px;
            background: #334155;
            color: #fff;
        }}
        .rank-1 {{ background: linear-gradient(135deg, #f59e0b, #d97706); color: #fff; }}
        .rank-2 {{ background: linear-gradient(135deg, #94a3b8, #64748b); color: #fff; }}
        .rank-3 {{ background: linear-gradient(135deg, #b45309, #78350f); color: #fff; }}

        .shop-pill {{
            background: #1e293b;
            color: #38bdf8;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
            white-space: nowrap;
        }}
        .price-hl {{
            font-weight: 700;
            font-size: 15px;
            color: #f87171;
        }}
        .sku-expand-btn {{
            background: #1e293b;
            border: 1px solid #334155;
            color: #94a3b8;
            padding: 4px 10px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 11px;
            transition: all 0.2s;
        }}
        .sku-expand-btn:hover {{
            background: #ef4444;
            border-color: #ef4444;
            color: #fff;
        }}

        /* SKU 展开面板 */
        .sku-drawer {{
            display: none;
            background: #0f172a;
            padding: 14px 18px;
            border-radius: 8px;
            margin-top: 10px;
            border-left: 3px solid #ef4444;
        }}
        .sku-drawer.open {{ display: block; }}
        .sku-table {{
            width: 100%;
            margin-top: 8px;
            border-collapse: collapse;
            font-size: 12px;
        }}
        .sku-table th {{ background: #1e293b; padding: 6px 10px; }}
        .sku-table td {{ padding: 6px 10px; border-bottom: 1px solid #1e293b; }}

        /* 主图悬浮展示 */
        .thumb-img {{
            width: 48px;
            height: 48px;
            object-fit: cover;
            border-radius: 6px;
            cursor: pointer;
            border: 1px solid #334155;
            transition: transform 0.2s;
        }}
        .thumb-img:hover {{ transform: scale(1.15); border-color: #ef4444; }}

        /* 模态图片预览框 */
        #img-modal {{
            display: none;
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.85);
            z-index: 999999;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }}
        #img-modal.open {{ display: flex; }}
        #modal-img-container {{
            max-width: 90%;
            max-height: 90%;
            background: #111827;
            padding: 16px;
            border-radius: 12px;
            display: flex;
            gap: 20px;
            box-shadow: 0 25px 60px rgba(0,0,0,0.9);
            border: 1px solid #334155;
        }}
        #modal-img {{
            max-width: 450px;
            max-height: 450px;
            object-fit: contain;
            border-radius: 8px;
        }}
        #modal-info {{
            max-width: 400px;
            overflow-y: auto;
            color: #cbd5e1;
            font-size: 13px;
        }}

        /* 标签与徽章 */
        .tag {{
            display: inline-block;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 11px;
            margin-right: 4px;
            margin-bottom: 4px;
        }}
        .tag-mat {{ background: rgba(59, 130, 246, 0.2); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3); }}
        .tag-mkt {{ background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }}
        
        .progress-bar {{
            height: 8px;
            background: #1e293b;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 4px;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #ef4444, #f97316);
        }}
    </style>
</head>
<body>

    <!-- 顶部总览 -->
    <div class="app-header">
        <div class="header-title">
            <h1>🏷️ 公司旗下床垫 95 款 1.8米全量 SKU 与主图深度分析大屏</h1>
            <p>规格限定: 1800mm*2000mm (sku_properties=21433:50753460) | 核心指标: 平台加补后到手价 | 数据源: 生意参谋+天猫详情实时采集+RapidOCR</p>
        </div>
        <div class="header-stats">
            <div class="stat-badge">
                <div class="num" id="stat-total-prod">95</div>
                <div class="lbl">核心在售床垫</div>
            </div>
            <div class="stat-badge">
                <div class="num" id="stat-total-sku">1,283</div>
                <div class="lbl">1.8m SKU配置款</div>
            </div>
            <div class="stat-badge">
                <div class="num" id="stat-median-price">￥1,268.2</div>
                <div class="lbl">1.8m 到手价中位数</div>
            </div>
        </div>
    </div>

    <!-- 6大维度 Tab 导航 -->
    <div class="nav-tabs">
        <button class="tab-btn active" onclick="switchTab(0)">🎯 1. 自定义价格段与SKU检索</button>
        <button class="tab-btn" onclick="switchTab(1)">📊 2. 按价格带归类透视</button>
        <button class="tab-btn" onclick="switchTab(2)">🏆 3. 按排名梯队深度归类</button>
        <button class="tab-btn" onclick="switchTab(3)">🏬 4. 按店铺矩阵归类</button>
        <button class="tab-btn" onclick="switchTab(4)">⚖️ 5. 多维度多组横向对比</button>
        <button class="tab-btn" onclick="switchTab(5)">🖼️ 6. 主图视觉卖点与到手价透视</button>
    </div>

    <!-- ========================================== -->
    <!-- TAB 1: 自定义价格段与 SKU 检索 -->
    <!-- ========================================== -->
    <div class="tab-content active" id="tab-0">
        <!-- 筛选器 -->
        <div class="filter-panel">
            <div class="filter-row">
                <div class="filter-label">1.8m加补价</div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <input type="number" id="filter-pmin" class="filter-input" style="width: 90px;" placeholder="最低价" value="0">
                    <span style="color: var(--text-dim);">-</span>
                    <input type="number" id="filter-pmax" class="filter-input" style="width: 90px;" placeholder="最高价" value="3000">
                    <button class="sku-expand-btn" onclick="applyTab1Filter()">🔍 筛选</button>
                    <button class="sku-expand-btn" onclick="resetTab1Filter()">重置</button>
                </div>
                <div class="filter-label" style="margin-left: 20px;">关键词搜索</div>
                <input type="text" id="filter-kw" class="filter-input" style="width: 220px;" placeholder="搜索款式、材质、店铺、标题..." oninput="applyTab1Filter()">
            </div>
            <div class="filter-row">
                <div class="filter-label">核心店铺</div>
                <div class="pill-group" id="shop-pills"></div>
            </div>
            <div class="filter-row">
                <div class="filter-label">材质与特性</div>
                <div class="pill-group" id="mat-pills">
                    <div class="pill" onclick="toggleMatPill(this, '黄麻')">黄麻</div>
                    <div class="pill" onclick="toggleMatPill(this, '乳胶')">乳胶</div>
                    <div class="pill" onclick="toggleMatPill(this, '弹簧')">独立袋弹簧</div>
                    <div class="pill" onclick="toggleMatPill(this, '全拆')">全拆洗</div>
                    <div class="pill" onclick="toggleMatPill(this, '双面')">双面睡感</div>
                    <div class="pill" onclick="toggleMatPill(this, '护脊')">护脊加硬</div>
                    <div class="pill" onclick="toggleMatPill(this, '薄')">薄垫/榻榻米</div>
                    <div class="pill" onclick="toggleMatPill(this, '儿童')">儿童/青少年</div>
                    <div class="pill" onclick="toggleMatPill(this, '宿舍')">学生宿舍</div>
                    <div class="pill" onclick="toggleMatPill(this, '酒店')">五星酒店款</div>
                </div>
            </div>
        </div>

        <!-- KPI 动态统计栏 -->
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="val blue" id="kpi-f-prod">95</div>
                <div class="lbl">符合条件商品数</div>
            </div>
            <div class="kpi-card">
                <div class="val amber" id="kpi-f-sku">1,283</div>
                <div class="lbl">包含款式配置 (SKU)</div>
            </div>
            <div class="kpi-card">
                <div class="val red" id="kpi-f-min">￥174.25</div>
                <div class="lbl">区间最低起步价</div>
            </div>
            <div class="kpi-card">
                <div class="val red" id="kpi-f-median">￥1,268.20</div>
                <div class="lbl">加补到手价中位数</div>
            </div>
            <div class="kpi-card">
                <div class="val green" id="kpi-f-gmv">￥1,175,692</div>
                <div class="lbl">对应昨日支付金额</div>
            </div>
        </div>

        <!-- 商品与 SKU 表格 -->
        <div class="table-wrap">
            <table>
                <thead>
                    <tr>
                        <th style="width: 50px;">排名</th>
                        <th style="width: 60px;">主图</th>
                        <th style="width: 140px;">所属店铺</th>
                        <th>商品标题与核心卖点</th>
                        <th style="width: 130px;">1.8m起步到手价</th>
                        <th style="width: 140px;">1.8m款式价格区间</th>
                        <th style="width: 90px;">款式数量</th>
                        <th style="width: 110px;">昨日销售额</th>
                        <th style="width: 100px;">操作</th>
                    </tr>
                </thead>
                <tbody id="tab1-tbody"></tbody>
            </table>
        </div>
    </div>

    <!-- ========================================== -->
    <!-- TAB 2: 按价格带归类透视 -->
    <!-- ========================================== -->
    <div class="tab-content" id="tab-1">
        <div class="kpi-grid" id="band-kpi-grid"></div>
        <div class="table-wrap">
            <table>
                <thead>
                    <tr>
                        <th>价格带区间</th>
                        <th>定位与代表类型</th>
                        <th>商品数量 (占比)</th>
                        <th>1.8m SKU数量 (占比)</th>
                        <th>加补后到手价中位数</th>
                        <th>加补后到手价均值</th>
                        <th>典型代表款式与店铺</th>
                    </tr>
                </thead>
                <tbody id="tab2-tbody"></tbody>
            </table>
        </div>
    </div>

    <!-- ========================================== -->
    <!-- TAB 3: 按排名梯队深度归类 -->
    <!-- ========================================== -->
    <div class="tab-content" id="tab-2">
        <div class="kpi-grid" id="tier-kpi-grid"></div>
        <div class="table-wrap">
            <table>
                <thead>
                    <tr>
                        <th>排名梯队</th>
                        <th>商品数</th>
                        <th>SKU总数</th>
                        <th>销售额贡献</th>
                        <th>销售额占比</th>
                        <th>1.8m到手价中位数</th>
                        <th>1.8m到手均价</th>
                        <th>1.8m起步价区间</th>
                        <th>梯队爆款特征提炼</th>
                    </tr>
                </thead>
                <tbody id="tab3-tbody"></tbody>
            </table>
        </div>
    </div>

    <!-- ========================================== -->
    <!-- TAB 4: 按店铺矩阵归类 -->
    <!-- ========================================== -->
    <div class="tab-content" id="tab-3">
        <div class="table-wrap">
            <table>
                <thead>
                    <tr>
                        <th>店铺名称</th>
                        <th>上榜商品款数</th>
                        <th>1.8m SKU总数</th>
                        <th>昨日支付金额</th>
                        <th>昨日支付件数</th>
                        <th>1.8m到手价中位数</th>
                        <th>1.8m到手均价</th>
                        <th>1.8m价格带覆盖</th>
                        <th>核心主打方向</th>
                    </tr>
                </thead>
                <tbody id="tab4-tbody"></tbody>
            </table>
        </div>
    </div>

    <!-- ========================================== -->
    <!-- TAB 5: 多维度横向对比 -->
    <!-- ========================================== -->
    <div class="tab-content" id="tab-4">
        <div class="table-wrap" style="margin-bottom: 20px;">
            <h3 style="padding: 16px; border-bottom: 1px solid var(--border); color: #60a5fa;">🧬 核心材质对比 (黄麻 vs 乳胶 vs 独立弹簧 vs 记忆棉)</h3>
            <table>
                <thead>
                    <tr>
                        <th>材质与工艺特征</th>
                        <th>涉及商品数</th>
                        <th>覆盖SKU款型数</th>
                        <th>1.8m到手价中位数</th>
                        <th>1.8m到手均价</th>
                        <th>最低到手价</th>
                        <th>最高到手价</th>
                        <th>主要销售贡献店铺</th>
                    </tr>
                </thead>
                <tbody id="tab5-mat-tbody"></tbody>
            </table>
        </div>
        <div class="table-wrap">
            <h3 style="padding: 16px; border-bottom: 1px solid var(--border); color: #f87171;">📐 结构与功能对比 (全拆洗 vs 传统 | 厚垫 vs 薄垫)</h3>
            <table>
                <thead>
                    <tr>
                        <th>结构形态与功能</th>
                        <th>商品数</th>
                        <th>SKU数</th>
                        <th>1.8m到手价中位数</th>
                        <th>1.8m均价</th>
                        <th>客群画像与典型场景</th>
                    </tr>
                </thead>
                <tbody id="tab5-struct-tbody"></tbody>
            </table>
        </div>
    </div>

    <!-- ========================================== -->
    <!-- TAB 6: 主图视觉卖点与到手价透视 -->
    <!-- ========================================== -->
    <div class="tab-content" id="tab-5">
        <div class="filter-panel">
            <div class="filter-row">
                <div class="filter-label">主图高频卖点</div>
                <div class="pill-group" id="ocr-selling-pills"></div>
            </div>
            <div class="filter-row">
                <div class="filter-label">大促利益点</div>
                <div class="pill-group" id="ocr-mkt-pills"></div>
            </div>
        </div>
        <div class="table-wrap">
            <table>
                <thead>
                    <tr>
                        <th style="width: 50px;">排名</th>
                        <th style="width: 80px;">主图</th>
                        <th style="width: 140px;">店铺</th>
                        <th>商品标题与直达</th>
                        <th style="width: 120px;">1.8m起步加补价</th>
                        <th>主图提取核心卖点标签</th>
                        <th>主图营销利益标签</th>
                        <th>主图 RapidOCR 文本摘要</th>
                    </tr>
                </thead>
                <tbody id="tab6-tbody"></tbody>
            </table>
        </div>
    </div>

    <!-- 图片放大预览模态框 -->
    <div id="img-modal" onclick="closeImgModal(event)">
        <div id="modal-img-container" onclick="event.stopPropagation()">
            <img id="modal-img" src="" alt="商品高清主图">
            <div id="modal-info">
                <h3 id="modal-title" style="color: #fff; margin-bottom: 8px;"></h3>
                <div id="modal-shop" style="color: #38bdf8; margin-bottom: 12px;"></div>
                <div style="margin-bottom: 10px;">
                    <b style="color: #f87171; font-size: 16px;" id="modal-price"></b>
                </div>
                <div style="margin-bottom: 12px;" id="modal-tags"></div>
                <div style="background: #0f172a; padding: 10px; border-radius: 6px; font-size: 12px; line-height: 1.6;">
                    <b style="color: #cbd5e1;">RapidOCR 识别文本：</b>
                    <p id="modal-ocr" style="color: #94a3b8; margin-top: 4px; white-space: pre-wrap;"></p>
                </div>
            </div>
        </div>
    </div>

    <script>
        const DB = {db_json_str};

        let activeTab = 0;
        let selectedShops = new Set();
        let selectedMats = new Set();

        function switchTab(idx) {{
            document.querySelectorAll('.tab-btn').forEach((b, i) => {{
                b.classList.toggle('active', i === idx);
            }});
            document.querySelectorAll('.tab-content').forEach((c, i) => {{
                c.classList.toggle('active', i === idx);
            }});
            activeTab = idx;
        }}

        // 初始化店铺筛选 Pill
        function initShopPills() {{
            const shopCounts = {{}};
            DB.products.forEach(p => {{
                shopCounts[p.shop] = (shopCounts[p.shop] || 0) + 1;
            }});
            const container = document.getElementById('shop-pills');
            container.innerHTML = '';
            Object.entries(shopCounts).sort((a,b) => b[1] - a[1]).forEach(([shop, cnt]) => {{
                const el = document.createElement('div');
                el.className = 'pill';
                el.innerText = `${{shop}} (${{cnt}})`;
                el.onclick = () => {{
                    if (selectedShops.has(shop)) {{
                        selectedShops.delete(shop);
                        el.classList.remove('active');
                    }} else {{
                        selectedShops.add(shop);
                        el.classList.add('active');
                    }}
                    applyTab1Filter();
                }};
                container.appendChild(el);
            }});
        }}

        function toggleMatPill(el, kw) {{
            if (selectedMats.has(kw)) {{
                selectedMats.delete(kw);
                el.classList.remove('active');
            }} else {{
                selectedMats.add(kw);
                el.classList.add('active');
            }}
            applyTab1Filter();
        }}

        function resetTab1Filter() {{
            document.getElementById('filter-pmin').value = '0';
            document.getElementById('filter-pmax').value = '3000';
            document.getElementById('filter-kw').value = '';
            selectedShops.clear();
            selectedMats.clear();
            document.querySelectorAll('#tab-0 .pill').forEach(p => p.classList.remove('active'));
            applyTab1Filter();
        }}

        function applyTab1Filter() {{
            const pmin = parseFloat(document.getElementById('filter-pmin').value) || 0;
            const pmax = parseFloat(document.getElementById('filter-pmax').value) || 999999;
            const kw = document.getElementById('filter-kw').value.trim().toLowerCase();

            const matched = DB.products.filter(p => {{
                const price = p.min_price || 0;
                if (price < pmin || price > pmax) return false;
                if (selectedShops.size > 0 && !selectedShops.has(p.shop)) return false;
                
                if (selectedMats.size > 0) {{
                    const fullText = (p.title + ' ' + (p.selling_points || []).join(' ')).toLowerCase();
                    for (let m of selectedMats) {{
                        if (!fullText.includes(m.toLowerCase())) return false;
                    }}
                }}

                if (kw) {{
                    const skuNames = (p.skus || []).map(s => s.name).join(' ');
                    const searchCorpus = (p.title + ' ' + p.shop + ' ' + skuNames).toLowerCase();
                    if (!searchCorpus.includes(kw)) return false;
                }}
                return true;
            }});

            renderTab1Table(matched);
        }}

        function renderTab1Table(products) {{
            const tbody = document.getElementById('tab1-tbody');
            tbody.innerHTML = '';

            let totalSkus = 0;
            let totalGmv = 0;
            const prices = [];

            products.forEach(p => {{
                totalSkus += p.sku_count || 0;
                totalGmv += p.sales_amount || 0;
                if (p.min_price && p.min_price > 1) prices.push(p.min_price);

                const tr = document.createElement('tr');
                const rankCls = p.rank === 1 ? 'rank-1' : p.rank === 2 ? 'rank-2' : p.rank === 3 ? 'rank-3' : '';
                
                const tagsHtml = (p.selling_points || []).map(t => `<span class="tag tag-mat">${{t}}</span>`).join('') +
                                 (p.marketing_text || []).map(t => `<span class="tag tag-mkt">${{t}}</span>`).join('');

                tr.innerHTML = `
                    <td><span class="rank-badge ${{rankCls}}">${{p.rank}}</span></td>
                    <td>
                        <img class="thumb-img" src="${{p.local_img_path}}" onerror="this.src='${{p.main_img_url}}'" 
                             onclick="openImgModal('${{p.rank}}')" title="点击放大查看主图及OCR详情">
                    </td>
                    <td><span class="shop-pill">${{p.shop}}</span></td>
                    <td>
                        <a href="${{p.link}}" target="_blank" style="color: #fff; text-decoration: none; font-weight: 500;" title="点击直达天猫1.8m详情页">
                            ${{p.title}} ↗
                        </a>
                        <div style="margin-top: 4px;">${{tagsHtml}}</div>
                    </td>
                    <td><b class="price-hl">￥${{p.min_price ? p.min_price.toFixed(2) : '-'}}</b></td>
                    <td>￥${{p.min_price ? p.min_price.toFixed(0) : '-'}} ~ ￥${{p.max_price ? p.max_price.toFixed(0) : '-'}}</td>
                    <td><span style="background: #334155; padding: 2px 8px; border-radius: 4px; font-weight: 600;">${{p.sku_count}} 款</span></td>
                    <td style="color: #34d399; font-weight: 600;">￥${{p.sales_amount.toLocaleString()}}</td>
                    <td>
                        <button class="sku-expand-btn" onclick="toggleSkuDrawer('${{p.itemId}}')">展开款式 (${{p.sku_count}})</button>
                    </td>
                `;

                // SKU 抽屉行
                const trDrawer = document.createElement('tr');
                trDrawer.id = `drawer-row-${{p.itemId}}`;
                trDrawer.style.display = 'none';

                let skuRowsHtml = '';
                (p.skus || []).forEach((s, idx) => {{
                    const saveAmt = s.orig && s.price ? (s.orig - s.price).toFixed(1) : '-';
                    skuRowsHtml += `
                        <tr>
                            <td style="width: 30px; color: var(--text-dim);">${{idx + 1}}</td>
                            <td><b>${{s.name}}</b></td>
                            <td style="color: #f87171; font-weight: 700;">￥${{s.price}}</td>
                            <td style="color: var(--text-sub); text-decoration: line-through;">￥${{s.orig || '-'}}</td>
                            <td style="color: #34d399;">省 ￥${{saveAmt}}</td>
                            <td><span class="tag tag-mkt">${{s.tag || '平台加补后'}}</span></td>
                        </tr>
                    `;
                }});

                trDrawer.innerHTML = `
                    <td colspan="9" style="padding: 0 14px 14px 14px;">
                        <div class="sku-drawer open">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <b style="color: #f87171;">📋 1800mm*2000mm 规格下全部款式与平台加补价明细 (共 ${{p.sku_count}} 款)</b>
                                <span style="font-size: 11px; color: var(--text-sub);">直达链接: <a href="${{p.link}}" target="_blank" style="color: #38bdf8;">${{p.link}}</a></span>
                            </div>
                            <table class="sku-table">
                                <thead>
                                    <tr>
                                        <th>#</th>
                                        <th>款式/配置名称</th>
                                        <th>平台加补后到手价</th>
                                        <th>优惠前原价</th>
                                        <th>优惠差额</th>
                                        <th>价格属性</th>
                                    </tr>
                                </thead>
                                <tbody>${{skuRowsHtml}}</tbody>
                            </table>
                        </div>
                    </td>
                `;

                tbody.appendChild(tr);
                tbody.appendChild(trDrawer);
            }});

            // 更新 KPI
            prices.sort((a,b) => a - b);
            const med = prices.length > 0 ? prices[Math.floor(prices.length / 2)] : 0;
            const minP = prices.length > 0 ? prices[0] : 0;

            document.getElementById('kpi-f-prod').innerText = products.length;
            document.getElementById('kpi-f-sku').innerText = totalSkus.toLocaleString();
            document.getElementById('kpi-f-min').innerText = `￥${{minP.toFixed(2)}}`;
            document.getElementById('kpi-f-median').innerText = `￥${{med.toFixed(2)}}`;
            document.getElementById('kpi-f-gmv').innerText = `￥${{Math.round(totalGmv).toLocaleString()}}`;
        }}

        function toggleSkuDrawer(itemId) {{
            const row = document.getElementById(`drawer-row-${{itemId}}`);
            if (row) {{
                row.style.display = row.style.display === 'none' ? 'table-row' : 'none';
            }}
        }}

        // 渲染 Tab 2 价格带
        function renderTab2() {{
            const grid = document.getElementById('band-kpi-grid');
            const tbody = document.getElementById('tab2-tbody');
            grid.innerHTML = '';
            tbody.innerHTML = '';

            DB.price_bands_stats.forEach(b => {{
                const card = document.createElement('div');
                card.className = 'kpi-card';
                card.innerHTML = `
                    <div class="val red">${{b.label}}</div>
                    <div class="lbl">${{b.sub}}</div>
                    <div style="margin-top: 8px; font-size: 13px;"><b>${{b.sku_count}}</b> 款配置 (${{b.sku_pct}}%)</div>
                    <div class="progress-bar"><div class="progress-fill" style="width: ${{b.sku_pct}}%;"></div></div>
                `;
                grid.appendChild(card);

                // 找代表爆款
                const prodsInBand = DB.products.filter(p => p.min_price >= b.min && p.min_price <= b.max);
                const sampleTitles = prodsInBand.slice(0, 2).map(p => `• [#${{p.rank}} ${{p.shop}}] ${{p.title.slice(0, 18)}}...`).join('<br>');

                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><b style="color: #f87171; font-size: 14px;">${{b.label}}</b></td>
                    <td style="color: var(--text-sub);">${{b.sub}}</td>
                    <td><b>${{b.prod_count}} 款</b> (${{b.prod_pct}}%)</td>
                    <td><b>${{b.sku_count}} 款</b> (${{b.sku_pct}}%)</td>
                    <td style="color: #34d399; font-weight: 700;">￥${{b.median.toFixed(2)}}</td>
                    <td>￥${{b.mean.toFixed(2)}}</td>
                    <td style="font-size: 11px; color: #cbd5e1;">${{sampleTitles || '暂无商品'}}</td>
                `;
                tbody.appendChild(tr);
            }});
        }}

        // 渲染 Tab 3 排名梯队
        function renderTab3() {{
            const grid = document.getElementById('tier-kpi-grid');
            const tbody = document.getElementById('tab3-tbody');
            grid.innerHTML = '';
            tbody.innerHTML = '';

            const totalGmv = DB.products.reduce((acc, p) => acc + (p.sales_amount || 0), 0);

            DB.rank_tiers_stats.forEach(t => {{
                const pct = ((t.sales_amount / totalGmv) * 100).toFixed(1);
                const card = document.createElement('div');
                card.className = 'kpi-card';
                card.innerHTML = `
                    <div class="val blue">${{t.label}}</div>
                    <div class="lbl">贡献营收: ￥${{Math.round(t.sales_amount).toLocaleString()}}</div>
                    <div style="margin-top: 8px; font-size: 13px;">占比 <b>${{pct}}%</b> | 中位到手价: <b>￥${{t.median_price.toFixed(0)}}</b></div>
                    <div class="progress-bar"><div class="progress-fill" style="width: ${{pct}}%; background: #38bdf8;"></div></div>
                `;
                grid.appendChild(card);

                let summaryDesc = '';
                if (t.id === 'tier_top10') summaryDesc = '🌟 绝对核心爆款群：主打独立袋弹簧+双面睡感+2cm乳胶/黄麻，价格集中在 1100-1400元黄金带，单款客单稳定在 1800+';
                else if (t.id === 'tier_11_30') summaryDesc = '🚀 潜力放量梯队：全拆黄麻薄垫、儿童护脊专用床垫高频出现，价格覆盖 600-1100元性价比带';
                else if (t.id === 'tier_31_60') summaryDesc = '⚓ 腰部基石梯队：主攻加硬护脊、折叠榻榻米、超厚五星酒店款，承接细分场景搜索流量';
                else summaryDesc = '📦 长尾补齐梯队：包含学生宿舍专用单薄垫、特权定金、以及特定定制款';

                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><b style="color: #60a5fa; font-size: 14px;">${{t.label}}</b></td>
                    <td><b>${{t.prod_count}}</b> 款</td>
                    <td><b>${{t.sku_count}}</b> 款</td>
                    <td style="color: #34d399; font-weight: 700;">￥${{t.sales_amount.toLocaleString()}}</td>
                    <td><b style="color: #f87171;">${{pct}}%</b></td>
                    <td style="color: #fbbf24; font-weight: 700;">￥${{t.median_price.toFixed(2)}}</td>
                    <td>￥${{t.mean_price.toFixed(2)}}</td>
                    <td>￥${{t.min_start_price.toFixed(0)}} ~ ￥${{t.max_start_price.toFixed(0)}}</td>
                    <td style="font-size: 12px; color: #cbd5e1;">${{summaryDesc}}</td>
                `;
                tbody.appendChild(tr);
            }});
        }}

        // 渲染 Tab 4 店铺矩阵
        function renderTab4() {{
            const tbody = document.getElementById('tab4-tbody');
            tbody.innerHTML = '';

            DB.top_shops_stats.forEach(s => {{
                let focus = '综合家用/全拆/加硬';
                if (s.shop.includes('moonlight')) focus = '🏆 旗舰主力：家用防塌独立弹簧、全拆尊耀、大促主攻';
                else if (s.shop.includes('睡眠骑士')) focus = '🏨 五星酒店超厚30cm、梦舒乳胶、高性价比';
                else if (s.shop.includes('铂马仕')) focus = '🪵 天然椰棕/S黄麻护脊、加硬双人、超薄折叠';
                else if (s.shop.includes('悠梦思')) focus = '✨ 华夫格独立袋、亲民全拆S黄麻、软硬双面';
                else if (s.shop.includes('麻师傅')) focus = '🌿 纯S形天然黄麻护腰加硬、全拆洗专用';
                else if (s.shop.includes('派乐熊') || s.shop.includes('PARELER')) focus = '👶 儿童青少年专用护脊、0胶水0甲醛、学生薄垫';

                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><span class="shop-pill" style="font-size: 12px; padding: 4px 8px;">${{s.shop}}</span></td>
                    <td><b>${{s.prod_count}}</b> 款</td>
                    <td><b>${{s.sku_count}}</b> 款</td>
                    <td style="color: #34d399; font-weight: 700;">￥${{s.sales_amount.toLocaleString()}}</td>
                    <td><b>${{s.sales_qty}}</b> 件</td>
                    <td style="color: #f87171; font-weight: 700;">￥${{s.median_price.toFixed(2)}}</td>
                    <td>￥${{s.mean_price.toFixed(2)}}</td>
                    <td>￥${{s.min_price.toFixed(0)}} ~ ￥${{s.max_price.toFixed(0)}}</td>
                    <td style="font-size: 12px; color: #cbd5e1;">${{focus}}</td>
                `;
                tbody.appendChild(tr);
            }});
        }}

        // 渲染 Tab 5 横向对比
        function renderTab5() {{
            const matTbody = document.getElementById('tab5-mat-tbody');
            matTbody.innerHTML = '';

            const MATS = [
                {{ name: '天然黄麻/S型黄麻', kw: '黄麻' }},
                {{ name: '天然乳胶/泰国乳胶', kw: '乳胶' }},
                {{ name: '独立袋弹簧/贝纹弹簧', kw: '独立袋' }},
                {{ name: '记忆棉/凝胶慢回弹', kw: '记忆棉' }},
                {{ name: '邦尼尔整网/加密加固弹簧', kw: '弹簧' }},
            ];

            MATS.forEach(m => {{
                const prods = DB.products.filter(p => (p.title + ' ' + (p.selling_points || []).join(' ')).includes(m.kw));
                let skus = [];
                prods.forEach(p => {{
                    p.skus.forEach(s => {{
                        if (s.price && s.price > 1) skus.push(s.price);
                    }});
                }});
                skus.sort((a,b) => a - b);
                const med = skus.length > 0 ? skus[Math.floor(skus.length / 2)] : 0;
                const avg = skus.length > 0 ? (skus.reduce((a,b)=>a+b,0)/skus.length) : 0;
                const minP = skus.length > 0 ? skus[0] : 0;
                const maxP = skus.length > 0 ? skus[skus.length-1] : 0;

                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><b style="color: #60a5fa; font-size: 14px;">${{m.name}}</b></td>
                    <td><b>${{prods.length}}</b> 款</td>
                    <td><b>${{skus.length}}</b> 款</td>
                    <td style="color: #f87171; font-weight: 700;">￥${{med.toFixed(2)}}</td>
                    <td>￥${{avg.toFixed(2)}}</td>
                    <td>￥${{minP.toFixed(2)}}</td>
                    <td>￥${{maxP.toFixed(2)}}</td>
                    <td style="font-size: 11px; color: #cbd5e1;">全店铺高频标配 (moonlightfamily / 麻师傅 / 铂马仕 / 睡眠骑士)</td>
                `;
                matTbody.appendChild(tr);
            }});

            const structTbody = document.getElementById('tab5-struct-tbody');
            structTbody.innerHTML = '';
            const STRUCTS = [
                {{ name: '全拆洗 / 可调节软硬结构', kw: '全拆', desc: '新趋势主推：看得见的环保无胶，深受青年夫妻与注重健康家庭喜爱' }},
                {{ name: '软硬双面睡感 (正面乳胶+反面黄麻)', kw: '双面', desc: '主力走量杀手锏：一垫两睡，闭眼选不踩坑，退换货率低' }},
                {{ name: '超厚款 (22-30cm 酒店/主卧厚垫)', kw: '30cm', desc: '品质升级：主卧大床首选，包裹感强，客单价达 1500~2000元' }},
                {{ name: '超薄款 (5-15cm 榻榻米/折叠/宿舍/儿童)', kw: '薄', desc: '场景放量：高低床、极简矮床、宿舍租房，客单 200~900元' }}
            ];
            STRUCTS.forEach(st => {{
                const prods = DB.products.filter(p => (p.title + ' ' + (p.skus || []).map(s=>s.name).join(' ')).includes(st.kw));
                let skus = [];
                prods.forEach(p => p.skus.forEach(s => {{ if (s.price && s.price > 1) skus.push(s.price); }}));
                skus.sort((a,b) => a - b);
                const med = skus.length > 0 ? skus[Math.floor(skus.length / 2)] : 0;
                const avg = skus.length > 0 ? (skus.reduce((a,b)=>a+b,0)/skus.length) : 0;

                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><b style="color: #f87171; font-size: 14px;">${{st.name}}</b></td>
                    <td><b>${{prods.length}}</b> 款</td>
                    <td><b>${{skus.length}}</b> 款</td>
                    <td style="color: #34d399; font-weight: 700;">￥${{med.toFixed(2)}}</td>
                    <td>￥${{avg.toFixed(2)}}</td>
                    <td style="font-size: 12px; color: #cbd5e1;">${{st.desc}}</td>
                `;
                structTbody.appendChild(tr);
            }});
        }}

        // 渲染 Tab 6 主图透视
        function renderTab6() {{
            const tbody = document.getElementById('tab6-tbody');
            tbody.innerHTML = '';

            DB.products.forEach(p => {{
                const tr = document.createElement('tr');
                const sellTags = (p.selling_points || []).map(t => `<span class="tag tag-mat">${{t}}</span>`).join('') || '<span style="color:var(--text-dim);">-</span>';
                const mktTags = (p.marketing_text || []).map(t => `<span class="tag tag-mkt">${{t}}</span>`).join('') || '<span style="color:var(--text-dim);">-</span>';

                tr.innerHTML = `
                    <td><b>#${{p.rank}}</b></td>
                    <td>
                        <img class="thumb-img" src="${{p.local_img_path}}" onerror="this.src='${{p.main_img_url}}'" 
                             onclick="openImgModal('${{p.rank}}')" style="width: 54px; height: 54px;">
                    </td>
                    <td><span class="shop-pill">${{p.shop}}</span></td>
                    <td><a href="${{p.link}}" target="_blank" style="color:#fff; text-decoration:none;">${{p.title}} ↗</a></td>
                    <td><b class="price-hl">￥${{p.min_price ? p.min_price.toFixed(2) : '-'}}</b></td>
                    <td>${{sellTags}}</td>
                    <td>${{mktTags}}</td>
                    <td style="font-size: 11px; color: #94a3b8; max-width: 280px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${{p.ocr_raw}}">
                        ${{p.ocr_raw ? p.ocr_raw.slice(0, 70) : '未提取到清晰文字'}}
                    </td>
                `;
                tbody.appendChild(tr);
            }});
        }}

        // 图片模态框
        function openImgModal(rank) {{
            const p = DB.products.find(item => item.rank == rank);
            if (!p) return;
            const modal = document.getElementById('img-modal');
            const img = document.getElementById('modal-img');
            img.src = p.local_img_path;
            img.onerror = () => {{ img.src = p.main_img_url; }};
            document.getElementById('modal-title').innerText = `#${{p.rank}} ${{p.title}}`;
            document.getElementById('modal-shop').innerText = `所属店铺: ${{p.shop}} | 1.8m款式数: ${{p.sku_count}}`;
            document.getElementById('modal-price').innerText = `1.8m 平台加补后最低到手价: ￥${{p.min_price ? p.min_price.toFixed(2) : '-'}} (最高 ￥${{p.max_price}})`;
            
            const tagsHtml = (p.selling_points || []).map(t => `<span class="tag tag-mat">${{t}}</span>`).join('') +
                             (p.marketing_text || []).map(t => `<span class="tag tag-mkt">${{t}}</span>`).join('');
            document.getElementById('modal-tags').innerHTML = tagsHtml;
            document.getElementById('modal-ocr').innerText = p.ocr_raw || '未识别到文字';

            modal.classList.add('open');
        }}

        function closeImgModal(e) {{
            document.getElementById('img-modal').classList.remove('open');
        }}

        document.addEventListener('keydown', e => {{
            if (e.key === 'Escape') closeImgModal();
        }});

        // 页面初始化
        window.onload = () => {{
            initShopPills();
            applyTab1Filter();
            renderTab2();
            renderTab3();
            renderTab4();
            renderTab5();
            renderTab6();
        }};
    </script>
</body>
</html>
"""
    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_template)
    print(f"🎉 成功生成公司旗下 95 款床垫全量 SKU 交互分析大屏: {OUT_HTML}")

if __name__ == "__main__":
    build_dashboard()
