from os import getcwd
from pathlib import Path
from unittest.mock import patch

from page_loader.scripts.page_loader import (
    PageLoaderConfig,
    main,
    process_arguments,
)


def test_process_arguments_without_output():
    page_url = "https://foo.bar"

    config = process_arguments([page_url])

    expected_config = PageLoaderConfig(page_url=page_url, output=Path(getcwd()))

    assert config.page_url == expected_config.page_url
    assert (
        config.output == expected_config.output
    ), "it should use current working directory when -o isn't provided"


def test_process_arguments_with_output():
    page_url = "https://foo.bar"
    output = "/var/tmp"

    config = process_arguments([page_url, f"-o={output}"])

    expected_config = PageLoaderConfig(page_url=page_url, output=Path(output))

    assert config.page_url == expected_config.page_url
    assert (
        config.output == expected_config.output
    ), "it should convert -o value into Path"


def test_main():
    page_url = "https://foo.bar"
    output = "/var/tmp"
    file_path = "foo.html"

    # fix process_arguments behavior
    patch(
        "page_loader.scripts.page_loader.process_arguments",
        return_value=PageLoaderConfig(page_url=page_url, output=Path(output)),
    ).start()
    # fix download behavior
    patch("page_loader.scripts.page_loader.download", return_value=file_path).start()
    print_patch = patch("builtins.print").start()

    main()

    # main should call print with file path returned from download
    print_patch.assert_called_once_with(file_path)
