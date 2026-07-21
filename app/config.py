import configparser
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config.ini"

_parser = configparser.ConfigParser()
_parser.read(CONFIG_PATH)

HOST = _parser.get("server", "host", fallback="127.0.0.1")
PORT = _parser.getint("server", "port", fallback=8000)

_db_path = Path(_parser.get("database", "path", fallback="bc_grouping.db"))
DB_PATH = str(_db_path if _db_path.is_absolute() else PROJECT_ROOT / _db_path)
