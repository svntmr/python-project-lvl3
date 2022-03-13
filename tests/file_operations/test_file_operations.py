from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from page_loader.file_operations import (
    generate_file_name_from_page_url,
    save_file,
    store_page_content,
)


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


def test_save_file():
    content = "<h1>foo, bar!</h1>"
    file_name = "foo-bar.html"
    with TemporaryDirectory() as folder:
        folder_path = Path(folder)
        filepath = save_file(content, file_name, folder_path)

        assert filepath == folder_path.joinpath(
            file_name
        ), "it should return path to the file in folder"
        assert filepath.read_text() == content, "it should write the given content"


def test_save_file_raises_if_folder_does_not_exist():
    content = "<h1>foo, bar!</h1>"
    file_name = "foo-bar.html"
    folder = "/folder/that/does/not/exists"

    with pytest.raises(RuntimeError) as runtime_error:
        save_file(content, file_name, folder)

        assert runtime_error.value == "folder for content saving doesn't exist!"


def test_store_page_content():
    page_url = "https://ru.hexlet.io/courses.html"
    content = "<h1>foo, bar!</h1>"

    expected_file_name = "ru-hexlet-io-courses.html"

    with TemporaryDirectory() as folder:
        folder_path = Path(folder)

        filepath = store_page_content(page_url, content, folder_path)

        expected_file_path = str(folder_path.joinpath(expected_file_name).resolve())

        assert (
            filepath == expected_file_path
        ), "it should return path to the file in folder"
        assert (
            Path(filepath).read_text() == content
        ), "it should write the given content"
