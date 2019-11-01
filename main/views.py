from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views.generic.base import FormView, TemplateView

from openhumans.models import OpenHumansMember


class Index(TemplateView):

    template_name = "main/index.html"

    def get(self, request, *args, **kwargs):
        print("IN GET")
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Log out"""
        if request.user.is_authenticated:
            logout(request)
            return redirect('index')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        auth_url = OpenHumansMember.get_auth_url()
        print(auth_url)
        context['auth_url'] = auth_url
        return context


class Dashboard(TemplateView):

    template_name = "main/dashboard.html"