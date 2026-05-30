import datetime
import json
import logging

import pyodbc

from agent import queries

logger = logging.getLogger(__name__)

DRIVER_DEFAULT = "ODBC Driver 17 for SQL Server"


class Extractor:
    def __init__(self, server, database, username, password, driver=DRIVER_DEFAULT):
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.driver = driver
        self.conn = None

    def _montar_conn_str(self, database=None):
        db = database or self.database
        return (
            f"DRIVER={{{self.driver}}};"
            f"SERVER={self.server};"
            f"DATABASE={db};"
            f"UID={self.username};"
            f"PWD={self.password};"
        )

    def connect(self):
        try:
            self.conn = pyodbc.connect(self._montar_conn_str())
            logger.info("Conexão com SQL Server bem-sucedida (%s)", self.server)
        except Exception as e:
            logger.error("Erro ao conectar em %s: %s", self.server, e)
            raise

    def _execute_query(self, query, conn=None):
        cursor = (conn or self.conn).cursor()
        cursor.execute(query)
        colunas = [c[0] for c in cursor.description]
        return [dict(zip(colunas, row)) for row in cursor.fetchall()]

    def _coletar_fragmentacao_todos_dbs(self):
        bancos = self._execute_query(queries.DATABASES_PARA_ESCANEAR)
        resultado = []
        for banco in bancos:
            nome_db = banco["name"]
            try:
                conn_db = pyodbc.connect(self._montar_conn_str(nome_db), timeout=10)
                try:
                    fragmentos = self._execute_query(queries.FRAGMENTED_INDEXES_LOCAL, conn=conn_db)
                    for f in fragmentos:
                        f["database_name"] = nome_db
                        resultado.append(f)
                finally:
                    conn_db.close()
            except Exception as e:
                logger.warning("Falha ao escanear índices de %s: %s", nome_db, e)
        return resultado

    def extract_all_data(self):
        if not self.conn:
            raise RuntimeError("Conexão não estabelecida — chame connect() antes.")

        logger.info("Extraindo dados de saúde do servidor %s", self.server)
        resultados = {}

        secoes_simples = [
            ("database_status", queries.DATABASE_STATUS),
            ("backup_status", queries.BACKUP_STATUS),
            ("active_locks", queries.ACTIVE_LOCKS),
            ("slow_queries", queries.SLOW_QUERIES),
        ]
        for chave, query in secoes_simples:
            try:
                resultados[chave] = self._execute_query(query)
            except Exception as e:
                logger.error("Falha ao executar %s em %s: %s", chave, self.server, e)
                resultados[chave] = []

        try:
            resultados["fragmented_indexes"] = self._coletar_fragmentacao_todos_dbs()
        except Exception as e:
            logger.error("Falha ao coletar fragmentação em %s: %s", self.server, e)
            resultados["fragmented_indexes"] = []

        logger.info("Extração concluída para %s", self.server)
        return resultados

    @staticmethod
    def _serializar(o):
        if isinstance(o, (datetime.datetime, datetime.date)):
            return o.isoformat()
        raise TypeError(f"Tipo {o.__class__.__name__} não é serializável em JSON")

    def save_data_to_json(self, data, caminho):
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, default=self._serializar)
        logger.info("Dados salvos em %s", caminho)

    def close(self):
        if self.conn:
            try:
                self.conn.close()
                logger.info("Conexão com %s fechada", self.server)
            finally:
                self.conn = None
