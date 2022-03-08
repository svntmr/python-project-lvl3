import re
from pathlib import Path
from typing import Union
from urllib.parse import urlsplit


def store_page_content(page_url: str, content: str, folder: Union[str, Path]) -> str:
    file_name = generate_file_name_from_page_url(page_url)

    filepath = save_file(content, file_name, folder)

    return str(filepath.resolve())


def generate_file_name_from_page_url(page_url: str) -> str:
    parsed_url = urlsplit(page_url)
    path = parsed_url.path
    # exclude file extension
    if "." in path:
        path = parsed_url.path.split(".")[0]
    url_without_schema = f"{parsed_url.netloc}{path}"
    url_with_digits_replaced = re.sub(r"\W", "-", url_without_schema)
    return f"{url_with_digits_replaced}.html"


def save_file(content: str, file_name: str, folder: Union[str, Path]) -> Path:
    folder = Path(folder)
    if not folder.is_dir():
        raise RuntimeError("folder for content saving doesn't exist!")

    filepath = folder.joinpath(file_name)
    with filepath.open("w") as file:
        file.write(content)

    return filepath
