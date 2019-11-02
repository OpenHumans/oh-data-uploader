import re
import urllib

from django.conf import settings

import requests


def get_datatypes():
    url = "{}/api/public/datatypes/".format(settings.OPENHUMANS_OH_BASE_URL)
    response_json = requests.get(url).json()
    datatypes = response_json['results']
    while response_json['next']:
        response_json = requests.get(response_json['next']).json()
        datatypes.append(response_json['results'])
    return datatypes


def get_datatypes_by_id(datatypes=None):
    if not datatypes:
        datatypes = get_datatypes()
    return { int(dt['id']):dt for dt in datatypes }


def get_datatype_id_from_url(url):
    url_parsed = urllib.parse.urlparse(url)
    dtid = re.match('/api/public/datatype/(?P<dtid>.*)/', url_parsed.path).group('dtid')
    return int(dtid)