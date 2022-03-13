from unittest.mock import patch

import pytest
from page_loader.comm import get_page_content
from requests import Response


@pytest.fixture
def ok_response() -> Response:
    response = Response()
    response.status_code = 200
    response._content = b"""<h1>foo, bar!</h1>"""

    return response


@pytest.fixture
def not_ok_response() -> Response:
    response = Response()
    response.status_code = 404
    response._content = b"""Page not found!"""

    return response


def test_get_page_content_makes_get_request_and_returns_response_content(ok_response):
    page_url = "https://foo.bar"

    with patch("requests.get", return_value=ok_response) as get_patch:
        content = get_page_content(page_url)

        get_patch.assert_called_once_with(page_url)
        assert content == ok_response.text, "it should return response text"


def test_get_page_content_throws_on_not_ok_status_code(not_ok_response):
    page_url = "https://foo.bar"

    with patch("requests.get", return_value=not_ok_response) as get_patch:
        with pytest.raises(RuntimeError) as runtime_error:

            get_page_content(page_url)

            get_patch.assert_called_once_with(page_url)
            assert runtime_error.value == (
                f"get request to {page_url} returned not OK status code - "
                f"{not_ok_response.status_code}. "
                f"Response message: {not_ok_response.text}"
            )
