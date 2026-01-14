from django.db import models

class Publisher(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name

class Platform(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Genre(models.Model):
    name = models.CharField(max_length=80, unique=True)

    def __str__(self):
        return self.name

class AgeRating(models.Model):
    code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.code

class Game(models.Model):
    name = models.CharField(max_length=300)
    year = models.IntegerField(null=True, blank=True)

    publisher = models.ForeignKey(Publisher, on_delete=models.PROTECT, related_name="games")
    platform = models.ForeignKey(Platform, on_delete=models.PROTECT, related_name="games")
    genre = models.ForeignKey(Genre, on_delete=models.PROTECT, related_name="games")
    age_rating = models.ForeignKey(AgeRating, on_delete=models.SET_NULL, null=True, blank=True)

    developer = models.CharField(max_length=200, null=True, blank=True)

    critic_score = models.FloatField(null=True, blank=True)
    critic_count = models.IntegerField(null=True, blank=True)
    user_score = models.FloatField(null=True, blank=True)
    user_count = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ("name", "platform", "year")

    def __str__(self):
        return f"{self.name} ({self.platform})"

class Region(models.Model):
    code = models.CharField(max_length=10, unique=True)  # NA/EU/JP/OTHER/GLOBAL

    def __str__(self):
        return self.code

class Sale(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="sales")
    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    sales_millions = models.FloatField()

    class Meta:
        unique_together = ("game", "region")

    def __str__(self):
        return f"{self.game} {self.region}: {self.sales_millions}"
