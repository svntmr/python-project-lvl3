from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import mock_open, patch

import pytest
from page_loader.file_operations import (
    generate_file_name,
    generate_file_name_from_page_url,
    generate_file_name_prefix_from_page_url,
    save_assets,
    save_file,
)
from tests.paths import file_operations_tests_resources_path


@pytest.mark.parametrize(
    "page_url, expected_file_name",
    [
        pytest.param(
            "https://ru.hexlet.io/courses",
            "ru-hexlet-io-courses.html",
            id="page url without file extension",
        ),
        pytest.param(
            "https://ru.hexlet.io/courses?foo=bar",
            "ru-hexlet-io-courses.html",
            id="page url without file extension with query parameters",
        ),
        pytest.param(
            "https://ru.hexlet.io/courses.html",
            "ru-hexlet-io-courses.html",
            id="page url with file extension",
        ),
        pytest.param(
            "https://ru.hexlet.io/courses.xml?foo=bar",
            "ru-hexlet-io-courses.html",
            id="page url with file extension and query parameters",
        ),
    ],
)
def test_generate_file_name_from_page_url(page_url, expected_file_name):
    assert (
        generate_file_name_from_page_url(page_url) == expected_file_name
    ), "wrong file name was generated"


@pytest.mark.parametrize(
    "page_url, expected_file_name",
    [
        pytest.param(
            "https://ru.hexlet.io/courses",
            "ru-hexlet-io",
            id="page url without file extension",
        ),
        pytest.param(
            "https://ru.hexlet.io/courses?foo=bar",
            "ru-hexlet-io",
            id="page url without file extension with query parameters",
        ),
        pytest.param(
            "https://ru.hexlet.io/courses.html",
            "ru-hexlet-io",
            id="page url with file extension",
        ),
        pytest.param(
            "https://ru.hexlet.io/courses.xml?foo=bar",
            "ru-hexlet-io",
            id="page url with file extension and query parameters",
        ),
    ],
)
def test_generate_file_name_prefix_from_page_url(page_url, expected_file_name):
    assert (
        generate_file_name_prefix_from_page_url(page_url) == expected_file_name
    ), "wrong file name prefix was generated"


def test_generate_file_name():
    page_url = "https://ru.hexlet.io/courses"
    file_name_prefix = "foo-bar"
    src = "/assets/professions/nodejs.png"

    file_name = generate_file_name(file_name_prefix, src, page_url)

    expected_file_name = "foo-bar-assets-professions-nodejs.png"

    assert file_name == expected_file_name


def test_generate_file_name_href_with_full_link():
    page_url = "https://ru.hexlet.io/courses"
    file_name_prefix = "foo-bar"
    src = "https://ru.hexlet.io/packs/js/runtime.js"

    file_name = generate_file_name(file_name_prefix, src, page_url)

    expected_file_name = "ru-hexlet-io-packs-js-runtime.js"

    assert file_name == expected_file_name


def test_generate_file_name_link():
    page_url = "https://ru.hexlet.io/courses"
    file_name_prefix = "ru-hexlet-io-courses"
    src = "/courses"

    file_name = generate_file_name(file_name_prefix, src, page_url)

    expected_file_name = "ru-hexlet-io-courses.html"

    assert file_name == expected_file_name


def test_generate_file_name_full_link():
    page_url = "https://ru.hexlet.io/courses"
    file_name_prefix = "ru-hexlet-io-courses"
    src = "https://ru.hexlet.io/courses"

    file_name = generate_file_name(file_name_prefix, src, page_url)

    expected_file_name = "ru-hexlet-io-courses.html"

    assert file_name == expected_file_name


def test_generate_file_name_link_with_extension():
    page_url = "https://ru.hexlet.io/courses"
    file_name_prefix = "ru-hexlet-io-courses"
    src = "https://ru.hexlet.io/lessons.rss"

    file_name = generate_file_name(file_name_prefix, src, page_url)

    expected_file_name = "ru-hexlet-io-lessons.rss"

    assert file_name == expected_file_name


def test_save_file_str():
    content = "<h1>foo, bar!</h1>"
    file_name = "foo-bar.html"
    with TemporaryDirectory() as folder:
        folder_path = Path(folder)
        filepath = save_file(content, file_name, folder_path)

        assert filepath == folder_path.joinpath(
            file_name
        ), "it should return path to the file in folder"
        assert filepath.read_text() == content, "it should write the given content"


def test_save_file_bytes():
    content = b"<h1>foo, bar!</h1>"
    file_name = "foo-bar.html"
    with TemporaryDirectory() as folder:
        folder_path = Path(folder)
        filepath = save_file(content, file_name, folder_path)

        assert filepath == folder_path.joinpath(
            file_name
        ), "it should return path to the file in folder"
        assert filepath.read_bytes() == content, "it should write the given content"


def test_save_file_raises_if_folder_does_not_exist():
    content = "<h1>foo, bar!</h1>"
    file_name = "foo-bar.html"
    folder = Path("/folder/that/does/not/exists")

    with pytest.raises(RuntimeError) as runtime_error:
        save_file(content, file_name, folder)

    assert str(runtime_error.value) == "folder for content saving doesn't exist!"


def test_save_file_makes_error_log_on_write_fail():
    content = "<h1>foo, bar!</h1>"
    file_name = "foo-bar.html"
    with TemporaryDirectory() as folder:
        folder_path = Path(folder)

        logger_error_patch = patch("logging.Logger.error").start()
        # make open to throw Exception
        with patch("pathlib.Path.open", mock_open()) as mock_file:
            mock_file.side_effect = Exception()
            with pytest.raises(Exception):
                save_file(content, file_name, folder_path)

        logger_error_patch.assert_called_once_with(
            "something went wrong on file writing, see exception message above"
        )

    patch.stopall()


def test_save_assets():
    asset_content = file_operations_tests_resources_path(
        "assets/professions/nodejs.png"
    ).read_bytes()

    with TemporaryDirectory() as folder:
        assets_folder = Path(folder).resolve().joinpath("foo-bar_files")
        assets_folder.mkdir(parents=True, exist_ok=True)

        asset_path = assets_folder.joinpath("foo-bar-assets-professions-nodejs.png")
        assets_path_with_content = {asset_path: asset_content}

        save_assets(assets_path_with_content)

        assert asset_path.exists()
        assert asset_path.read_bytes() == asset_content
