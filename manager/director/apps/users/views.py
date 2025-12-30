from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from director.apps.users.forms import AcceptGuidelinesForm
from director.apps.utils.decorators import guidelines_not_required


@guidelines_not_required
@login_required
def accept_guidelines(request):
    if request.user.accepted_guidelines:
        messages.error(request, "You already accepted the guidelines.")
        return redirect("sites:index")

    accept_guidelines_form = AcceptGuidelinesForm(request.POST)

    if request.method == "POST" and accept_guidelines_form.is_valid() and accept_guidelines_form.cleaned_data["accept_guidelines"] == True:
        request.user.accepted_guidelines = True
        request.user.save()
        messages.success(request, "Thank you for accepting the guidelines.")

        return redirect("sites:index")

    return render(request, "users/accept_guidelines.html", {"form": accept_guidelines_form})


@login_required
def banned_view(request):
    if not request.user.is_currently_banned:
        messages.error(request, "You cannot access this page.")
        return redirect("sites:index")

    return render(request, "users/banned.html")
