from django.core.management.base import BaseCommand
from django.db import transaction
import pandas as pd

from catalog.models import Publisher, Platform, Genre, AgeRating, Game, Region, Sale

# Expected columns in CSV (typical for this dataset):
# Name, Platform, Year_of_Release, Genre, Publisher, Developer,
# NA_Sales, EU_Sales, JP_Sales, Other_Sales, Global_Sales,
# Critic_Score, Critic_Count, User_Score, User_Count, Rating

REGIONS = [
    ("NA", "NA_Sales"),
    ("EU", "EU_Sales"),
    ("JP", "JP_Sales"),
    ("OTHER", "Other_Sales"),
    ("GLOBAL", "Global_Sales"),
]

class Command(BaseCommand):
    help = "Load Video Game Sales with Ratings CSV into PostgreSQL"

    def add_arguments(self, parser):
        parser.add_argument("--path", required=True, help="Path to CSV file")

    @transaction.atomic
    def handle(self, *args, **opts):
        path = opts["path"]
        df = pd.read_csv(path)

        for code, _ in REGIONS:
            Region.objects.get_or_create(code=code)

        def norm_str(x):
            if pd.isna(x):
                return None
            s = str(x).strip()
            return s if s else None

        def to_float(v):
            if pd.isna(v): return None
            try: return float(v)
            except: return None

        def to_int(v):
            if pd.isna(v): return None
            try: return int(v)
            except: return None

        created_games = 0

        for _, row in df.iterrows():
            name = norm_str(row.get("Name"))
            if not name:
                continue

            platform_name = norm_str(row.get("Platform")) or "Unknown"
            genre_name = norm_str(row.get("Genre")) or "Unknown"
            publisher_name = norm_str(row.get("Publisher")) or "Unknown"
            rating_code = norm_str(row.get("Rating"))

            year_val = row.get("Year_of_Release")
            year = int(year_val) if pd.notna(year_val) else None

            publisher, _ = Publisher.objects.get_or_create(name=publisher_name)
            platform, _ = Platform.objects.get_or_create(name=platform_name)
            genre, _ = Genre.objects.get_or_create(name=genre_name)
            age_rating = None
            if rating_code:
                age_rating, _ = AgeRating.objects.get_or_create(code=rating_code)

            game, game_created = Game.objects.get_or_create(
                name=name,
                platform=platform,
                year=year,
                defaults={
                    "publisher": publisher,
                    "genre": genre,
                    "age_rating": age_rating,
                    "developer": norm_str(row.get("Developer")),
                    "critic_score": to_float(row.get("Critic_Score")),
                    "critic_count": to_int(row.get("Critic_Count")),
                    "user_score": to_float(row.get("User_Score")),
                    "user_count": to_int(row.get("User_Count")),
                }
            )

            if not game_created:
                game.publisher = publisher
                game.genre = genre
                game.age_rating = age_rating
                game.developer = norm_str(row.get("Developer"))
                game.critic_score = to_float(row.get("Critic_Score"))
                game.critic_count = to_int(row.get("Critic_Count"))
                game.user_score = to_float(row.get("User_Score"))
                game.user_count = to_int(row.get("User_Count"))
                game.save()

            if game_created:
                created_games += 1

            for region_code, col in REGIONS:
                val = row.get(col)
                if pd.isna(val):
                    continue
                try:
                    sales = float(val)
                except:
                    continue
                region = Region.objects.get(code=region_code)
                Sale.objects.update_or_create(
                    game=game,
                    region=region,
                    defaults={"sales_millions": sales}
                )

        self.stdout.write(self.style.SUCCESS(f"Done. Created games: {created_games}"))
