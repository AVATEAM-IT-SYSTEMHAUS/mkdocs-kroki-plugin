import base64
import requests
import zlib

from .util import info, debug, error


class KrokiClient():
    def __init__(self, server_url, http_method):
        self.server_url = server_url
        self.http_method = http_method

        if http_method not in ['GET', 'POST']:
            error(f'HttpMethod config error: {http_method} -> using GET!')
            self.http_method = 'GET'

        info(f'Initialized: {self.http_method}, {self.server_url}')

    def _kroki_uri(self, kroki_type):
        return f'{self.server_url}/{kroki_type}/svg'

    def _get_url(self, kroki_type, kroki_diagram_data):
        kroki_data_param = \
            base64.urlsafe_b64encode(
                zlib.compress(str.encode(kroki_diagram_data), 9)).decode()

        if len(kroki_data_param) >= 4096:
            debug(f'Length of encoded diagram is {len(kroki_data_param)}. '
                  'Kroki may not be able to read the data completely!')

        kroki_uri = self._kroki_uri(kroki_type)
        return f'{kroki_uri}/{kroki_data_param}'

    def get_url(self, kroki_type, kroki_diagram_data):
        debug(f'get_url: {kroki_type}')

        if self.http_method != 'GET':
            error(f'HTTP method is {self.http_method}!')
            return None

        return self._get_url(kroki_type, kroki_diagram_data)

    def get_image_data(self, kroki_type, kroki_diagram_data):
        if self.http_method == 'GET':
            url = self._get_url(kroki_type, kroki_diagram_data)

            debug(f'get_image_data [GET {url[:50]}..]')
            r = requests.get(url)
        else:  # POST
            url = self._kroki_uri(kroki_type)

            debug(f'get_image_data [POST {url}]')
            r = requests.post(url, json={
                "diagram_source": kroki_diagram_data
            })

        debug(f'get_image_data [Response: {r}]')

        if r.status_code != requests.codes.ok:
            error(f'Could not retrive image data, got: {r}')
            return None

        return r.text
