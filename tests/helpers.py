from bs4 import BeautifulSoup
from bs4.element import Tag


def make_tag(name: str, **kwargs) -> Tag:
    return BeautifulSoup().new_tag(name, **kwargs)
