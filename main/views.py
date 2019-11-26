from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import FormView, TemplateView, View

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


class RedirectPageMixin(object):
    """hack to store page and use to redirect once logged in"""
    curr_page = None

    def get_curr_page(self):
        return self.curr_page

    def dispatch(self, request, *args, **kwargs):
        curr_page = self.get_curr_page()
        if request.user.is_anonymous:
            if curr_page:
                request.session['latest_anon'] = curr_page
        else:
            if curr_page:
                request.session['latest_auth'] = curr_page
            if 'latest_anon' in request.session:
                latest_anon = request.session.pop('latest_anon')
                return redirect(latest_anon)
        return super().dispatch(request, *args, **kwargs)


class Index(RedirectPageMixin, TemplateView):
    curr_page = 'index'
    template_name = "main/index.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        auth_url = OpenHumansMember.get_auth_url()
        context.update({
            'auth_url': auth_url,
        })
        return context


class LogoutView(View):

    def post(self, request, *args, **kwargs):
        """Log out"""
        if request.user.is_authenticated:
            latest_auth = request.session.get('latest_auth', None)
            logout(request)
            if latest_auth:
                return redirect(latest_auth)
            return redirect('index')


class Dashboard(LoginRequiredMixin, TemplateView):

    template_name = "main/dashboard.html"

    def dispatch(self, request, *args, **kwargs):
        try:
            self.datafiles = get_datafiles_with_datatypes(self.request.user)
        except Exception as exception:
            # print(exception)
            # Can arise due to bad token from revoked auth, log out to fix.
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


class UploadFileView(RedirectPageMixin, TemplateView):

    template_name = "main/upload.html"

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.datatype = get_datatypes_by_id()[int(request.GET['datatype_id'])]
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update({
            'auth_url': OpenHumansMember.get_auth_url(),
            'datatype': self.datatype,
            'oh_direct_upload_url': OH_DIRECT_UPLOAD,
            'oh_direct_upload_complete_url': OH_DIRECT_UPLOAD_COMPLETE_URL,
        })
        return context

    def get_curr_page(self):
        curr = '/upload?datatype_id={}'.format(self.request.GET['datatype_id'])
        return(curr)


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