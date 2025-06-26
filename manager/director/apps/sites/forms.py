from django import forms

from .models import Site


class CreateSiteForm(forms.ModelForm):
    """The :class:`forms.ModelForm` for creating a website (static/dynamic).

    Please note that there is logic in create_form.html that relies directly on the form names and model values.
    If you change anything here, please ensure that creating a site using the form still works.
    """

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
