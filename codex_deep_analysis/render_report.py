"""Render one auditable source of results into Markdown, offline HTML and CSV."""
import html
import re
from pathlib import Path

HERE=Path(__file__).resolve().parent

def n(v,d=1): return '未知' if v is None else f'{v:,.{d}f}'
def pct(v,d=1): return '未知' if v is None else f'{v*100:.{d}f}%'
def money(v): return '未知' if v is None else '¥'+n(v,2)
def table(headers,rows):
    clean=lambda v:str(v).replace('|','／').replace('\n',' ')
    return '\n'.join(['|'+'|'.join(headers)+'|','|'+'|'.join(['---']*len(headers))+'|']+
                     ['|'+'|'.join(clean(v) for v in row)+'|' for row in rows])

def render(data,cfg,rows,members):
    from pipeline import csvout
    t=data['tracks'];a=data['audit'];winner=t[0];strict=data['strict_dual'];product_data=data.get('products',{})
    complete=product_data.get('status')=='complete';ps=product_data.get('ranking',[])
    champion=ps[0] if complete else None
    lead=(champion['score']-ps[1]['score']) if complete else None
    parts=['# 床垫 Top300：赛道竞选、产品落子与终极选拔',
           '> Codex 独立分析 · 版本 2.0-audited · 分析日期 2026-09-17。源数据采集日期与榜单定义未提供，不能视为当日市场。',
           '## 决策摘要',
           f"赛道优胜：{winner['id']} {winner['name']}，综合决策分 {n(winner['score'])}/100；候选预算 ¥1,500–3,000。{cfg['assumption']}",
           (f"产品终选：{champion['id']} {champion['name']}，四角色综合分 {n(champion['score'])}/100，拟定主图价 {money(champion['hero_price'])}，对应 {champion['hero_spec']}。这是优先打样/小批试销方案，不是已被销量验证的爆品。" if champion else '产品终选尚待四角色统一评审完成；下文产品方案及成本测算仍为候选。'),
           (f"终选可信边界：第一名仅领先第二名 {ps[1]['id']} {ps[1]['name']} {n(lead,2)}分。两款应列为同一优先级对比打样；在当前固定权重下指定{champion['id']}为终选，不能把小分差解释成确定性优势。" if complete else '评审未齐全前不比较产品名次。'),
           f"关键证据：T1 宽口径 {winner['n']} 商品、{winner['shops']} 店、{winner['sku_n']} 去重命中 SKU；Top50 {winner['top50']} 款，占 {pct(winner['top50_rate'])}。严格双面子集 {strict['n']} 商品、{strict['shops']} 店，Top50 {strict['top50']} 款；其最大店份额 {pct(strict['largest_shop_share'])}，需正视品牌集中。",
           '本次最重要的数据修正：主图 OCR 与商品排名存在明确错配，已彻底取消按排名连接。SKU 清洗、套餐隔离和价格重算先于评分；主图只使用图片池整体标签频次。旧稿中的预置产品分已废弃。',
           '## 0. 数据审计与可用边界',
           table(['项目','核验结果'],[
               ['商品 / 原始SKU',f"{a['raw_products']} / {a['raw_skus']}"],
               ['完全相同 SKU 名+价格的重复行（诊断数）',a['raw_exact_duplicate_rows']],
               *[[k,v] for k,v in a['mutually_exclusive_cleaning_counts'].items()],
               ['清洗后 SKU / 有效价格商品',f"{a['clean_skus']} / {a['clean_products']}"],
               ['保留行中可识别整垫厚度',f"{a['height_known']} / {a['clean_skus']}"],
               ['保留行中套餐标记 / 定制标记',f"{a['bundle_flags']} / {a['custom_flags']}（可重叠）"],
               ['图片记录 / 有效图片 / 解析价格',f"{a['image_records']} / {a['valid_images']} / {a['main_image_prices']}"],
               ['HTML 内嵌主图数据与独立JSON一致',str(a['embedded_images_equal_json'])],
               ['重复商品ID',len(a['duplicate_item_ids'])]]),
           '清洗排除原因互斥：先排无效价格，再排低于100元待核价格、定金/差价/单床架，最后去除同商品内空白归一后的SKU名+价格重复。完全重复诊断数与排除计数不是同一统计口径。未删除原数据；每一行保留 Rxxx-Sxxx 来源编号及排除原因。低于100元仅标记待核验，不认定为错误或虚假。',
           '套餐/定制是第二层口径：T1–T4排除，T5允许整套智能系统但排除明确单床架。没有明确标记的赠品/套装仍可能漏出。商品ID互异仍可能属于同一品牌系列，不能视作独立消费者样本。',
           '原页面以1.8m SKU为口径，但部分“默认款/标准1.8m”是抓取回填，尺寸不能全部独立验证。新产品拟价统一标明真实180×200cm；宿舍赛道结论仅限本样本中的规格，不外推到0.9m成交市场。',
           '### 已确认的主图错配样例',
           table(['原排名键','HTML商品/店铺','JSON OCR摘录'],[[v['rank'],v['shop']+' / '+v['title'],v['ocr'][:115]] for v in a['image_mismatch_examples']]),
           '目前没有商品ID—原图文件—OCR的可靠映射，也没有原图可逐张重建；不按品牌猜测回填。主图标签、主图价及视觉形式不参与商品筛选、排名对比或单品价格差分析。图片池标签也是既有自动识别结果，例如“AI陪伴”不必然是智能电动功能，不能把标签当检测结果。',
           '### 价格与排名的正确解释',
           '排名仅是提供的数据中的顺序，缺少榜单指标、观察窗口与销量。低排名数值不等于某项功能导致热卖；价格是记录价格，包含多种优惠条件。折扣只作促销强度描述，既不是实际成交占比，也不是毛利空间。没有销量权重，因此“SKU中位价”不能称为消费者支付中位数。',
           f"原HTML汇总SKU中位价 ¥760.33；本次清洗并排除套餐/定制后为 {money(data['baseline']['clean_sku_median'])}。分析赛道时先在商品内计算命中SKU中位价，再对商品等权取中位，避免几十个SKU的单店放大价格带。",
           table(['价格带（左闭右开）','命中商品','去重SKU','Top50商品','商品等权价中位'],[[b['band'],b['n'],b['sku_n'],b['top50'],money(b['median_price'])] for b in data['baseline']['bands']]),
           '一个商品可出现在多个价格带；这些商品数不能相加当作市场份额。',
           '## 1. 五个多维赛道方案竞选',
           '### 1.1 候选规则：人群/场景 × 价格 × 功能结构 × 厚度',
           table(['方案','价格闭区间','整垫厚度','切入逻辑'],[[x['id']+' '+x['name'],f"{x['price'][0]}–{x['price'][1]}",'系统规格' if x['height'] is None else f"{x['height'][0]}–{x['height'][1]}cm",x['angle']] for x in cfg['tracks']]),
           '每一条命中记录须在“同一商品标题+当前单条SKU名称”同时满足所有关键词组，并满足本SKU价格；不跨其他SKU拼接功能，不使用OCR。标题级词只代表该商品系列有宣称，不保证每个变体都具有该功能，命中明细是人工核对线索。',
           '厚度优先读SKU中明确总厚/厚度及规格位置，只取整垫候选值，不把全商品的乳胶层、黄麻层厚度取平均。未知厚度保留并标记；另跑必须识别厚度的严格版本。上下界闭区间。所有关键词正则完整保存在 scoring_config.json。',
           table(['方案','必须同时命中的关键词组'],[[x['id'],' AND '.join('('+g+')' for g in x['groups'])] for x in cfg['tracks']]),
           '### 1.2 五维评价标准与五套权重',
           '可观测的三维占各权重方案60%–80%；其余为明确公开的工程/表达先验判断。没有成本和销量，因此不制造“利润分”或“需求规模”。证据广度只表示榜单样本覆盖。',
           table(['维度','计算规则（0–100）','解释'],[
               ['需求验证','60×(301−商品排名中位)/300 + 40×min(Top50比例/0.40,1)','全榜Top50基准为16.7%；40%是评分饱和锚点，非经验概率'],
               ['证据广度','60×min(商品数/60,1)+40×min(店铺数/25,1)','60商品/25店为决策锚点；避免SKU数量直接充当容量'],
               ['竞争可进入性','60×(1−店铺HHI)+40×(1−最大店份额)','HHI=各店商品份额平方和；不能衡量广告竞争和品牌壁垒'],
               ['供应可执行性','材料成熟/结构装配/履约/质检售后四项均值','人工工程判断，不是实际工厂能力'],
               ['表达可验证性','问题清晰/演示直观/差异表达/宣称证据四项均值','人工内容判断，不是CTR或转化率']]),
           table(['权重方案']+cfg['dimensions'],[[name]+[str(w)+'%' for w in weights] for name,weights in cfg['lenses'].items()]),
           table(['赛道','供应4子项','表达4子项','判断依据'],[[x['id'],str(x['supply']),str(x['proof']),x['assumption_reason']] for x in cfg['tracks']]),
           '各权重方案分=五维加权和；原始综合分=五套分均值×75%+最低一套分×25%。证据调整分=50+n/(n+20)×(原始综合分−50)，n为命中商品数；空样本为0。这是人为设定的保守证据惩罚，不是贝叶斯后验、置信区间或成功概率。候选得分保留全精度计算，展示一位小数。',
           '### 1.3 赛道排名与基础指标',
           table(['名次','赛道','商品/SKU/店','中位排名','Top50占比','等权价中位','最大店份额','综合分'],[[i,x['id']+' '+x['name'],f"{x['n']}/{x['sku_n']}/{x['shops']}",n(x['median_rank']),pct(x['top50_rate']),money(x['median_price']),pct(x['largest_shop_share']),n(x['score'])] for i,x in enumerate(t,1)]),
           table(['赛道']+cfg['dimensions'],[[x['id']]+[n(x['dimension_scores'][k]) for k in cfg['dimensions']] for x in t]),
           table(['赛道']+list(cfg['lenses'])+['原始综合','证据调整'],[[x['id']]+[n(x['lens_scores'][k]) for k in cfg['lenses']]+[n(x['raw_score']),n(x['score'])] for x in t]),
           '五类可重叠，不是互斥市场分区。标题关键词宽窄不同，排名是对所定义策略的比较，不能直接比较真实市场规模。',
           table(['重叠方案','交集商品数'],[[x['left']+'∩'+x['right'],x['products']] for x in data['overlap']]),
           '### 1.4 稳健性与反证',
           table(['情景','第一名','第一名样本','第一名分','第二名/分'],[[s['scenario'],s['ranking'][0]['id'],s['ranking'][0]['n'],n(s['ranking'][0]['score']),s['ranking'][1]['id']+' / '+n(s['ranking'][1]['score'])] for s in data['sensitivity']['scenarios']]),
           f"均衡权重独立乘0.8–1.2后归一，固定种子 {data['sensitivity']['seed']}，1000次第一名次数：{data['sensitivity']['weight_winners']}。这是所设扰动范围内的稳定性，不是统计置信度。未覆盖全部关键词变化、时间趋势或新竞争者。",
           f"T1收紧到双面/双睡感的子集：{strict['n']}款，Top30 {strict['top30']}款，Top50 {strict['top50']}款，中位排名 {n(strict['median_rank'])}，商品等权价 {money(strict['median_price'])}，HHI {n(strict['hhi'],3)}，最大店占 {pct(strict['largest_shop_share'])}。宽口径的分散竞争不能直接外推到最终双感产品。",
           '### 1.5 胜出与不选其余方案的原因',
           'T1有较好的排名表现、跨店样本和成熟基础结构；相对适合以单一清晰主张开发首款。它并非“无竞争蓝海”，需要用实规格标价、清晰睡感说明和可信结构证据争取转化。',
           'T3样本分散、制造简单，是本模型第二名；但排名表现弱、1.8m样本对宿舍核心尺寸代表性不足，低客单履约预算紧。T2有独立人群价值，但儿童适配与环保宣称验证成本更高。T4样本窄、信任投入较大。T5机械电控和售后能力要求显著超出常规首款床垫假设。以上是决策场景判断，已有成熟供应链/品牌的团队可能选择不同。',
           '### 1.6 直接竞品证据',
           '以下为T1排名最靠前的命中SKU，每个商品仅展示一条；可通过原链接复核（尚未联网验证当前在售状态）。']
    examples=[]
    for rank in sorted({r['rank'] for r in members[winner['id']]})[:15]:
        rs=[r for r in members[winner['id']] if r['rank']==rank]
        mid=sorted(rs,key=lambda r:abs(r['price']-(sum(x['price'] for x in rs)/len(rs))))[0]
        examples.append(mid)
    parts.append(table(['来源行','排名/店铺','SKU','记录价','整垫厚度'],[[r['row_id'],str(r['rank'])+'/'+r['shop'],r['sku_name'],money(r['price']),n(r['height'])] for r in examples]))
    csvout('重点竞品.csv',examples)
    parts+=['## 2. 胜出赛道的五款差异化落子',
            '以下为共同评审版本，全部面向T1成人主卧价带。主图价均对应180×200cm明确配置，未预设政府补贴、认证、100晚试睡或免费取旧。更便宜的梯度是另一配置，不能代替主图主销规格。层厚为未压缩的工程设计目标，总厚需打样检验，密度、ILD/硬度、弹簧线径/圈数/数量与公差均需供应商填写。',
            '双面翻转改变的是整张睡感；只有P5针对夫妻同一时刻左右不同软硬。该区别已经落实到主图、SKU和结构。']
    for p in sorted(ps,key=lambda p:p['id']):
        parts += [f"### {p['id']} {p['name']} · {p['position']}",
                  f"人群：{p['audience']}。问题边界：{p['problem']}。",
                  f"主图第一卖点：{p['hero']}。第二信息：{p['subhero']}。",
                  f"视觉背景与构图：{p['visual']}",
                  '利益点：'+'；'.join(p['benefits'])+'。',
                  f"主图标价：{p['hero_price_text']}；{p['hero_spec']}。",
                  f"SKU文字：`{p['sku_text']}`",
                  table(['内材由上到下','名义厚度cm'],[[name,h] for name,h in p['layers']]+[['总厚',p['height']]]),
                  '结构说明：'+p['construction_note'],
                  table(['梯度','拟价','明确配置'],[[x['name'],money(x['price']),x['detail']] for x in p['tiers']]),
                  '服务利益：'+p['service'],
                  '打样门槛：'+'；'.join(p['gates'])+'。',
                  f"数据支持（T1池内的相关词交集，不代表同构产品或销量）：{p['evidence']['n']}商品，{p['evidence']['shops']}店，Top50 {p['evidence']['top50']}款，商品等权价中位 {money(p['evidence']['median_price'])}。关键词组："+' AND '.join(p['evidence_groups'])+'。']
    parts+=['### 2.6 经济模型：先算预算，不把折扣当毛利',
            '制造包装成本、单均履约费、平台费率、售后准备金、广告费率均为待报价的情景输入。贡献=售价−制造包装−履约−售价×(平台费率+售后准备率+广告费率)。这是未计固定费用与所得税等税务影响的运营贡献估算，不等于会计毛利/净利润；退款收入、平台优惠和税票须用真实账单替换后再做财务核算。',
            table(['情景','制造包装','履约','平台费','售后准备','广告'],[['顺利','基准×0.9','基准−30元','6%','5%','15%'],['基准','产品输入','产品输入','6%','8%','20%'],['压力','基准×1.15','基准+50元','6%','12%','28%']]),
            table(['产品','拟价','假设制造包装','基准履约','基准贡献/率','压力贡献','15%目标制造包装上限','15%目标CAC上限'],[[p['id'],money(p['hero_price']),money(p['cost_assumption']),money(p['freight_assumption']),money(p['economics'][1]['contribution'])+' / '+pct(p['economics'][1]['contribution_rate'],2),money(p['economics'][2]['contribution']),money(p['economics'][1]['max_manufacturing_packaging_at_15pct']),money(p['economics'][1]['max_cac_at_15pct'])] for p in sorted(ps,key=lambda p:p['id'])]),
            '15%只是本方案预设贡献目标。不能用试算正贡献证明可赚钱：若供应商报价、广告和退运成本触及压力情景，可能转负。优先核成本与CAC上限，再决定是否按拟价投放。服务费用没有明确覆盖时，不上主图承诺。',
            '## 3. 多智能体专家终极选拔',
            '四个独立角色基于同一五款候选和同一评分配置评审；原始意见保存在 expert_reviews。各子项0–100分：50表示证据/可执行性不足，70表示具可测试基础，85表示相对较强，95以上需要充分验证；实际专家分为判断，不是检测或真实转化。数据30%、操盘25%、供应链25%、视觉20%，不按主代理偏好覆盖独立评分。',
            table(['角色','角色权重','内部子项权重'],[[role,str(cfg['product_weights'][role])+'%', '；'.join(k+' '+str(v)+'%' for k,v in rub.items())] for role,rub in cfg['product_rubric'].items()])]
    if complete:
        parts.append(table(['名次','产品']+list(cfg['product_weights'])+['总分'],[[i,p['id']+' '+p['name']]+[n(p['expert_scores'][role]) for role in cfg['product_weights']]+[n(p['score'])] for i,p in enumerate(ps,1)]))
        parts.append('### 3.1 全部评审分数、理由与反对意见')
        for p in ps:
            parts += [f"#### {p['id']} {p['name']}",table(['角色','子项分','加权分','依据','主要反对意见','上线门槛'],[[r['role'],'；'.join(k+':'+str(v) for k,v in r['scores'].items()),n(r['total']),r['reason'],r['objection'],r['gate']] for r in p['reviews']])]
        parts+=['### 3.2 终选稳健性',
                table(['权重情景','第一名','P1','P2','P3','P4','P5'],[[s['scenario'],s['winner']]+[n(s['scores']['P'+str(i)]) for i in range(1,6)] for s in product_data['sensitivity']['scenarios']]),
                f"角色权重±20%乘数扰动1000次：{product_data['sensitivity']['weight_winners']}；固定权重、各角色判断分独立±5分扰动1000次：{product_data['sensitivity']['score_jitter_winners']}。种子20260917，均不是成功概率。",
                f"第一、二名分差仅{n(lead,2)}分，低于专家判断的合理精度。产品冠军依赖权重；相较之下，T1赛道在已测试情景中较稳定。务必把‘选赛道相对稳定’和‘选具体款存在分歧’分开理解。",
                '### 3.3 终极方案与执行边界',
                f"优先打样：{champion['id']} {champion['name']}。主图使用“{champion['hero']}”，拟价 {money(champion['hero_price'])} 对应 {champion['hero_spec']}。优势在于需求证据、结构、可解释卖点和试销成本之间的相对平衡；最关键的反对意见仍以上述独立评审为准。",
                f"先同时对比打样{champion['id']}与{ps[1]['id']}，用真实成本、盲测睡感、咨询/误购和小批转化打破近似平局。若尚无这些新证据，按固定权重选择{champion['id']}；不能为了显得结论明确而抹去分歧。",
                '首发只锁定主销180×200cm单规格；150×200cm需另核报价再扩，不复制本数据的尺寸回填。三档价格是产品路线图，不同时铺满库存。侧重一个主张做小批测试，再按供应门槛推进差异化款；未报价前不承诺量产。',
                f"对优胜方案按基准输入，15%贡献目标对应制造包装上限 {money(champion['economics'][1]['max_manufacturing_packaging_at_15pct'])}、CAC上限 {money(champion['economics'][1]['max_cac_at_15pct'])}。压力贡献 {money(champion['economics'][2]['contribution'])}，因此推荐是有成本与售后门槛的推荐。"]
    else:
        parts.append('待完成角色：'+', '.join(product_data.get('missing_reviews',[]))+'。在评审齐全之前不宣布产品冠军。')
    parts+=['## 4. 验证计划与上线清单',
            table(['阶段','操作','可执行门槛'],[
                ['供应报价','至少2家按同一BOM与180×200规格报价；拆制造、包装、区域运费、逆向运费、质保','代入经济模型，满足选定贡献目标；不得为满足价格删改未告知的材料'],
                ['工程样品','标定各层尺寸/密度/弹簧规格；检查整垫高度、硬度、异响、耐久、边缘承托','工厂与第三方制定适用标准和检验条件；未检不得上对应性能宣称'],
                ['睡感访谈','以成人目标人群盲测正反面，记录体重区间、偏好与不适反馈','小样本只用来发现缺陷，不宣传舒适率/护脊率'],
                ['主图AB','同配置、同售价、同人群、同预算，比较翻面主张和结构主张，其他元素固定','先小额获取CTR/CVR基线，再按基线计算样本量；不凭几十点击定赢家'],
                ['小批履约','预设样品批量和总亏损预算，追踪上楼失败、破损、异响、退运、重发','预算由实际报价与团队资金确定；未获得数据前不凭本报告放大投放'],
                ['扩量复核','按真实成交价、账单、CAC、退款后净收入和逆向成本重算','至少完成首轮售后观察；贡献未达标则改价/改结构/缩量']]),
            '主图顺序建议：一个明确产品承诺 → 一个可见结构证据 → 一项可兑现服务 → 一个规格对应价格。A类必须写明面料适用范围；整垫0胶、抗菌、乳胶含量、透气/静音效果等须有对应资料。竞争者宣称和自动OCR标签不能变成自家产品证明。',
            '## 5. 主图图片池洞察（不关联商品排名）',
            '296条有效图片元数据中按标签去重计数，可多标签；占比之和可超过100%。未查看原始图片，不进行美学效果或真实转化率判断。图片池中缺少某表达不等于需求蓝海。',
            table(['标签类别','标签','图片数','有效图片占比'],[[{'selling_points':'卖点','marketing_text':'权益','visual_format':'形式'}[k],x['label'],x['count'],pct(x['share'])] for k,rs in data['images'].items() for x in rs]),
            '本次仅把整体表达惯例用于主图信息组织；不使用“Top30更常采用某形式”等失去映射基础的推断，也不沿用OCR解析价格与同排名SKU的价差。',
            '## 6. 复跑、审计与后续数据',
            '在项目根目录执行：',
            '```powershell\npython .\\codex_deep_analysis\\analyze_market.py\npython .\\codex_deep_analysis\\test_analysis.py\n```',
            '只读取根目录HTML/JSON；所有代码、配置、评审、报告和明细在 codex_deep_analysis 内。scoring_config.json控制候选与权重，product_concepts.json控制产品与经济假设，expert_reviews为独立意见；脚本不调用模型自动刷新专家意见，修改方案后须重新评审。',
            'outputs/全量SKU清洗台账.csv保留每条原始记录与排除原因；赛道命中明细.csv保留过滤命中；analysis_result.json保留公式输入、全分数、敏感性和源文件SHA-256；重点竞品.csv带原商品链接。所有CSV为UTF-8 BOM，可用Excel打开。',
            '下一次提高结论质量最需要：商品ID与原图/OCR映射、榜单采集时间/指标、近30/90天销量与成交价、广告CAC、退货原因与逆向成本、实际BOM和供应报价。缺少这些时，本报告只能进行条件化选品决策，不能承诺爆发销量。']
    markdown='\n\n'.join(parts)+'\n'
    (HERE/'深度分析报告.md').write_text(markdown,encoding='utf-8')
    summary=['# 三阶段决策摘要',parts[3],parts[4],parts[5],parts[6],
             '## 赛道排名',table(['赛道','分数','样本商品'],[[x['name'],n(x['score']),x['n']] for x in t]),
             '## 产品终选',table(['产品','拟定主销价','综合分'],[[p['id']+' '+p['name'],money(p['hero_price']),n(p.get('score'))] for p in ps]),
             '## 必须记住的边界','主图OCR已确认错配，不按排名连接；成本、价格和产品表现为待验证设计。终选表示优先打样，小批测试和供应报价通过后才能放量。',
             '完整理由、原始评审、每款结构/主图/SKU/梯度价格、敏感性与成本压力测试见《深度分析报告.md》。']
    (HERE/'决策摘要.md').write_text('\n\n'.join(summary)+'\n',encoding='utf-8')
    if ps:
        csvout('产品方案与评分.csv',[{**{k:p[k] for k in ['id','name','hero_price','hero_spec','hero','subhero','sku_text','height','score']},**p['expert_scores'],'evidence_products':p['evidence']['n']} for p in ps])
        csvout('经济模型情景.csv',[{'product_id':p['id'],**e} for p in ps for e in p['economics']])
        csvout('产品专家评审.csv',[{'product_id':p['id'],**r} for p in ps for r in p['reviews']])
    (HERE/'index.html').write_text(to_html(markdown),encoding='utf-8')

