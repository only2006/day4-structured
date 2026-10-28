import logging
import os
import statistics
import time

from dotenv import load_dotenv
from openai import OpenAI

from extractor import extract_job

load_dotenv()

logging.basicConfig(
    level=logging.WARNING,     # 只看失败，避免刷屏
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
)

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url=os.getenv("LLM_BASE_URL", "https://api.deepseek.com"),
)
MODEL = os.getenv("LLM_MODEL", "deepseek-chat")

# 20 条真实 JD，覆盖各种边界情况
SAMPLES: list[str] = [
    "Python开发工程师，广州，12-20K，大专，1-3年，熟悉Django、MySQL。",
    "AI应用开发工程师，深圳，20-35K·14薪，本科，熟悉RAG、LangChain、向量数据库。",
    "大模型算法工程师，北京，40-70K，硕士，有顶会论文优先。",
    "数据分析实习生，东莞，150元/天，在校生，会SQL和Excel。",
    "Java后端开发，佛山，10-18K，本科，3年经验，Spring Cloud。",
    "前端开发工程师，珠海，8-15K，大专，Vue3、TypeScript。",
    "技术支持工程师，中山，6-9K，大专，负责客户系统部署与售后，需出差。",
    "AI训练师，惠州，5-8K，大专，负责数据标注与质量检查。",
    "Prompt工程师，深圳，15-30K，本科，负责提示词设计与效果优化。",
    "全栈开发，广州，15-25K，本科，React + Node.js + PostgreSQL。",
    "算法工程师（CV方向），深圳，30-50K，硕士，目标检测。",
    "产品经理（AI方向），广州，18-30K，本科，负责AI产品规划。",
    "运维工程师，江门，7-12K，大专，Linux、Nginx、Docker。",
    "软件测试工程师，东莞，8-13K，大专，会写Python自动化脚本。",
    "某创业公司招聘：",
    "AI应用开发（远程），薪资面议，负责Agent工作流搭建。",
    "数据标注员，汕头，4-6K，不限学历，坐班。",
    "嵌入式开发，深圳，15-25K，本科，C/C++，RTOS。",
    "AI产品售前，广州，面议，需3年以上经验，负责方案讲解。",
    "爬虫工程师，广州，10-18K，大专，Scrapy、反爬经验。",
]

ROUNDS = 5   # 20 条 × 5 轮 = 100 次调用


def main() -> None:
    total = success = 0
    retry_counts: list[int] = []
    failures: list[tuple[int, str]] = []
    latencies: list[float] = []
    start_all = time.time()

    for round_no in range(1, ROUNDS + 1):
        for idx, jd in enumerate(SAMPLES):
            total += 1
            t0 = time.time()
            try:
                job, used = extract_job(client, MODEL, jd)
                latencies.append(time.time() - t0)
                success += 1
                retry_counts.append(used - 1)
                if round_no == 1:
                    print(f"[{idx:02d}] {job.title} | {job.city} | "
                          f"{job.salary_min_k}-{job.salary_max_k}K | "
                          f"AI={job.is_ai_related}")
            except Exception as exc:              # noqa: BLE001
                failures.append((idx, str(exc)[:120]))
                print(f"[{idx:02d}] ❌ 失败：{str(exc)[:80]}")

        print(f"--- 第 {round_no} 轮完成，累计 {success}/{total} ---")

    rate = success / total * 100
    print("\n========== 验收结果 ==========")
    print(f"总调用     : {total}")
    print(f"成功       : {success}")
    print(f"成功率     : {rate:.1f}%   （目标 > 95%）")
    if retry_counts:
        print(f"平均重试   : {statistics.mean(retry_counts):.2f} 次")
        print(f"一次通过率 : {retry_counts.count(0) / len(retry_counts) * 100:.1f}%")
    if latencies:
        print(f"平均耗时   : {statistics.mean(latencies):.2f} 秒")
    print(f"总耗时     : {time.time() - start_all:.0f} 秒")

    if failures:
        print("\n失败样本：")
        for idx, msg in failures[:10]:
            print(f"  [{idx}] {msg}")


if __name__ == "__main__":
    main()