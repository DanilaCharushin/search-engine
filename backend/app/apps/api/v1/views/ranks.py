from django.http import HttpRequest, HttpResponse

from app.apps.core.page_ranker import PageRanker


def calculate_ranks(request: HttpRequest) -> HttpResponse:
    iterations_count = int(request.GET.get("ic", -1))  # noqa
    d_coefficient = float(request.GET.get("d", -1))  # noqa

    params = {}
    iterations_count != -1 and params.update({"iterations_count": iterations_count})
    d_coefficient != -1 and params.update({"d_coefficient": d_coefficient})

    page_ranks = PageRanker.calculate_ranks(**params)
    return HttpResponse("<br>".join(map(str, page_ranks)))
