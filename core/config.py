import configparser
from dataclasses import dataclass, field

PREFIXO_INSTANCIA = "SQL_SERVER:"
DRIVER_DEFAULT = "ODBC Driver 17 for SQL Server"


@dataclass
class InstanciaSQL:
    apelido: str
    server: str
    database: str
    username: str
    password: str
    driver: str = DRIVER_DEFAULT


@dataclass
class Config:
    intervalo_minutos: int
    diretorio_relatorios: str
    nivel_log: str
    ollama_host: str
    ollama_modelo: str
    ollama_timeout: int
    instancias: list = field(default_factory=list)


def _exigir(parser, secao, campo):
    if not parser.has_option(secao, campo):
        raise ValueError(f"Campo obrigatório ausente em [{secao}]: {campo}")
    valor = parser.get(secao, campo).strip()
    if not valor:
        raise ValueError(f"Campo obrigatório vazio em [{secao}]: {campo}")
    return valor


def carregar_config(caminho="config.ini") -> Config:
    parser = configparser.ConfigParser()
    lidos = parser.read(caminho, encoding="utf-8")
    if not lidos:
        raise FileNotFoundError(f"Arquivo de configuração não encontrado: {caminho}")

    if not parser.has_section("GLOBAL"):
        raise ValueError("Seção [GLOBAL] ausente no config.ini")
    if not parser.has_section("OLLAMA"):
        raise ValueError("Seção [OLLAMA] ausente no config.ini")

    try:
        intervalo = int(_exigir(parser, "GLOBAL", "intervalo_minutos"))
    except ValueError:
        raise ValueError("[GLOBAL] intervalo_minutos deve ser inteiro")

    try:
        ollama_timeout = int(_exigir(parser, "OLLAMA", "timeout"))
    except ValueError:
        raise ValueError("[OLLAMA] timeout deve ser inteiro")

    instancias = []
    for secao in parser.sections():
        if not secao.startswith(PREFIXO_INSTANCIA):
            continue
        apelido = secao[len(PREFIXO_INSTANCIA):].strip()
        if not apelido:
            raise ValueError(f"Seção sem apelido após '{PREFIXO_INSTANCIA}': [{secao}]")
        driver = parser.get(secao, "driver", fallback=DRIVER_DEFAULT).strip() or DRIVER_DEFAULT
        instancias.append(
            InstanciaSQL(
                apelido=apelido,
                server=_exigir(parser, secao, "server"),
                database=_exigir(parser, secao, "database"),
                username=_exigir(parser, secao, "username"),
                password=_exigir(parser, secao, "password"),
                driver=driver,
            )
        )

    if not instancias:
        raise ValueError(
            f"Nenhuma instância configurada. Adicione ao menos uma seção [{PREFIXO_INSTANCIA}<apelido>]."
        )

    return Config(
        intervalo_minutos=intervalo,
        diretorio_relatorios=_exigir(parser, "GLOBAL", "diretorio_relatorios"),
        nivel_log=parser.get("GLOBAL", "nivel_log", fallback="INFO").strip().upper(),
        ollama_host=_exigir(parser, "OLLAMA", "host"),
        ollama_modelo=_exigir(parser, "OLLAMA", "modelo"),
        ollama_timeout=ollama_timeout,
        instancias=instancias,
    )
