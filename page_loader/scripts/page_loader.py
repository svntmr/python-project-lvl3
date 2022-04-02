import argparse
from dataclasses import dataclass
from os import getcwd
from pathlib import Path
from typing import List, Optional

from page_loader.core import download


@dataclass(frozen=True)
class PageLoaderConfig:
    page_url: str
    output: Path


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Page Loader")
    parser.add_argument("page_url", type=str)
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help=(
            "Relative or absolute path to folder where the page content should be "
            "saved (it should exists and be writeable!). The default output directory "
            "is the current working directory"
        ),
        default=getcwd(),
    )
    return parser


def process_arguments(arguments: Optional[List] = None) -> PageLoaderConfig:
    parser = create_parser()

    parsed_args = parser.parse_args(arguments)

    return PageLoaderConfig(
        page_url=parsed_args.page_url,
        output=Path(parsed_args.output),
    )


def main():
    config = process_arguments()
    file_path = download(config.page_url, config.output)
    print(file_path)


if __name__ == "__main__":
    main()
