from __future__ import annotations

import json
from typing import Any

from openai import OpenAI


SYSTEM_PROMPT = """
Voce e um agente especialista em SQL Server e saude de banco de dados.
Analise as metricas recebidas e responda em portugues do Brasil.
Seja pratico: informe classificacao de risco, causas provaveis e acoes recomendadas.
Nao invente dados que nao estejam no JSON.
"""


def analyze_with_grok(payload: dict[str, Any], api_key: str | None, base_url: str, model: str) -> str:
    if not api_key:
        return (
            "Analise por IA nao executada: configure XAI_API_KEY no arquivo .env "
            "para habilitar o diagnostico generativo com Grok."
        )

    client = OpenAI(api_key=api_key, base_url=base_url)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT.strip()},
            {
                "role": "user",
                "content": (
                    "Analise este health check de SQL Server e retorne diagnostico "
                    "e recomendacoes objetivas:\n"
                    f"{json.dumps(payload, ensure_ascii=False, indent=2)}"
                ),
            },
        ],
        temperature=0.2,
    )
    content = response.choices[0].message.content
    return content.strip() if content else "O Grok nao retornou conteudo para a analise."
