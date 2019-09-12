from django.views.generic.base import TemplateView

from openhumans.models import OpenHumansMember


class Index(TemplateView):

    template_name = "main/index.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        auth_url = OpenHumansMember.get_auth_url()
        print(auth_url)
        context['auth_url'] = auth_url
        return context