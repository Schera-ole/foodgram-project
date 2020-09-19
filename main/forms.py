from django import forms
from multiselectfield import MultiSelectFormField

from .models import Recipe, TAGS_CHOICES


class RecipeForm(forms.ModelForm):
    tags = MultiSelectFormField(choices=TAGS_CHOICES)

    class Meta:
        model = Recipe
        fields = ('title','tags','ingredient','time','text','image',)
        