from django import forms
from django.forms.widgets import Textarea, TextInput
from django.template.loader import render_to_string

from .models import Site


class DirectorSelect(forms.Select):
    def __init__(self, attrs=None, choices=None):
        super().__init__(attrs=attrs, choices=choices)
        if choices is None:
            choices = [("")]

    def render(self, name, value, attrs=None, renderer=None):
        return render_to_string(
            "components/dropdown.html",
            {
                "extra_div_classes": self.attrs.get("extra_div_classes", ""),
                "extra_input_classes": self.attrs.get("extra_input_classes", ""),
                "extra_li_classes": self.attrs.get("extra_li_classes", ""),
                "elem_name": name,
                "elem_id": self.attrs.get("id", "id_" + name),
                "choices": self.choices,
            },
        )


class CreateSiteForm(forms.ModelForm):
    PURPOSES = (
        ("project", "Project"),
        ("user", "User"),
        ("activity", "Activity"),
        ("other", "Other"),
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["purpose"].choices = CreateSiteForm.PURPOSES

    class Meta:
        model = Site
        fields = ["name", "description", "mode", "purpose"]
        widgets = {
            "name": TextInput(attrs={"class": "dt-input block"}),
            "description": Textarea(attrs={"class": "dt-input block lg:max-h-44 sm:max-h-16"}),
            "purpose": DirectorSelect(),
            "mode": forms.HiddenInput(),
        }
