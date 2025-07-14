from django import forms

from .models import Site
from ..users.models import User


class CreateSiteForm(forms.ModelForm):
    """The :class:`forms.ModelForm` for creating a website (static/dynamic).

    Please note that there is logic in create_form.html that relies directly on the form names and model values.
    If you change anything here, please ensure that creating a site using the form still works.
    """

    MODES = (
        ("static", "Static"),
        ("dynamic", "Dynamic"),
    )

    PURPOSES = (
        ("project", "Project"),
        ("user", "User"),
        ("activity", "Activity"),
        ("other", "Other"),
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["mode"].choices = CreateSiteForm.MODES
        self.fields["purpose"].choices = CreateSiteForm.PURPOSES
        self.fields["users"].queryset = User.objects.filter(is_student=True)

    class Meta:
        model = Site
        fields = ["name", "description", "mode", "purpose", "users"]
