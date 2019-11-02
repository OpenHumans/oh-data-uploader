from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views.generic import FormView, TemplateView

from openhumans.models import OpenHumansMember

from .utils import get_datatypes, get_datatypes_by_id, get_datatype_id_from_url

OH_BASE_URL = settings.OPENHUMANS_OH_BASE_URL
OH_API_BASE = OH_BASE_URL + '/api/direct-sharing'
OH_DIRECT_UPLOAD = OH_API_BASE + '/project/files/upload/direct/'
OH_DIRECT_UPLOAD_COMPLETE_URL = OH_API_BASE + '/project/files/upload/complete/'


class Index(TemplateView):

    template_name = "main/index.html"

    def get(self, request, *args, **kwargs):
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
        context.update({
            'auth_url': auth_url,
        })
        return context


class Dashboard(TemplateView):

    template_name = "main/dashboard.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        datafiles = self.request.user.openhumansmember.list_files()
        datatypes_by_id = get_datatypes_by_id()
        for df in datafiles:
            dt_ids = []
            for url in df['datatypes']:
                dt_ids.append(get_datatype_id_from_url(url))
            df['datatypes'] = [datatypes_by_id[dt_id] for dt_id in dt_ids]
        context.update({
            'datafiles': datafiles,
        })
        return context


class UploadFileView(TemplateView):

    template_name = "main/upload.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update({
            'datatypes': get_datatypes(),
            'oh_direct_upload_url': OH_DIRECT_UPLOAD,
            'oh_direct_upload_complete_url': OH_DIRECT_UPLOAD_COMPLETE_URL,
        })
        return context