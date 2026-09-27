# -*- coding: utf-8 -*-
"""
=============================================================================
将多周期快照切换、生命周期异动标签与大盘去重池交互组件应用至两个 HTML 文件
=============================================================================
"""
import os
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_HTML = os.path.join(BASE_DIR, "index.html")
DASHBOARD_HTML = os.path.join(BASE_DIR, "床垫300款排名与SKU价格交互分析大屏.html")

SNAPSHOT_CSS = """
        /* 📅 榜单周期快照选择器样式 */
        .snapshot-pills {
            display: flex;
            align-items: center;
            gap: 6px;
            flex-wrap: wrap;
        }
        .snapshot-pill-btn {
            background: rgba(15, 23, 42, 0.7);
            border: 1px solid #334155;
            color: #94a3b8;
            padding: 5px 12px;
            border-radius: 16px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 5px;
            white-space: nowrap;
        }
        .snapshot-pill-btn:hover {
            color: #fff;
            border-color: #10b981;
            background: rgba(16, 185, 129, 0.15);
        }
        .snapshot-pill-btn.active {
            background: linear-gradient(135deg, #059669, #10b981);
            border-color: #34d399;
            color: #fff;
            box-shadow: 0 0 10px rgba(16, 185, 129, 0.4);
        }
        .snapshot-pill-btn.btn-all-dedup.active {
            background: linear-gradient(135deg, #d97706, #f59e0b);
            border-color: #fbbf24;
            box-shadow: 0 0 10px rgba(245, 158, 11, 0.4);
        }
"""

SNAPSHOT_HTML_BAR = """<!-- 🌐 对比数据源与榜单周期快照全局切换栏 -->
    <div class="source-filter-bar">
        <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
            <span style="font-size: 13px; font-weight: 700; color: #cbd5e1; display: flex; align-items: center; gap: 6px;">
                <span>🌐 全局数据源:</span>
            </span>
            <div class="source-pills">
                <button class="source-pill-btn active" id="src-btn-all" onclick="setSourceFilter('all')">
                    <span>🌟 全域融合 (395款 / 4,039 SKU)</span>
                </button>
                <button class="source-pill-btn btn-company" id="src-btn-comp" onclick="setSourceFilter('company')">
                    <span>🏢 仅看公司自营 (95款 / 1,283 SKU)</span>
                </button>
                <button class="source-pill-btn btn-market" id="src-btn-mkt" onclick="setSourceFilter('market')">
                    <span>🌐 仅看天猫大盘 (300款 / 2,756 SKU)</span>
                </button>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
            <span style="font-size: 12px; font-weight: 700; color: #94a3b8; display: flex; align-items: center; gap: 4px;">
                <span>📅 榜单周期快照:</span>
            </span>
            <div class="snapshot-pills" id="snapshot-pills">
                <button class="snapshot-pill-btn btn-all-dedup" id="snap-btn-all-dedup" onclick="setSnapshotFilter('all_dedup')" title="查看两期合并去重后的全部334款大盘爆款与4,661条SKU (全域417款)">
                    <span>🌟 历史大盘全量去重池 (334款)</span>
                </button>
                <button class="snapshot-pill-btn active" id="snap-btn-latest" onclick="setSnapshotFilter('latest')" title="查看最新一期2026-09-27排名前300榜单与2,756条SKU">
                    <span>📅 最新30天 (2026-09-27) [300款]</span>
                </button>
                <button class="snapshot-pill-btn" id="snap-btn-prev" onclick="setSnapshotFilter('history_20260920')" title="回溯上期2026-09-20排名前300榜单与3,561条SKU">
                    <span>📅 上期历史 (2026-09-20) [300款]</span>
                </button>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 10px;">
            <button class="btn btn-sm" id="btn-top-compare-modal" onclick="openSideBySideModal()" style="display: none; background: linear-gradient(135deg, #0284c7, #2563eb); border: none; color: #fff; font-weight: 700; padding: 6px 14px; border-radius: 6px; box-shadow: 0 0 10px rgba(56,189,248,0.4); cursor: pointer;">
                <span>⚖️ 打开横向对比工作台 (<span id="dock-btn-badge">0</span>/5)</span>
            </button>
        </div>
    </div>"""

