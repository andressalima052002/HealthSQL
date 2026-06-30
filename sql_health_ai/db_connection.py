from contextlib import contextmanager
from typing import Iterator

import pyodbc

from sql_health_ai.config import AppConfig


@contextmanager
def get_connection(config: AppConfig) -> Iterator[pyodbc.Connection]:
    connection = pyodbc.connect(config.sql_connection_string, timeout=10)
    try:
        yield connection
    finally:
        connection.close()
