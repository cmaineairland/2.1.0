import os
from serpapi import GoogleSearch

def google_search(keyword):
    """
    使用 SerpAPI 进行 Google 搜索，并返回搜索结果中的链接列表。
    :param keyword: 搜索关键词
    :return: 包含搜索结果链接的列表
    """
    params = {
        "api_key": os.getenv("SERPAPI_API_KEY"),
        "engine": "google",
        "q": keyword
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    organic_results = results.get("organic_results", [])
    links = [result.get("link") for result in organic_results if result.get("link")]
    return links