import json
import logging

import ollama

logger = logging.getLogger(__name__)


class AIAnalyzer:
    def __init__(self, host, modelo, timeout):
        self.host = host
        self.modelo = modelo
        self.timeout = timeout
        try:
            self.client = ollama.Client(host=host, timeout=timeout)
            self.client.list()
            logger.info("Conexão com Ollama (%s) OK — modelo configurado: %s", host, modelo)
        except Exception as e:
            logger.error(
                "Falha ao conectar no Ollama (%s). Verifique se 'ollama serve' está rodando "
                "e se o modelo '%s' foi baixado ('ollama pull %s'). Erro: %s",
                host, modelo, modelo, e,
            )
            raise

    def _build_prompt(self, health_data_json, apelido_instancia):
        return f"""
Você é um DBA Sênior especialista em SQL Server, encarregado de analisar um relatório
de saúde da instância **{apelido_instancia}**.
Sua tarefa é interpretar os dados brutos em formato JSON, identificar problemas,
fornecer recomendações claras e calcular um "Score de Saúde" de 0 a 100.

**Instruções para Análise:**
1.  **Resumo Geral:** Comece com uma visão geral do estado do banco de dados.
2.  **Pontos de Atenção:** Detalhe cada problema encontrado nas seções a seguir:
    - `database_status`: Verifique se todos os bancos de dados estão 'ONLINE'.
    - `backup_status`: Verifique se os backups (especialmente do tipo 'D' - Full) são recentes (últimas 24-30 horas). Aponte bancos sem backup recente.
    - `active_locks`: Aponte se existem locks ativos. Locks não são inerentemente ruins, mas locks de longa duração ou em grande quantidade podem indicar problemas.
    - `fragmented_indexes`: Liste os índices com fragmentação acima de 30% e o perigo que isso representa (lentidão em leituras).
    - `slow_queries`: Liste as queries mais lentas e explique por que elas podem ser um problema (alto consumo de CPU/memória, I/O intensivo).
3.  **Recomendações Práticas:** Para cada problema, forneça uma solução.
    - Ex: Para índices fragmentados, sugira `ALTER INDEX ... REBUILD` ou `REORGANIZE`.
    - Ex: Para queries lentas, sugira analisar o plano de execução, criar índices ou reescrever a query.
4.  **Score de Saúde (0-100%):** Calcule uma pontuação. Comece em 100% e deduza pontos com base na gravidade e quantidade dos problemas. Justifique sua pontuação.
    - Exemplo de dedução:
        - Banco de dados não-ONLINE: -40 pontos por banco.
        - Backup full com mais de 24h: -15 pontos por banco.
        - Cada índice muito fragmentado (>70%): -5 pontos.
        - Cada query no top 10 de lentidão: -3 pontos.
        - Presença de locks: -5 pontos (apenas como um alerta).

**Formato da Saída:**
Use markdown válido para formatar a resposta, com títulos para cada seção.

**Dados para Análise:**
```json
{health_data_json}
```
"""

    def analisar_relatorio(self, health_data, apelido_instancia):
        prompt = self._build_prompt(
            json.dumps(health_data, indent=2, ensure_ascii=False, default=str),
            apelido_instancia,
        )
        logger.info("Enviando dados de %s para análise da IA (modelo %s)", apelido_instancia, self.modelo)
        resposta = self.client.chat(
            model=self.modelo,
            messages=[{"role": "user", "content": prompt}],
        )
        return resposta["message"]["content"]
