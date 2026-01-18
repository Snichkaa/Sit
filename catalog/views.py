from django.db.models import Sum, Avg
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpRequest, HttpResponse
from django.template import engines

from .models import Publisher, Platform, Genre, Game, Sale, Region
from .forms import GameForm

jinja = engines["jinja2"]


def render_jinja(request: HttpRequest, template_name: str, context: dict):
    tmpl = jinja.get_template(template_name)
    # В Jinja2-шаблонах удобнее работать с переменными напрямую,
    # поэтому раскладываем context в корень.
    html = tmpl.render({**context, "request": request})
    return HttpResponse(html)


def index(request):
    global_region = Region.objects.filter(code="GLOBAL").first()

    top_genres = []
    top_platforms = []
    if global_region:
        top_genres = (
            Sale.objects.filter(region=global_region)
            .values("game__genre__name")
            .annotate(total=Sum("sales_millions"))
            .order_by("-total")[:10]
        )
        top_platforms = (
            Sale.objects.filter(region=global_region)
            .values("game__platform__name")
            .annotate(total=Sum("sales_millions"))
            .order_by("-total")[:10]
        )

    avg_critic_by_genre = (
        Game.objects.exclude(critic_score__isnull=True)
        .values("genre__name")
        .annotate(avg_score=Avg("critic_score"))
        .order_by("-avg_score")[:10]
    )

    return render_jinja(
        request,
        "catalog/index.html",
        {
            "top_genres": list(top_genres),
            "top_platforms": list(top_platforms),
            "avg_critic_by_genre": list(avg_critic_by_genre),
        },
    )


def publishers(request):
    return render_jinja(
        request,
        "catalog/tables/publishers.html",
        {"rows": Publisher.objects.order_by("name")[:5000]},
    )


def platforms(request):
    return render_jinja(
        request,
        "catalog/tables/platforms.html",
        {"rows": Platform.objects.order_by("name")},
    )


def genres(request):
    return render_jinja(
        request,
        "catalog/tables/genres.html",
        {"rows": Genre.objects.order_by("name")},
    )


def games(request):
    qs = (
        Game.objects.select_related("publisher", "platform", "genre", "age_rating")
        .order_by("name")[:2000]
    )
    return render_jinja(request, "catalog/tables/games.html", {"rows": qs})


def sales(request):
    qs = Sale.objects.select_related("game", "region").order_by("game__name")[:5000]
    return render_jinja(request, "catalog/tables/sales.html", {"rows": qs})


def game_create(request):
    if request.method == "POST":
        form = GameForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("games")
    else:
        form = GameForm()
    return render_jinja(
        request, "catalog/forms/game_form.html", {"form": form, "mode": "create"}
    )


def game_update(request, pk: int):
    obj = get_object_or_404(Game, pk=pk)
    if request.method == "POST":
        form = GameForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect("games")
    else:
        form = GameForm(instance=obj)
    return render_jinja(
        request,
        "catalog/forms/game_form.html",
        {"form": form, "mode": "edit", "obj": obj},
    )


def game_delete(request, pk: int):
    obj = get_object_or_404(Game, pk=pk)
    if request.method == "POST":
        obj.delete()
        return redirect("games")
    return render_jinja(
        request, "catalog/forms/game_confirm_delete.html", {"obj": obj}
    )
