import base64
import requests
import zlib

from functools import partial
from mkdocs.plugins import log

from .config import KrokiDiagramTypes


info = partial(log.info, f'{__name__} %s')
debug = partial(log.debug, f'{__name__} %s')
error = partial(log.error, f'{__name__} %s')


class KrokiClient():
    def __init__(self, server_url, http_method, diagram_types: KrokiDiagramTypes):
        self.server_url = server_url
        self.http_method = http_method
        self.diagram_types = diagram_types

        if http_method not in ['GET', 'POST']:
            error(f'HttpMethod config error: {http_method} -> using GET!')
            self.http_method = 'GET'

        info(f'Initialized: {self.http_method}, {self.server_url}')

    def _kroki_uri(self, kroki_type):
        file_type = self.diagram_types.get_file_ext(kroki_type)
        return f'{self.server_url}/{kroki_type}/{file_type}'

    def _get_url(self, kroki_type, kroki_diagram_data, kroki_diagram_options={}):
        kroki_data_param = \
            base64.urlsafe_b64encode(
                zlib.compress(str.encode(kroki_diagram_data), 9)).decode()

        kroki_query_param = \
            "&".join([f'{k}={v}' for k, v in kroki_diagram_options.items()]) if len(kroki_diagram_options) > 0 else ''
        if len(kroki_data_param) >= 4096:
            debug(f'Length of encoded diagram is {len(kroki_data_param)}. '
                  'Kroki may not be able to read the data completely!')

        kroki_uri = self._kroki_uri(kroki_type)
        debug(f'{kroki_uri}/{kroki_data_param}?{kroki_query_param}')
        return f'{kroki_uri}/{kroki_data_param}?{kroki_query_param}'

    def get_url(self, kroki_type, kroki_diagram_data, kroki_diagram_options={}):
        debug(f'get_url: {kroki_type}')

        if self.http_method != 'GET':
            error(f'HTTP method is {self.http_method}. Config error!')
            return None

        return self._get_url(kroki_type, kroki_diagram_data, kroki_diagram_options)

    def get_image_data(self, kroki_type, kroki_diagram_data, kroki_diagram_options={}):
        try:
            if self.http_method == 'GET':
                url = self._get_url(kroki_type, kroki_diagram_data, kroki_diagram_options)

                debug(f'get_image_data [GET {url[:50]}..]')
                r = requests.get(url)
            else:  # POST
                url = self._kroki_uri(kroki_type)

                debug(f'get_image_data [POST {url}]')

                r = requests.post(url, json={
                    "diagram_source": kroki_diagram_data,
                    "diagram_options": kroki_diagram_options
                })

            debug(f'get_image_data [Response: {r}]')
            if r.status_code == requests.codes.ok:
                return r.content
            else:
                error(f'Could not retrive image data, got: {r}')

        except Exception as e:
            error(e)
