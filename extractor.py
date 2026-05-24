# agent/extractor.py
import pyodbc
import json
from agent import queries

class Extractor:
    def __init__(self, server, database, username, password):
        self.conn_str = (
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={server};'
            f'DATABASE={database};'
            f'UID={username};'
            f'PWD={password};'
        )
        self.conn = None

    def connect(self):
        try:
            self.conn = pyodbc.connect(self.conn_str)
            print("Conexão com o SQL Server bem-sucedida.")
        except Exception as e:
            print(f"Erro ao conectar ao SQL Server: {e}")
            raise

    def _execute_query(self, query):
        cursor = self.conn.cursor()
        cursor.execute(query)
        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        return results

    def extract_all_data(self):
        if not self.conn:
            print("A conexão não foi estabelecida.")
            return None

        print("Extraindo dados de saúde do banco...")
        health_data = {
            "database_status": self._execute_query(queries.DATABASE_STATUS),
            "backup_status": self._execute_query(queries.BACKUP_STATUS),
            "active_locks": self._execute_query(queries.ACTIVE_LOCKS),
            "fragmented_indexes": self._execute_query(queries.FRAGMENTED_INDEXES),
            "slow_queries": self._execute_query(queries.SLOW_QUERIES),
        }
        print("Extração concluída.")
        return health_data

    def save_data_to_json(self, data, filename="health_report.json"):
        # pyodbc pode retornar tipos de dados não serializáveis em JSON (como datetime)
        # Esta função auxiliar converte esses tipos para string
        def default_serializer(o):
            import datetime
            if isinstance(o, (datetime.datetime, datetime.date)):
                return o.isoformat()
            raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, default=default_serializer)
        print(f"Dados salvos em {filename}")

    def close(self):
        if self.conn:
            self.conn.close()
            print("Conexão com o SQL Server fechada.")