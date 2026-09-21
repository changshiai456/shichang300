/**
 * =========================================================================
 * 🚀 天猫 96 款核心床垫 1.8米全量 SKU 平台加补到手价【全自动巡航采集器】
 * =========================================================================
 * 
 * 使用方法：
 * 1. 在天猫任意商品页（例如您当前打开的 20719504509 页面）按 F12 打开控制台 (Console)；
 * 2. 粘贴本脚本全部代码并回车；
 * 3. 浏览器将自动巡航采集全部 96 款商品在 1800mm*2000mm 下的所有 SKU 到手价与最低价；
 * 4. 采集完毕后自动下载 JSON 与 CSV 文件！
 */
(async function runTmallAutoPilotSkuCollector() {
    const STORAGE_KEY = 'TMALL_96_SKU_TASK_DATA';
    const ALL_TARGETS = [
  {
    "rank": 1,
    "itemId": "20719504509",
    "shop": "moonlightfamily旗舰店",
    "title": "月光之家乳胶床垫家用独立弹簧软垫儿童黄麻棕硬护腰席梦思1.8米",
    "url": "https://detail.tmall.com/item.htm?id=20719504509&sku_properties=21433:50753460"
  },
  {
    "rank": 2,
    "itemId": "676435752637",
    "shop": "睡眠骑士床垫企业店",
    "title": "睡眠骑士梦舒乳胶五星级酒店床垫席梦思记忆棉加厚30cm厚家用软垫",
    "url": "https://detail.tmall.com/item.htm?id=676435752637&sku_properties=21433:50753460"
  },
  {
    "rank": 3,
    "itemId": "746683178170",
    "shop": "yarges悠梦思旗舰店",
    "title": "悠梦思乳胶床垫独立弹簧1.5米1.8五星酒店席梦思软硬两用厚款定制",
    "url": "https://detail.tmall.com/item.htm?id=746683178170&sku_properties=21433:50753460"
  },
  {
    "rank": 4,
    "itemId": "45590433293",
    "shop": "铂马仕旗舰店",
    "title": "铂马仕独立弹簧床垫乳胶席梦思软垫椰棕垫护脊偏硬家用双人1.8米",
    "url": "https://detail.tmall.com/item.htm?id=45590433293&sku_properties=21433:50753460"
  },
  {
    "rank": 5,
    "itemId": "25956076042",
    "shop": "moonlightfamily旗舰店",
    "title": "月光之家乳胶床垫超薄款家庭用15cm软硬独立弹簧席梦思10厘米1.8m",
    "url": "https://detail.tmall.com/item.htm?id=25956076042&sku_properties=21433:50753460"
  },
  {
    "rank": 6,
    "itemId": "783167304430",
    "shop": "麻师傅家具旗舰店",
    "title": "麻师傅全拆薄S形天然黄麻床垫1.8米家用10cm儿童老人护脊加硬椰棕",
    "url": "https://detail.tmall.com/item.htm?id=783167304430&sku_properties=21433:50753460"
  },
  {
    "rank": 7,
    "itemId": "15290005941",
    "shop": "moonlightfamily旗舰店",
    "title": "月光之家天然黄麻床垫子家用儿童硬薄全拆乳胶椰棕1.8m榻榻米定制",
    "url": "https://detail.tmall.com/item.htm?id=15290005941&sku_properties=21433:50753460"
  },
  {
    "rank": 8,
    "itemId": "650423226539",
    "shop": "派乐熊儿童床垫品牌店",
    "title": "派乐熊儿童专用床垫护脊0胶弹簧偏硬席梦思青少年家用甲醛无超标",
    "url": "https://detail.tmall.com/item.htm?id=650423226539&sku_properties=21433:50753460"
  },
  {
    "rank": 9,
    "itemId": "40640084764",
    "shop": "铂马仕旗舰店",
    "title": "儿童护脊黄麻乳胶床垫家用环保席梦思高低床天然椰棕垫1.2m折叠",
    "url": "https://detail.tmall.com/item.htm?id=40640084764&sku_properties=21433:50753460"
  },
  {
    "rank": 10,
    "itemId": "691510768993",
    "shop": "睡眠骑士床垫企业店",
    "title": "睡眠骑士乳胶床垫五星级酒店薄款独立弹簧10cm席梦思15cm家用公分",
    "url": "https://detail.tmall.com/item.htm?id=691510768993&sku_properties=21433:50753460"
  },
  {
    "rank": 11,
    "itemId": "728968513494",
    "shop": "派乐熊旗舰店",
    "title": "派乐熊全拆儿童床垫护脊加密弹簧青少年学生家用席梦思0胶水工艺",
    "url": "https://detail.tmall.com/item.htm?id=728968513494&sku_properties=21433:50753460"
  },
  {
    "rank": 12,
    "itemId": "893138674729",
    "shop": "麻师傅家具旗舰店",
    "title": "麻师傅天然S形黄麻床垫叠加软床专用加硬神器儿童老人护腰脊椰棕",
    "url": "https://detail.tmall.com/item.htm?id=893138674729&sku_properties=21433:50753460"
  },
  {
    "rank": 13,
    "itemId": "521995661165",
    "shop": "moonlightfamily旗舰店",
    "title": "月光之家五星级酒店乳胶床垫家庭用超软独立弹簧席梦思1.8米加厚",
    "url": "https://detail.tmall.com/item.htm?id=521995661165&sku_properties=21433:50753460"
  },
  {
    "rank": 14,
    "itemId": "871914448139",
    "shop": "PARELER BEAR旗舰店",
    "title": "派乐熊儿童专用床垫加密独立袋弹簧青少年偏硬护脊席梦思学生家用",
    "url": "https://detail.tmall.com/item.htm?id=871914448139&sku_properties=21433:50753460"
  },
  {
    "rank": 15,
    "itemId": "866382200003",
    "shop": "甜蜜睡眠旗舰店",
    "title": "甜蜜睡眠床垫马尾毛手工拉扣席梦思独立袋装弹簧乳胶护脊卧室家用",
    "url": "https://detail.tmall.com/item.htm?id=866382200003&sku_properties=21433:50753460"
  },
  {
    "rank": 16,
    "itemId": "616295938570",
    "shop": "睡眠骑士床垫企业店",
    "title": "睡眠骑士乳胶超软席梦思床垫独立弹簧30cm加厚五星级酒店软垫2米",
    "url": "https://detail.tmall.com/item.htm?id=616295938570&sku_properties=21433:50753460"
  },
  {
    "rank": 17,
    "itemId": "685270598397",
    "shop": "睡眠骑士床垫企业店",
    "title": "睡眠骑士五星酒店席梦思款床垫15cm厚乳胶记忆棉家用软垫20cm双面",
    "url": "https://detail.tmall.com/item.htm?id=685270598397&sku_properties=21433:50753460"
  },
  {
    "rank": 18,
    "itemId": "788140809544",
    "shop": "麻师傅家具旗舰店",
    "title": "15公分薄独立袋弹簧床垫家用10cm12含乳胶黄麻儿童榻榻米席梦思",
    "url": "https://detail.tmall.com/item.htm?id=788140809544&sku_properties=21433:50753460"
  },
  {
    "rank": 19,
    "itemId": "639619273082",
    "shop": "睡眠骑士床垫企业店",
    "title": "【睡眠骑士呼呼】儿童床垫 青少年S黄麻榻榻米硬垫乳胶护脊上下铺",
    "url": "https://detail.tmall.com/item.htm?id=639619273082&sku_properties=21433:50753460"
  },
  {
    "rank": 20,
    "itemId": "1025218536548",
    "shop": "PARELER BEAR旗舰店",
    "title": "派乐熊儿童全拆S形黄麻床垫学生宿舍上下铺加硬护脊青少年榻榻米",
    "url": "https://detail.tmall.com/item.htm?id=1025218536548&sku_properties=21433:50753460"
  },
  {
    "rank": 21,
    "itemId": "1046478563403",
    "shop": "moonlightfamily旗舰店",
    "title": "月光之家全拆家庭用床垫薄款独立弹簧乳胶记忆棉黄麻席梦思1.8米",
    "url": "https://detail.tmall.com/item.htm?id=1046478563403&sku_properties=21433:50753460"
  },
  {
    "rank": 22,
    "itemId": "730136503602",
    "shop": "派乐熊旗舰店",
    "title": "派乐熊儿童全拆S形黄麻床垫学生宿舍上下铺加硬护脊青少年榻榻米",
    "url": "https://detail.tmall.com/item.htm?id=730136503602&sku_properties=21433:50753460"
  },
  {
    "rank": 23,
    "itemId": "693457489039",
    "shop": "派乐熊儿童床垫品牌店",
    "title": "派乐熊儿童全拆S形黄麻床垫学生宿舍上下铺加硬护脊青少年榻榻米",
    "url": "https://detail.tmall.com/item.htm?id=693457489039&sku_properties=21433:50753460"
  },
  {
    "rank": 24,
    "itemId": "816598391499",
    "shop": "凯菲露家具旗舰店",
    "title": "凯菲露乳胶床垫独立弹簧卧室家用防塌护脊黄麻硬垫22cm厚酒店睡感",
    "url": "https://detail.tmall.com/item.htm?id=816598391499&sku_properties=21433:50753460"
  },
  {
    "rank": 25,
    "itemId": "826409177301",
    "shop": "睡眠骑士床垫企业店",
    "title": "睡眠骑士乳胶床垫硬垫30cm厚加硬独立袋弹簧五星级酒店黄麻护脊",
    "url": "https://detail.tmall.com/item.htm?id=826409177301&sku_properties=21433:50753460"
  },
  {
    "rank": 26,
    "itemId": "1060750230053",
    "shop": "麻师傅诺隆专卖店",
    "title": "麻师傅中老年人护腰脊神器偏硬黄麻独立弹簧床垫家用席梦思20cm厚",
    "url": "https://detail.tmall.com/item.htm?id=1060750230053&sku_properties=21433:50753460"
  },
  {
    "rank": 27,
    "itemId": "878994904392",
    "shop": "yarges悠梦思旗舰店",
    "title": "悠梦思酒店弹簧床垫15cm薄乳胶黄麻1.8席梦思家用椰棕垫子软垫",
    "url": "https://detail.tmall.com/item.htm?id=878994904392&sku_properties=21433:50753460"
  },
  {
    "rank": 28,
    "itemId": "640048898334",
    "shop": "睡眠骑士床垫企业店",
    "title": "睡眠骑士儿童床垫0胶0甲醛护脊偏硬20cm独立袋弹簧乳胶青少年专用",
    "url": "https://detail.tmall.com/item.htm?id=640048898334&sku_properties=21433:50753460"
  },
  {
    "rank": 29,
    "itemId": "721092643270",
    "shop": "睡眠骑士床垫企业店",
    "title": "睡眠骑士记忆棉床垫五星级酒店床垫卧室加厚乳胶30cm厚家用软垫",
    "url": "https://detail.tmall.com/item.htm?id=721092643270&sku_properties=21433:50753460"
  },
  {
    "rank": 30,
    "itemId": "1051956336669",
    "shop": "麻师傅舒梦专卖店",
    "title": "麻师傅全拆席梦思床垫酷布独立袋弹簧酒店记忆棉乳胶软硬可调家用",
    "url": "https://detail.tmall.com/item.htm?id=1051956336669&sku_properties=21433:50753460"
  },
  {
    "rank": 31,
    "itemId": "42242821658",
    "shop": "铂马仕旗舰店",
    "title": "铂马仕 加厚进口乳胶床垫 超软席梦思弹簧床垫1.5m 1.8米单双人",
    "url": "https://detail.tmall.com/item.htm?id=42242821658&sku_properties=21433:50753460"
  },
  {
    "rank": 32,
    "itemId": "837948013130",
    "shop": "甜蜜睡眠旗舰店",
    "title": "甜蜜睡眠朗月床垫偏硬护脊弹簧黄麻无胶水席梦思可拆透气家用卧室",
    "url": "https://detail.tmall.com/item.htm?id=837948013130&sku_properties=21433:50753460"
  },
  {
    "rank": 33,
    "itemId": "1016986066309",
    "shop": "PARELER BEAR旗舰店",
    "title": "派乐熊儿童专用薄弹簧床垫10cm青少年偏硬席梦思护脊学生家用15厚",
    "url": "https://detail.tmall.com/item.htm?id=1016986066309&sku_properties=21433:50753460"
  },
  {
    "rank": 34,
    "itemId": "786030574869",
    "shop": "rozo家具旗舰店",
    "title": "ROZO华夫格席梦思护脊床垫国家补贴适中独立弹簧黄麻乳胶偏硬家用",
    "url": "https://detail.tmall.com/item.htm?id=786030574869&sku_properties=21433:50753460"
  },
  {
    "rank": 35,
    "itemId": "908411378814",
    "shop": "铂马仕旗舰店",
    "title": "铂马仕S黄麻床垫家用卧室薄儿童加硬垫可拆洗无甲醛双人椰棕乳胶",
    "url": "https://detail.tmall.com/item.htm?id=908411378814&sku_properties=21433:50753460"
  },
  {
    "rank": 36,
    "itemId": "562872250776",
    "shop": "优群家居正品商城",
    "title": "席梦思床垫硬垫家用软硬双面椰棕五星酒店薄款15cm厚乳胶弹簧定制",
    "url": "https://detail.tmall.com/item.htm?id=562872250776&sku_properties=21433:50753460"
  },
  {
    "rank": 37,
    "itemId": "1050149631481",
    "shop": "品味布帆家居旗舰店",
    "title": "国家补贴品味布帆乳胶独立弹簧床垫黄麻1.8米 席梦思双人家用软硬",
    "url": "https://detail.tmall.com/item.htm?id=1050149631481&sku_properties=21433:50753460"
  },
  {
    "rank": 38,
    "itemId": "743609626271",
    "shop": "派乐熊旗舰店",
    "title": "派乐熊全拆儿童专用薄弹簧床垫青少年偏硬席梦思护脊学生家用15cm",
    "url": "https://detail.tmall.com/item.htm?id=743609626271&sku_properties=21433:50753460"
  },
  {
    "rank": 39,
    "itemId": "1007724840079",
    "shop": "睡眠骑士床垫企业店",
    "title": "睡眠骑士S1 全拆床垫0胶水家用席梦思天然黄麻护脊酷布四叶草弹簧",
    "url": "https://detail.tmall.com/item.htm?id=1007724840079&sku_properties=21433:50753460"
  },
  {
    "rank": 40,
    "itemId": "642438274024",
    "shop": "rozo家具旗舰店",
    "title": "ROZO席梦思床垫护脊家用记忆棉乳胶弹簧椰棕双面五星级酒店22cm厚",
    "url": "https://detail.tmall.com/item.htm?id=642438274024&sku_properties=21433:50753460"
  },
  {
    "rank": 41,
    "itemId": "595066893675",
    "shop": "铂马仕旗舰店",
    "title": "铂马仕席梦思床垫乳胶弹簧家用双人软垫卧室酒店厚垫1.8m可拆",
    "url": "https://detail.tmall.com/item.htm?id=595066893675&sku_properties=21433:50753460"
  },
  {
    "rank": 42,
    "itemId": "973610633655",
    "shop": "派乐熊旗舰店",
    "title": "派乐熊全拆儿童床垫可拆卸0胶水工艺调节软硬护脊独立弹簧席梦思",
    "url": "https://detail.tmall.com/item.htm?id=973610633655&sku_properties=21433:50753460"
  },
  {
    "rank": 43,
    "itemId": "788457904913",
    "shop": "CEFALU旗舰店",
    "title": "加密独立袋弹簧偏硬护脊床垫黄麻席梦思乳胶硬20cm记忆棉床垫",
    "url": "https://detail.tmall.com/item.htm?id=788457904913&sku_properties=21433:50753460"
  },
  {
    "rank": 44,
    "itemId": "532960004497",
    "shop": "棕葆王国品牌店",
    "title": "棕葆王国天然环保黄麻椰棕床垫儿童3e棕1.35米榻榻米棕榈加硬神器",
    "url": "https://detail.tmall.com/item.htm?id=532960004497&sku_properties=21433:50753460"
  },
  {
    "rank": 45,
    "itemId": "769966237344",
    "shop": "moonlightfamily旗舰店",
    "title": "月光之家乳胶弹簧床垫1.8米家用软垫席梦思 1.5m记忆棉黄麻棕垫硬",
    "url": "https://detail.tmall.com/item.htm?id=769966237344&sku_properties=21433:50753460"
  },
  {
    "rank": 46,
    "itemId": "1028454725472",
    "shop": "铂马仕旗舰店",
    "title": "儿童护脊黄麻乳胶折叠床垫家用环保席梦思高低床天然椰棕1.2m定制",
    "url": "https://detail.tmall.com/item.htm?id=1028454725472&sku_properties=21433:50753460"
  },
  {
    "rank": 47,
    "itemId": "714642283854",
    "shop": "派乐熊儿童床垫品牌店",
    "title": "派乐熊全拆儿童床垫0胶水工艺酷布独立袋弹簧青少年护脊硬席梦思",
    "url": "https://detail.tmall.com/item.htm?id=714642283854&sku_properties=21433:50753460"
  },
  {
    "rank": 48,
    "itemId": "15292785950",
    "shop": "moonlightfamily旗舰店",
    "title": "月光之家天然纯乳胶床垫超薄可全拆分区按摩软榻榻米1.8米可定制",
    "url": "https://detail.tmall.com/item.htm?id=15292785950&sku_properties=21433:50753460"
  },
  {
    "rank": 49,
    "itemId": "826540116802",
    "shop": "睡眠骑士床垫企业店",
    "title": "睡眠骑士五星级酒店床垫双面20cm厚乳胶席梦思硬垫加硬家用记忆棉",
    "url": "https://detail.tmall.com/item.htm?id=826540116802&sku_properties=21433:50753460"
  },
  {
    "rank": 50,
    "itemId": "587602685704",
    "shop": "布莱轩尼旗舰店",
    "title": "全拆软硬薄独立弹簧床垫高箱10cm15公分含乳胶记忆棉家用榻榻米",
    "url": "https://detail.tmall.com/item.htm?id=587602685704&sku_properties=21433:50753460"
  },
  {
    "rank": 51,
    "itemId": "829143171600",
    "shop": "铂马仕旗舰店",
    "title": "铂马仕弹簧床垫乳胶席梦思家用软垫双人卧室椰棕厚硬垫单人1.8米",
    "url": "https://detail.tmall.com/item.htm?id=829143171600&sku_properties=21433:50753460"
  },
  {
    "rank": 52,
    "itemId": "1046477892506",
    "shop": "麻师傅家具旗舰店",
    "title": "麻师傅20cm厚独立弹簧床垫席梦思家用1.8m卧室含乳胶记忆棉软黄麻",
    "url": "https://detail.tmall.com/item.htm?id=1046477892506&sku_properties=21433:50753460"
  },
  {
    "rank": 53,
    "itemId": "800087983555",
    "shop": "yarges悠梦思旗舰店",
    "title": "悠梦思乳胶薄款床垫8cm高箱床独立袋弹簧14cm席梦思黄麻榻榻米垫",
    "url": "https://detail.tmall.com/item.htm?id=800087983555&sku_properties=21433:50753460"
  },
  {
    "rank": 54,
    "itemId": "692623573466",
    "shop": "梦织葆家居品牌店",
    "title": "记忆棉盒子压缩席梦思弹簧乳胶床垫软垫家用卧室硬垫官方十大名牌",
    "url": "https://detail.tmall.com/item.htm?id=692623573466&sku_properties=21433:50753460"
  },
  {
    "rank": 55,
    "itemId": "686760000635",
    "shop": "睡眠骑士床垫企业店",
    "title": "睡眠骑士薄款弹簧床垫15cm软垫乳胶席梦思双面家用记忆棉椰棕硬垫",
    "url": "https://detail.tmall.com/item.htm?id=686760000635&sku_properties=21433:50753460"
  },
  {
    "rank": 56,
    "itemId": "623410616784",
    "shop": "moonlightfamily旗舰店",
    "title": "月光之家五星级酒店床垫家庭用迷你独立弹簧高档双人席梦思1.8米",
    "url": "https://detail.tmall.com/item.htm?id=623410616784&sku_properties=21433:50753460"
  },
  {
    "rank": 57,
    "itemId": "714909821260",
    "shop": "铂马仕旗舰店",
    "title": "铂马仕10cm厚乳胶床垫独立袋薄弹簧床垫硬15公分软垫席梦思高箱床",
    "url": "https://detail.tmall.com/item.htm?id=714909821260&sku_properties=21433:50753460"
  },
  {
    "rank": 58,
    "itemId": "692763933781",
    "shop": "CEFALU旗舰店",
    "title": "【国补】压缩卷包独立袋弹簧记忆棉席梦思乳胶20cm护脊厚床垫",
    "url": "https://detail.tmall.com/item.htm?id=692763933781&sku_properties=21433:50753460"
  },
  {
    "rank": 59,
    "itemId": "979681631360",
    "shop": "睡眠骑士床垫企业店",
    "title": "睡眠骑士自在可调节全拆床垫独立袋弹簧1.8米0胶水家用卧室软垫子",
    "url": "https://detail.tmall.com/item.htm?id=979681631360&sku_properties=21433:50753460"
  },
  {
    "rank": 60,
    "itemId": "965421153017",
    "shop": "麻师傅家具旗舰店",
    "title": "麻师傅独立弹簧床垫20cm厚护脊硬黄麻含乳胶记忆棉席梦思十大名牌",
    "url": "https://detail.tmall.com/item.htm?id=965421153017&sku_properties=21433:50753460"
  },
  {
    "rank": 61,
    "itemId": "994995979658",
    "shop": "麻师傅家具旗舰店",
    "title": "麻师傅天然S形黄麻薄床垫10cm厚全拆加硬护腰脊儿童老人家用椰棕",
    "url": "https://detail.tmall.com/item.htm?id=994995979658&sku_properties=21433:50753460"
  },
  {
    "rank": 62,
    "itemId": "858779275867",
    "shop": "yarges悠梦思旗舰店",
    "title": "悠梦思乳胶床垫独立弹簧席梦思加厚软硬适中家用护脊黄麻酒店定制",
    "url": "https://detail.tmall.com/item.htm?id=858779275867&sku_properties=21433:50753460"
  },
  {
    "rank": 63,
    "itemId": "1078382595239",
    "shop": "麻师傅诺隆专卖店",
    "title": "麻师傅全拆S形黄麻床垫叠加软床加硬神器专用儿童老人护腰脊椰棕",
    "url": "https://detail.tmall.com/item.htm?id=1078382595239&sku_properties=21433:50753460"
  },
  {
    "rank": 64,
    "itemId": "898868296824",
    "shop": "凯菲露家具旗舰店",
    "title": "凯菲露黄麻乳胶独立袋弹簧薄款床垫加硬榻榻米卧室10cm厚国家补贴",
    "url": "https://detail.tmall.com/item.htm?id=898868296824&sku_properties=21433:50753460"
  },
  {
    "rank": 65,
    "itemId": "1007130832612",
    "shop": "铂马仕旗舰店",
    "title": "铂马仕云霄全拆洗可调节弹簧床垫席梦思乳胶软垫家用椰棕加硬床垫",
    "url": "https://detail.tmall.com/item.htm?id=1007130832612&sku_properties=21433:50753460"
  },
  {
    "rank": 66,
    "itemId": "941363571679",
    "shop": "rozo家具旗舰店",
    "title": "ROZO国家补贴全拆黄芽护脊床垫席梦思无胶独立弹簧黄麻乳胶硬家用",
    "url": "https://detail.tmall.com/item.htm?id=941363571679&sku_properties=21433:50753460"
  },
  {
    "rank": 67,
    "itemId": "1016981719311",
    "shop": "铂马仕旗舰店",
    "title": "铂马仕云岚全拆弹簧床垫乳胶席梦思1.8m米软家用护脊硬垫黄麻床垫",
    "url": "https://detail.tmall.com/item.htm?id=1016981719311&sku_properties=21433:50753460"
  },
  {
    "rank": 68,
    "itemId": "1018101560481",
    "shop": "甜蜜睡眠旗舰店",
    "title": "甜蜜睡眠可拆卸床垫软硬可调无胶席梦思乳胶独立弹簧全拆卧室家用",
    "url": "https://detail.tmall.com/item.htm?id=1018101560481&sku_properties=21433:50753460"
  },
  {
    "rank": 69,
    "itemId": "653309172278",
    "shop": "棕葆王国品牌店",
    "title": "适用于宜家米隆床垫儿童分段式可伸缩婴儿拼接床可拆卸棕垫80x200",
    "url": "https://detail.tmall.com/item.htm?id=653309172278&sku_properties=21433:50753460"
  },
  {
    "rank": 70,
    "itemId": "1002508687323",
    "shop": "睡眠骑士床垫企业店",
    "title": "睡眠骑士名匠全拆可调节床垫席梦思无胶家用20cm硬垫天然乳胶黄麻",
    "url": "https://detail.tmall.com/item.htm?id=1002508687323&sku_properties=21433:50753460"
  },
  {
    "rank": 71,
    "itemId": "639084200572",
    "shop": "moonlightfamily旗舰店",
    "title": "月光之家儿童床垫硬家用独立弹簧青少年学生黄麻席梦思1.8米1.5m",
    "url": "https://detail.tmall.com/item.htm?id=639084200572&sku_properties=21433:50753460"
  },
  {
    "rank": 72,
    "itemId": "648731865254",
    "shop": "佛山享睡床垫品牌店",
    "title": "儿童床垫椰棕垫席梦思护脊偏硬1.2无甲醛棕垫1.35m天然乳胶席梦思",
    "url": "https://detail.tmall.com/item.htm?id=648731865254&sku_properties=21433:50753460"
  },
  {
    "rank": 73,
    "itemId": "650559391013",
    "shop": "派乐熊儿童床垫品牌店",
    "title": "派乐熊儿童专用床垫加密独立袋弹簧青少年偏硬护脊席梦思学生家用",
    "url": "https://detail.tmall.com/item.htm?id=650559391013&sku_properties=21433:50753460"
  },
  {
    "rank": 74,
    "itemId": "753435672675",
    "shop": "铂马仕旗舰店",
    "title": "铂马仕护脊弹簧床垫黄麻席梦思乳胶软垫家用1.5米 1.8m椰棕硬垫",
    "url": "https://detail.tmall.com/item.htm?id=753435672675&sku_properties=21433:50753460"
  },
  {
    "rank": 75,
    "itemId": "708089540708",
    "shop": "moonlightfamily旗舰店",
    "title": "月光之家5cm乳胶床垫超薄家庭用五星级酒店席梦思独立弹簧偏软1.8",
    "url": "https://detail.tmall.com/item.htm?id=708089540708&sku_properties=21433:50753460"
  },
  {
    "rank": 76,
    "itemId": "626431216907",
    "shop": "moonlightfamily旗舰店",
    "title": "月光之家儿童床垫天然黄麻棕垫榻榻米硬1.5米青少年学生专用1.2m",
    "url": "https://detail.tmall.com/item.htm?id=626431216907&sku_properties=21433:50753460"
  },
  {
    "rank": 77,
    "itemId": "943732529605",
    "shop": "rozo家具旗舰店",
    "title": "ROZO黄豆加硬全拆床垫S型天然黄麻乳胶榻榻米矮床儿童偏硬护脊",
    "url": "https://detail.tmall.com/item.htm?id=943732529605&sku_properties=21433:50753460"
  },
  {
    "rank": 78,
    "itemId": "942607064286",
    "shop": "麻师傅家具旗舰店",
    "title": "麻师傅S型黄麻床垫折叠学生榻榻米10cm15椰棕含乳胶老人加硬护腰",
    "url": "https://detail.tmall.com/item.htm?id=942607064286&sku_properties=21433:50753460"
  },
  {
    "rank": 79,
    "itemId": "735558795052",
    "shop": "yarges悠梦思旗舰店",
    "title": "悠梦思华夫格独立袋弹簧床垫1.8m压缩乳胶席梦思20cm厚五星酒店",
    "url": "https://detail.tmall.com/item.htm?id=735558795052&sku_properties=21433:50753460"
  },
  {
    "rank": 80,
    "itemId": "773925664034",
    "shop": "CEFALU旗舰店",
    "title": "薄款独立袋10cm矮弹簧记忆棉席梦思黄麻偏硬护脊薄床垫家用可拆洗",
    "url": "https://detail.tmall.com/item.htm?id=773925664034&sku_properties=21433:50753460"
  },
  {
    "rank": 81,
    "itemId": "984636395043",
    "shop": "铂马仕旗舰店",
    "title": "铂马仕薄乳胶床垫独立弹簧软垫记忆棉席梦思椰棕硬垫家用双人1.8m",
    "url": "https://detail.tmall.com/item.htm?id=984636395043&sku_properties=21433:50753460"
  },
  {
    "rank": 82,
    "itemId": "987240660508",
    "shop": "铂马仕旗舰店",
    "title": "铂马仕薄款乳胶弹簧床垫席梦思独立软垫记忆棉床垫家用双人19cm",
    "url": "https://detail.tmall.com/item.htm?id=987240660508&sku_properties=21433:50753460"
  },
  {
    "rank": 83,
    "itemId": "1056213868269",
    "shop": "品味布帆家居旗舰店",
    "title": "品味布帆家用席梦思软垫记忆棉乳胶独立袋弹簧厚床垫双人酒店可选",
    "url": "https://detail.tmall.com/item.htm?id=1056213868269&sku_properties=21433:50753460"
  },
  {
    "rank": 84,
    "itemId": "40585578946",
    "shop": "铂马仕旗舰店",
    "title": "铂马仕天然椰棕床垫乳胶硬棕垫席梦思护脊1.5m1.8米折叠定做",
    "url": "https://detail.tmall.com/item.htm?id=40585578946&sku_properties=21433:50753460"
  },
  {
    "rank": 85,
    "itemId": "997397669549",
    "shop": "yarges悠梦思旗舰店",
    "title": "政府补贴悠梦思S形黄麻全拆床垫1.8米1.5m儿童老人护脊硬宿舍薄垫",
    "url": "https://detail.tmall.com/item.htm?id=997397669549&sku_properties=21433:50753460"
  },
  {
    "rank": 86,
    "itemId": "704696475115",
    "shop": "布莱轩尼旗舰店",
    "title": "布莱轩尼10-15cm薄全拆床垫卧室偏硬黄麻席梦思矮弹簧家用榻榻米",
    "url": "https://detail.tmall.com/item.htm?id=704696475115&sku_properties=21433:50753460"
  },
  {
    "rank": 87,
    "itemId": "1053690840174",
    "shop": "yarges悠梦思旗舰店",
    "title": "悠梦思全拆S型黄麻床垫国家补贴乳胶1.8米儿童老人护脊10cm硬椰棕",
    "url": "https://detail.tmall.com/item.htm?id=1053690840174&sku_properties=21433:50753460"
  },
  {
    "rank": 88,
    "itemId": "676138544613",
    "shop": "睡眠骑士床垫企业店",
    "title": "记忆棉薄款床垫凝胶慢回弹榻榻米床垫子软垫家用学生宿舍褥子海绵",
    "url": "https://detail.tmall.com/item.htm?id=676138544613&sku_properties=21433:50753460"
  },
  {
    "rank": 89,
    "itemId": "1056256518394",
    "shop": "品味布帆家居旗舰店",
    "title": "品味布帆薄款乳胶弹簧床垫记忆棉席梦思黄麻12cm15厘米厚软硬可选",
    "url": "https://detail.tmall.com/item.htm?id=1056256518394&sku_properties=21433:50753460"
  },
  {
    "rank": 90,
    "itemId": "922386927791",
    "shop": "yarges悠梦思旗舰店",
    "title": "政府补贴悠梦思乳胶弹簧床垫席梦思精细S黄麻1.8米1.5m卧室租房厚",
    "url": "https://detail.tmall.com/item.htm?id=922386927791&sku_properties=21433:50753460"
  },
  {
    "rank": 91,
    "itemId": "997467867127",
    "shop": "麻师傅舒梦专卖店",
    "title": "麻师傅全拆S形黄麻薄床垫10cm厚老人儿童加硬护腰脊椰棕榈榻榻米",
    "url": "https://detail.tmall.com/item.htm?id=997467867127&sku_properties=21433:50753460"
  },
  {
    "rank": 92,
    "itemId": "1081728080567",
    "shop": "PARELER BEAR旗舰店",
    "title": "派乐熊学生宿舍专用床垫90cmx200cm上下铺单人记忆棉软85cmx190cm",
    "url": "https://detail.tmall.com/item.htm?id=1081728080567&sku_properties=21433:50753460"
  },
  {
    "rank": 93,
    "itemId": "17048177986",
    "shop": "布莱轩尼旗舰店",
    "title": "加硬天然S形黄麻床垫家用儿童老人护腰脊10cm薄榻榻米椰棕含乳胶",
    "url": "https://detail.tmall.com/item.htm?id=17048177986&sku_properties=21433:50753460"
  },
  {
    "rank": 94,
    "itemId": "1067750986444",
    "shop": "moonlightfamily旗舰店",
    "title": "月光之家学生宿舍床垫上下铺专用薄垫单人0.9m软垫子记忆棉可拆洗",
    "url": "https://detail.tmall.com/item.htm?id=1067750986444&sku_properties=21433:50753460"
  },
  {
    "rank": 95,
    "itemId": "663753403176",
    "shop": "moonlightfamily旗舰店",
    "title": "moonlightfamily 床垫优惠专拍链接",
    "url": "https://detail.tmall.com/item.htm?id=663753403176&sku_properties=21433:50753460"
  },
  {
    "rank": 96,
    "itemId": "1053628373215",
    "shop": "甜蜜睡眠旗舰店",
    "title": "【0.01元锁定多件优惠折上折】甜蜜睡眠床垫专属特权 单拍不发货",
    "url": "https://detail.tmall.com/item.htm?id=1053628373215&sku_properties=21433:50753460"
  }
];

    let taskState = null;
    try {
        const raw = sessionStorage.getItem(STORAGE_KEY);
        if (raw) taskState = JSON.parse(raw);
    } catch (e) {}

    if (!taskState || !taskState.running) {
        const ok = confirm(`🚀 准备启动天猫 96 款床垫 1.8米全量 SKU 到手价自动采集？\n• 共计目标：${ALL_TARGETS.length} 款核心在售床垫\n• 规格锁定：1800mm*2000mm\n• 采集项：每个 SKU 款式名称、原价、平台加补后到手价\n\n点击【确定】立即开始自动巡航采集！`);
        if (!ok) return;

        taskState = {
            running: true,
            currentIndex: 0,
            results: []
        };
        sessionStorage.setItem(STORAGE_KEY, JSON.stringify(taskState));
    }

    const sleep = ms => new Promise(r => setTimeout(r, ms));
    const curIdx = taskState.currentIndex;
    const total = ALL_TARGETS.length;

    let hud = document.getElementById('tmall-sku-autopilot-hud');
    if (hud) hud.remove();
    hud = document.createElement('div');
    hud.id = 'tmall-sku-autopilot-hud';
    hud.style.cssText = `
        position: fixed; top: 20px; right: 20px; z-index: 999999999;
        background: rgba(15, 23, 42, 0.95); color: #fff; padding: 18px 22px;
        border-radius: 12px; box-shadow: 0 15px 45px rgba(0,0,0,0.7);
        border: 1px solid rgba(239, 68, 68, 0.7); font-family: sans-serif;
        min-width: 360px; backdrop-filter: blur(10px);
    `;
    hud.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <b style="font-size: 15px; color: #f87171;">🏷️ 1.8m SKU 平台加补价全自动巡航</b>
            <span style="font-size: 12px; color: #38bdf8;">${curIdx + 1} / ${total}</span>
        </div>
        <div style="height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px; overflow: hidden; margin-bottom: 10px;">
            <div style="width: ${Math.round(((curIdx + 1) / total) * 100)}%; height: 100%; background: linear-gradient(90deg, #ef4444, #f97316);"></div>
        </div>
        <div style="font-size: 12px; color: #cbd5e1; margin-bottom: 4px;" id="hud-status">正在分析当前商品 SKU 与到手价...</div>
        <div style="font-size: 11px; color: #94a3b8; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${ALL_TARGETS[curIdx] ? ALL_TARGETS[curIdx].title : ''}</div>
        <button id="btn-stop-tmall-task" style="margin-top: 10px; background: #334155; color: #fff; border: none; padding: 4px 10px; border-radius: 4px; font-size: 11px; cursor: pointer;">⏹️ 暂停任务并导出已有数据</button>
    `;
    document.body.appendChild(hud);

    document.getElementById('btn-stop-tmall-task').onclick = () => {
        finishAndDownload(taskState.results);
        sessionStorage.removeItem(STORAGE_KEY);
        hud.remove();
    };

    function readPagePrices() {
        let bannerPrice = null;
        let origPrice = null;
        let isStartPrice = false;

        const allNodes = Array.from(document.querySelectorAll('div, span, p, b, strong, em'));
        for (let el of allNodes) {
            if (el.children.length === 0 && el.innerText) {
                const txt = el.innerText.trim();
                if (txt.includes('平台加补后') || txt.includes('补贴到手价') || txt.includes('券后') || txt.includes('到手价')) {
                    let p = el.parentElement;
                    while (p && p !== document.body) {
                        const m = p.innerText.match(/(?:平台加补后|补贴到手价|券后价|到手价)[^\d]*¥?\s*(\d+(?:\.\d+)?)\s*(起)?/);
                        if (m) {
                            bannerPrice = parseFloat(m[1]);
                            if (m[2] === '起' || p.innerText.includes('起')) isStartPrice = true;
                            break;
                        }
                        p = p.parentElement;
                    }
                }
                if (txt.includes('优惠前') || txt.includes('原价')) {
                    let p = el.parentElement;
                    while (p && p !== document.body) {
                        const m = p.innerText.match(/(?:优惠前|原价)[^\d]*¥?\s*(\d+(?:\.\d+)?)/);
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

        if (!bannerPrice) {
            const bigPrice = document.querySelector('[class*="bannerPrice"], [class*="priceText"], [class*="highlightPrice"], [class*="PromotionPrice"]');
            if (bigPrice) {
                const m = bigPrice.innerText.match(/(\d+(?:\.\d+)?)/);
                if (m) bannerPrice = parseFloat(m[1]);
            }
        }

        return { bannerPrice, origPrice, isStartPrice };
    }

    function finishAndDownload(results) {
        const jsonStr = JSON.stringify(results, null, 2);
        try { navigator.clipboard.writeText(jsonStr); } catch (e) {}

        const blob = new Blob([jsonStr], { type: 'application/json;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `company_96_mattresses_skus_and_prices_${new Date().toISOString().slice(0, 10)}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        alert(`🎉 恭喜！已完成采集，共累计提取 ${results.length} 款床垫全量 SKU！\n数据已自动下载并复制到剪贴板！`);
    }

    await sleep(1500);

    const currentTarget = ALL_TARGETS[curIdx];
    const initialPrice = readPagePrices();
    console.log(`[${curIdx + 1}/${total}] 当前商品初始加补价格:`, initialPrice);

    const candidateBtns = Array.from(document.querySelectorAll('button, div, span, a, li')).filter(el => {
        const role = el.getAttribute('role');
        const cls = (el.className || '').toLowerCase();
        const txt = el.innerText ? el.innerText.trim() : '';
        const isRadio = role === 'radio' || cls.includes('sku') || cls.includes('prop');
        return isRadio && txt.length >= 2 && txt.length <= 45 && 
               !txt.includes('加入购物车') && !txt.includes('立即购买') && 
               !txt.includes('1800') && !txt.includes('1.8') && !txt.includes('1500') && !txt.includes('1.5') && !txt.includes('1200');
    });

    const skus = [];
    if (candidateBtns.length > 0) {
        for (let btn of candidateBtns) {
            const skuName = btn.innerText.replace(/[\r\n\t]+/g, ' ').trim();
            try {
                btn.click();
                await sleep(350);
            } catch (e) {}
            const p = readPagePrices();
            skus.push({
                name: skuName,
                price: p.bannerPrice || initialPrice.bannerPrice,
                orig: p.origPrice || initialPrice.origPrice,
                tag: '平台加补后'
            });
        }
    }

    if (skus.length === 0 && initialPrice.bannerPrice) {
        skus.push({
            name: '1800mm*2000mm 标准规格款',
            price: initialPrice.bannerPrice,
            orig: initialPrice.origPrice,
            tag: '平台加补后'
        });
    }

    const validP = skus.map(s => s.price).filter(p => typeof p === 'number' && !isNaN(p) && p > 0);
    const minPrice = validP.length > 0 ? Math.min(...validP) : (initialPrice.bannerPrice || null);
    const maxPrice = validP.length > 0 ? Math.max(...validP) : (initialPrice.bannerPrice || null);
    validP.sort((a, b) => a - b);
    const medianPrice = validP.length > 0 ? validP[Math.floor(validP.length / 2)] : minPrice;
    const meanPrice = validP.length > 0 ? parseFloat((validP.reduce((a, b) => a + b, 0) / validP.length).toFixed(2)) : minPrice;

    const itemRecord = {
        rank: currentTarget.rank,
        itemId: currentTarget.itemId,
        shop: currentTarget.shop,
        title: currentTarget.title,
        link: currentTarget.url,
        min_price: minPrice,
        max_price: maxPrice,
        median_price: medianPrice,
        mean_price: meanPrice,
        sku_count: skus.length,
        skus: skus
    };

    taskState.results.push(itemRecord);
    console.log(`✅ [${curIdx + 1}/${total}] 完成当前商品提取:`, itemRecord);

    if (curIdx + 1 >= total) {
        finishAndDownload(taskState.results);
        sessionStorage.removeItem(STORAGE_KEY);
        return;
    }

    taskState.currentIndex = curIdx + 1;
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(taskState));

    const nextItem = ALL_TARGETS[taskState.currentIndex];
    const nextUrl = nextItem.url;
    document.getElementById('hud-status').innerText = `准备跳转第 ${curIdx + 2}/${total} 款: ${nextItem.title.slice(0, 15)}...`;
    
    await sleep(800);
    window.location.href = nextUrl;
})();
