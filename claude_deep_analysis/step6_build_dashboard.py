# -*- coding: utf-8 -*-
"""
Step6 生成交互式决策大屏（单文件离线可用）
把三阶段结果内嵌进 HTML，无外部依赖。
输出 爆品孵化决策大屏.html
"""
import json, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))

track = json.load(open(os.path.join(BASE, "track_result.json"), encoding="utf-8"))
products = json.load(open(os.path.join(BASE, "products.json"), encoding="utf-8"))
review = json.load(open(os.path.join(BASE, "review_result.json"), encoding="utf-8"))

DATA = json.dumps({"track": track, "products": products, "review": review},
                  ensure_ascii=False, separators=(",", ":"))

HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>床垫爆品孵化决策大屏 · 三阶段全链路</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#0d1117;color:#e6edf3;font-family:"Microsoft YaHei","PingFang SC",system-ui,sans-serif;padding:24px;line-height:1.7}
a{color:inherit}
.wrap{max-width:1440px;margin:0 auto}
h1{font-size:26px;font-weight:700;letter-spacing:1px}
.sub{color:#7d8590;font-size:13px;margin-top:6px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:14px;margin:22px 0}
.kpi{background:linear-gradient(160deg,#161b22,#11161d);border:1px solid #21262d;border-radius:12px;padding:16px 18px}
.kpi .l{font-size:12px;color:#7d8590}
.kpi .v{font-size:24px;font-weight:700;color:#58a6ff;margin-top:4px}
.kpi .v.gold{color:#e3b341}
.kpi .n{font-size:11px;color:#6e7681;margin-top:2px}
.tabs{display:flex;gap:8px;margin:26px 0 18px;flex-wrap:wrap}
.tab{padding:9px 20px;border:1px solid #30363d;border-radius:8px;background:#161b22;cursor:pointer;font-size:14px;transition:.15s}
.tab:hover{border-color:#58a6ff}
.tab.on{background:#1f6feb;border-color:#1f6feb;color:#fff;font-weight:600}
.panel{display:none}
.panel.on{display:block}
.card{background:#161b22;border:1px solid #21262d;border-radius:12px;padding:20px;margin-bottom:16px}
.card.win{border-color:#e3b341;box-shadow:0 0 0 1px rgba(227,179,65,.25)}
.ch{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;margin-bottom:6px}
.ch .id{font-size:13px;font-weight:700;color:#0d1117;background:#58a6ff;border-radius:5px;padding:2px 9px}
.ch .id.gold{background:#e3b341}
.ch .nm{font-size:18px;font-weight:700}
.ch .sc{margin-left:auto;font-size:22px;font-weight:700;color:#e3b341}
.ang{color:#7d8590;font-size:13px;margin-bottom:12px}
.bars{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:8px 22px;margin:12px 0}
.bar{font-size:12px}
.bar .t{display:flex;justify-content:space-between;color:#8b949e}
.bar .t b{color:#e6edf3}
.bar .g{height:6px;background:#21262d;border-radius:3px;margin-top:4px;overflow:hidden}
.bar .g i{display:block;height:100%;background:linear-gradient(90deg,#1f6feb,#58a6ff);border-radius:3px}
.bar.hi .g i{background:linear-gradient(90deg,#d29922,#e3b341)}
.bar.lo .g i{background:linear-gradient(90deg,#8b3a3a,#da3633)}
ul{margin:8px 0 8px 18px;font-size:13px;color:#adbac7}
li{margin:3px 0}
table{width:100%;border-collapse:collapse;font-size:13px;margin-top:10px}
th,td{border-bottom:1px solid #21262d;padding:8px 10px;text-align:left}
th{color:#7d8590;font-weight:600;font-size:12px;background:#11161d}
tr:hover td{background:#1c2128}
td.num{text-align:right;font-variant-numeric:tabular-nums}
.mini{font-size:12px;color:#7d8590}
.tagrow{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0}
.tag{background:#1c2128;border:1px solid #30363d;border-radius:5px;padding:2px 9px;font-size:12px;color:#adbac7}
.tag.k{border-color:#1f6feb;color:#79c0ff}
.sec{margin-top:16px;padding-top:14px;border-top:1px dashed #21262d}
.sec h4{font-size:13px;color:#e3b341;margin-bottom:6px;font-weight:700}
.sec p{font-size:13px;color:#adbac7}
.warn{background:#2d1a1a;border:1px solid #5c2b2b;border-radius:8px;padding:12px 14px;font-size:13px;color:#ffa198;margin-top:12px}
.note{background:#12211a;border:1px solid #23503a;border-radius:8px;padding:12px 14px;font-size:13px;color:#7ee787;margin-top:12px}
.exp{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:14px;margin-top:12px}
.exp .b{background:#11161d;border:1px solid #21262d;border-radius:10px;padding:14px}
.exp .b h5{font-size:13px;margin-bottom:8px;display:flex;justify-content:space-between}
.exp .b h5 span{color:#e3b341;font-weight:700}
.foot{color:#6e7681;font-size:12px;margin-top:30px;text-align:center}
</style>
</head>
<body>
<div class="wrap">
  <h1>床垫爆品孵化决策大屏 · 三阶段全链路</h1>
  <div class="sub">数据源 298 款有效商品 / 4594 条 SKU / 300 张主图 OCR　｜　赛道竞选 → 爆品设计 → 专家评审</div>

  <div class="kpis" id="kpis"></div>

  <div class="tabs">
    <div class="tab on" data-p="p1">阶段 1 · 赛道竞选</div>
    <div class="tab" data-p="p2">阶段 2 · 爆品设计</div>
    <div class="tab" data-p="p3">阶段 3 · 专家评审</div>
  </div>

  <div class="panel on" id="p1"></div>
  <div class="panel" id="p2"></div>
  <div class="panel" id="p3"></div>

  <div class="foot">所有 Top50 率 / 排名中位 / 渗透率 / SKU 拥挤度均由 298 款榜单实算；BOM 成本与毛利率为设计侧估算值。</div>
</div>

<script>
const D = __DATA__;

const esc = s => String(s).replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
const bar = (label, v, max) => {
  const pct = Math.max(0, Math.min(100, v / max * 100));
  const cls = v / max >= 0.8 ? 'hi' : (v / max <= 0.3 ? 'lo' : '');
  return `<div class="bar ${cls}"><div class="t"><span>${esc(label)}</span><b>${v}</b></div>
          <div class="g"><i style="width:${pct}%"></i></div></div>`;
};

/* ---------- KPI ---------- */
const bestTrack = D.track.tracks.find(t => t.id === D.track.best);
const champ = D.review.results.find(r => r.id === D.review.champion);
document.getElementById('kpis').innerHTML = `
  <div class="kpi"><div class="l">最佳赛道</div><div class="v gold">${esc(bestTrack.id)}</div><div class="n">${esc(bestTrack.name)}</div></div>
  <div class="kpi"><div class="l">赛道综合得分</div><div class="v">${bestTrack.total}</div><div class="n">5 个方案竞选胜出</div></div>
  <div class="kpi"><div class="l">赛道头部命中率</div><div class="v">${bestTrack.top50_rate}%</div><div class="n">全站基线 16.4%</div></div>
  <div class="kpi"><div class="l">赛道排名中位</div><div class="v">${bestTrack.rank_median}</div><div class="n">命中 ${bestTrack.n} 款 / 占全站 ${bestTrack.supply_pct}%</div></div>
  <div class="kpi"><div class="l">终极爆品</div><div class="v gold">${esc(champ.id)}</div><div class="n">${esc(champ.name)}</div></div>
  <div class="kpi"><div class="l">爆品综合得分</div><div class="v">${champ.total}</div><div class="n">四专家加权</div></div>`;

/* ---------- 阶段 1 ---------- */
const L = D.track.dim_label;
let h1 = `<div class="card"><div class="ch"><span class="nm">竞选总览</span></div>
  <table><thead><tr><th>名次</th><th>方案</th><th>切入角度</th>
  <th class="num">命中款数</th><th class="num">排名中位</th><th class="num">Top50率</th>
  <th class="num">价格中位</th><th class="num">CR3</th><th class="num">总分</th></tr></thead><tbody>`;
D.track.tracks.slice().sort((a,b)=>b.total-a.total).forEach((t,i)=>{
  h1 += `<tr><td>${i+1}</td><td><b>${esc(t.id)}</b> ${esc(t.name)}</td><td class="mini">${esc(t.angle)}</td>
    <td class="num">${t.n}</td><td class="num">${t.rank_median}</td><td class="num">${t.top50_rate}%</td>
    <td class="num">¥${t.price_median}</td><td class="num">${t.cr3}%</td>
    <td class="num"><b style="color:#e3b341">${t.total}</b></td></tr>`;
});
h1 += `</tbody></table></div>`;

D.track.tracks.slice().sort((a,b)=>b.total-a.total).forEach(t=>{
  const win = t.id === D.track.best;
  h1 += `<div class="card ${win?'win':''}">
    <div class="ch"><span class="id ${win?'gold':''}">${esc(t.id)}</span><span class="nm">${esc(t.name)}</span>
      <span class="sc">${t.total}</span></div>
    <div class="ang">${esc(t.angle)}${win?'　★ 胜出方案':''}</div>
    <ul>${t.logic.map(x=>`<li>${esc(x)}</li>`).join('')}</ul>
    <div class="bars">${Object.keys(t.dims).map(k=>bar(L[k], t.dims[k], 10)).join('')}</div>
    <div class="mini">命中 ${t.n} 款（占全站 ${t.supply_pct}%）｜SKU 合计 ${t.sku_total} 条｜
      排名中位 ${t.rank_median}｜价格中位 ¥${t.price_median}｜Top50 ${t.top50} 款（${t.top50_rate}%）｜
      Top100 率 ${t.top100_rate}%｜CR3 ${t.cr3}%｜SKU 中位 ${t.sku_median}｜价宽比 ${t.span_median}</div>
    <div class="tagrow">${t.top_brands.map(b=>`<span class="tag">${esc(b[0])} ×${b[1]}</span>`).join('')}</div>
    ${win ? `<div class="sec"><h4>赛道现有玩家（前 12）</h4>
      <table><thead><tr><th class="num">排名</th><th>品牌</th><th class="num">中位价</th><th class="num">SKU</th><th>材质</th><th>功能</th></tr></thead><tbody>
      ${t.members.slice(0,12).map(m=>`<tr><td class="num">${m.rank}</td><td>${esc(m.brand)}</td>
        <td class="num">¥${Math.round(m.price)}</td><td class="num">${m.sku}</td>
        <td class="mini">${esc(m.mats.join(' / '))}</td><td class="mini">${esc(m.funcs.join(' / '))}</td></tr>`).join('')}
      </tbody></table></div>` : ''}
  </div>`;
});
document.getElementById('p1').innerHTML = h1;

/* ---------- 阶段 2 ---------- */
let h2 = `<div class="card"><div class="ch"><span class="nm">设计硬约束</span></div>
  <ul><li>SKU 数控制在 9~15 个 —— 该档位全站 Top50 率 26.8%，为各档最高；赛道头部款 SKU 中位为 12</li>
  <li>价宽比(最高价/最低价) 控制在 1.5~2.5 —— 超过 2.5 后 Top50 率从 20.8% 跌至 9.3%</li>
  <li>主图标价策略优先「精准对标」——贴最低 SKU 门槛价，全站该策略排名中位 60，优于高配锚定 115 与深度补贴 256</li></ul></div>`;

D.products.forEach(p => {
  const win = p.id === D.review.champion;
  const ladder = p.ladder.slice().sort((a,b)=>a.price-b.price);
  h2 += `<div class="card ${win?'win':''}">
    <div class="ch"><span class="id ${win?'gold':''}">${esc(p.id)}</span><span class="nm">${esc(p.name)}</span>
      <span class="sc">¥${p.price_min}-${p.price_max}</span></div>
    <div class="ang">${esc(p.position)}</div>
    <div class="note"><b>切入缺口：</b>${esc(p.gap)}</div>

    <div class="sec"><h4>① 主图卖点</h4>
      <ul>${p.main_image_points.map(x=>`<li>${esc(x)}</li>`).join('')}</ul></div>
    <div class="sec"><h4>② 视觉背景</h4><p>${esc(p.visual)}</p></div>
    <div class="sec"><h4>③ 利益点</h4>
      <div class="tagrow">${p.benefits.map(x=>`<span class="tag k">${esc(x)}</span>`).join('')}</div></div>
    <div class="sec"><h4>④ 主图标价</h4><p><b style="color:#e3b341;font-size:18px">¥${p.main_image_price}</b>　${esc(p.price_anchor)}</p></div>
    <div class="sec"><h4>⑤ 内材构造（厚度 ${p.thickness}cm）</h4><p>${esc(p.construction)}</p></div>
    <div class="sec"><h4>⑥ SKU 文字与梯度定价</h4>
      <table><thead><tr><th class="num">价格</th><th class="num">毛利率</th><th>SKU 名称</th></tr></thead><tbody>
      ${ladder.map(s=>{
        const g = ((s.price - s.cost)/s.price*100).toFixed(1);
        const hit = s.price === p.main_image_price;
        return `<tr><td class="num"${hit?' style="color:#e3b341;font-weight:700"':''}>¥${s.price}${hit?' ◀主图':''}</td>
                <td class="num">${g}%</td><td>${esc(s.sku)}</td></tr>`;
      }).join('')}
      </tbody></table>
      <div class="mini" style="margin-top:8px">SKU ${p.sku_count} 个｜价宽比 ${p.span_ratio}｜中位价 ¥${p.price_median}｜毛利率中位 ${p.gross_margin}%（BOM 为设计估算）</div>
    </div>
  </div>`;
});
document.getElementById('p2').innerHTML = h2;

/* ---------- 阶段 3 ---------- */
const enames = D.review.experts.map(e=>e.name);
let h3 = `<div class="card"><div class="ch"><span class="nm">终极选拔结果</span></div>
  <div class="mini">专家权重：${D.review.experts.map(e=>e.name+' '+e.weight+'%').join('　｜　')}</div>
  <table><thead><tr><th>名次</th><th>方案</th>${enames.map(n=>`<th class="num">${esc(n)}</th>`).join('')}<th class="num">综合</th></tr></thead><tbody>`;
D.review.results.slice().sort((a,b)=>b.total-a.total).forEach((r,i)=>{
  h3 += `<tr><td>${i+1}</td><td><b>${esc(r.id)}</b> ${esc(r.name)}</td>
    ${enames.map(n=>`<td class="num">${r.detail[n].score.toFixed(1)}</td>`).join('')}
    <td class="num"><b style="color:#e3b341">${r.total}</b></td></tr>`;
});
h3 += `</tbody></table></div>`;

D.review.results.slice().sort((a,b)=>b.total-a.total).forEach(r=>{
  const win = r.id === D.review.champion;
  h3 += `<div class="card ${win?'win':''}">
    <div class="ch"><span class="id ${win?'gold':''}">${esc(r.id)}</span><span class="nm">${esc(r.name)}</span>
      <span class="sc">${r.total}</span></div>
    <div class="exp">
    ${enames.map(n=>{
      const d = r.detail[n];
      return `<div class="b"><h5>${esc(n)}<span>${d.score.toFixed(1)}/100</span></h5>
        ${Object.keys(d.dims).map(k=>bar(k+'（'+d.weights[k]+'%）', d.dims[k], 10)).join('')}
        <ul>${d.notes.map(x=>`<li>${esc(x)}</li>`).join('')}</ul></div>`;
    }).join('')}
    </div></div>`;
});
h3 += `<div class="card"><div class="ch"><span class="nm">决策提示</span></div>
  <div class="warn"><b>冠军方案的两个风险：</b>撞车规避度仅 1.20 分（全场最低）—— 赛道内已有 176 条 SKU 落在 ¥1399-2799，
  差异化完全押在「检测报告可视化」一个支点上；供应链得分仅 54.4 —— 10 个 SKU 的备货风险项只有 2.90 分，
  数据侧要的宽 SKU 矩阵与供应链侧要的窄 SKU 直接冲突，只能靠首批小批量试销分摊。</div>
  <div class="note"><b>备选建议：</b>次席 P3 仅落后 1.69 分且供应链得分略高，若已有母婴/儿童供应链则更稳；
  P5 综合第 3，但拿下全场最高的供应链分 71.9（可卷包压缩、毛利中位 56.2%），适合作为并行的轻资产验证款。</div></div>`;
document.getElementById('p3').innerHTML = h3;

/* ---------- Tabs ---------- */
document.querySelectorAll('.tab').forEach(t=>{
  t.onclick = () => {
    document.querySelectorAll('.tab').forEach(x=>x.classList.remove('on'));
    document.querySelectorAll('.panel').forEach(x=>x.classList.remove('on'));
    t.classList.add('on');
    document.getElementById(t.dataset.p).classList.add('on');
  };
});
</script>
</body>
</html>
"""

out = HTML.replace("__DATA__", DATA)
path = os.path.join(BASE, "爆品孵化决策大屏.html")
with open(path, "w", encoding="utf-8") as f:
    f.write(out)
print("写出:", path, len(out), "字符")
