from sql_health_ai.ai_analyzer import analyze_with_grok
from sql_health_ai.collectors import SqlServerCollector, mock_metrics
from sql_health_ai.config import load_config
from sql_health_ai.console_report import print_report
from sql_health_ai.db_connection import get_connection
from sql_health_ai.score_engine import calculate_score


def main() -> None:
    config = load_config()

    if config.use_mock_data:
        metrics = mock_metrics()
    else:
        with get_connection(config) as connection:
            collector = SqlServerCollector(connection, config.sql_database)
            metrics = collector.collect()

    score = calculate_score(metrics)
    payload = {
        "metrics": metrics.to_dict(),
        "score": score.__dict__,
    }
    ai_analysis = analyze_with_grok(
        payload,
        api_key=config.xai_api_key,
        base_url=config.xai_base_url,
        model=config.grok_model,
    )
    print_report(metrics, score, ai_analysis)


if __name__ == "__main__":
    main()
