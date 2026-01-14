from django import forms
from .models import Game

class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = [
            "name", "year",
            "publisher", "platform", "genre", "age_rating",
            "developer",
            "critic_score", "critic_count",
            "user_score", "user_count",
        ]
