import time

import requests

from models.paper import Paper


OPENALEX_URL = "https://api.openalex.org/works"


def reconstruct_abstract(
    inverted_index
) -> str | None:
    """
    OpenAlex 的摘要使用 inverted index 保存。

    例如：

    {
        "This": [0],
        "study": [1],
        "shows": [2]
    }

    将其重新还原为：

    "This study shows"
    """

    if not inverted_index:
        return None

    words = []

    for word, positions in inverted_index.items():

        for position in positions:

            words.append(
                (position, word)
            )

    # 根据单词位置排序
    words.sort(
        key=lambda item: item[0]
    )

    abstract = " ".join(
        word
        for _, word in words
    )

    return abstract


def extract_authors(
    authorships
) -> list[str]:
    """
    从 OpenAlex authorships 中提取作者姓名。
    """

    authors = []

    for authorship in authorships or []:

        author = (
            authorship.get("author")
            or {}
        )

        name = author.get(
            "display_name"
        )

        if name:
            authors.append(name)

    return authors


def normalize_doi(
    doi: str | None
) -> str | None:
    """
    统一 DOI 格式。

    OpenAlex 可能返回：

    https://doi.org/10.xxxx/xxxx

    转换成：

    10.xxxx/xxxx
    """

    if not doi:
        return None

    doi = doi.strip()

    doi = doi.removeprefix(
        "https://doi.org/"
    )

    doi = doi.removeprefix(
        "http://doi.org/"
    )

    doi = doi.removeprefix(
        "doi:"
    )

    return doi.strip()


def extract_venue(
    work
) -> str | None:
    """
    提取期刊 / 会议名称。
    """

    primary_location = (
        work.get("primary_location")
        or {}
    )

    source = (
        primary_location.get("source")
        or {}
    )

    return source.get(
        "display_name"
    )


def normalize_paper(
    work
) -> Paper:
    """
    把 OpenAlex 原始数据转换成
    我们系统内部统一的 Paper 对象。
    """

    abstract = reconstruct_abstract(
        work.get(
            "abstract_inverted_index"
        )
    )

    paper = Paper(

        id=work.get("id") or "",

        title=work.get(
            "title"
        ) or "",

        authors=extract_authors(
            work.get(
                "authorships"
            )
        ),

        year=work.get(
            "publication_year"
        ),

        doi=normalize_doi(
            work.get("doi")
        ),

        abstract=abstract,

        venue=extract_venue(
            work
        ),

        citation_count=work.get(
            "cited_by_count",
            0
        ),

        relevance_score=work.get(
            "relevance_score"
        ),

        open_access_url=(
            work.get(
                "open_access"
            )
            or {}
        ).get(
            "oa_url"
        ),

        source="openalex",
    )

    return paper


def request_openalex(
    params: dict,
    max_retries: int = 5,
) -> dict:
    """
    请求 OpenAlex API。

    对以下错误进行有限重试：

    429：
        Too Many Requests

    5xx：
        OpenAlex 服务端暂时异常

    使用 Exponential Backoff：

    第一次等待 1 秒
    第二次等待 2 秒
    第三次等待 4 秒
    第四次等待 8 秒
    第五次等待 16 秒
    """

    for attempt in range(
        max_retries
    ):

        try:

            response = requests.get(
                OPENALEX_URL,
                params=params,
                timeout=30,
            )

        except requests.exceptions.Timeout:

            wait_time = 2 ** attempt

            print(
                f"OpenAlex timeout. "
                f"Retrying in "
                f"{wait_time}s..."
            )

            time.sleep(
                wait_time
            )

            continue

        except requests.exceptions.RequestException as error:

            wait_time = 2 ** attempt

            print(
                f"OpenAlex request error: "
                f"{error}"
            )

            print(
                f"Retrying in "
                f"{wait_time}s..."
            )

            time.sleep(
                wait_time
            )

            continue

        # 请求成功
        if response.status_code == 200:

            return response.json()

        # 429 限流
        if response.status_code == 429:

            wait_time = 2 ** attempt

            print(
                "OpenAlex rate limited "
                "(HTTP 429). "
                f"Waiting {wait_time}s..."
            )

            time.sleep(
                wait_time
            )

            continue

        # 服务端错误
        if 500 <= response.status_code < 600:

            wait_time = 2 ** attempt

            print(
                "OpenAlex server error "
                f"(HTTP "
                f"{response.status_code})."
            )

            print(
                f"Retrying in "
                f"{wait_time}s..."
            )

            time.sleep(
                wait_time
            )

            continue

        # 其他错误例如：
        # 400 / 401 / 403
        # 通常不适合一直重试
        response.raise_for_status()

    raise RuntimeError(
        "OpenAlex request failed "
        f"after {max_retries} retries."
    )


def search_papers(
    query: str,
    start_year: int = 2020,
    end_year: int = 2026,
    top_k: int = 10,
    api_key: str | None = None,
) -> list[Paper]:
    """
    搜索 OpenAlex 文献。

    参数：

    query:
        搜索关键词

    start_year:
        起始年份

    end_year:
        截止年份

    top_k:
        返回论文数量

    api_key:
        OpenAlex API Key。
        没有时可以传 None。
    """

    if not query.strip():

        raise ValueError(
            "query 不能为空"
        )

    if start_year > end_year:

        raise ValueError(
            "start_year 不能大于 end_year"
        )

    if top_k <= 0:

        raise ValueError(
            "top_k 必须大于 0"
        )

    # 当前 MVP 不需要一次拿很多
    top_k = min(
        top_k,
        100
    )

    params = {

        "search": query,

        "filter": (
            f"from_publication_date:"
            f"{start_year}-01-01,"
            f"to_publication_date:"
            f"{end_year}-12-31"
        ),

        "per_page": top_k,
    }

    # 有 API Key 就带上
    if api_key:

        params[
            "api_key"
        ] = api_key

    data = request_openalex(
        params=params,
        max_retries=5,
    )

    papers = []

    for work in data.get(
        "results",
        []
    ):

        paper = normalize_paper(
            work
        )

        papers.append(
            paper
        )

    return papers