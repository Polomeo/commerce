from django import forms
from .models import Category


class CreateListingForm(forms.Form):
    categories = Category.objects.all()

    title = forms.CharField(max_length=64,
                            required=True)
    description = forms.CharField(max_length=300,
                                  widget=forms.Textarea,
                                  required=True)
    base_bid = forms.FloatField(min_value=1.0,
                                required=True)
    img_url = forms.URLField(empty_value='')
    category = forms.ModelChoiceField(queryset=categories,
                                      required=True)