def update_html(filepath):
    print(f"正在更新: {os.path.basename(filepath)}")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. 注入 CSS (在 .source-filter-bar 之前)
    if "/* 📅 榜单周期快照选择器样式 */" not in content:
        content = content.replace("/* =================== 全域横向对比与数据源切换组件样式 =================== */",
                                  "/* =================== 全域横向对比与数据源切换组件样式 =================== */" + SNAPSHOT_CSS)

    # 2. 替换切换栏 DOM
    m_bar = re.search(r'<!-- 🌐 对比数据源全局切换栏 -->[\s\S]*?</div>\s*</div>', content)
    if m_bar:
        content = content[:m_bar.start()] + SNAPSHOT_HTML_BAR + content[m_bar.end():]
        print("  ✅ 成功替换数据源与快照切换栏 DOM")
    else:
        print("  ⚠️ 未找到数据源切换栏 DOM 替换点")

    # 3. 顶部 JS 变量初始化
    old_vars = "var currentSourceFilter = 'all'; // 'all' | 'company' | 'market'"
    new_vars = """var currentSourceFilter = 'all'; // 'all' | 'company' | 'market'
        var currentSnapshotFilter = 'latest'; // 'latest' | 'history_20260920' | 'all_dedup'
        var currentLifecycleFilter = 'all'; // 'all' | 'new_entrant' | 'stable' | 'departed' | 'company_only'"""
    if "var currentSnapshotFilter" not in content:
        content = content.replace(old_vars, new_vars, 1)
        print("  ✅ 成功注入全局快照与生命周期变量")

    # 4. 注入 setSnapshotFilter 与 setLifecycleFilter 函数
    func_hook = "// 1. 数据源切换逻辑"
    new_funcs = """// 1.0 榜单周期快照切换
        function setSnapshotFilter(snap) {
            currentSnapshotFilter = snap;
            document.querySelectorAll('#snapshot-pills .snapshot-pill-btn').forEach(btn => btn.classList.remove('active'));
            if (snap === 'all_dedup') document.getElementById('snap-btn-all-dedup')?.classList.add('active');
            else if (snap === 'latest') document.getElementById('snap-btn-latest')?.classList.add('active');
            else if (snap === 'history_20260920') document.getElementById('snap-btn-prev')?.classList.add('active');

            const allBtn = document.getElementById('src-btn-all');
            const mktBtn = document.getElementById('src-btn-mkt');
            if (snap === 'all_dedup') {
                if (allBtn) allBtn.innerHTML = '<span>🌟 全域去重池 (417款 / 5,715 SKU)</span>';
                if (mktBtn) mktBtn.innerHTML = '<span>🌐 历史大盘去重 (334款 / 4,661 SKU)</span>';
            } else if (snap === 'latest') {
                if (allBtn) allBtn.innerHTML = '<span>🌟 最新全域大盘+自营 (395款 / 4,039 SKU)</span>';
                if (mktBtn) mktBtn.innerHTML = '<span>🌐 最新天猫大盘 (300款 / 2,756 SKU)</span>';
            } else if (snap === 'history_20260920') {
                if (allBtn) allBtn.innerHTML = '<span>🌟 上期全域大盘+自营 (395款 / 4,844 SKU)</span>';
                if (mktBtn) mktBtn.innerHTML = '<span>🌐 上期天猫大盘 (300款 / 3,561 SKU)</span>';
            }

            updateHeaderStatsUI();
            runCustomFilter();
        }

        // 1.0.1 生命周期状态过滤
        function setLifecycleFilter(val) {
            currentLifecycleFilter = val;
            runCustomFilter();
        }

        // 1. 数据源切换逻辑"""
    if "function setSnapshotFilter" not in content:
        content = content.replace(func_hook, new_funcs, 1)
        print("  ✅ 成功注入 setSnapshotFilter 函数")

    # 5. 更新 updateHeaderStatsUI
    old_update_header = re.search(r'function updateHeaderStatsUI\(\)\s*\{[\s\S]*?meanEl\.innerText = `￥\$\{DB\.meta\.overall_price_mean\.toFixed\(2\)\}`;[\s\S]*?\}', content)
    if old_update_header:
        new_update_header = """function updateHeaderStatsUI() {
            const prodEl = document.getElementById('stat-header-prod');
            const prodLbl = document.getElementById('stat-header-prod-lbl');
            const skuEl = document.getElementById('stat-header-sku');
            const medEl = document.getElementById('stat-header-med');
            const meanEl = document.getElementById('stat-header-mean');
            if (!prodEl) return;

            let curProds = DB.products;
            if (currentSnapshotFilter && currentSnapshotFilter !== 'all_dedup') {
                curProds = curProds.filter(p => (p.snapshots || []).includes(currentSnapshotFilter) || (p.is_company && currentSourceFilter !== 'market'));
            }
            if (currentSourceFilter === 'company') {
                curProds = curProds.filter(p => p.is_company);
                if (prodLbl) prodLbl.innerText = '公司自营商品';
            } else if (currentSourceFilter === 'market') {
                curProds = curProds.filter(p => !p.is_company);
                if (prodLbl) prodLbl.innerText = (currentSnapshotFilter === 'all_dedup' ? '天猫大盘去重池' : (currentSnapshotFilter === 'history_20260920' ? '天猫大盘(上期)' : '天猫大盘(最新)'));
            } else {
                if (prodLbl) prodLbl.innerText = (currentSnapshotFilter === 'all_dedup' ? '全域去重总商品' : '全域融合商品');
            }

            const allSkus = curProds.flatMap(p => p.skus || []);
            const allPrices = allSkus.map(s => s.price).filter(p => p > 0).sort((a, b) => a - b);
            const med = allPrices.length ? allPrices[Math.floor(allPrices.length / 2)] : 0;
            const mean = allPrices.length ? (allPrices.reduce((a, b) => a + b, 0) / allPrices.length) : 0;

            prodEl.innerText = `${curProds.length} 款`;
            if (skuEl) skuEl.innerText = `${allSkus.length.toLocaleString()} 条`;
            if (medEl) medEl.innerText = `￥${med.toFixed(2)}`;
            if (meanEl) meanEl.innerText = `￥${mean.toFixed(2)}`;
        }"""
        content = content[:old_update_header.start()] + new_update_header + content[old_update_header.end():]
        print("  ✅ 成功升级 updateHeaderStatsUI 动态中位数与均价计算")

    # 6. 更新 runCustomFilter 过滤逻辑与有效排名计算
    old_source_filter_block = re.search(r'let sourceProds = DB\.products;[\s\S]*?sourceProds = sourceProds\.filter\(p => favRankSet\.has\(p\.unique_id \|\| p\.rank\)\);\s*\}', content)
    if old_source_filter_block:
        new_source_filter_block = """let sourceProds = DB.products;
            if (currentSnapshotFilter && currentSnapshotFilter !== 'all_dedup') {
                sourceProds = sourceProds.filter(p => (p.snapshots || []).includes(currentSnapshotFilter) || (p.is_company && currentSourceFilter !== 'market'));
            }
            if (currentSourceFilter === 'company') {
                sourceProds = sourceProds.filter(p => p.is_company);
            } else if (currentSourceFilter === 'market') {
                sourceProds = sourceProds.filter(p => !p.is_company);
            }
            if (currentLifecycleFilter && currentLifecycleFilter !== 'all') {
                sourceProds = sourceProds.filter(p => p.lifecycle_status === currentLifecycleFilter);
            }
            if (isTab1FavOnly) {
                sourceProds = sourceProds.filter(p => favRankSet.has(p.unique_id || p.rank));
            }"""
        content = content[:old_source_filter_block.start()] + new_source_filter_block + content[old_source_filter_block.end():]
        print("  ✅ 成功升级 runCustomFilter 过滤逻辑 (支持快照与生命周期过滤)")

    # 7. 更新 runCustomFilter 中的 rank 判定
    old_rank_check = re.search(r'sourceProds\.forEach\(p =>\s*\{\s*if \(p\.rank < minRank \|\| p\.rank > maxRank\) return;', content)
    if old_rank_check:
        new_rank_check = """sourceProds.forEach(p => {
                let effRank = p.rank;
                if (currentSnapshotFilter === 'history_20260920' && p.market_rank_prev) {
                    effRank = p.market_rank_prev;
                } else if (currentSnapshotFilter === 'latest' && p.market_rank_latest) {
                    effRank = p.market_rank_latest;
                } else if (p.market_rank_latest) {
                    effRank = p.market_rank_latest;
                } else if (p.market_rank_prev) {
                    effRank = p.market_rank_prev;
                } else if (p.company_rank) {
                    effRank = p.company_rank;
                }
                if (effRank < minRank || effRank > maxRank) return;"""
        content = content[:old_rank_check.start()] + new_rank_check + content[old_rank_check.end():]
        print("  ✅ 成功升级商品排名自适应判定 (effRank)")

    # 8. 更新 matchedProducts.push 传递 effRank
    old_push = "matchedProducts.push({\n                    product: p,"
    new_push = "matchedProducts.push({\n                    product: p,\n                    effRank: effRank,"
    if old_push in content and "effRank: effRank" not in content:
        content = content.replace(old_push, new_push, 1)
        print("  ✅ 成功传递 effRank 到 matchedProducts")

    # 9. 更新 renderCustomSkuTable 表头与行数据 (增加“榜单动态”列)
    old_th = '<th data-col="rank" style="width: 55px;" onclick="sortTab1Table(\'rank\')">排名 ↕</th>'
    new_th = """<th data-col="rank" style="width: 55px;" onclick="sortTab1Table('rank')">排名 ↕</th>
                                <th data-col="lifecycle" style="width: 110px;" onclick="event.stopPropagation()">
                                    <div style="display: flex; align-items: center; justify-content: space-between; gap: 4px;">
                                        <span onclick="sortTab1Table('lifecycle')">榜单动态 ↕</span>
                                        <select class="th-filter-select" id="v2-lifecycle-filter" onchange="setLifecycleFilter(this.value)" onclick="event.stopPropagation()">
                                            <option value="all" ${currentLifecycleFilter === 'all' ? 'selected' : ''}>全部</option>
                                            <option value="new_entrant" ${currentLifecycleFilter === 'new_entrant' ? 'selected' : ''}>🆕新晋</option>
                                            <option value="stable" ${currentLifecycleFilter === 'stable' ? 'selected' : ''}>🔥在榜</option>
                                            <option value="departed" ${currentLifecycleFilter === 'departed' ? 'selected' : ''}>🔻跌出</option>
                                            <option value="company_only" ${currentLifecycleFilter === 'company_only' ? 'selected' : ''}>🏢自营</option>
                                        </select>
                                    </div>
                                </th>"""
    if old_th in content and 'data-col="lifecycle"' not in content:
        content = content.replace(old_th, new_th, 1)
        print("  ✅ 成功添加【榜单动态】表头与快捷筛选下拉框")

    # 10. 更新 flatSkus.push 携带生命周期字段
    old_flat_push = "rank: p.rank,\n                        shop: p.shop,"
    new_flat_push = """rank: item.effRank || p.rank,
                        rank_display: (p.is_company ? `自营 #${p.company_rank}` : (item.effRank ? `大盘 #${item.effRank}` : p.display_rank)),
                        lifecycle_status: p.lifecycle_status || '',
                        lifecycle_badge: p.lifecycle_badge || '',
                        rank_change_text: p.rank_change_text || '',
                        shop: p.shop,"""
    if old_flat_push in content:
        content = content.replace(old_flat_push, new_flat_push, 1)
        print("  ✅ 成功将生命周期字段映射至 flatSkus")

    # 11. 更新每行 HTML 渲染榜单动态徽章
    old_row_rank = re.search(r'<!-- 排名 -->\s*<td style="color: var\(--text-dim\); text-align: center; font-weight: 700; font-size: 13px; font-family: ui-monospace, monospace;">\s*#\$\{s\.rank\}\s*</td>', content)
    if old_row_rank:
        new_row_rank = """<!-- 排名 -->
                        <td style="color: var(--text-dim); text-align: center; font-weight: 700; font-size: 13px; font-family: ui-monospace, monospace;">
                            #${s.rank}
                        </td>

                        <!-- 榜单动态 -->
                        <td style="text-align: center; white-space: nowrap;">
                            ${renderLifecycleTag(s.lifecycle_status, s.rank_change_text, s.rank)}
                        </td>"""
        content = content[:old_row_rank.start()] + new_row_rank + content[old_row_rank.end():]
        print("  ✅ 成功渲染榜单动态标签单元格")

    # 12. 注入 renderLifecycleTag 辅助函数
    if "function renderLifecycleTag" not in content:
        helper_code = """
        function renderLifecycleTag(status, changeText, rank) {
            if (status === 'new_entrant') {
                return `
                    <div style="display: flex; align-items: center; justify-content: center; gap: 4px;" title="${escapeHtml(changeText)}">
                        <span class="badge" style="background: rgba(16,185,129,0.18); color: #34d399; border: 1px solid rgba(16,185,129,0.35); font-weight: 700; font-size: 11px; padding: 2px 6px;">🆕 新晋</span>
                        <span style="font-size: 11px; color: #34d399; font-weight: 700; font-family: ui-monospace, monospace;">#${rank}</span>
                    </div>
                `;
            } else if (status === 'stable') {
                const isUp = (changeText || '').includes('升');
                const isDown = (changeText || '').includes('降');
                const color = isUp ? '#f87171' : (isDown ? '#38bdf8' : '#94a3b8');
                const bg = isUp ? 'rgba(239,68,68,0.15)' : (isDown ? 'rgba(56,189,248,0.15)' : 'rgba(148,163,184,0.12)');
                return `
                    <div style="display: flex; align-items: center; justify-content: center; gap: 4px;" title="${escapeHtml(changeText)}">
                        <span class="badge" style="background: ${bg}; color: ${color}; border: 1px solid ${color}40; font-weight: 600; font-size: 11px; padding: 2px 5px;">🔥 持续</span>
                        <span style="font-size: 11px; color: ${color}; font-weight: 700;">${escapeHtml(changeText)}</span>
                    </div>
                `;
            } else if (status === 'departed') {
                return `
                    <div style="display: flex; align-items: center; justify-content: center; gap: 4px;" title="${escapeHtml(changeText)}">
                        <span class="badge" style="background: rgba(148,163,184,0.15); color: #94a3b8; border: 1px solid rgba(148,163,184,0.3); font-weight: 600; font-size: 11px; padding: 2px 5px;">🔻 跌出</span>
                        <span style="font-size: 11px; color: #94a3b8;">曾#${rank}</span>
                    </div>
                `;
            } else {
                return `
                    <div style="display: flex; align-items: center; justify-content: center; gap: 4px;" title="公司自营专属床垫">
                        <span class="badge" style="background: rgba(168,85,247,0.18); color: #c084fc; border: 1px solid rgba(168,85,247,0.35); font-weight: 700; font-size: 11px; padding: 2px 6px;">🏢 自营</span>
                        <span style="font-size: 11px; color: #c084fc; font-weight: 700;">#${rank}</span>
                    </div>
                `;
            }
        }
        """
        content = content.replace("function renderCustomSkuTable(", helper_code + "\n        function renderCustomSkuTable(", 1)
        print("  ✅ 成功注入 renderLifecycleTag 辅助函数")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"🎉 完成写入: {os.path.basename(filepath)}\n")

def main():
    for f in [INDEX_HTML, DASHBOARD_HTML]:
        if os.path.exists(f):
            update_html(f)

if __name__ == "__main__":
    main()
