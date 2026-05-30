DATABASE_STATUS = "SELECT name, state_desc FROM sys.databases;"

BACKUP_STATUS = """
SELECT
   d.name,
   b.type,
   b.backup_finish_date
FROM sys.databases d
LEFT JOIN (
   SELECT
      database_name,
      type,
      backup_finish_date,
      ROW_NUMBER() OVER(PARTITION BY database_name, type ORDER BY backup_finish_date DESC) as rn
   FROM msdb.dbo.backupset
) b ON d.name = b.database_name AND b.rn = 1
ORDER BY d.name;
"""

ACTIVE_LOCKS = """
SELECT
    tl.resource_type,
    tl.resource_database_id,
    DB_NAME(tl.resource_database_id) AS db_name,
    tl.request_mode,
    tl.request_status,
    es.session_id,
    es.login_name,
    es.host_name,
    es.program_name
FROM sys.dm_tran_locks AS tl
JOIN sys.dm_exec_sessions AS es ON tl.request_session_id = es.session_id
WHERE tl.request_session_id <> @@SPID;
"""

SLOW_QUERIES = """
SELECT TOP 10
    qs.total_elapsed_time / qs.execution_count / 1000 AS avg_elapsed_time_ms,
    qs.execution_count,
    SUBSTRING(st.text, (qs.statement_start_offset/2) + 1,
        ((CASE qs.statement_end_offset
          WHEN -1 THEN DATALENGTH(st.text)
         ELSE qs.statement_end_offset
         END - qs.statement_start_offset)/2) + 1) AS statement_text
FROM sys.dm_exec_query_stats AS qs
CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) AS st
ORDER BY avg_elapsed_time_ms DESC;
"""

DATABASES_PARA_ESCANEAR = """
SELECT name
FROM sys.databases
WHERE state_desc = 'ONLINE'
  AND database_id > 4
  AND name NOT IN ('distribution', 'ReportServer', 'ReportServerTempDB')
ORDER BY name;
"""

FRAGMENTED_INDEXES_LOCAL = """
SELECT
    s.name AS schema_name,
    t.name AS table_name,
    i.name AS index_name,
    ips.avg_fragmentation_in_percent
FROM sys.dm_db_index_physical_stats(DB_ID(), NULL, NULL, NULL, 'SAMPLED') AS ips
JOIN sys.indexes AS i ON ips.object_id = i.object_id AND ips.index_id = i.index_id
JOIN sys.tables t ON i.object_id = t.object_id
JOIN sys.schemas s ON t.schema_id = s.schema_id
WHERE ips.avg_fragmentation_in_percent > 30.0
  AND i.name IS NOT NULL
ORDER BY ips.avg_fragmentation_in_percent DESC;
"""
