from copy import copy
from pathlib import Path
from typing import Dict, List, Union

from bs4 import BeautifulSoup
from bs4.element import Tag
from page_loader.comm import get_page_content
from page_loader.file_operations import (
    generate_file_name_from_src,
    generate_file_name_prefix_from_page_url,
    save_assets,
    save_file,
)


def download(page_url: str, output: Path) -> str:
    """
    Downloads and stores page content with assets into provided folder
    then returns path to saved page

    :param page_url: page url to download
    :type page_url: str
    :param output: folder to save page content
    :type output: Path
    :return: path to saved page
    :rtype: str
    :raises RuntimeError: if output folder doesn't exist
    """
    page_content = get_page_content(page_url)

    file_path = process_page_content(page_url, page_content, output)

    return file_path


def process_page_content(page_url: str, content: str, folder: Path) -> str:
    """
    Processes page content and downloads assets into provided folder
    then returns path to saved page

    :param page_url: page url
    :type page_url: str
    :param content: page content
    :type content: str
    :param folder: folder to save page contents
    :type folder: Path
    :return: path to saved page
    :rtype: str
    :raises RuntimeError: if output folder doesn't exist
    """
    soup = BeautifulSoup(content, features="html.parser")
    file_name_prefix = generate_file_name_prefix_from_page_url(page_url)
    # parse and download page assets
    assets = get_page_assets(soup)
    # save assets using base name
    updated_assets = process_assets(
        assets=assets,
        file_name_prefix=file_name_prefix,
        page_url=page_url,
        folder=folder,
    )
    # update page code with new assets
    updated_content = update_page_assets(soup, updated_assets)
    # save page new content
    file_name = f"{file_name_prefix}.html"
    filepath = save_file(updated_content, file_name, folder)

    return str(filepath.resolve())


def get_page_assets(soup: BeautifulSoup) -> List[Tag]:
    """
    Extracts assets from the given page

    :param soup: page soup
    :type soup: BeautifulSoup
    :return: list of assets
    :rtype: List[Tag]
    """
    images = soup.findAll("img")
    return list(images)


def process_assets(
    assets: List[Tag], page_url: str, file_name_prefix: str, folder: Union[str, Path]
) -> Dict[Tag, Tag]:
    """
    Creates the folder for assets storing, downloads and saves asset contents,
    updates asset tags with new src and returns mapping with old assets
    connected to updated assets

    :param assets: list of asset tags
    :type assets: List[Tag]
    :param page_url: page url
    :type page_url: str
    :param file_name_prefix: prefix for the file names
    :type file_name_prefix: str
    :param folder: folder to save page contents
    :type folder: Path
    :return: mapping with old assets connected to updated assets
    :rtype: Dict[Tag, Tag]
    :raises RuntimeError: if output folder doesn't exist
    """
    if not assets:
        return {}
    # create folder
    assets_folder = file_name_prefix + "_files"
    assets_folder_path = Path(folder).joinpath(assets_folder)
    assets_folder_path.mkdir(parents=True, exist_ok=True)

    # download assets
    assets_content = {
        asset: get_page_content(page_url + asset.attrs["src"]) for asset in assets
    }

    new_assets_path_content = {}
    updated_assets = {}
    for asset in assets:
        new_asset_file_name = generate_file_name_from_src(
            file_name_prefix, asset.attrs["src"]
        )
        new_asset_path = assets_folder_path.joinpath(new_asset_file_name)
        # assign new path to old content
        new_assets_path_content[new_asset_path] = assets_content[asset]

        # update asset with new src
        asset_copy = copy(asset)
        asset_copy.attrs["src"] = f"{assets_folder}/{new_asset_file_name}"
        # connect old asset with new asset
        updated_assets[asset] = asset_copy
    # save assets
    save_assets(new_assets_path_content)
    # return assets with new names back
    return updated_assets


def update_page_assets(soup: BeautifulSoup, assets: Dict[Tag, Tag]) -> str:
    """
    Replaces old assets with new assets with updated src attribute

    :param soup: page soup
    :type soup: BeautifulSoup
    :param assets: mapping with old assets connected to updated assets
    :type assets: Dict[Tag, Tag]
    :return: updated page content
    :rtype: str
    """
    soup_copy = copy(soup)
    for original_asset, updated_asset in assets.items():
        original_asset_in_soup = soup_copy.find(
            original_asset.name, src=original_asset.attrs["src"]
        )
        original_asset_in_soup.replace_with(updated_asset)
    return soup_copy.prettify()
