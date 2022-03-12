from page_loader.comm import get_page_content
from page_loader.file_operations import store_page_content


def download(page_url: str, output: str) -> str:
    page_content = get_page_content(page_url)

    file_path = store_page_content(page_url, page_content, output)

    return file_path
