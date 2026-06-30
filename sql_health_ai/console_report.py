from __future__ import annotations

import json

from sql_health_ai.collectors import HealthMetrics
from sql_health_ai.score_engine import ScoreResult


def print_report(metrics: HealthMetrics, score: ScoreResult, ai_analysis: str) -> None:
    print("=" * 55)
    print("SQL SERVER INTELLIGENT HEALTH CHECK")
    print("=" * 55)
    print(f"Banco analisado: {metrics.database_name}")
    print(f"Status do banco: {metrics.database_status}")
    print(f"Modelo de recovery: {metrics.recovery_model}")
    print(f"Ultimo backup full: {metrics.last_backup_finish or 'nao encontrado'}")
    print(f"Horas desde o backup: {_format_number(metrics.last_backup_hours)}")
    print(f"Erro de backup: {'sim' if metrics.backup_error else 'nao'}")
    print(f"Locks ativos: {metrics.active_locks}")
    print(f"Sessoes bloqueadas: {metrics.blocking_sessions}")
    print(f"Indices fragmentados: {metrics.fragmented_indexes}")
    print(f"Maior fragmentacao: {metrics.max_fragmentation_percent:.2f}%")
    print(f"Queries lentas: {metrics.slow_queries}")
    print(f"Query mais lenta media: {metrics.slowest_query_ms:.2f} ms")
    print("-" * 55)
    print(f"Score Geral: {score.score}/100")
    print(f"Classificacao: {score.classification}")
    print("-" * 55)
    print("Problemas Detectados:")
    if score.penalties:
        for penalty in score.penalties:
            print(f"- {penalty}")
    else:
        print("- Nenhum problema critico detectado")
    print("-" * 55)
    print("Payload enviado para IA:")
    print(json.dumps({"metrics": metrics.to_dict(), "score": score.__dict__}, ensure_ascii=False, indent=2))
    print("-" * 55)
    print("Diagnostico da IA - Grok:")
    print(ai_analysis)
    print("=" * 55)


def _format_number(value: float | None) -> str:
    if value is None:
        return "nao encontrado"
    return f"{value:.2f}"
