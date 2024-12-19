from django import forms

from .models import Site

# todo: maybe move into tailwind theme?
input_css = "block mt-1 w-full bg-gray-100 rounded-md border-transparent focus:bg-white focus:border-gray-500 focus:ring-0"
select_css = "block bg-gray-100 w-full mt-0 px-2 border-0 border-b-2 border-gray-200 focus:bg-white dark:focus:ring-0 focus:border-black rounded-md"


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
            "name": forms.TextInput(attrs={"class": input_css}),
            "description": forms.TextInput(attrs={"class": input_css}),
            "purpose": forms.Select(attrs={"class": select_css}, choices=[("")]),
            "mode": forms.Select(attrs={"class": select_css}),
        }
