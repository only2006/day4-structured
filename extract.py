import json
import re


def extract_json(text: str) -> str:
    """从模型输出里抠出 JSON 字符串，容忍 markdown 包裹和多余解释。"""
    text = text.strip()

    # 去掉 ```json ... ``` 包裹
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    # 兜底：截取第一个 { 到最后一个 }
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"输出里找不到 JSON：{text[:100]}")

    return text[start : end + 1]