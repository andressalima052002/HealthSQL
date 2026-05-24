# main.py
import configparser
from agent.extractor import Extractor
from ai.analyzer import AIAnalyzer

def main():
    config = configparser.ConfigParser()
    config.read('config.ini')

    # --- Etapa 1: Extração de Dados ---
    try:
        sql_config = config['SQL_SERVER']
        extractor = Extractor(
            server=sql_config['SERVER'],
            database=sql_config['DATABASE'],
            username=sql_config['USERNAME'],
            password=sql_config['PASSWORD']
        )
        extractor.connect()
        health_data = extractor.extract_all_data()
        extractor.save_data_to_json(health_data)
        extractor.close()
    except Exception as e:
        print(f"Falha na etapa de extração de dados: {e}")
        return

    # --- Etapa 2: Análise com IA ---
    try:
        ai_config = config['GEMINI_API']
        analyzer = AIAnalyzer(api_key=ai_config['API_KEY'])
        analysis_result = analyzer.analyze_health_report()

        print("\n--- RELATÓRIO DE SAÚDE DO BANCO DE DADOS ---\n")
        print(analysis_result)
    except Exception as e:
        print(f"Falha na etapa de análise com IA: {e}")

if __name__ == "__main__":
    main()