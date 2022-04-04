import re
from pathlib import Path
from typing import Mapping, Union
from urllib.parse import urlsplit

from loguru import logger


def generate_file_name_from_page_url(page_url: str) -> str:
    """
    Generates file name for the main page file using page url

    :param page_url: page url
    :type page_url: str
    :return: prefix for the page file names
    (e.g. ru-hexlet-io-courses.html for https://ru.hexlet.io/courses)
    :rtype: str
    """
    parsed_url = urlsplit(page_url)
    path = parsed_url.path
    # exclude file extension
    if "." in path:
        path = parsed_url.path.split(".")[0]
    url_without_schema = f"{parsed_url.netloc}{path}"
    url_with_digits_replaced = re.sub(r"\W", "-", url_without_schema) + ".html"
    return url_with_digits_replaced


def generate_file_name_prefix_from_page_url(page_url: str) -> str:
    """
    Generates prefix for the page file names using page url

    :param page_url: page url
    :type page_url: str
    :return: prefix for the page file names
    (e.g. ru-hexlet-io for https://ru.hexlet.io/courses)
    :rtype: str
    """
    parsed_url = urlsplit(page_url)
    domain = parsed_url.netloc
    domain_with_digits_replaced = re.sub(r"\W", "-", domain)
    return domain_with_digits_replaced


def generate_file_name(file_name_prefix: str, attribute: str, page_url: str) -> str:
    """
    Generates file name from asset tag attribute with file_name_prefix

    :param file_name_prefix: prefix for page file names
    :type file_name_prefix: str
    :param attribute: asset tag src attribute
    :type attribute: str
    :return: file name
    :rtype: str
    """
    # actual links
    if attribute.startswith("http"):
        parsed_url = urlsplit(attribute)
        path, extension = parsed_url.path.split(".")
        return re.sub(r"\W", "-", parsed_url.netloc + path) + f".{extension}"
    elif "." not in attribute:
        parsed_url = urlsplit(page_url)
        return re.sub(r"\W", "-", parsed_url.netloc + attribute) + ".html"
    path, extension = attribute.split(".")
    path_with_digits_replaced = re.sub(r"\W", "-", path)
    final_path = file_name_prefix + path_with_digits_replaced + "." + extension
    return final_path


def save_file(content: Union[str, bytes], file_name: str, folder: Path) -> Path:
    """
    Saves content into provided folder under provided file name

    :param content: file content
    :type content: Union[str, bytes]
    :param file_name: file name
    :type file_name: str
    :param folder: folder to save file into, should exist and be writeable
    :type folder:
    :return: stored file path
    :rtype: Path
    :raises RuntimeError: if output folder doesn't exist
    """
    if not folder.is_dir():
        error_message = "folder for content saving doesn't exist!"
        logger.exception(error_message)
        raise RuntimeError(error_message)

    filepath = folder.joinpath(file_name)
    if isinstance(content, str):
        mode = "w"
    else:
        mode = "wb"
    with filepath.open(mode) as file:
        file.write(content)

    return filepath


def save_assets(assets_path_with_content: Mapping[Path, Union[bytes, str]]) -> None:
    """
    Saves assets according to their path

    :param assets_path_with_content: assets path with content
    :type assets_path_with_content: Mapping[Path, Union[bytes, str]]
    :raises RuntimeError: if asset path folder doesn't exist
    """
    for asset_path, content in assets_path_with_content.items():
        asset_folder, asset_file_name = asset_path.parent.resolve(), asset_path.name
        save_file(content, asset_file_name, asset_folder)
