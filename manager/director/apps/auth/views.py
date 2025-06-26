from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django_htmx.http import HttpResponseClientRedirect


class HTMXLoginView(LoginView):
    template_name = "auth/login.html"

    def form_valid(self, form: AuthenticationForm):
        response = super().form_valid(form)

        if self.request.htmx:
            return HttpResponseClientRedirect(self.get_redirect_url())

        return response

    def form_invalid(self, form: AuthenticationForm):
        if self.request.htmx:
            return render(
                self.request,
                "auth/login.html.partials/password.html",
                self.get_context_data(form=form),
            )

        return super().form_invalid(form)


@login_required
def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect("sites:index")
