from django import forms

from .models import Site


class CreateSiteForm(forms.ModelForm):
    class Meta:
        model = Site
        fields = ["name", "description", "mode", "purpose", "users"]
