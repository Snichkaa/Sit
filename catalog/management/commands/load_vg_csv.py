from __future__ import annotations

import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.core.management.base import BaseCommand, CommandParser
from django.db import transaction

from catalog.models import Developer, Game, GameSale, Genre, Platform, Publisher, Rating, Region


REGIONS = [
    ("NA", "North America"),
    ("EU", "Europe"),
    ("JP", "Japan"),
    ("OTHER", "Other"),
    ("GLOBAL", "Global"),
]


def to_int(value):
    try:
        if value is None or value == "":
            return None
        return int(float(value))
    except Exception:
        return None


def to_float(value):
    try:
        if value is None or value == "":
            return None
        return float(value)
    except Exception:
        return None


def to_decimal(value) -> Decimal:
    try:
        if value is None or value == "":
            return Decimal("0")
        return Decimal(str(value)).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        return Decimal("0")


class Command(BaseCommand):
    help = "Загружает данные из CSV (Video Games Sales) в PostgreSQL и нормализованные таблицы."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--csv",
            dest="csv_path",
            default="data/Video_Games_Sales_as_at_22_Dec_2016.csv",
            help="Путь к CSV файлу (относительно корня проекта)",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="Сколько строк загрузить (0 = все)",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        base_dir = Path.cwd()
        csv_path = (base_dir / options["csv_path"]).resolve()
        limit = options["limit"]

        if not csv_path.exists():
            raise SystemExit(f"CSV не найден: {csv_path}")

        # Regions bootstrap
        for code, name in REGIONS:
            Region.objects.get_or_create(code=code, defaults={"name": name})

        regions = {r.code: r for r in Region.objects.all()}

        created_games = 0
        processed = 0

        self.stdout.write(self.style.NOTICE(f"Читаю CSV: {csv_path}"))

        with csv_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                processed += 1
                if limit and processed > limit:
                    break

                name = (row.get("Name") or "").strip()
                platform_code = (row.get("Platform") or "").strip()
                genre_name = (row.get("Genre") or "").strip()
                publisher_name = (row.get("Publisher") or "").strip()
                developer_name = (row.get("Developer") or "").strip()
                rating_code = (row.get("Rating") or "").strip()

                if not name or not platform_code or not genre_name:
                    continue

                platform, _ = Platform.objects.get_or_create(code=platform_code)
                genre, _ = Genre.objects.get_or_create(name=genre_name)

                publisher = None
                if publisher_name:
                    publisher, _ = Publisher.objects.get_or_create(name=publisher_name)

                developer = None
                if developer_name:
                    developer, _ = Developer.objects.get_or_create(name=developer_name)

                rating = None
                if rating_code:
                    rating, _ = Rating.objects.get_or_create(code=rating_code)

                game, created = Game.objects.get_or_create(
                    name=name,
                    platform=platform,
                    year_of_release=to_int(row.get("Year_of_Release")),
                    defaults={
                        "genre": genre,
                        "publisher": publisher,
                        "developer": developer,
                        "rating": rating,
                        "critic_score": to_float(row.get("Critic_Score")),
                        "critic_count": to_int(row.get("Critic_Count")),
                        "user_score": to_float(row.get("User_Score")),
                        "user_count": to_int(row.get("User_Count")),
                    },
                )

                if not created:
                    # ensure FK and metrics are filled if empty
                    changed = False
                    if game.genre_id != genre.id:
                        game.genre = genre
                        changed = True
                    for attr, val in [
                        ("publisher", publisher),
                        ("developer", developer),
                        ("rating", rating),
                    ]:
                        if getattr(game, f"{attr}_id") is None and val is not None:
                            setattr(game, attr, val)
                            changed = True

                    for attr, val in [
                        ("critic_score", to_float(row.get("Critic_Score"))),
                        ("critic_count", to_int(row.get("Critic_Count"))),
                        ("user_score", to_float(row.get("User_Score"))),
                        ("user_count", to_int(row.get("User_Count"))),
                    ]:
                        if getattr(game, attr) is None and val is not None:
                            setattr(game, attr, val)
                            changed = True

                    if changed:
                        game.save(update_fields=[
                            "genre", "publisher", "developer", "rating",
                            "critic_score", "critic_count", "user_score", "user_count"
                        ])

                if created:
                    created_games += 1

                sales_map = {
                    "NA": row.get("NA_Sales"),
                    "EU": row.get("EU_Sales"),
                    "JP": row.get("JP_Sales"),
                    "OTHER": row.get("Other_Sales"),
                    "GLOBAL": row.get("Global_Sales"),
                }

                for rcode, sval in sales_map.items():
                    region = regions.get(rcode)
                    if not region:
                        continue
                    GameSale.objects.update_or_create(
                        game=game,
                        region=region,
                        defaults={"sales_millions": to_decimal(sval)},
                    )

                if processed % 1000 == 0:
                    self.stdout.write(f"Обработано строк: {processed}")

        self.stdout.write(self.style.SUCCESS(f"Готово. Строк обработано: {processed}. Новых игр создано: {created_games}"))
