from copy import copy
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Union
from urllib.parse import urlsplit

from bs4 import BeautifulSoup
from bs4.element import Tag
from page_loader.comm import get_page_content
from page_loader.file_operations import (
    generate_file_name,
    generate_file_name_from_page_url,
    generate_file_name_prefix_from_page_url,
    save_assets,
    save_file,
)
from page_loader.logging import get_logger

logger = get_logger("page_loader.core")


@dataclass(frozen=True)
class PageAssets:
    src: List[Tag]
    href: List[Tag]

    def to_dict(self) -> Dict[str, List[Tag]]:
        return {
            "src": self.src,
            "href": self.href,
        }


@dataclass(frozen=True)
class PageAssetsWithUpdatedAssets:
    src: Dict[Tag, Tag]
    href: Dict[Tag, Tag]


def download(page_url: str, output: Path) -> str:
    """
    Downloads and stores page content with assets into provided folder,
    then returns path to saved page

    :param page_url: page url to download
    :type page_url: str
    :param output: folder to save page content
    :type output: Path
    :return: path to saved page
    :rtype: str
    :raises RuntimeError: if output folder doesn't exist
    """
    try:
        page_content = get_page_content(page_url)
    except Exception:
        logger.error(
            f"something went wrong while getting the page {page_url} content, "
            "see exception above"
        )
        raise

    try:
        file_path = process_page_content(page_url, page_content, output)
    except Exception:
        logger.error(
            f"something went wrong while processing page {page_url} content, "
            "see exception above"
        )
        raise

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
    page_assets = get_page_assets(soup, page_url)
    # save assets using base name
    try:
        updated_assets = process_assets(
            assets=page_assets,
            file_name_prefix=file_name_prefix,
            page_url=page_url,
            folder=folder,
        )
    except Exception:
        logger.error(
            f"something went wrong while assets update for page {page_url}, "
            "see exception above"
        )
        raise

    # update page code with new assets
    updated_content = update_page_assets(soup, updated_assets)
    # save page new content
    file_name = generate_file_name_from_page_url(page_url)
    filepath = save_file(updated_content, file_name, folder)

    return str(filepath.resolve())


def get_page_assets(soup: BeautifulSoup, page_url: str) -> PageAssets:
    """
    Extracts assets from the given page

    :param soup: page soup
    :type soup: BeautifulSoup
    :param page_url: page url
    :type page_url: str
    :return: page assets
    :rtype: PageAssets
    """
    images = list(soup.findAll("img"))
    domain = urlsplit(page_url).netloc
    scripts = [
        script
        for script in soup.findAll("script")
        if "src" in script.attrs
        and (
            script.attrs["src"].startswith("/")
            or urlsplit(script.attrs["src"]).netloc == domain
        )
    ]
    links = [
        link
        for link in soup.findAll("link")
        if link.attrs["href"].startswith("/")
        or urlsplit(link.attrs["href"]).netloc == domain
    ]
    return PageAssets(src=images + scripts, href=links)


def process_assets(
    assets: PageAssets,
    page_url: str,
    file_name_prefix: str,
    folder: Union[str, Path],
) -> PageAssetsWithUpdatedAssets:
    """
    Creates the folder for assets storing, downloads and saves asset contents,
    updates asset tags with new reference attribute and returns old assets
    connected to updated assets

    :param assets: page assets
    :type assets: PageAssets
    :param page_url: page url
    :type page_url: str
    :param file_name_prefix: prefix for the file names
    :type file_name_prefix: str
    :param folder: folder to save page contents
    :type folder: Path
    :return: page assets with updated assets
    :rtype: PageAssetsWithUpdatedAssets
    :raises RuntimeError: if output folder doesn't exist
    """
    if not assets.src and not assets.href:
        return PageAssetsWithUpdatedAssets(
            src={},
            href={},
        )
    # create folder
    assets_folder = generate_file_name_from_page_url(page_url).split(".")[0] + "_files"
    assets_folder_path = Path(folder).joinpath(assets_folder)
    assets_folder_path.mkdir(parents=True, exist_ok=True)

    # download assets
    assets_content: Dict[str, Dict[Tag, Union[bytes, str]]] = {
        "src": {},
        "href": {},
    }
    for reference_attribute, assets_of_type in assets.to_dict().items():
        for asset in assets_of_type:
            assets_content[reference_attribute][asset] = get_page_content(
                page_url + asset.attrs[reference_attribute]
                if asset.attrs[reference_attribute].startswith("/")
                else asset.attrs[reference_attribute]
            )

    new_assets_path_content = {}
    updated_assets: Dict[str, Dict[Tag, Tag]] = {
        "src": {},
        "href": {},
    }
    for reference_attribute, assets_of_type in assets.to_dict().items():
        for asset in assets_of_type:
            new_asset_file_name = generate_file_name(
                file_name_prefix,
                asset.attrs[reference_attribute],
                page_url,
            )
            new_asset_path = assets_folder_path.joinpath(new_asset_file_name)
            # assign new path to old content
            new_assets_path_content[new_asset_path] = assets_content[
                reference_attribute
            ][asset]

            # update asset with new attribute
            asset_copy = copy(asset)
            asset_copy.attrs[
                reference_attribute
            ] = f"{assets_folder}/{new_asset_file_name}"
            # connect old asset with new asset
            updated_assets[reference_attribute][asset] = asset_copy
    assets_with_updated_assets = PageAssetsWithUpdatedAssets(
        src=updated_assets["src"], href=updated_assets["href"]
    )
    # save assets
    save_assets(new_assets_path_content)
    # return assets with new names back
    return assets_with_updated_assets


def update_page_assets(soup: BeautifulSoup, assets: PageAssetsWithUpdatedAssets) -> str:
    """
    Replaces old assets with new assets with updated assets

    :param soup: page soup
    :type soup: BeautifulSoup
    :param assets: page assets connected to updated assets
    :type assets: PageAssetsWithUpdatedAssets
    :return: updated page content
    :rtype: str
    """
    soup_copy = copy(soup)
    for original_src_asset, updated_src_asset in assets.src.items():
        original_asset_in_soup = soup_copy.find(
            original_src_asset.name, src=original_src_asset.attrs["src"]
        )
        original_asset_in_soup.replace_with(updated_src_asset)
    for original_link_asset, updated_link_asset in assets.href.items():
        original_asset_in_soup = soup_copy.find(
            original_link_asset.name, href=original_link_asset.attrs["href"]
        )
        original_asset_in_soup.replace_with(updated_link_asset)
    return soup_copy.prettify()
