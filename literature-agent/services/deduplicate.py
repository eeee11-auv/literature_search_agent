import re

from models.paper import Paper


def normalize_doi(doi: str | None) -> str | None:
    """
    标准化 DOI，方便比较。
    """

    if not doi:
        return None

    doi = doi.strip().lower()

    doi = doi.removeprefix("https://doi.org/")
    doi = doi.removeprefix("http://doi.org/")
    doi = doi.removeprefix("doi:")

    return doi.strip()


def normalize_title(title: str) -> str:
    """
    标准化论文标题。
    """

    if not title:
        return ""

    title = title.lower().strip()

    # 删除标点
    title = re.sub(
        r"[^\w\s]",
        " ",
        title
    )

    # 多个空格合并成一个
    title = re.sub(
        r"\s+",
        " ",
        title
    )

    return title.strip()


def deduplicate_papers(
    papers: list[Paper]
) -> list[Paper]:
    """
    对论文列表进行去重。

    优先根据 DOI 去重；
    没有 DOI 时根据标准化标题去重。
    """

    unique_papers = []

    seen_dois = set()
    seen_titles = set()

    for paper in papers:

        doi = normalize_doi(
            paper.doi
        )

        title = normalize_title(
            paper.title
        )

        # 有 DOI：优先通过 DOI 判断重复
        if doi:

            if doi in seen_dois:
                continue

            seen_dois.add(doi)

        # 没有 DOI：使用标题判断
        else:

            if title in seen_titles:
                continue

        if title:
            seen_titles.add(title)

        unique_papers.append(
            paper
        )

    return unique_papers