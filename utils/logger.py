import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

DEFAULT_LOG_DIR = Path(__file__).resolve().parents[2] / "logs"
DEFAULT_LOG_DIR.mkdir(parents=True, exist_ok=True)

_DEF_LOG_FILE = DEFAULT_LOG_DIR / "system.log"

def setup_logger(name: str = "concode", level: int = logging.INFO, log_file: str | None = None) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(level)

    ch = logging.StreamHandler()
    ch.setLevel(level)
    fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    file_path = Path(log_file) if log_file else _DEF_LOG_FILE
    fh = RotatingFileHandler(file_path, maxBytes=1_000_000, backupCount=3)
    fh.setLevel(level)
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    return logger
