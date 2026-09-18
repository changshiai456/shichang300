# -*- coding: utf-8 -*-
"""
Step4 阶段2：爆品落子设计
在最佳赛道 T1(1500-2000元腰部护脊主力) 内落地 5 款差异化产品。
每款含：主图卖点 / 视觉背景 / 利益点 / 主图标价 / SKU文字 / 内材构造 / 梯度定价。

两条硬约束（来自 step1/step3 实测）：
  · SKU 数控制在 9~15 个 —— 该档位全站 Top50 率 26.8% 最高，赛道头部款 SKU 中位为 12
  · 价宽比(max/min) 控制在 1.5~2.5 —— 超过 2.5 后 Top50 率从 20.8% 跌到 9.3%
标注说明：
  tags_*  与全站 300 款可比，评审阶段用真实 Top50 率回算；cost 为设计侧 BOM 估算值。
输出 products.json / design_report.txt
"""
import json, os, sys, statistics as st

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = []


def p(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    enc = sys.stdout.encoding or "utf-8"
    print(s.encode(enc, errors="replace").decode(enc, errors="replace"))


PRODUCTS = [
    {
        "id": "P1",
        "name": "云岩 · 零胶双睡感主力款",
        "gap": "赛道内 0胶渗透已达 95.2% 但全部停留在文案层；「质检认证与绿标背书」视觉全站 Top50 率 31.8% 为各视觉形式之首，本赛道渗透仅 9.5%",
        "position": "赛道价格中位正面强攻位，用可视化检测报告把「0胶」从口号变成证据",
        "main_image_points": [
            "整垫0胶水 · 附SGS甲醛检出报告编号",
            "一垫两睡感：A面偏硬护脊 / B面适中释压",
            "25cm 独立袋弹簧 + 3cm 天然乳胶",
        ],
        "visual": "冷白实验室台面 + 检测报告卡实拍置于垫面右下 + 绿色环保认证角标 + 结构剖面小图，弃用满屏红黄大字报",
        "benefits": ["整垫0胶·检测报告随货", "180天免费试睡", "10年弹簧质保", "送装一体入户"],
        "main_image_price": 1399,
        "price_anchor": "精准对标引流：主图价 = 最低 SKU 门槛价（全站该策略排名中位 60，为四种标价策略最优）",
        "tags_selling": ["0胶水环保", "双面双睡感", "人体工学护腰护脊"],
        "tags_marketing": ["官方正品权威背书", "免费试睡保障", "超长弹簧质保", "免费送装一体"],
        "tags_visual": ["质检认证与绿标背书"],
        "tags_funcs": ["0胶/无胶", "透气", "分区支撑"],
        "tags_materials": ["弹簧", "乳胶", "黄麻"],
        "thickness": 25,
        "construction": "A类针织面料 → 1.5cm 3D透气网 → 3cm 天然乳胶(A面) / 2cm 黄麻(B面) → 5区独立袋弹簧(2.0mm线径/¢6cm) → 环保毡 → 侧围3D透气带；全结构热熔无胶工艺",
        "ladder": [
            {"sku": "云岩 Lite【偏硬护脊/22CM】入门0胶·学生青年首选", "price": 1399, "cost": 640},
            {"sku": "云岩 儿童版【偏硬/20CM】A类母婴面料·青少年护脊", "price": 1499, "cost": 680},
            {"sku": "云岩 标准版【双睡感/25CM】整垫0胶·检测报告随货", "price": 1699, "cost": 780},
            {"sku": "【卧室套装】云岩标准版 + A类抗菌床笠*1", "price": 1799, "cost": 830},
            {"sku": "云岩 标准版 加宽【双睡感/25CM·1.8×2.0m】大床型", "price": 1899, "cost": 870},
            {"sku": "云岩 Pro【双睡感/26CM】乳胶加厚至5cm·五区升级", "price": 1999, "cost": 920},
            {"sku": "云岩 Pro 0胶Plus【双睡感/26CM】面层可拆晾晒", "price": 2199, "cost": 1010},
            {"sku": "云岩 Max【双睡感/25CM】2.0线径加固边·适配大体重", "price": 2299, "cost": 1060},
            {"sku": "【卧室套装】云岩Pro + 床笠*1 + 乳胶枕*2", "price": 2499, "cost": 1160},
            {"sku": "云岩 Max Plus【双睡感/28CM】双层弹簧旗舰", "price": 2799, "cost": 1320},
        ],
    },
    {
        "id": "P2",
        "name": "磐石 · 大体重加硬承托款",
        "gap": "「重压/大体重」全站 52 款 Top50 率 19.2%，赛道渗透 28.6% 却无一款把承重做成主诉求；赛道内 28cm+ 厚度段为 0 款完全空白",
        "position": "以承重数字为唯一心智锚点，切 85kg+ 人群与夫妻同睡塌陷痛点",
        "main_image_points": [
            "单侧承重 150kg · 固边不塌陷",
            "28cm 双层独立袋弹簧叠加结构",
            "偏硬 H1 护脊 · 睡三年不塌腰",
        ],
        "visual": "深灰工业质感背景 + 垫边缘承压形变对比图（普通垫 vs 本款）+ 承重测试数值角标 + 双层弹簧剖面透视",
        "benefits": ["承重150kg承诺", "塌陷包退", "15年弹簧质保", "0胶整垫"],
        "main_image_price": 1599,
        "price_anchor": "精准对标引流：主图价 = 最低 SKU 门槛价",
        "tags_selling": ["人体工学护腰护脊", "独立袋装静音弹簧", "0胶水环保"],
        "tags_marketing": ["超长弹簧质保", "官方正品权威背书", "免费试睡保障"],
        "tags_visual": ["3D分层结构透视"],
        "tags_funcs": ["重压/大体重", "0胶/无胶", "厚垫", "分区支撑"],
        "tags_materials": ["弹簧", "黄麻", "乳胶"],
        "thickness": 28,
        "construction": "A类加厚提花面料 → 2cm 高密度硬质棉 → 3cm 天然黄麻硬核层 → 上层2.2mm线径独立袋弹簧 → 隔离毡 → 下层整网加固弹簧 → 8cm 环边泡棉固边（防塌陷核心）",
        "ladder": [
            {"sku": "磐石 Lite【偏硬H1/24CM】单层加固·承重120kg", "price": 1599, "cost": 730},
            {"sku": "磐石 承重版【偏硬H1/28CM】单侧承重150kg·固边防塌", "price": 1899, "cost": 880},
            {"sku": "【卧室套装】磐石承重版 + 加固床笠*1", "price": 1999, "cost": 930},
            {"sku": "磐石 承重版 加宽【偏硬H1/28CM·1.8×2.0m】", "price": 2099, "cost": 970},
            {"sku": "磐石 双睡感【A面H1/B面H2·28CM】夫妻软硬各半", "price": 2199, "cost": 1020},
            {"sku": "磐石 Pro【偏硬H1/30CM】双层弹簧·承重180kg", "price": 2399, "cost": 1120},
            {"sku": "【卧室套装】磐石Pro + 床笠*1 + 护颈枕*2", "price": 2499, "cost": 1180},
            {"sku": "磐石 Pro 0胶【偏硬H1/30CM】整垫0胶·面层可拆", "price": 2699, "cost": 1270},
            {"sku": "磐石 Max【偏硬H1/32CM】三层结构·承重200kg", "price": 2899, "cost": 1380},
        ],
    },
    {
        "id": "P3",
        "name": "净眠 · 全拆机洗母婴款",
        "gap": "「可拆洗」全站 61 款 Top50 率 23.0%、排名中位 112 为功能标签最优，赛道渗透仅 23.8%；而高渗透的「抗菌防螨」(赛道 47.6%) 全站 Top50 率仅 12.8%，属无效同质化",
        "position": "用「洗」替代「抗菌」话术，把不可验证的抑菌承诺换成可操作的家庭清洁行为",
        "main_image_points": [
            "外套+面层双层可拆 · 家用洗衣机直接洗",
            "A类母婴面料 · 婴幼儿可直接接触",
            "24cm 三区护脊 · 儿童青少年脊椎发育适配",
        ],
        "visual": "浅木色儿童房场景 + 拉链拆解三步分解图 + 洗衣机滚筒实拍小图 + A类认证绿标",
        "benefits": ["双层可拆机洗", "A类母婴认证", "180天试睡", "免费送装"],
        "main_image_price": 1099,
        "price_anchor": "精准对标引流：主图价 = 最低 SKU 门槛价",
        "tags_selling": ["母婴A类抗菌防螨", "人体工学护腰护脊", "0胶水环保"],
        "tags_marketing": ["免费试睡保障", "官方正品权威背书", "免费送装一体", "买赠高价值赠品"],
        "tags_visual": ["质检认证与绿标背书"],
        "tags_funcs": ["可拆洗", "0胶/无胶", "儿童青少年", "分区支撑"],
        "tags_materials": ["弹簧", "乳胶", "黄麻"],
        "thickness": 24,
        "construction": "可拆外套(A类针织·360°拉链) → 可拆面层(3cm乳胶+抗菌纤维) → 三区独立袋弹簧(1.8mm) → 2cm 黄麻硬核层 → 防滑底布；外套与面层均支持家用洗衣机水洗",
        "ladder": [
            {"sku": "净眠 婴童版【偏硬/15CM】0-6岁·整垫可机洗", "price": 1099, "cost": 480},
            {"sku": "净眠 儿童版【偏硬/20CM】青少年护脊·可拆机洗", "price": 1299, "cost": 590},
            {"sku": "净眠 标准版【适中/24CM】双层可拆·A类母婴面料", "price": 1599, "cost": 760},
            {"sku": "【母婴套装】净眠标准版 + 可洗替换外套*1", "price": 1799, "cost": 850},
            {"sku": "净眠 Pro【双睡感/25CM】外套+面层+夹层三层可拆", "price": 1899, "cost": 900},
            {"sku": "净眠 标准版 加宽【适中/24CM·1.8×2.0m】", "price": 1999, "cost": 940},
            {"sku": "净眠 Max【适中/26CM】5cm乳胶加厚·全拆可机洗", "price": 2099, "cost": 990},
            {"sku": "【母婴套装】净眠Pro + 替换外套*1 + 儿童枕*2", "price": 2299, "cost": 1090},
            {"sku": "净眠 Max Plus【双睡感/28CM】双层弹簧·全拆洗旗舰", "price": 2499, "cost": 1190},
        ],
    },
    {
        "id": "P4",
        "name": "栖光 · 28cm酒店旗舰",
        "gap": "赛道价格断层：21 款商品的 SKU 落点在 ¥2500-3200 几乎为零（2900-2999 为 0 条）；同时 28cm+ 厚度在赛道内 0 款",
        "position": "补赛道顶配位，承接 1500-2000 客群的升级需求，同时抬高店铺价格天花板",
        "main_image_points": [
            "28cm 五星酒店同款厚度",
            "七区分区支撑 · 肩腰臀独立塌陷",
            "乳胶+记忆棉双释压层",
        ],
        "visual": "暖金光影酒店套房场景 + 整垫侧面厚度标尺 + 七分区剖面透视",
        "benefits": ["酒店同款规格", "花呗12期免息", "15年质保", "送装一体"],
        "main_image_price": 2699,
        "price_anchor": "高配品质锚定：主图主推旗舰配置（全站该策略排名中位 115，适合拉高客单）",
        "tags_selling": ["天然乳胶释压", "人体工学护腰护脊", "0压记忆棉深睡"],
        "tags_marketing": ["花呗免息分期", "官方正品权威背书", "免费送装一体", "超长弹簧质保"],
        "tags_visual": ["极简家居场景沉浸"],
        "tags_funcs": ["厚垫", "分区支撑", "酒店同款", "0胶/无胶"],
        "tags_materials": ["弹簧", "乳胶", "记忆棉"],
        "thickness": 28,
        "construction": "天丝面料 → 3cm 慢回弹记忆棉 → 4cm 天然乳胶 → 七区独立袋弹簧(2.0mm/¢6.5cm) → 2cm 黄麻 → 环边加固泡棉",
        "ladder": [
            {"sku": "栖光 Lite【适中/24CM】三区分区·轻旗舰", "price": 1999, "cost": 940},
            {"sku": "栖光 标准版【适中/26CM】五区分区·入门旗舰", "price": 2299, "cost": 1090},
            {"sku": "栖光 旗舰版【适中/28CM】七区分区·酒店同款", "price": 2699, "cost": 1290},
            {"sku": "【卧室套装】栖光旗舰版 + 天丝床笠*1", "price": 2899, "cost": 1390},
            {"sku": "栖光 旗舰版 加宽【适中/28CM·1.8×2.0m】", "price": 2999, "cost": 1430},
            {"sku": "栖光 Pro【双睡感/30CM】双层弹簧·软硬两面", "price": 3199, "cost": 1550},
            {"sku": "栖光 Pro 0胶【双睡感/30CM】整垫0胶·面层可拆", "price": 3499, "cost": 1700},
            {"sku": "【卧室套装】栖光Pro + 床笠*1 + 乳胶枕*2", "price": 3599, "cost": 1740},
            {"sku": "栖光 Max【双睡感/32CM】三层结构·总统套房同款", "price": 3999, "cost": 1950},
        ],
    },
    {
        "id": "P5",
        "name": "轻眠 · 12cm旧床改造薄垫",
        "gap": "厚度 8-15cm 全站排名中位 94 为最优段但仅 29 款供给；赛道内该段仅 6 款且无一款主打「旧床改造」场景",
        "position": "场景错位切入——不卖新床垫，卖「旧床救活方案」，卷包压缩物流成本约为厚垫的 1/3",
        "main_image_points": [
            "12cm 厚 · 铺在旧床/硬板床上直接用",
            "卷包压缩发货 · 电梯楼梯都能进",
            "0胶黄麻+乳胶双层 · 不是普通薄褥子",
        ],
        "visual": "对比式构图：左侧塌陷旧床垫 + 右侧铺上本款后的平整效果，中间卷包压缩袋实拍与厚度标尺",
        "benefits": ["卷包免上楼费", "旧床直铺", "0胶整垫", "7天无理由"],
        "main_image_price": 999,
        "price_anchor": "精准对标引流：主图价 = 最低 SKU 门槛价",
        "tags_selling": ["天然黄麻/硬核护脊", "0胶水环保", "人体工学护腰护脊"],
        "tags_marketing": ["平台/政府大额补贴", "买赠高价值赠品", "免费试睡保障"],
        "tags_visual": ["促销大字报冲击型"],
        "tags_funcs": ["薄垫/褥垫", "0胶/无胶", "透气"],
        "tags_materials": ["黄麻", "乳胶"],
        "thickness": 12,
        "construction": "A类针织面料 → 2cm 天然乳胶 → 8cm S型黄麻硬核层 → 1cm 3D透气网 → 防滑底布；无弹簧结构，可卷包压缩",
        "ladder": [
            {"sku": "轻眠 Lite【偏硬/8CM】极简护脊·租房首选", "price": 999, "cost": 420},
            {"sku": "轻眠 儿童版【偏硬/10CM】青少年护脊·可卷包", "price": 1149, "cost": 500},
            {"sku": "轻眠 标准版【偏硬/12CM】旧床直铺·卷包发货", "price": 1299, "cost": 560},
            {"sku": "轻眠 标准版 加宽【偏硬/12CM·1.8×2.0m】", "price": 1449, "cost": 630},
            {"sku": "【租房套装】轻眠标准版 + 抗菌床笠*1", "price": 1499, "cost": 660},
            {"sku": "轻眠 Pro【适中/15CM】乳胶加厚至4cm", "price": 1599, "cost": 700},
            {"sku": "轻眠 双面【A面偏硬/B面适中·15CM】一垫两用", "price": 1699, "cost": 750},
            {"sku": "轻眠 Pro 加宽【适中/15CM·1.8×2.0m】", "price": 1799, "cost": 790},
            {"sku": "【卧室套装】轻眠双面 + 床笠*1 + 护颈枕*2", "price": 1899, "cost": 840},
            {"sku": "轻眠 Max【双面/18CM】加厚黄麻·准整垫体验", "price": 1999, "cost": 880},
        ],
    },
]

p("=" * 78)
p("阶段 2 · 爆品落子设计（赛道 T1：1500-2000元腰部护脊主力）")
p("=" * 78)
p("共 5 款差异化方案，每款含 主图卖点/视觉背景/利益点/主图标价/SKU文字/内材构造/梯度定价")
p("硬约束：SKU 9~15 个（该档全站 Top50 率 26.8% 最高）｜价宽比 1.5~2.5（超 2.5 后 Top50 率腰斩）")
p("")

for pr in PRODUCTS:
    prices = [s["price"] for s in pr["ladder"]]
    gm = [(s["price"] - s["cost"]) / s["price"] * 100 for s in pr["ladder"]]
    pr["price_min"], pr["price_max"] = min(prices), max(prices)
    pr["price_median"] = st.median(prices)
    pr["span_ratio"] = round(max(prices) / min(prices), 2)
    pr["sku_count"] = len(pr["ladder"])
    pr["gross_margin"] = round(st.median(gm), 1)

    p("=" * 78)
    p(f"【{pr['id']}】{pr['name']}")
    p("=" * 78)
    p(f"切入缺口：{pr['gap']}")
    p(f"定位：{pr['position']}")
    p("")
    p("① 主图卖点（首图三行主文案）：")
    for s in pr["main_image_points"]:
        p(f"     · {s}")
    p(f"② 视觉背景：{pr['visual']}")
    p(f"③ 利益点：{' ｜ '.join(pr['benefits'])}")
    p(f"④ 主图标价：¥{pr['main_image_price']}　{pr['price_anchor']}")
    p(f"⑤ 内材构造：{pr['construction']}")
    p(f"⑥ 厚度：{pr['thickness']}cm")
    p("")
    p("⑦ SKU文字 与 梯度定价：")
    p("     " + "价格".ljust(9) + "毛利率".ljust(9) + "SKU 名称")
    for s in sorted(pr["ladder"], key=lambda z: z["price"]):
        g = (s["price"] - s["cost"]) / s["price"] * 100
        p(f"     ¥{str(s['price']).ljust(8)}{g:5.1f}%   {s['sku']}")
    p(f"     价格区间 ¥{pr['price_min']}-{pr['price_max']}｜价宽比 {pr['span_ratio']}｜"
      f"SKU 数 {pr['sku_count']}｜中位价 ¥{pr['price_median']:.0f}｜毛利率中位 {pr['gross_margin']}%")
    p("")

with open(os.path.join(BASE, "products.json"), "w", encoding="utf-8") as f:
    json.dump(PRODUCTS, f, ensure_ascii=False, indent=1)
with open(os.path.join(BASE, "design_report.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(OUT))
print("\n>>> products.json / design_report.txt 已生成")
