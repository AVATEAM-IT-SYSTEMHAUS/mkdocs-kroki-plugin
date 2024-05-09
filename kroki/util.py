from os import makedirs, path
from uuid import NAMESPACE_OID, uuid3

from mkdocs.plugins import get_plugin_logger
from mkdocs.structure.files import File as MkDocsFile
from mkdocs.structure.files import Files as MkDocsFiles
from mkdocs.structure.pages import Page as MkDocsPage

log = get_plugin_logger(__name__)


class DownloadedImage:
    def __init__(self, file_content: bytes, file_extension: str, additional_metadata: dict) -> None:
        file_uuid = uuid3(NAMESPACE_OID, f"{additional_metadata}{file_content}")

        self.file_name = f"kroki-generated-{file_uuid}.{file_extension}"
        self.file_content = file_content

    def save(self, files: MkDocsFiles, page: MkDocsPage) -> None:
        # wherever MkDocs wants to host or build, we plant the image next
        # to the generated static page
        page_abs_dest_dir = path.dirname(page.file.abs_dest_path)
        makedirs(page_abs_dest_dir, exist_ok=True)

        file_path = path.join(page_abs_dest_dir, self.file_name)

        with open(file_path, "wb") as file:
            file.write(self.file_content)

        # make MkDocs believe that the file was present from the beginning
        file_src_uri = path.join(path.dirname(page.file.src_uri), self.file_name)
        file_dest_uri = path.join(path.dirname(page.file.dest_uri), self.file_name)

        dummy_file = MkDocsFile(
            path=file_src_uri,
            src_dir="",
            dest_dir="",
            use_directory_urls=False,
            dest_uri=file_dest_uri,
        )
        # MkDocs will not copy the file in this case
        dummy_file.abs_src_path = dummy_file.abs_dest_path = file_path

        files.append(dummy_file)
