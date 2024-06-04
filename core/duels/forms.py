from django import forms
from django.core.exceptions import ValidationError
from .models import Duels

class DuelForm(forms.ModelForm):
    class Meta:
        model = Duels
        fields = ['winner']

    def clean(self):
        cleaned_data = super().clean()
        players = [cleaned_data.get('player_1'), cleaned_data.get('player_2')]
        winner = cleaned_data.get('winner')

        if winner and players:
            if winner not in players:
                raise ValidationError("The winner must be one of the duelists.")

        return cleaned_data