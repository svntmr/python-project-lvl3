from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from bs4 import BeautifulSoup
from page_loader import download
from page_loader.core import (
    PageAssets,
    PageAssetsWithUpdatedAssets,
    get_page_assets,
    process_assets,
    process_page_content,
    update_page_assets,
)
from page_loader.file_operations import generate_file_name_prefix_from_page_url
from tests.helpers import make_tag
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
    expected_asset_file_name = "ru-hexlet-io-assets-professions-nodejs.png"

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


def test_process_page_content_page_with_script_and_link_tags():
    page_url = "https://ru.hexlet.io/courses"
    # page content with assets
    content = file_operations_tests_resources_path(
        "page_with_script_and_link_tags.html"
    ).read_text()
    css_asset_content = file_operations_tests_resources_path(
        "assets/application.css"
    ).read_text()
    courses_asset_content = file_operations_tests_resources_path(
        "courses.html"
    ).read_text()
    node_js_picture_asset_content = file_operations_tests_resources_path(
        "assets/professions/nodejs.png"
    ).read_bytes()
    js_runtime_asset_content = file_operations_tests_resources_path(
        "packs/js/runtime.js"
    ).read_text()

    # page content with updated assets
    expected_updated_content = file_operations_tests_resources_path(
        "updated_page_with_script_and_link_tags.html"
    ).read_text()

    expected_file_name = "ru-hexlet-io-courses.html"
    expected_assets_folder_name = "ru-hexlet-io-courses_files"
    expected_css_asset_file_name = "ru-hexlet-io-assets-application.css"
    expected_courses_asset_file_name = "ru-hexlet-io-courses.html"
    expected_node_js_picture_asset_file_name = (
        "ru-hexlet-io-assets-professions-nodejs.png"
    )
    expected_js_runtime_asset_file_name = "ru-hexlet-io-packs-js-runtime.js"

    with TemporaryDirectory() as folder:
        folder_path = Path(folder)
        patch(
            "page_loader.core.get_page_content",
            side_effect=[
                node_js_picture_asset_content,
                js_runtime_asset_content,
                css_asset_content,
                courses_asset_content,
            ],
        ).start()

        filepath = process_page_content(page_url, content, folder_path)

        expected_file_path = str(folder_path.joinpath(expected_file_name).resolve())
        expected_asset_folder_path = folder_path.joinpath(expected_assets_folder_name)
        expected_css_asset_file_path = expected_asset_folder_path.joinpath(
            expected_css_asset_file_name
        )
        expected_courses_asset_file_path = expected_asset_folder_path.joinpath(
            expected_courses_asset_file_name
        )
        expected_node_js_picture_asset_file_path = expected_asset_folder_path.joinpath(
            expected_node_js_picture_asset_file_name
        )
        expected_js_runtime_asset_file_path = expected_asset_folder_path.joinpath(
            expected_js_runtime_asset_file_name
        )

        assert (
            filepath == expected_file_path
        ), "it should return path to the file in folder"
        assert expected_asset_folder_path.exists(), "it should create assets folder"
        assert (
            expected_css_asset_file_path.read_text() == css_asset_content
        ), "it should save css asset into assets folder"
        assert (
            expected_courses_asset_file_path.read_text() == courses_asset_content
        ), "it should save courses asset into assets folder"
        assert (
            expected_node_js_picture_asset_file_path.read_bytes()
            == node_js_picture_asset_content
        ), "it should save node js picture asset into assets folder"
        assert (
            expected_js_runtime_asset_file_path.read_text() == js_runtime_asset_content
        ), "it should save js runtime asset into assets folder"
        assert (
            Path(filepath).read_text() == expected_updated_content
        ), "it should update page content with new assets location"

    patch.stopall()


def test_get_page_assets_page_without_assets():
    page_url = "https://ru.hexlet.io/courses.html"
    content = "<h1>\n foo, bar!\n</h1>"
    soup = BeautifulSoup(content, features="html.parser")

    assets = get_page_assets(soup, page_url)

    expected_assets = PageAssets(src=[], href=[])

    assert (
        assets == expected_assets
    ), "it should return empty list as page has no assets"


def test_get_page_assets_page_with_assets():
    page_url = "https://ru.hexlet.io/courses.html"
    content = file_operations_tests_resources_path(
        "page_content_with_assets.html"
    ).read_text()
    soup = BeautifulSoup(content, features="html.parser")

    assets = get_page_assets(soup, page_url)

    expected_assets = PageAssets(
        src=[
            make_tag(
                "img",
                src="/assets/professions/nodejs.png",
                alt="Node.js profession icon",
            )
        ],
        href=[],
    )

    assert assets == expected_assets, "it should extract assets tags"


