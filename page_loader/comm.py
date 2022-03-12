from http import HTTPStatus

import requests


def get_page_content(page_url: str) -> str:
    response = requests.get(page_url)

    if response.status_code != HTTPStatus.OK:
        raise RuntimeError(
            f"get request to {page_url} returned not OK status code - "
            f"{response.status_code}. Response message: {response.text}"
        )

    return response.text
