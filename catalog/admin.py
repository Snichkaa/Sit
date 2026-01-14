from django.contrib import admin
from .models import Publisher, Platform, Genre, AgeRating, Game, Region, Sale

admin.site.register(Publisher)
admin.site.register(Platform)
admin.site.register(Genre)
admin.site.register(AgeRating)
admin.site.register(Game)
admin.site.register(Region)
admin.site.register(Sale)
