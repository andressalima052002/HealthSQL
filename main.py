import logging
from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler

from core.config import carregar_config
from core.logger import setup_logging
from core.scheduler import rodar_health_check


def main():
    try:
        config = carregar_config()
    except Exception as e:
        print(f"Erro ao carregar config.ini: {e}")
        return

    setup_logging(nivel=config.nivel_log, diretorio="logs")
    logger = logging.getLogger(__name__)

    logger.info(
        "HealthSQL iniciado | %d instância(s) configurada(s) | intervalo: %d min",
        len(config.instancias), config.intervalo_minutos,
    )

    scheduler = BlockingScheduler()
    scheduler.add_job(
        rodar_health_check,
        trigger="interval",
        minutes=config.intervalo_minutos,
        args=[config],
        next_run_time=datetime.now(),
        max_instances=1,
        coalesce=True,
    )

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Encerrando HealthSQL...")


if __name__ == "__main__":
    main()
