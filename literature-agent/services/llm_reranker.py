import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


ROOT_DIR = Path(__file__).resolve().parent.parent

load_dotenv(
    ROOT_DIR / ".env"
)


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)


def parse_scores(text: str):

    if not text:
        raise ValueError(
            "LLM returned empty content."
        )

    text = text.strip()

    start = text.find("[")
    end = text.rfind("]")

    if start == -1 or end == -1:
        raise ValueError(
            f"No JSON array found:\n{text}"
        )

    return json.loads(
        text[start:end + 1]
    )


def rerank_papers(
    topic,
    ranked_papers,
    top_k=10,
    min_score=60,
):

    candidates = []


    for index, (_, paper) in enumerate(
        ranked_papers,
        start=1,
    ):

        candidates.append({
            "id": index,
            "title": paper.title,
            "abstract": (
                paper.abstract or ""
            )[:1500],
            "venue": paper.venue or "",
        })


    prompt = f"""
You are evaluating scientific papers
for literature research.

Research topic:

{topic}


Score each paper from 0 to 100
based on semantic relevance.


Scoring guide:

90-100:
Directly studies cancer or tumor diagnosis
using Mueller matrix or polarimetric imaging.

70-89:
Strongly related to cancer tissue,
tumor pathology, or biomedical polarimetry.

50-69:
Related Mueller matrix or polarimetric
methodology, but not directly cancer diagnosis.

0-49:
Unrelated domain, plant imaging,
general optics, or method-only research
without meaningful cancer relevance.


Return ONLY a JSON array.

Example:

[
    {{"id": 1, "score": 95}},
    {{"id": 2, "score": 40}}
]


Papers:

{json.dumps(
    candidates,
    ensure_ascii=False
)}
"""


    response = client.chat.completions.create(

        model="openrouter/free",

        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],

        temperature=0.1,
    )


    text = (
        response
        .choices[0]
        .message.content
        or ""
    )


    print(
        "\nRaw LLM Reranker Output:"
    )

    print(text)


    scores = parse_scores(
        text
    )


    paper_map = {
        index: paper
        for index, (_, paper)
        in enumerate(
            ranked_papers,
            start=1,
        )
    }


    results = []


    for item in scores:

        paper_id = item.get("id")
        score = item.get("score")


        if paper_id not in paper_map:
            continue


        if not isinstance(
            score,
            (int, float)
        ):
            continue


        score = max(
            0,
            min(100, score)
        )


        if score >= min_score:

            results.append(
                (
                    score,
                    paper_map[paper_id],
                )
            )


    results.sort(
        key=lambda item: item[0],
        reverse=True,
    )


    return results[:top_k]