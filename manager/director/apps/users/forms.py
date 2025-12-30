from django import forms


class AcceptGuidelinesForm(forms.Form):
    accept_guidelines = forms.BooleanField(required=True, label="I agree to the guidelines above")
