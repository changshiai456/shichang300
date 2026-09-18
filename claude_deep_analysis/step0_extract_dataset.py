# -*- coding: utf-8 -*-
"""
从大屏 HTML 中抽取内嵌的 DB(300款商品/4594条SKU) 与 MAIN_IMAGE_DATA(首图OCR),
合并为独立数据集 dataset.json, 供后续赛道竞选与爆品设计分析使用。
"""
import io
import json
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, "床垫300款排名与SKU价格交互分析大屏.html")
OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def grab_json_object(text, start_idx):
    """从 start_idx（'{' 位置）开始做括号配对，返回 JSON 字符串与结束位置。"""
    depth = 0
    in_str = False
    esc = False
    for i in range(start_idx, len(text)):
        ch = text[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start_idx:i + 1], i + 1
    raise ValueError("未找到配对的右括号")


def extract(varname, text):
    m = re.search(r"const\s+%s\s*=\s*" % varname, text)
    if not m:
        raise ValueError("未找到变量 %s" % varname)
    brace = text.index("{", m.end())
    raw, _ = grab_json_object(text, brace)
    return json.loads(raw)


def main():
    with open(HTML, "r", encoding="utf-8") as f:
        text = f.read()

    db = extract("DB", text)
    mid = extract("MAIN_IMAGE_DATA", text)

    print("DB keys:", list(db.keys()))
    print("products:", len(db["products"]))
    print("main_image records:", len(mid))

    # 以 rank 为键合并首图 OCR 数据
    merged = []
    for p in db["products"]:
        rank = str(p["rank"])
        img = mid.get(rank, {})
        row = dict(p)
        row["ocr_raw"] = img.get("ocr_raw", "")
        row["ocr_lines"] = img.get("ocr_lines", [])
        row["selling_points"] = img.get("selling_points", [])
        row["marketing_text"] = img.get("marketing_text", [])
        row["visual_format"] = img.get("visual_format", [])
        row["price_analysis"] = img.get("price_analysis", {})
        row["has_image"] = img.get("has_image", False)
        merged.append(row)

    out = {
        "meta": {
            "total_products": db["total_products"],
            "total_skus": db["total_skus"],
            "overall_price_median": db["overall_price_median"],
            "overall_price_mean": db["overall_price_mean"],
            "source": "床垫300款排名与SKU价格交互分析大屏.html",
        },
        "price_bands_stats": db["price_bands_stats"],
        "rank_tiers_stats": db["rank_tiers_stats"],
        "top_shops_stats": db["top_shops_stats"],
        "products": merged,
    }

    path = os.path.join(OUT_DIR, "dataset.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)

    total_sku = sum(len(p["skus"]) for p in merged)
    with_ocr = sum(1 for p in merged if p["ocr_raw"])
    print("写出:", path)
    print("SKU 总数校验:", total_sku)
    print("含首图OCR商品数:", with_ocr)


if __name__ == "__main__":
    main()
