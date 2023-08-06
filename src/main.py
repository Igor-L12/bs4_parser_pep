import logging
import re
from collections import defaultdict
from urllib.parse import urljoin

import requests_cache
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (BASE_DIR, DOWNLOADS_DIR, EXPECTED_STATUS, MAIN_DOC_URL,
                       MAIN_PEP_URL)
from exceptions import ParserFindTagException
from outputs import control_output
from utils import create_soup, find_tag, get_response

WHATS_NEW_TITLE = ('Ссылка на статью', 'Заголовок', 'Редактор, Автор')
NOT_FOUND_MESSAGE = 'Не удалось получить ответ для URL: {version_link}'
LATEST_VERSIONS_MESSAGE = 'Ничего не найдено'
LATEST_VERSIONS_TITLE = ('Ссылка на документацию', 'Версия', 'Статус')
DOWNLOAD_MESSAGE = 'Архив был загружен и сохранён: {archive_path}'
PEPS_TITLE = ('Статус', 'Количество')
INCORRECT_STATUS_MESSAGE = (
    'Несовпадающие статусы:\n'
    '{pep_link}\n'
    'Статус в карточке: {status_on_peps_page}\n'
    'Ожидаемые статусы: {expected_status}'
)
PEPS_TOTAL = 'Всего'
PARSER_START_MESSAGE = 'Парсер запущен'
PARSER_ARGS_MESSAGE = 'Аргументы командной строки: {args}'
PARSER_STOP_MESSAGE = 'Парсер завершил работу.'
ERROR_MESSAGE = 'Произошла шибка: {error}'


def whats_new(session):
    """Собирает данные об изменениях в версиях."""
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    soup = create_soup(session, whats_new_url)
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all('li',
                                              attrs={'class': 'toctree-l1'})
    results = [WHATS_NEW_TITLE]

    log_messages = []

    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, 'a')
        version_link = urljoin(whats_new_url, version_a_tag['href'])
        soup = create_soup(session, version_link)
        response = get_response(session, version_link)
        if response is None:
            log_messages.append(NOT_FOUND_MESSAGE.format(
                version_link=version_link))
        h1 = find_tag(soup, 'h1')
        h1_text = h1.text.replace(chr(182), '')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append((version_link, h1_text, dl_text))

    for message in log_messages:
        logging.info(message)

    return results


def latest_versions(session):
    """Собирает данные об актуальных версиях."""
    soup = create_soup(session, MAIN_DOC_URL)
    sidebar = find_tag(soup, 'div', {'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise ParserFindTagException(LATEST_VERSIONS_MESSAGE)
    results = [LATEST_VERSIONS_TITLE]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        version, status = a_tag.text, ''
        if text_match:
            version, status = text_match.groups()
        results.append((link, version, status))
    return results


def download(session):
    """Скачивает pdf- файл с документацией."""
    downloads_dir = BASE_DIR / DOWNLOADS_DIR
    downloads_dir.mkdir(exist_ok=True)
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    if response is None:
        return
    soup = create_soup(session, downloads_url)
    table_tag = find_tag(soup, 'table', {'class': 'docutils'})
    pdf_a4_tag = table_tag.find_all('a',
                                    {'href': re.compile(r'.+pdf-a4\.zip$')})
    for url in pdf_a4_tag:
        if 'Download' not in url.text:
            continue
        pdf_a4_link = url['href']
        archive_url = urljoin(downloads_url, pdf_a4_link)
        filename = archive_url.split('/')[-1]
        archive_path = downloads_dir / filename
        response = session.get(archive_url)
        with open(archive_path, 'wb') as file:
            file.write(response.content)
        logging.info(DOWNLOAD_MESSAGE.format(archive_path=archive_path))


def pep(session):
    soup = create_soup(session, MAIN_PEP_URL)
    numerical_table_tag = find_tag(soup,
                                   'section',
                                   attrs={'id': 'numerical-index'})
    body_table_tag = find_tag(numerical_table_tag, 'tbody')
    pep_rows = body_table_tag.find_all('tr')
    results = [PEPS_TITLE]
    count_of_statuses = {}

    count_of_statuses = defaultdict(int)
    incorrect_status_messages = []

    for row in tqdm(pep_rows):
        preview_status = find_tag(row, 'td').text[1:]
        pep_a_tag = find_tag(row, 'a')
        pep_link = urljoin(MAIN_PEP_URL, pep_a_tag['href'])
        sibling_soup = create_soup(session, pep_link)
        status_tag = sibling_soup.find(string='Status')
        status_on_peps_page = status_tag.parent.find_next_sibling().text
        count_of_statuses[status_on_peps_page] += 1
        if status_on_peps_page not in EXPECTED_STATUS[preview_status]:
            incorrect_status_messages.append(
                INCORRECT_STATUS_MESSAGE.format(
                    pep_link=pep_link, status_on_peps_page=status_on_peps_page,
                    expected_status=EXPECTED_STATUS[preview_status])
            )
    results.extend(sorted(count_of_statuses.items()))
    results.append((PEPS_TOTAL, len(pep_rows)))

    for message in incorrect_status_messages:
        logging.info(message)

    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    """Основная функция."""
    configure_logging()
    logging.info(PARSER_START_MESSAGE)
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    try:
        args = arg_parser.parse_args()
        logging.info(PARSER_ARGS_MESSAGE.format(args=args))
        session = requests_cache.CachedSession()
        if args.clear_cache:
            session.cache.clear()
        parser_mode = args.mode
        results = MODE_TO_FUNCTION.get(parser_mode)
        if results is not None:
            results = results(session)
            if results is not None:
                control_output(results, args)
        logging.info(PARSER_STOP_MESSAGE)
    except Exception as error:
        logging.exception(ERROR_MESSAGE.format(error=error))


if __name__ == '__main__':
    main()
