# Codex 独立深度分析

先读 `决策摘要.md`，细节见 `深度分析报告.md`；双击 `index.html` 可离线浏览完整报告。

## 复跑

仅需 Python 3.10+ 标准库，在项目根目录执行：

```powershell
python .\codex_deep_analysis\analyze_market.py
python .\codex_deep_analysis\test_analysis.py
```

脚本只读取根目录 `index.html`、`main_images_full_analysis.json`，并记录同名中文HTML的哈希；所有输出都在本目录。无网络依赖，无API调用。

## 代码与假设

- `analyze_market.py`：公开入口。
- `pipeline.py`：抽取、清洗、候选筛选、评分、敏感性分析。
- `scoring_config.json`：5个多维赛道、5套权重、评分锚点和4角色产品评审权重。
- `product_concepts.json`：统一5款设计、层厚、主图、SKU、梯度价格、成本假设。
- `product_review.py`：独立评审合成、权重/判断分扰动、成本情景。
- `expert_reviews/`：数据、操盘、供应链、视觉智能体的原始评审；每条均有反对意见和门槛。
- `render_report.py`：由同一结果生成Markdown及离线HTML，不手工维护第二套分数。
- `test_analysis.py`：来源、去重、厚度、价格、评分、经济模型与输出一致性校验。
- `outputs/`：机器可读结果、清洗台账、赛道逐行证据、竞品和评分CSV。

专家意见不是脚本运行时重新生成的。修改产品方案、赛道或评分标准后应重新审议专家文件，不能直接沿用旧分。

## 数据修正

主图OCR与同排名商品存在明确错配，原始图片/商品ID映射缺失。故从V2起禁止按rank回连OCR，图片池只做整体标签分析。排名不是销量，折扣不是毛利，设计价格和BOM成本均未报价验证。初稿里的预置产品分已移除。

`_db_raw.json`、`outputs/stage1_preliminary.json` 为早期抽取/中间核验文件，不是最终依据；最终依据统一为 `outputs/analysis_result.json`。所有原项目文件保留。