def test_get_page_assets_page_with_scripts_and_links():
    page_url = "https://ru.hexlet.io/courses.html"
    content = file_operations_tests_resources_path(
        "page_with_script_and_link_tags.html"
    ).read_text()
    soup = BeautifulSoup(content, features="html.parser")

    assets = get_page_assets(soup, page_url)

    expected_assets = PageAssets(
        src=[
            make_tag(
                "img",
                src="/assets/professions/nodejs.png",
                alt="Node.js profession icon",
            ),
            make_tag("script", src="https://ru.hexlet.io/packs/js/runtime.js"),
        ],
        href=[
            make_tag(
                "link", href="/assets/application.css", media="all", rel="stylesheet"
            ),
            make_tag("link", href="/courses", rel="canonical"),
        ],
    )

    assert assets == expected_assets, "it should extract assets tags"


def test_process_assets():
    assets = PageAssets(
        src=[
            make_tag(
                "img",
                src="/assets/professions/nodejs.png",
                alt="Node.js profession icon",
            )
        ],
        href=[],
    )
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
    expected_processed_assets = PageAssetsWithUpdatedAssets(
        src={
            assets.src[0]: make_tag(
                "img",
                src=f"{expected_asset_folder_name}/{expected_asset_name}",
                alt="Node.js profession icon",
            )
        },
        href={},
    )
    expected_assets_folder_content = [expected_asset_path]

    assert processed_assets == expected_processed_assets
    assert expected_assets_folder.exists()
    assert list(expected_assets_folder.iterdir()) == expected_assets_folder_content
    assert expected_asset_path.read_bytes() == asset_content

    patch.stopall()


def test_update_page_assets_without_assets():
    content = "<h1>\n foo, bar!\n</h1>"
    soup = BeautifulSoup(content, features="html.parser")
    assets = PageAssetsWithUpdatedAssets(
        src={},
        href={},
    )

    updated_page_content = update_page_assets(soup, assets)

    assert updated_page_content == content


def test_update_page_assets_with_assets():
    content = file_operations_tests_resources_path(
        "page_content_with_assets.html"
    ).read_text()
    soup = BeautifulSoup(content, features="html.parser")
    assets = PageAssetsWithUpdatedAssets(
        src={
            make_tag(
                "img",
                src="/assets/professions/nodejs.png",
                alt="Node.js profession icon",
            ): make_tag(
                "img",
                src="ru-hexlet-io-courses_files/"
                "ru-hexlet-io-assets-professions-nodejs.png",
                alt="Node.js profession icon",
            )
        },
        href={},
    )

    updated_page_content = update_page_assets(soup, assets)

    expected_page_content = file_operations_tests_resources_path(
        "updated_page_content_with_assets.html"
    ).read_text()

    assert updated_page_content == expected_page_content


def test_update_page_assets_with_scripts_and_links():
    content = file_operations_tests_resources_path(
        "page_with_script_and_link_tags.html"
    ).read_text()
    soup = BeautifulSoup(content, features="html.parser")

    assets = PageAssetsWithUpdatedAssets(
        src={
            make_tag(
                "img",
                src="/assets/professions/nodejs.png",
                alt="Node.js profession icon",
            ): make_tag(
                "img",
                src=(
                    "ru-hexlet-io-courses_files/"
                    "ru-hexlet-io-assets-professions-nodejs.png"
                ),
                alt="Node.js profession icon",
            ),
            make_tag(
                "script", src="https://ru.hexlet.io/packs/js/runtime.js"
            ): make_tag(
                "script",
                src="ru-hexlet-io-courses_files/ru-hexlet-io-packs-js-runtime.js",
            ),
        },
        href={
            make_tag(
                "link",
                href="/assets/application.css",
                media="all",
                rel="stylesheet",
            ): make_tag(
                "link",
                href="ru-hexlet-io-courses_files/ru-hexlet-io-assets-application.css",
                media="all",
                rel="stylesheet",
            ),
            make_tag("link", href="/courses", rel="canonical",): make_tag(
                "link",
                href="ru-hexlet-io-courses_files/ru-hexlet-io-courses.html",
                rel="canonical",
            ),
        },
    )

    updated_page_content = update_page_assets(soup, assets)

    expected_page_content = file_operations_tests_resources_path(
        "updated_page_with_script_and_link_tags.html"
    ).read_text()

    assert updated_page_content == expected_page_content
