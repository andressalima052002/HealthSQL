from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import pyodbc


@dataclass
class HealthMetrics:
    database_name: str
    database_status: str
    recovery_model: str
    last_backup_hours: float | None
    last_backup_finish: str | None
    backup_error: bool
    backup_error_message: str | None
    active_locks: int
    blocking_sessions: int
    fragmented_indexes: int
    max_fragmentation_percent: float
    slow_queries: int
    slowest_query_ms: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class SqlServerCollector:
    def __init__(self, connection: pyodbc.Connection, database_name: str) -> None:
        self.connection = connection
        self.database_name = database_name

    def collect(self) -> HealthMetrics:
        database_status = self._fetch_database_status()
        last_backup = self._fetch_last_backup()
        backup_error = self._fetch_backup_error()
        locks = self._fetch_locks()
        indexes = self._fetch_fragmented_indexes()
        slow_queries = self._fetch_slow_queries()

        return HealthMetrics(
            database_name=self.database_name,
            database_status=database_status["state_desc"],
            recovery_model=database_status["recovery_model_desc"],
            last_backup_hours=last_backup["hours_since_backup"],
            last_backup_finish=last_backup["backup_finish_date"],
            backup_error=backup_error["has_error"],
            backup_error_message=backup_error["message"],
            active_locks=locks["active_locks"],
            blocking_sessions=locks["blocking_sessions"],
            fragmented_indexes=indexes["fragmented_indexes"],
            max_fragmentation_percent=indexes["max_fragmentation_percent"],
            slow_queries=slow_queries["slow_queries"],
            slowest_query_ms=slow_queries["slowest_query_ms"],
        )

    def _fetch_one(self, query: str) -> pyodbc.Row:
        cursor = self.connection.cursor()
        cursor.execute(query)
        row = cursor.fetchone()
        if row is None:
            raise RuntimeError("A consulta nao retornou dados.")
        return row

    def _safe_database_name(self) -> str:
        return self.database_name.replace("'", "''")

    def _fetch_database_status(self) -> dict[str, str]:
        row = self._fetch_one(
            f"""
            SELECT state_desc, recovery_model_desc
            FROM sys.databases
            WHERE name = '{self._safe_database_name()}'
            """
        )
        return {
            "state_desc": row.state_desc,
            "recovery_model_desc": row.recovery_model_desc,
        }

    def _fetch_last_backup(self) -> dict[str, Any]:
        cursor = self.connection.cursor()
        cursor.execute(
            f"""
            SELECT TOP 1
                DATEDIFF(MINUTE, backup_finish_date, GETDATE()) / 60.0 AS hours_since_backup,
                CONVERT(varchar(19), backup_finish_date, 120) AS backup_finish_date
            FROM msdb.dbo.backupset
            WHERE database_name = '{self._safe_database_name()}'
              AND type = 'D'
            ORDER BY backup_finish_date DESC
            """
        )
        row = cursor.fetchone()
        if row is None:
            return {"hours_since_backup": None, "backup_finish_date": None}
        return {
            "hours_since_backup": float(row.hours_since_backup) if row.hours_since_backup is not None else None,
            "backup_finish_date": row.backup_finish_date,
        }

    def _fetch_backup_error(self) -> dict[str, Any]:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT TOP 1
                CASE WHEN run_status = 0 THEN 1 ELSE 0 END AS has_error,
                message
            FROM msdb.dbo.sysjobhistory
            WHERE step_name LIKE '%backup%'
               OR message LIKE '%backup%'
            ORDER BY instance_id DESC
            """
        )
        row = cursor.fetchone()
        if row is None:
            return {"has_error": False, "message": None}
        return {
            "has_error": bool(row.has_error),
            "message": row.message if bool(row.has_error) else None,
        }

    def _fetch_locks(self) -> dict[str, int]:
        row = self._fetch_one(
            f"""
            SELECT
                COUNT(*) AS active_locks,
                SUM(CASE WHEN r.blocking_session_id <> 0 THEN 1 ELSE 0 END) AS blocking_sessions
            FROM sys.dm_tran_locks l
            LEFT JOIN sys.dm_exec_requests r ON l.request_session_id = r.session_id
            WHERE l.resource_database_id = DB_ID('{self._safe_database_name()}')
            """
        )
        return {
            "active_locks": int(row.active_locks or 0),
            "blocking_sessions": int(row.blocking_sessions or 0),
        }

    def _fetch_fragmented_indexes(self) -> dict[str, Any]:
        row = self._fetch_one(
            f"""
            SELECT
                COUNT(*) AS fragmented_indexes,
                ISNULL(MAX(avg_fragmentation_in_percent), 0) AS max_fragmentation_percent
            FROM sys.dm_db_index_physical_stats(DB_ID('{self._safe_database_name()}'), NULL, NULL, NULL, 'LIMITED')
            WHERE index_id > 0
              AND page_count >= 100
              AND avg_fragmentation_in_percent > 30
            """
        )
        return {
            "fragmented_indexes": int(row.fragmented_indexes or 0),
            "max_fragmentation_percent": float(row.max_fragmentation_percent or 0),
        }

    def _fetch_slow_queries(self) -> dict[str, Any]:
        row = self._fetch_one(
            """
            SELECT
                COUNT(*) AS slow_queries,
                ISNULL(MAX((total_elapsed_time / NULLIF(execution_count, 0)) / 1000.0), 0) AS slowest_query_ms
            FROM sys.dm_exec_query_stats
            WHERE (total_elapsed_time / NULLIF(execution_count, 0)) / 1000.0 > 1000
            """
        )
        return {
            "slow_queries": int(row.slow_queries or 0),
            "slowest_query_ms": float(row.slowest_query_ms or 0),
        }


def mock_metrics() -> HealthMetrics:
    return HealthMetrics(
        database_name="HealthSQL_Pilot",
        database_status="ONLINE",
        recovery_model="FULL",
        last_backup_hours=28.0,
        last_backup_finish="2026-06-28 18:20:00",
        backup_error=False,
        backup_error_message=None,
        active_locks=5,
        blocking_sessions=2,
        fragmented_indexes=3,
        max_fragmentation_percent=46.8,
        slow_queries=4,
        slowest_query_ms=2450.0,
    )
