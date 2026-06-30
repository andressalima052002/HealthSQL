from dataclasses import dataclass

from sql_health_ai.collectors import HealthMetrics


@dataclass
class ScoreResult:
    score: int
    classification: str
    penalties: list[str]


def calculate_score(metrics: HealthMetrics) -> ScoreResult:
    score = 100
    penalties: list[str] = []

    if metrics.database_status.upper() != "ONLINE":
        score -= 40
        penalties.append("Banco de dados nao esta ONLINE")

    if metrics.last_backup_hours is None:
        score -= 35
        penalties.append("Nenhum backup full encontrado")
    elif metrics.last_backup_hours > 24:
        score -= 20
        penalties.append("Backup full acima de 24 horas")

    if metrics.backup_error:
        score -= 30
        penalties.append("Erro recente em job/historico de backup")

    if metrics.active_locks > 3:
        score -= 15
        penalties.append("Locks ativos acima do ideal")

    if metrics.blocking_sessions > 0:
        score -= 15
        penalties.append("Sessoes bloqueadas detectadas")

    if metrics.fragmented_indexes > 0:
        score -= 10
        penalties.append("Indices com fragmentacao acima de 30%")

    if metrics.slow_queries > 0:
        score -= 15
        penalties.append("Queries lentas detectadas")

    score = max(score, 0)
    return ScoreResult(
        score=score,
        classification=_classify(score),
        penalties=penalties,
    )


def _classify(score: int) -> str:
    if score >= 90:
        return "Saudavel"
    if score >= 70:
        return "Risco Moderado"
    if score >= 50:
        return "Risco Alto"
    return "Critico"
