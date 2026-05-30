import logging
from datetime import datetime
from pathlib import Path

from agent.extractor import Extractor
from ai.analyzer import AIAnalyzer

logger = logging.getLogger(__name__)


def processar_instancia(instancia, analyzer, config):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    dir_inst = Path(config.diretorio_relatorios) / instancia.apelido
    dir_inst.mkdir(parents=True, exist_ok=True)
    caminho_json = dir_inst / f"health_{ts}.json"
    caminho_md = dir_inst / f"analysis_{ts}.md"

    extractor = Extractor(
        server=instancia.server,
        database=instancia.database,
        username=instancia.username,
        password=instancia.password,
        driver=instancia.driver,
    )
    try:
        extractor.connect()
        health_data = extractor.extract_all_data()
        extractor.save_data_to_json(health_data, caminho_json)

        try:
            analise = analyzer.analisar_relatorio(health_data, instancia.apelido)
            caminho_md.write_text(analise, encoding="utf-8")
            logger.info("Análise IA salva em %s", caminho_md)
        except Exception as e:
            logger.error(
                "Falha na análise da IA para %s (JSON bruto preservado em %s): %s",
                instancia.apelido, caminho_json, e,
            )
    finally:
        extractor.close()


def rodar_health_check(config):
    logger.info("=== Iniciando ciclo de health-check (%d instâncias) ===", len(config.instancias))
    try:
        analyzer = AIAnalyzer(
            host=config.ollama_host,
            modelo=config.ollama_modelo,
            timeout=config.ollama_timeout,
        )
    except Exception as e:
        logger.error("Não foi possível inicializar o analyzer Ollama: %s", e)
        return

    for instancia in config.instancias:
        try:
            processar_instancia(instancia, analyzer, config)
        except Exception as e:
            logger.error(
                "Falha ao processar instância %s: %s", instancia.apelido, e, exc_info=True
            )
            continue

    logger.info("=== Ciclo concluído ===")
