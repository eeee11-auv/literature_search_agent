import requests

from models.paper import Paper


CROSSREF_URL = "https://api.crossref.org/works"


def get_first(items):
    """
    Crossref 很多字段是 list，
    这里只取第一个。
    """

    if not items:
        return None

    return items[0]


def extract_year(item):
    """
    从 Crossref 的 published 字段中提取年份。
    """

    published = (
        item.get("published")
        or item.get("published-print")
        or item.get("published-online")
    )

    if not published:
        return None

    date_parts = published.get(
        "date-parts"
    )

    if not date_parts:
        return None

    if not date_parts[0]:
        return None

    return date_parts[0][0]


def extract_authors(item):
    """
    提取作者姓名。
    """

    authors = []

    for author in item.get("author", []):

        given = author.get(
            "given",
            ""
        )

        family = author.get(
            "family",
            ""
        )

        name = f"{given} {family}".strip()

        if name:
            authors.append(name)

    return authors


def normalize_crossref_paper(item):
    """
    把 Crossref 原始结果统一转换成 Paper。
    """

    title = get_first(
        item.get("title")
    ) or ""

    venue = get_first(
        item.get("container-title")
    )

    doi = item.get("DOI")

    url = item.get("URL")

    return Paper(
        id=doi or url or title,

        title=title,

        authors=extract_authors(
            item
        ),

        year=extract_year(
            item
        ),

        doi=doi,

        abstract=item.get(
            "abstract"
        ),

        venue=venue,

        citation_count=item.get(
            "is-referenced-by-count",
            0
        ),

        relevance_score=None,

        open_access_url=url,

        source="crossref",
    )


def search_crossref(
    query: str,
    start_year: int = 2020,
    end_year: int = 2026,
    top_k: int = 5,
) -> list[Paper]:

    params = {
        "query.bibliographic": query,

        "filter": (
            f"from-pub-date:{start_year}-01-01,"
            f"until-pub-date:{end_year}-12-31"
        ),

        "rows": top_k,

        
        "mailto": "1767580775@qq.com",
    }

    response = requests.get(
        CROSSREF_URL,
        params=params,
        timeout=20,
    )

    response.raise_for_status()

    data = response.json()

    items = (
        data.get("message", {})
        .get("items", [])
    )

    papers = []

    for item in items:

        paper = normalize_crossref_paper(
            item
        )

        papers.append(
            paper
        )

    return papers