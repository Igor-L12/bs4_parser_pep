from bs4 import BeautifulSoup
from requests import RequestException

from exceptions import ParserFindTagException

REQUEST_ERROR_MESSAGE = 'Возникла ошибка при загрузке страницы {url} {error}'

TAG_NOT_FOUND_ERROR_MESSAGE = 'Не найден тег {} {}'


def get_response(session, url, encoding='utf-8'):
    """Выполняет get запрос и возвращает ответ в указанной кодировке."""
    try:
        response = session.get(url)
        response.encoding = encoding
        return response
    except RequestException as error:
        error_message = REQUEST_ERROR_MESSAGE.format(url=url, error=error)
        raise ConnectionError(error_message)


def find_tag(soup, tag, attrs=None):
    """Выполняет поиск элемента по заданным параметрам."""
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        error_message = TAG_NOT_FOUND_ERROR_MESSAGE.format(tag, attrs)
        raise ParserFindTagException(error_message)
    return searched_tag


def create_soup(session, url, features='lxml'):
    response = get_response(session, url)
    return BeautifulSoup(response.text, features=features)
