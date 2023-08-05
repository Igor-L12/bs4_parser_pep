from pathlib import Path

BASE_DIR = Path(__file__).parent
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
MAIN_DOC_URL = 'https://docs.python.org/3/'
MAIN_PEP_URL = 'https://peps.python.org/'
PRETTY_CHOICE = 'pretty'
FILE_CHOICE = 'file'
RESULTS_DIR = 'results'
LOGS_DIR = BASE_DIR / 'logs'
LOG_FILE_PATH = LOGS_DIR / 'parser.log'
LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
DT_FORMAT = '%d.%m.%Y %H:%M:%S'
DOWNLOADS_DIR = 'downloads'
EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}
