import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


# =========================
# 读取 .env
# =========================

ROOT_DIR = Path(__file__).resolve().parent.parent

load_dotenv(
    ROOT_DIR / ".env"
)


api_key = os.getenv(
    "OPENROUTER_API_KEY"
)


if not api_key:
    raise RuntimeError(
        "OPENROUTER_API_KEY 没有读取到"
    )


# =========================
# OpenRouter Client
# =========================

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)


# =========================
# 解析 LLM 输出
# =========================

def parse_queries(text: str) -> list[str]:

    if not text:
        raise ValueError(
            "LLM returned empty content."
        )

    text = text.strip()

    print(
        "\nRaw LLM output:"
    )

    print(text)

    # -------------------------
    # 去除 Markdown code fence
    # -------------------------

    if text.startswith("```"):

        lines = text.splitlines()

        # 删除第一行 ```json
        if lines:
            lines = lines[1:]

        # 删除最后一行 ```
        if (
            lines
            and lines[-1].strip() == "```"
        ):
            lines = lines[:-1]

        text = "\n".join(
            lines
        ).strip()

    # -------------------------
    # 找 JSON 数组
    # -------------------------

    start = text.find("[")
    end = text.rfind("]")

    if start == -1 or end == -1:

        raise ValueError(
            "LLM output does not contain "
            "a JSON array."
        )

    json_text = text[
        start:end + 1
    ]

    try:

        queries = json.loads(
            json_text
        )

    except json.JSONDecodeError as error:

        raise ValueError(
            f"Invalid JSON returned by LLM:\n"
            f"{json_text}"
        ) from error

    # -------------------------
    # 检查结果类型
    # -------------------------

    if not isinstance(
        queries,
        list
    ):
        raise ValueError(
            "LLM output must be a list."
        )

    clean_queries = []

    for query in queries:

        if not isinstance(
            query,
            str
        ):
            continue

        query = query.strip()

        if query:
            clean_queries.append(
                query
            )

    return clean_queries


# =========================
# Query Planner
# =========================

def generate_queries(
    topic: str,
    max_queries: int = 5,
) -> list[str]:

    print(
        "\n>>> Calling LLM Query Planner..."
    )

    prompt = f"""
You are a scientific literature search expert.

Research topic:

{topic}

Generate exactly {max_queries} academic search queries.

Requirements:

1. Preserve important technical phrases.
2. Include scientific synonyms.
3. Use terminology commonly found in academic papers.
4. Avoid overly broad queries.
5. Each query should use different wording.
6. Return ONLY a JSON array of strings.
7. Do not include explanations.
8. Do not include Markdown.

Example output:

[
  "Mueller matrix imaging cancer diagnosis",
  "polarimetric imaging tumor tissue"
]
"""

    response = client.chat.completions.create(

        model="openrouter/free",

        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],

        temperature=0.2,
    )

    text = (
        response
        .choices[0]
        .message.content
        or ""
    )

    queries = parse_queries(
        text
    )

    return queries[
        :max_queries
    ]