import csv
import datetime as dt
import logging

from prettytable import PrettyTable

from constants import (BASE_DIR, DATETIME_FORMAT, FILE_CHOICE, PRETTY_CHOICE,
                       RESULTS_DIR)

LOG_RESULT_MESSAGE = 'Файл с результатами был сохранён: {}'


def default_output(results, cli_args):
    """Выводит данные в консоль."""
    for row in results:
        print(*row)


def pretty_output(results, cli_args):
    """Выводит данные в консоль в виде таблицы."""
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


def file_output(results, cli_args):
    """Сохраняет данные в csv файл."""
    results_dir = BASE_DIR / RESULTS_DIR
    results_dir.mkdir(exist_ok=True)
    parser_mode = cli_args.mode
    now = dt.datetime.now()
    now_formatted = now.strftime(DATETIME_FORMAT)
    file_name = f'{parser_mode}_{now_formatted}.csv'
    file_path = results_dir / file_name
    with open(file_path, 'w', encoding='utf-8') as f:
        writer = csv.writer(f, dialect=csv.unix_dialect)
        writer.writerows(results)
    logging.info(LOG_RESULT_MESSAGE.format(file_path))


OUTPUT_FUNCTION = {
    PRETTY_CHOICE: pretty_output,
    FILE_CHOICE: file_output,
}


def control_output(results, cli_args):
    """Вызывает соответствующую функцию вывода."""
    output = cli_args.output

    output_function = OUTPUT_FUNCTION.get(output, default_output)
    output_function(results, cli_args)
