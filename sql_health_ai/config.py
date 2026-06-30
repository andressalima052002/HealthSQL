import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "sim"}


@dataclass(frozen=True)
class AppConfig:
    sql_server: str
    sql_database: str
    sql_username: str
    sql_password: str
    sql_driver: str
    sql_encrypt: str
    sql_trust_certificate: str
    xai_api_key: str | None
    xai_base_url: str
    grok_model: str
    use_mock_data: bool

    @property
    def sql_connection_string(self) -> str:
        authentication = "Trusted_Connection=yes;" if not self.sql_username else (
            f"UID={self.sql_username};"
            f"PWD={self.sql_password};"
        )
        return (
            f"DRIVER={{{self.sql_driver}}};"
            f"SERVER={self.sql_server};"
            f"DATABASE={self.sql_database};"
            f"{authentication}"
            f"Encrypt={self.sql_encrypt};"
            f"TrustServerCertificate={self.sql_trust_certificate};"
        )


def load_config() -> AppConfig:
    return AppConfig(
        sql_server=os.getenv("SQL_SERVER", "localhost"),
        sql_database=os.getenv("SQL_DATABASE", "master"),
        sql_username=os.getenv("SQL_USERNAME", ""),
        sql_password=os.getenv("SQL_PASSWORD", ""),
        sql_driver=os.getenv("SQL_DRIVER", "ODBC Driver 18 for SQL Server"),
        sql_encrypt=os.getenv("SQL_ENCRYPT", "yes"),
        sql_trust_certificate=os.getenv("SQL_TRUST_CERTIFICATE", "yes"),
        xai_api_key=os.getenv("XAI_API_KEY"),
        xai_base_url=os.getenv("XAI_BASE_URL", "https://api.x.ai/v1"),
        grok_model=os.getenv("GROK_MODEL", "grok-4.3"),
        use_mock_data=_env_bool("USE_MOCK_DATA", False),
    )
