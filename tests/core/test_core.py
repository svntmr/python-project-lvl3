from unittest.mock import patch

from page_loader import download


def test_download_calls_get_page_content_and_store_page_content():
    page_url = "https://foo.bar"
    output = "."
    page_content = "<h1>foo, bar!</h1>"

    with patch(
        "page_loader.core.get_page_content", return_value=page_content
    ) as get_patch_content_patch:
        with patch("page_loader.core.store_page_content") as store_page_content_patch:
            download(page_url, output)

            get_patch_content_patch.assert_called_once_with(page_url)
            store_page_content_patch.assert_called_once_with(
                page_url, page_content, output
            )
