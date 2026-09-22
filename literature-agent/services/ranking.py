import re

from models.paper import Paper


STOPWORDS = {
    "the",
    "a",
    "an",
    "of",
    "for",
    "and",
    "in",
    "on",
    "to",
    "with",
    "using",
}


def normalize_text(text: str | None) -> str:
    """
    文本标准化。
    """

    if not text:
        return ""

    text = text.lower()

    text = re.sub(
        r"[^\w\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def extract_keywords(topic: str) -> list[str]:
    """
    从用户研究主题中提取基础关键词。
    """

    topic = normalize_text(topic)

    words = topic.split()

    keywords = []

    for word in words:

        if word in STOPWORDS:
            continue

        if len(word) <= 2:
            continue

        keywords.append(word)

    return keywords


def calculate_relevance_score(
    paper: Paper,
    topic: str,
    key_phrases: list[str] | None = None,
) -> float:
    """
    计算论文与研究主题的相关性。
    """

    title = normalize_text(
        paper.title
    )

    abstract = normalize_text(
        paper.abstract
    )

    keywords = extract_keywords(
        topic
    )

    score = 0.0

    # -------------------------
    # 1. 普通关键词匹配
    # -------------------------

    for keyword in keywords:

        # 标题里的关键词更重要
        if keyword in title:
            score += 3.0

        # 摘要里的关键词次之
        if keyword in abstract:
            score += 1.0

    # -------------------------
    # 2. 关键专业短语
    # -------------------------

    if key_phrases:

        for phrase in key_phrases:

            phrase = normalize_text(
                phrase
            )

            # 完整专业术语出现在标题
            if phrase in title:
                score += 12.0

            # 出现在摘要
            elif phrase in abstract:
                score += 6.0

    # -------------------------
    # 3. OpenAlex 原始相关性
    # -------------------------

    if paper.relevance_score:
        # OpenAlex relevance_score 数值范围不固定，
        # 所以这里只给很小的影响。
        score += min(
            paper.relevance_score / 100,
            3.0
        )

    return score


def rank_papers(
    papers: list[Paper],
    topic: str,
    key_phrases: list[str] | None = None,
) -> list[tuple[float, Paper]]:

    ranked = []

    for paper in papers:

        score = calculate_relevance_score(
            paper=paper,
            topic=topic,
            key_phrases=key_phrases,
        )

        ranked.append(
            (score, paper)
        )

    ranked.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    return ranked