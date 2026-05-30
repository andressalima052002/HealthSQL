import logging
import logging.handlers
from pathlib import Path

FORMATO = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATEFMT = "%Y-%m-%d %H:%M:%S"


def setup_logging(nivel="INFO", diretorio="logs"):
    Path(diretorio).mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(fmt=FORMATO, datefmt=DATEFMT)

    root = logging.getLogger()
    root.setLevel(getattr(logging, nivel.upper(), logging.INFO))

    for h in list(root.handlers):
        root.removeHandler(h)

    arquivo_handler = logging.handlers.RotatingFileHandler(
        filename=Path(diretorio) / "healthsql.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=10,
        encoding="utf-8",
    )
    arquivo_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    root.addHandler(arquivo_handler)
    root.addHandler(console_handler)

    logging.getLogger("apscheduler").setLevel(logging.WARNING)
