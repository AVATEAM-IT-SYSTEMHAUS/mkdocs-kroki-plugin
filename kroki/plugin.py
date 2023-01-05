import hashlib
import re
import tempfile

from functools import partial
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import File
from mkdocs import config
from mkdocs.plugins import log
from pathlib import Path
from os.path import relpath
import os

from .config import KrokiDiagramTypes
from .client import KrokiClient


info = partial(log.info, f'{__name__} %s')
debug = partial(log.debug, f'{__name__} %s')
error = partial(log.error, f'{__name__} %s')


class KrokiPlugin(BasePlugin):
    config_scheme = (
        ('ServerURL', config.config_options.Type(str, default=os.getenv('KROKI_SERVER_URL', 'https://kroki.io'))),
        ('EnableBlockDiag', config.config_options.Type(bool, default=True)),
        ('Enablebpmn', config.config_options.Type(bool, default=True)),
        ('EnableExcalidraw', config.config_options.Type(bool, default=True)),
        ('EnableMermaid', config.config_options.Type(bool, default=True)),
        ('EnableDiagramsnet', config.config_options.Type(bool, default=False)),
        ('HttpMethod', config.config_options.Type(str, default='GET')),
        ('DownloadImages', config.config_options.Type(bool, default=False)),
        ('EmbedImages', config.config_options.Type(bool, default=False)),
        ('DownloadDir', config.config_options.Type(str, default='images/kroki_generated')),
        ('FencePrefix', config.config_options.Type(str, default='kroki-')),
        ('FileTypes', config.config_options.Type(list, default=['svg'])),
        ('FileTypeOverrides', config.config_options.Type(dict, default={})),
    )

    fence_prefix = None
    diagram_types = None
    kroki_client = None

    def on_config(self, config, **_kwargs):
        info(f'Configuring: {self.config}')

        self.diagram_types = KrokiDiagramTypes(self.config['EnableBlockDiag'],
                                               self.config['Enablebpmn'],
                                               self.config['EnableExcalidraw'],
                                               self.config['EnableMermaid'],
                                               self.config['EnableDiagramsnet'],
                                               self.config['FileTypes'],
                                               self.config['FileTypeOverrides'])

        self.fence_prefix = self.config['FencePrefix']

        if self.config['HttpMethod'] == 'POST' and not self.config["DownloadImages"]:
            error('HttpMethod: Can\'t use POST without downloading the images! '
                  'Falling back to GET')
            self.config['HttpMethod'] = 'GET'

        self.kroki_client = KrokiClient(self.config['ServerURL'],
                                        self.config['HttpMethod'],
                                        self.diagram_types)

        self._tmp_dir = tempfile.TemporaryDirectory(prefix="mkdocs_kroki_")
        self._output_dir = Path(config.get("site_dir", "site"))

        self._prepare_download_dir()

        return config

    def _download_dir(self):
        return Path(self._tmp_dir.name) / Path(self.config["DownloadDir"])

    def _prepare_download_dir(self):
        self._download_dir().mkdir(parents=True, exist_ok=True)

    def _kroki_filename(self, kroki_data, kroki_type, page):
        digest = hashlib.md5(kroki_data.encode("utf8")).hexdigest()
        prefix = page.file.name.split(".")[0]
        file_type = self.diagram_types.get_file_ext(kroki_type)

        return f'{prefix}-{digest}.{file_type}'

    def _save_kroki_image_and_get_url(self, file_name, image_data, files):
        filepath = self._download_dir() / file_name
        with open(filepath, 'wb') as file:
            file.write(image_data)
        get_url = relpath(filepath, self._tmp_dir.name)

        mkdocs_file = File(get_url, self._tmp_dir.name, self._output_dir, False)
        files.append(mkdocs_file)

        return f'/{get_url}'

    def _replace_kroki_block(self, match_obj, files, page):
        kroki_type = match_obj.group(1).lower()
        kroki_options = match_obj.group(2)
        kroki_data = match_obj.group(3)

        kroki_diagram_options = dict(x.split('=') for x in kroki_options.strip().split(' ')) if kroki_options else {}
        get_url = None
        if self.config["DownloadImages"]:
            image_data = self.kroki_client.get_image_data(kroki_type, kroki_data, kroki_diagram_options)

            if image_data:
                file_name = self._kroki_filename(kroki_data, kroki_type, page)
                get_url = self._save_kroki_image_and_get_url(file_name, image_data, files)
        else:
            get_url = self.kroki_client.get_url(kroki_type, kroki_data, kroki_diagram_options)

        if get_url is not None:
            return f'![Kroki]({get_url})'

        return f'!!! error "Could not render!"\n\n```\n{kroki_data}\n```'

    def on_page_markdown(self, markdown, files, page, **_kwargs):
        debug(f'on_page_markdown [page: {page}]')

        kroki_regex = self.diagram_types.get_block_regex(self.fence_prefix)
        pattern = re.compile(kroki_regex, flags=re.IGNORECASE + re.DOTALL)

        def replace_kroki_block(match_obj):
            return self._replace_kroki_block(match_obj, files, page)

        return re.sub(pattern, replace_kroki_block, markdown)

    def on_post_build(self, **_kwargs):
        if hasattr(self, "_tmp_dir"):
            info(f'Cleaning {self._tmp_dir}')
            self._tmp_dir.cleanup()