def inline(text):
    text=html.escape(text)
    return re.sub(r'`([^`]+)`',r'<code>\1</code>',text)

def to_html(markdown):
    lines=markdown.splitlines();out=[];nav=[];i=0
    while i<len(lines):
        line=lines[i]
        if not line.strip(): i+=1;continue
        if line.startswith('```'):
            code=[];i+=1
            while i<len(lines) and not lines[i].startswith('```'): code.append(lines[i]);i+=1
            out.append('<pre><code>'+html.escape('\n'.join(code))+'</code></pre>');i+=1;continue
        if line.startswith('|'):
            headers=[x.strip() for x in line.strip('|').split('|')];i+=2;body=[]
            while i<len(lines) and lines[i].startswith('|'):
                body.append('<tr>'+''.join('<td>'+inline(x.strip())+'</td>' for x in lines[i].strip('|').split('|'))+'</tr>');i+=1
            out.append('<div class="table"><table><thead><tr>'+''.join('<th>'+inline(x)+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join(body)+'</tbody></table></div>');continue
        m=re.match(r'^(#{1,4}) (.*)',line)
        if m:
            level=len(m[1]);anchor=f'section-{len(out)}'
            if level==2:nav.append(f'<a href="#{anchor}">{inline(m[2])}</a>')
            out.append(f'<h{level} id="{anchor}">{inline(m[2])}</h{level}>')
        elif line.startswith('>'):out.append('<p class="meta">'+inline(line[1:].strip())+'</p>')
        else:out.append('<p>'+inline(line)+'</p>')
        i+=1
    return '''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Codex床垫深度决策报告</title><style>
    :root{color-scheme:light;--ink:#202a31;--muted:#596773;--line:#d7dfe1;--accent:#155a50}*{box-sizing:border-box}body{margin:0;background:#f7f8f5;color:var(--ink);font:16px/1.8 system-ui,'Microsoft YaHei',sans-serif}header{background:#173e38;color:#fff;padding:24px max(24px,calc((100vw - 1120px)/2));letter-spacing:.1em}main{max-width:1180px;margin:auto;padding:26px 30px 80px}nav{display:flex;flex-wrap:wrap;gap:8px 20px;padding:20px 0;border-bottom:1px solid var(--line)}nav a{font-size:14px;color:var(--accent);text-decoration:none}h1{font-size:34px;line-height:1.4;margin-top:30px}h2{margin:56px 0 18px;padding-top:16px;border-top:2px solid var(--accent);font-size:25px}h3{font-size:20px;margin-top:32px}h4{font-size:18px}p{max-width:100%;margin:14px 0}.meta{color:var(--muted);font-size:14px}.table{overflow:auto;margin:20px 0;background:#fff;border:1px solid var(--line)}table{border-collapse:collapse;width:100%;font-size:14px;min-width:640px}td,th{border-bottom:1px solid var(--line);padding:12px 14px;text-align:left;vertical-align:top;min-width:75px}th{background:#e5eeeb;font-weight:600}td{overflow-wrap:anywhere}tbody tr:nth-child(even){background:#f6f9f8}code{font:14px/1.6 ui-monospace,monospace;overflow-wrap:anywhere}pre{overflow:auto;background:#e8eeea;padding:18px;border-left:3px solid var(--accent)}@media(max-width:600px){main{padding:16px}h1{font-size:27px}h2{font-size:23px}td,th{padding:9px}nav{gap:10px}}@media print{header,nav{display:none}body{background:#fff;font-size:11pt}main{max-width:none;padding:0}.table{overflow:visible}table{min-width:0;font-size:8pt}h2,h3,h4{break-after:avoid}tr{break-inside:avoid}pre{white-space:pre-wrap}}
    </style></head><body><header>CODEX · 床垫市场决策研究</header><main><nav>'''+''.join(nav)+'</nav>'+''.join(out)+'</main></body></html>'
