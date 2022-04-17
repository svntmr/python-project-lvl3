import time
from http import HTTPStatus

import requests
from page_loader.logging import get_logger
from progress.bar import IncrementalBar

logger = get_logger("page_loader.comm")


def get_page_content(page_url: str) -> bytes:
    try:
        with requests.get(
            page_url,
            stream=True,
        ) as response:
            total_size = len(response.content)
            chunk_size = 1024
            steps = round(total_size / chunk_size)

            with IncrementalBar(
                f"Downloading {page_url} content", max=steps, check_tty=False
            ) as bar:
                for __ in response.iter_content(chunk_size=chunk_size):
                    time.sleep(0.001)
                    bar.next()
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

    return response.content
