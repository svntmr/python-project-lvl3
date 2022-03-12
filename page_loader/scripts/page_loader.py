import argparse
from os import getcwd

from page_loader.core import download


def main():
    args = parse_args()
    file_path = download(args.page_url, args.output)
    print(file_path)


def parse_args() -> argparse.Namespace:
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
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    main()
