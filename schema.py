from pydantic import BaseModel, Field


class JobPosting(BaseModel):
    """从招聘 JD 文本中抽取的结构化信息。"""

    title: str = Field(description="岗位名称")
    company: str | None = Field(default=None, description="公司名，没有则 null")
    city: str | None = Field(default=None, description="城市")
    salary_min_k: int | None = Field(default=None, description="月薪下限，单位千元")
    salary_max_k: int | None = Field(default=None, description="月薪上限，单位千元")
    education: str | None = Field(default=None, description="学历要求")
    experience: str | None = Field(default=None, description="经验要求")
    skills: list[str] = Field(default_factory=list, description="明确提到的技术名词")
    is_ai_related: bool = Field(description="是否与 AI / 大模型相关")
    summary: str = Field(description="一句话概括，不超过 30 字")