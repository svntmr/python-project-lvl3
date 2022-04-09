from http import HTTPStatus

import requests
from page_loader.logging import get_logger

logger = get_logger("page_loader.comm")


def get_page_content(page_url: str) -> str:
    try:
        response = requests.get(page_url)
    except Exception:
        error_message = f"get request to {page_url} failed, see exception message above"
        logger.error(error_message)
        raise

    if response.status_code != HTTPStatus.OK:
        error_message = (
            f"get request to {page_url} returned not OK status code - "
            f"{response.status_code}. Response message: {response.text}"
        )
        logger.error(error_message)
        raise RuntimeError(error_message)

    return response.text
