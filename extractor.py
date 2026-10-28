import logging
import time

from openai import OpenAI
from pydantic import ValidationError

from extract import extract_json
from prompts import FEW_SHOT, SYSTEM_PROMPT
from schema import JobPosting

logger = logging.getLogger(__name__)


def build_messages(jd_text: str) -> list[dict]:
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        *FEW_SHOT,
        {"role": "user", "content": f"待抽取的岗位描述：\n\n{jd_text}"},
    ]


def extract_job(
    client: OpenAI,
    model: str,
    jd_text: str,
    max_retries: int = 3,
) -> tuple[JobPosting, int]:
    """抽取岗位信息。返回 (结果, 实际尝试次数)。

    max_retries 包含首次尝试。
    """
    messages = build_messages(jd_text)
    last_error: Exception | None = None

    for attempt in range(1, max_retries + 1):
        raw = ""
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0,
                max_tokens=600,
                response_format={"type": "json_object"},
            )
            raw = response.choices[0].message.content or ""
            return JobPosting.model_validate_json(extract_json(raw)), attempt

        except (ValueError, ValidationError) as exc:
            last_error = exc
            logger.warning("第 %d 次抽取失败：%s", attempt, exc)

            # 关键：把错误回灌给模型，让它自己修
            messages.append({"role": "assistant", "content": raw})
            messages.append(
                {
                    "role": "user",
                    "content": (
                        f"上面的输出不符合要求，错误是：{exc}\n"
                        "请重新输出，只输出合法 JSON 对象，字段名和类型必须严格遵守。"
                    ),
                }
            )
            time.sleep(0.5 * attempt)   # 轻微退避

    raise RuntimeError(f"重试 {max_retries} 次仍失败：{last_error}")