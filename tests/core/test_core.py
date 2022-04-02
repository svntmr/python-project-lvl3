from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from bs4 import BeautifulSoup
from page_loader import download
from page_loader.core import (
    get_page_assets,
    process_assets,
    process_page_content,
    update_page_assets,
)
from page_loader.file_operations import generate_file_name_prefix_from_page_url
from tests.paths import file_operations_tests_resources_path


def test_download():
    with TemporaryDirectory() as folder:
        page_url = "https://ru.hexlet.io/courses.html"
        folder_path = Path(folder)

        content = file_operations_tests_resources_path(
            "page_content_with_assets.html"
        ).read_text()
        asset_content = file_operations_tests_resources_path(
            "assets/professions/nodejs.png"
        ).read_bytes()

        patch(
            "page_loader.core.get_page_content", side_effect=[content, asset_content]
        ).start()

        file_path = download(page_url, folder_path)

        expected_file_path = folder_path.joinpath("ru-hexlet-io-courses.html").resolve()
        expected_file_content = file_operations_tests_resources_path(
            "updated_page_content_with_assets.html"
        ).read_text()

        assert file_path == str(expected_file_path)
        assert Path(file_path).read_text() == expected_file_content

        patch.stopall()


def test_process_page_content_without_assets():
    page_url = "https://ru.hexlet.io/courses.html"
    content = "<h1>\n foo, bar!\n</h1>"

    expected_file_name = "ru-hexlet-io-courses.html"

    with TemporaryDirectory() as folder:
        folder_path = Path(folder)

        filepath = process_page_content(page_url, content, folder_path)

        expected_file_path = str(folder_path.joinpath(expected_file_name).resolve())

        assert (
            filepath == expected_file_path
        ), "it should return path to the file in folder"
        assert (
            Path(filepath).read_text() == content
        ), "it should write the given content"


def test_process_page_content_page_with_assets():
    page_url = "https://ru.hexlet.io/courses.html"
    # page content with assets
    content = file_operations_tests_resources_path(
        "page_content_with_assets.html"
    ).read_text()
    asset_content = file_operations_tests_resources_path(
        "assets/professions/nodejs.png"
    ).read_bytes()

    # page content with updated assets
    expected_updated_content = file_operations_tests_resources_path(
        "updated_page_content_with_assets.html"
    ).read_text()

    expected_file_name = "ru-hexlet-io-courses.html"
    expected_assets_folder_name = "ru-hexlet-io-courses_files"
    expected_asset_file_name = "ru-hexlet-io-courses-assets-professions-nodejs.png"

    with TemporaryDirectory() as folder:
        folder_path = Path(folder)
        patch("page_loader.core.get_page_content", return_value=asset_content).start()

        filepath = process_page_content(page_url, content, folder_path)

        expected_file_path = str(folder_path.joinpath(expected_file_name).resolve())
        expected_asset_folder_path = folder_path.joinpath(expected_assets_folder_name)
        expected_asset_file_path = expected_asset_folder_path.joinpath(
            expected_asset_file_name
        )

        assert (
            filepath == expected_file_path
        ), "it should return path to the file in folder"
        assert expected_asset_folder_path.exists(), "it should create assets folder"
        assert (
            expected_asset_file_path.read_bytes() == asset_content
        ), "it should save asset into assets folder"
        assert (
            Path(filepath).read_text() == expected_updated_content
        ), "it should update page content with new assets location"

    patch.stopall()


def test_get_page_assets_page_without_assets():
    content = "<h1>\n foo, bar!\n</h1>"
    soup = BeautifulSoup(content, features="html.parser")

    assets = get_page_assets(soup)

    expected_assets = []

    assert (
        assets == expected_assets
    ), "it should return empty list as page has no assets"


def test_get_page_assets_page_with_assets():
    content = file_operations_tests_resources_path(
        "page_content_with_assets.html"
    ).read_text()
    soup = BeautifulSoup(content, features="html.parser")

    assets = get_page_assets(soup)

    expected_assets = [
        BeautifulSoup().new_tag(
            "img", src="/assets/professions/nodejs.png", alt="Node.js profession icon"
        )
    ]

    assert assets == expected_assets, "it should extract assets tags"


def test_process_assets():
    assets = [
        BeautifulSoup().new_tag(
            "img", src="/assets/professions/nodejs.png", alt="Node.js profession icon"
        )
    ]
    page_url = "https://foo.bar"
    file_name_prefix = generate_file_name_prefix_from_page_url(page_url)
    with TemporaryDirectory() as folder:
        folder_path = Path(folder)

    asset_content = file_operations_tests_resources_path(
        "assets/professions/nodejs.png"
    ).read_bytes()
    patch("page_loader.core.get_page_content", return_value=asset_content).start()

    processed_assets = process_assets(
        assets=assets,
        page_url=page_url,
        file_name_prefix=file_name_prefix,
        folder=folder_path,
    )

    expected_asset_folder_name = f"{file_name_prefix}_files"
    expected_asset_name = f"{file_name_prefix}-assets-professions-nodejs.png"
    expected_assets_folder = folder_path.joinpath(expected_asset_folder_name)
    expected_asset_path = expected_assets_folder.joinpath(expected_asset_name)
    expected_processed_assets = {
        assets[0]: BeautifulSoup().new_tag(
            "img",
            src=f"{expected_asset_folder_name}/{expected_asset_name}",
            alt="Node.js profession icon",
        )
    }
    expected_assets_folder_content = [expected_asset_path]

    assert processed_assets == expected_processed_assets
    assert expected_assets_folder.exists()
    assert list(expected_assets_folder.iterdir()) == expected_assets_folder_content
    assert expected_asset_path.read_bytes() == asset_content

    patch.stopall()


def test_update_page_assets_without_assets():
    content = "<h1>\n foo, bar!\n</h1>"
    soup = BeautifulSoup(content, features="html.parser")
    assets = {}

    updated_page_content = update_page_assets(soup, assets)

    assert updated_page_content == content


def test_update_page_assets_with_assets():
    content = file_operations_tests_resources_path(
        "page_content_with_assets.html"
    ).read_text()
    soup = BeautifulSoup(content, features="html.parser")
    assets = {
        BeautifulSoup()
        .new_tag(
            "img", src="/assets/professions/nodejs.png", alt="Node.js profession icon"
        ): BeautifulSoup()
        .new_tag(
            "img",
            src="ru-hexlet-io-courses_files/"
            "ru-hexlet-io-courses-assets-professions-nodejs.png",
            alt="Node.js profession icon",
        )
    }

    updated_page_content = update_page_assets(soup, assets)

    expected_page_content = file_operations_tests_resources_path(
        "updated_page_content_with_assets.html"
    ).read_text()

    assert updated_page_content == expected_page_content
