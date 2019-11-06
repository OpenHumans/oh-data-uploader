from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import FormView, TemplateView

import ohapi
from openhumans.models import OpenHumansMember

from .utils import (
    get_datafiles_with_datatypes, get_datatypes,
    get_datatypes_by_id, get_datatype_id_from_url,
    sort_datatypes)

OH_BASE_URL = settings.OPENHUMANS_OH_BASE_URL
OH_DATATYPES_MANAGEMENT = OH_BASE_URL + '/data-management/datatypes/'
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


class Dashboard(LoginRequiredMixin, TemplateView):

    template_name = "main/dashboard.html"

    def dispatch(self, request, *args, **kwargs):
        try:
            self.datafiles = get_datafiles_with_datatypes(self.request.user)
        except Exception as exception:
            print(exception)
            if self.request.user.is_authenticated:
                logout(self.request)
                return redirect('index')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update({
            'datatypes': sort_datatypes(get_datatypes(uploadable=True)),
            'datafiles': self.datafiles,
            'open_humans_datatype_list': OH_DATATYPES_MANAGEMENT,
        })
        return context


class UploadFileView(LoginRequiredMixin, TemplateView):

    template_name = "main/upload.html"

    def get(self, request, *args, **kwargs):
        self.datatype = get_datatypes_by_id()[int(request.GET['datatype_id'])]
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update({
            'datatype': self.datatype,
            'oh_direct_upload_url': OH_DIRECT_UPLOAD,
            'oh_direct_upload_complete_url': OH_DIRECT_UPLOAD_COMPLETE_URL,
        })
        return context


class DeleteFileView(LoginRequiredMixin, TemplateView):
    template_name = "main/delete.html"

    def dispatch(self, request, *args, **kwargs):
        self.datafile_id = kwargs['datafile_id']
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        ohapi.api.delete_file(
            access_token=request.user.openhumansmember.get_access_token(),
            project_member_id=request.user.openhumansmember.oh_id,
            base_url=OH_BASE_URL,
            file_id=self.datafile_id,
        )
        return redirect('dashboard')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        datafiles = get_datafiles_with_datatypes(self.request.user)
        datafile = [df for df in datafiles if int(df['id']) == int(self.datafile_id)][0]
        context.update({
            'datafile': datafile,
        })
        return context