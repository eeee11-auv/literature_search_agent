import time

from planner.query_planner import generate_queries

from tools.openalex import search_papers
from tools.crossref import search_crossref

from services.deduplicate import deduplicate_papers
from services.ranking import rank_papers
from services.llm_reranker import rerank_papers


# ==========================================
# 配置
# ==========================================

topic = (
    "Mueller matrix imaging "
    "for cancer diagnosis"
)


START_YEAR = 2020
END_YEAR = 2026

QUERIES_COUNT = 5

OPENALEX_TOP_K = 5
CROSSREF_TOP_K = 5

USE_OPENALEX = True
USE_CROSSREF = True


# ==========================================
# Step 1
# LLM Query Planner
# ==========================================

print("\nStep 1: Generating search queries...")


queries = generate_queries(
    topic=topic,
    max_queries=QUERIES_COUNT,
)


print("\nLLM Generated Queries:")


for index, query in enumerate(
    queries,
    start=1,
):
    print(
        f"{index}. {query}"
    )


# ==========================================
# Step 2
# 多数据源搜索
# ==========================================

print("\nStep 2: Searching literature databases...")


all_papers = []


for index, query in enumerate(
    queries,
    start=1,
):

    print(
        "\n"
        + "=" * 80
    )

    print(
        f"Query [{index}/{len(queries)}]: "
        f"{query}"
    )


    # --------------------------------------
    # OpenAlex
    # --------------------------------------

    if USE_OPENALEX:

        print(
            "\n[OpenAlex] Searching..."
        )

        try:

            papers = search_papers(
                query=query,
                start_year=START_YEAR,
                end_year=END_YEAR,
                top_k=OPENALEX_TOP_K,
            )

            all_papers.extend(
                papers
            )

            print(
                "[OpenAlex] Retrieved:",
                len(papers)
            )

        except Exception as error:

            print(
                "[OpenAlex] Search failed:",
                error
            )


        time.sleep(1)


    # --------------------------------------
    # Crossref
    # --------------------------------------

    if USE_CROSSREF:

        print(
            "\n[Crossref] Searching..."
        )

        try:

            papers = search_crossref(
                query=query,
                start_year=START_YEAR,
                end_year=END_YEAR,
                top_k=CROSSREF_TOP_K,
            )

            all_papers.extend(
                papers
            )

            print(
                "[Crossref] Retrieved:",
                len(papers)
            )

        except Exception as error:

            print(
                "[Crossref] Search failed:",
                error
            )


        time.sleep(1)


# ==========================================
# Step 3
# 检查搜索结果
# ==========================================

print(
    "\n"
    + "=" * 80
)

print(
    "Raw results:",
    len(all_papers)
)


if not all_papers:

    print(
        "No papers were retrieved."
    )

    raise SystemExit


# ==========================================
# Step 4
# 去重
# ==========================================

print(
    "\nStep 3: Deduplicating papers..."
)


unique_papers = deduplicate_papers(
    all_papers
)


print(
    "Unique papers:",
    len(unique_papers)
)


# ==========================================
# Step 5
# 规则粗排
# ==========================================

print(
    "\nStep 4: Rule-based ranking..."
)


ranked_papers = rank_papers(

    papers=unique_papers,

    topic=topic,

    key_phrases=[
        "Mueller matrix",
        "polarimetric imaging",
        "polarimetry",
        "cancer tissue",
        "tumor tissue",
    ],
)


print(
    "Rule-ranked papers:",
    len(ranked_papers)
)


# ==========================================
# Step 6
# Top 15 交给 LLM
# ==========================================

candidate_papers = ranked_papers[:15]


print(
    "\nStep 5: LLM semantic reranking..."
)


try:

    final_papers = rerank_papers(

        topic=topic,

        ranked_papers=candidate_papers,

        top_k=10,

        min_score=60,
    )


except Exception as error:

    print(
        "LLM reranking failed:",
        error
    )

    print(
        "Falling back to rule ranking..."
    )

    final_papers = [
        (score, paper)
        for score, paper
        in candidate_papers[:10]
    ]


# ==========================================
# Step 7
# 输出最终结果
# ==========================================

print(
    "\n"
    + "=" * 80
)

print(
    "Final Relevant Papers:"
)


if not final_papers:

    print(
        "No papers passed the relevance threshold."
    )


for index, (
    score,
    paper
) in enumerate(
    final_papers,
    start=1,
):

    print(
        "\n"
        + "=" * 80
    )

    print(
        f"{index}. {paper.title}"
    )

    print(
        "Relevance Score:",
        round(score, 2)
    )

    print(
        "Authors:",
        ", ".join(
            paper.authors[:5]
        )
    )

    print(
        "Year:",
        paper.year
    )

    print(
        "Venue:",
        paper.venue
    )

    print(
        "DOI:",
        paper.doi
    )

    print(
        "Citations:",
        paper.citation_count
    )

    print(
        "Source:",
        paper.source
    )