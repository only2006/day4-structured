import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)
MODEL = "deepseek-chat"

# 一条需要"归一化"的测试 JD：15-25K 要拆成 15 和 25
SAMPLE_JD = "Python开发工程师，15-25K·13薪，本科，3年经验，熟悉FastAPI、MySQL"

# ---------- A. 只讲规则 ----------
PROMPT_A = (
    "请从文本中抽取岗位信息，输出 JSON，"
    "包含 title、salary_min_k、salary_max_k，薪资单位是千元。"
)

# ---------- B. 给两个例子（few-shot） ----------
PROMPT_B = """请从文本中抽取岗位信息，输出 JSON，包含 title、salary_min_k、salary_max_k。

【示例输入】
Python开发工程师，15-25K·13薪，本科，3年经验，熟悉FastAPI、MySQL

【示例输出】
{"title": "Python开发工程师", "salary_min_k": 15, "salary_max_k": 25}

【示例输入】
AI应用开发实习生，深圳，薪资面议

【示例输出】
{"title": "AI应用开发实习生", "salary_min_k": null, "salary_max_k": null}
"""


def is_valid_json(text: str) -> bool:
    """模型输出可能是 ```json 包裹或带解释，这里只判断能不能解析成 JSON。"""
    t = text.strip()
    if t.startswith("```"):
        t = t.strip("`")
        if t.lower().startswith("json"):
            t = t[4:]
    try:
        json.loads(t)
        return True
    except json.JSONDecodeError:
        return False


def run_once(prompt: str) -> bool:
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": f"{prompt}\n\n待抽取文本：{SAMPLE_JD}"}],
        temperature=0,
    )
    return is_valid_json(resp.choices[0].message.content or "")


def compare(rounds: int = 10) -> None:
    for label, prompt in [("A.只讲规则", PROMPT_A), ("B.给例子 ", PROMPT_B)]:
        ok = sum(run_once(prompt) for _ in range(rounds))
        print(f"{label}: {ok}/{rounds} 次输出合法 JSON  ({ok / rounds * 100:.0f}%)")


if __name__ == "__&#8203;main__":
    compare(10)