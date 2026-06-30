# HealthSQL

Agente inteligente em Python para analisar a saude de um SQL Server local, calcular um score tecnico e enviar as metricas para o Grok gerar diagnostico e recomendacoes.

O projeto foi pensado como piloto local: voce valida/acessa o banco pelo SQL Server Management Studio, e o Python se conecta ao mesmo servidor para automatizar a coleta.

## O que o agente analisa

- Status do banco
- Status do backup full
- Erro recente de backup
- Locks ativos
- Sessoes bloqueadas
- Indices fragmentados
- Queries lentas
- Score final
- Diagnostico no console com IA generativa Grok

## Estrutura

```text
sql_health_ai/
  config.py
  db_connection.py
  collectors.py
  score_engine.py
  ai_analyzer.py
  console_report.py
main.py
requirements.txt
.env.example
```

## Como configurar

1. Crie e ative um ambiente virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Instale as dependencias:

```powershell
pip install -r requirements.txt
```

3. Copie `.env.example` para `.env`:

```powershell
Copy-Item .env.example .env
```

4. No `.env`, preencha os dados do SQL Server que voce usa no SSMS.

Exemplos comuns:

```env
SQL_SERVER=localhost
SQL_DATABASE=master
```

```env
SQL_SERVER=localhost\SQLEXPRESS
SQL_DATABASE=SeuBanco
```

```env
SQL_SERVER=(localdb)\MSSQLLocalDB
SQL_DATABASE=SeuBanco
```

Para autenticacao Windows, deixe vazio:

```env
SQL_USERNAME=
SQL_PASSWORD=
```

Para autenticacao SQL Server, preencha:

```env
SQL_USERNAME=sa
SQL_PASSWORD=sua_senha
```

5. Configure o Grok:

```env
XAI_API_KEY=sua_chave_xai
XAI_BASE_URL=https://api.x.ai/v1
GROK_MODEL=grok-4.3
```

## Como executar

Modo demonstracao, sem conectar no SQL Server:

```powershell
$env:USE_MOCK_DATA="true"
python main.py
```

Modo real, conectado ao SQL Server local:

```powershell
$env:USE_MOCK_DATA="false"
python main.py
```

## Permissoes recomendadas no SQL Server

O usuario usado pelo Python precisa conseguir consultar metadados, `msdb` e DMVs:

- `VIEW SERVER STATE`
- Leitura em `msdb.dbo.backupset`
- Leitura em `msdb.dbo.sysjobhistory`

Para piloto local, se voce estiver usando uma conta administradora no SQL Server, provavelmente ja tera essas permissoes.

## Observacao

O SQL Server Management Studio nao executa o agente. Ele serve para voce acessar o banco, conferir o nome do servidor e validar queries. A automacao fica no Python.
