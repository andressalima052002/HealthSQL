# HealthSQL

**HealthSQL** é um projeto que utiliza Python e Inteligência Artificial Generativa (Google Gemini) para realizar uma análise de saúde completa em bancos de dados SQL Server.

O sistema é composto por um agente que coleta métricas vitais do banco de dados e um analisador de IA que interpreta esses dados para fornecer insights, recomendações e um score de saúde.

## Métricas Analisadas

- **Status dos Bancos:** Verifica se todos os bancos de dados estão online.
- **Status de Backup:** Analisa a data e o tipo dos últimos backups realizados.
- **Locks Ativos:** Identifica sessões que estão causando travamentos no banco.
- **Índices Fragmentados:** Encontra índices com alta fragmentação que podem degradar a performance.
- **Queries Lentas:** Lista as consultas mais demoradas que consomem mais recursos.
- **Score Final:** Gera uma pontuação de 0 a 100% para representar a saúde geral do ambiente.

## Como Executar

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/seu-usuario/HealthSQL.git
    cd HealthSQL
    ```

2.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure as credenciais:**
    - Renomeie `config.ini.example` para `config.ini` (ou crie o arquivo).
    - Preencha as informações do seu servidor SQL Server e sua chave de API do Google AI Studio (Gemini).

4.  **Execute a análise:**
    ```bash
    python main.py
    ```

O resultado completo da análise será exibido no seu console.