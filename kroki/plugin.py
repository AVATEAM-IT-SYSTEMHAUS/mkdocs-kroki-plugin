import base64
import hashlib
import zlib
import re
import tempfile
import pathlib
import urllib.request
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import File
from mkdocs import config


class KrokiPlugin(BasePlugin):
    config_scheme = (
        ('ServerURL', config.config_options.Type(
            str, default='https://kroki.io')),
        ('EnableBlockDiag', config.config_options.Type(
            bool, default=True)),
        ('Enablebpmn', config.config_options.Type(
            bool, default=True)),
        ('EnableExcalidraw', config.config_options.Type(
            bool, default=True)),
        ('EnableMermaid', config.config_options.Type(
            bool, default=True)),
        ('DownloadImages', config.config_options.Type(
            bool, default=False)),
        ('DownloadDir', config.config_options.Type(
            str, default='images/kroki_generated')),
    )

    kroki_re = ""

    kroki_base = (
        "bytefield",
        "ditaa",
        "erd",
        "graphviz",
        "nomnoml",
        "plantuml",
        "c4plantuml",
        "svgbob",
        "vega",
        "vegalite",
        "wavedrom",
        "pikchr",
    )

    kroki_blockdiag = (
        "blockdiag",
        "seqdiag",
        "actdiag",
        "nwdiag",
        "packetdiag",
        "rackdiag",
    )

    kroki_bpmn = (
        "bpmn",
    )

    kroki_excalidraw = (
        "excalidraw",
    )

    kroki_mermaid = (
        "mermaid",
    )

    def on_config(self, config, **kwargs):
        self.kroki_re += "|".join(self.kroki_base)
        if self.config['EnableBlockDiag']:
            self.kroki_re += "|" + "|".join(self.kroki_blockdiag)
        if self.config['Enablebpmn']:
            self.kroki_re += "|" + "|".join(self.kroki_bpmn)
        if self.config['EnableExcalidraw']:
            self.kroki_re += "|" + "|".join(self.kroki_excalidraw)
        if self.config['EnableMermaid']:
            self.kroki_re += "|" + "|".join(self.kroki_mermaid)
        self.kroki_re = r'(?:```kroki-)(' + self.kroki_re + ')\n(.*?)(?:```)'

        self._dir = tempfile.TemporaryDirectory(prefix="mkdocs_kroki_")
        self._output_dir = pathlib.Path(config.get("site_dir", "site"))

        return config

    def _krokiurl(self, matchobj):
        kroki_type = matchobj.group(1).lower()
        kroki_path = base64.urlsafe_b64encode(
            zlib.compress(str.encode(matchobj.group(2)), 9)
        ).decode()
        kroki_url = self.config["ServerURL"] + "/" + kroki_type + "/svg/" + kroki_path

        return kroki_url

    def _kroki_link(self, matchobj):
        return "![Kroki](" + self._krokiurl(matchobj) + ")"

    def _download_image(self, matchobj, target, page, files):
        url = self._krokiurl(matchobj)
        hash = hashlib.md5(url.encode("utf8")).hexdigest()
        prefix = page.file.name.split(".")[0]
        dest_path = pathlib.Path(self.config["DownloadDir"])

        (target / dest_path).mkdir(parents=True, exist_ok=True)

        filename = dest_path / f"{ prefix }-{ hash }.svg"
        urllib.request.urlretrieve(url, target / filename)

        file = File(
            filename, target, self._output_dir, False)
        files.append(file)

        pref = "/".join([".." for _ in pathlib.Path(page.file.src_path).parents][1:])

        return f"![Kroki](./{ pref }/{ filename })"

    def on_page_markdown(self, markdown, files, page, **kwargs):
        pattern = re.compile(self.kroki_re, flags=re.IGNORECASE + re.DOTALL)

        if not self.config["DownloadImages"]:
            return re.sub(pattern, self._kroki_link, markdown)

        target_dir = pathlib.Path(self._dir.name)

        def do_download(matchobj):
            return self._download_image(
                matchobj, target_dir, page, files)

        return re.sub(pattern, do_download, markdown)

    def on_post_build(self, **kwargs):
        if hasattr(self, "_dir"):
            self._dir.cleanup()
