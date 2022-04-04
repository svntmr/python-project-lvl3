from http import HTTPStatus

import requests
from loguru import logger


def get_page_content(page_url: str) -> str:
    response = requests.get(page_url)

    if response.status_code != HTTPStatus.OK:
        error_message = (
            f"get request to {page_url} returned not OK status code - "
            f"{response.status_code}. Response message: {response.text}"
        )
        logger.exception(error_message)
        raise RuntimeError(error_message)

    return response.text
