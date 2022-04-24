import hashlib
import re
import tempfile

from bs4 import BeautifulSoup
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import File
from mkdocs import config
from os.path import relpath
from pathlib import Path

from .client import KrokiClient
from .config import KrokiDiagramTypes
from .util import info, debug, clean_svg


class KrokiPlugin(BasePlugin):
    config_scheme = (
        ('ServerURL', config.config_options.Type(str, default='https://kroki.io')),
        ('EnableBlockDiag', config.config_options.Type(bool, default=True)),
        ('Enablebpmn', config.config_options.Type(bool, default=True)),
        ('EnableExcalidraw', config.config_options.Type(bool, default=True)),
        ('EnableMermaid', config.config_options.Type(bool, default=True)),
        ('HttpMethod', config.config_options.Type(str, default='GET')),
        ('InlineImages', config.config_options.Type(bool, default=False)),
        ('DownloadImages', config.config_options.Type(bool, default=False)),
        ('EmbedImages', config.config_options.Type(bool, default=False)),
        ('DownloadDir', config.config_options.Type(str, default='images/kroki_generated')),
        ('FencePrefix', config.config_options.Type(str, default='kroki-')),
    )

    fence_prefix = None
    diagram_types = None
    kroki_client = None

    def on_config(self, config, **_kwargs):
        info(f'Configuring: {self.config}')

        self.diagram_types = KrokiDiagramTypes(self.config['EnableBlockDiag'],
                                               self.config['Enablebpmn'],
                                               self.config['EnableExcalidraw'],
                                               self.config['EnableMermaid'])

        self.fence_prefix = self.config['FencePrefix']

        if self.config['HttpMethod'] == 'POST' and not self.config["DownloadImages"]:
            error('HttpMethod: Can\'t use POST without downloading the images! '
                  'Falling back to GET')
            self.config['HttpMethod'] = 'GET'

        self.kroki_client = KrokiClient(self.config['ServerURL'], self.config['HttpMethod'])

        self._tmp_dir = tempfile.TemporaryDirectory(prefix="mkdocs_kroki_")
        self._output_dir = Path(config.get("site_dir", "site"))

        self._prepare_download_dir()

        return config

    def _download_dir(self):
        return Path(self._tmp_dir.name) / Path(self.config["DownloadDir"])

    def _prepare_download_dir(self):
        self._download_dir().mkdir(parents=True, exist_ok=True)

    def _kroki_filename(self, kroki_data, page):
        digest = hashlib.md5(kroki_data.encode("utf8")).hexdigest()
        prefix = page.file.name.split(".")[0]

        return f'{prefix}-{digest}.svg'

    def _save_kroki_image_and_get_url(self, file_name, image_data, files):
        filepath = self._download_dir() / file_name
        with open(filepath, 'w') as file:
            file.write(image_data)

        get_url = relpath(filepath, self._tmp_dir.name)

        mkdocs_file = File(get_url, self._tmp_dir.name, self._output_dir, False)
        files.append(mkdocs_file)

        return f'/{get_url}'

    def _replace_kroki_block(self, match_obj, files, page):
        kroki_type = match_obj.group(1).lower()
        kroki_data = match_obj.group(2)

        get_url = None
        if self.config["DownloadImages"]:
            image_data = self.kroki_client.get_image_data(kroki_type, kroki_data)

            if image_data:
                file_name = self._kroki_filename(kroki_data, page)
                get_url = self._save_kroki_image_and_get_url(file_name, image_data, files)
        else:
            get_url = self.kroki_client.get_url(kroki_type, kroki_data)

        if get_url is not None:
            return f'![Kroki]({get_url})'

        return f'!!! error "Could not render!"\n\n```\n{kroki_data}\n```'

    def on_page_markdown(self, markdown, files, page, **_kwargs):
        if self.config['InlineImages']:
            return markdown

        debug(f'on_page_markdown [page: {page}]')

        kroki_regex = self.diagram_types.get_block_regex(self.fence_prefix)
        pattern = re.compile(kroki_regex, flags=re.IGNORECASE + re.DOTALL)

        def replace_kroki_block(match_obj):
            return self._replace_kroki_block(match_obj, files, page)

        return re.sub(pattern, replace_kroki_block, markdown)

    def on_page_content(self, html, page, config, files, **_kwargs):
        if not self.config['InlineImages']:
            return html

        soup = BeautifulSoup(html, 'html.parser')

        for diagram_type in self.diagram_types:
            diagram_fence = f'{self.fence_prefix}{diagram_type}'

            debug(f'looking for {diagram_fence} in {page.title}')
            pre_code_tags = (soup.select(f'pre code.{diagram_fence}')
                             or soup.select(f'pre code.language-{diagram_fence}'))

            for pre_code_tag in pre_code_tags:
                debug(f'inlining {pre_code_tag.name} in {page}')
                kroki_data = pre_code_tag.text

                image_data = self.kroki_client.get_image_data(diagram_type,
                                                              kroki_data)
                if image_data:
                    svg_tag = clean_svg(image_data)

                    container_tag = soup.new_tag('div', attrs={
                        'class': f'kroki {diagram_type}'
                        })
                    container_tag.append(svg_tag)

                    pre_code_tag.parent.replaceWith(container_tag)
        return str(soup)

    def on_post_build(self, **_kwargs):
        if hasattr(self, "_tmp_dir"):
            info(f'Cleaning {self._tmp_dir}')
            self._tmp_dir.cleanup()
