from django.http import HttpRequest, HttpResponse

from app.apps.core.distance import SearchProvider


def search_by_query(request: HttpRequest) -> HttpResponse:
    query = request.GET.get("q")  # noqa
    max_urls_count = int(request.GET.get("muc", -1))  # noqa

    params = {"query": query}
    max_urls_count != -1 and params.update({"max_urls_count": max_urls_count})

    result = SearchProvider.search(**params)
    return HttpResponse(result)
