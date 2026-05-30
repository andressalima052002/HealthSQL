# HealthSQL

**HealthSQL** é um projeto Python que coleta métricas de saúde de uma ou mais instâncias **SQL Server** e usa **Inteligência Artificial local (Ollama)** para gerar relatórios com diagnóstico, recomendações e um score de saúde — sem custo de API e sem enviar dados para fora.

O script roda como um serviço (loop com APScheduler) e gera relatórios periódicos em arquivo (JSON bruto + análise em Markdown).

## Métricas analisadas

- **Status dos bancos** — todos os databases estão online?
- **Status de backup** — data e tipo do último backup por banco.
- **Locks ativos** — sessões com locks no servidor.
- **Índices fragmentados** — varredura em todos os bancos online, lista índices com fragmentação >30%.
- **Queries lentas** — top 10 mais lentas via DMVs.
- **Score de saúde** — pontuação 0-100% calculada pela IA com base nos dados acima.

## Pré-requisitos

- **Python 3.10+**
- **Ollama** instalado e rodando ([ollama.com](https://ollama.com))
- **Microsoft ODBC Driver 17 for SQL Server** instalado no host onde o script vai rodar
- Pelo menos uma instância SQL Server acessível com credenciais de leitura

### Permissões SQL mínimas

O usuário configurado precisa de:
- `VIEW SERVER STATE` (para DMVs como `sys.dm_tran_locks`, `sys.dm_exec_query_stats`)
- `VIEW ANY DEFINITION`
- Acesso de leitura aos bancos a serem escaneados (para `sys.dm_db_index_physical_stats`)

Em ambiente de dev, `sysadmin` resolve. Em produção, use uma role customizada com só esses privilégios.

## Setup

### 1. Ollama

```bash
ollama serve              # deixa rodando em uma janela
ollama pull mistral:7b    # baixa o modelo (~4GB, só na primeira vez)
ollama run mistral:7b "diga oi"   # sanity check
```

> Pode trocar `mistral:7b` por `llama3.1:8b`, `qwen2.5:14b` ou outro modelo — basta ajustar em `config.ini`.

### 2. Ambiente Python

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Configuração

```bash
cp config.ini.example config.ini    # ou copie manualmente no Windows
```

Edite `config.ini` e preencha:
- `[GLOBAL]` — intervalo, diretório de relatórios, nível de log.
- `[OLLAMA]` — host, modelo, timeout.
- Uma ou mais seções `[SQL_SERVER:<apelido>]` — uma por instância monitorada. O `<apelido>` vira o nome da subpasta em `reports/`.

> ⚠️ `config.ini` está no `.gitignore` — não vai pro repositório. Senhas ficam locais.

## Como executar

```bash
python main.py
```

O script:
1. Roda a primeira coleta imediatamente.
2. Repete a cada `intervalo_minutos` (default: 60).
3. Mantém o processo vivo até `Ctrl+C`.

## Saída

```
reports/
└── <apelido_da_instancia>/
    ├── health_20260530_140000.json    ← dados brutos coletados
    ├── analysis_20260530_140000.md    ← análise da IA com score
    └── ...
logs/
└── healthsql.log                       ← log do scheduler (rotativo, 5MB x 10)
```

Se a IA falhar (ex: Ollama caiu), o JSON bruto é preservado mesmo assim.
Se uma instância falhar (ex: conexão recusada), as outras continuam sendo processadas.

## Estrutura do projeto

```
HealthSQL/
├── agent/        # extração de dados do SQL Server
├── ai/           # integração com Ollama
├── core/         # config, logger, scheduler
├── reports/      # relatórios gerados (gitignored)
├── logs/         # logs do app (gitignored)
├── main.py       # entrypoint
└── config.ini    # configuração (gitignored)
```

## Roadmap (fases futuras)

- Integração com Zabbix (zabbix_sender ou External Check)
- Suporte a Windows Authentication
- Limpeza automática de relatórios antigos
- Métricas adicionais (CPU, memória, wait stats, deadlocks)
- Dashboard web e notificações (email/Slack) por score baixo
- Migração para Cortex
