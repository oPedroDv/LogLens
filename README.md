# LogLens 🔍

Aplicação Python para ingestão, parsing e análise inteligente de arquivos de log, com geração automática de relatórios e exposição via API REST.

## Visão geral

O LogLens recebe arquivos de log em texto puro, interpreta seu conteúdo (timestamps, níveis, origens, mensagens), extrai estatísticas e padrões, gera insights automáticos sobre o comportamento do sistema analisado, e produz relatórios em Markdown e PDF — tudo exposto através de uma API construída com FastAPI.

### Funcionalidades planejadas

- [x] Upload de arquivos de log com deduplicação por hash de conteúdo
- [ ] Parsing de logs genéricos (timestamp, nível, origem, mensagem)
- [ ] Estatísticas: distribuição por nível, frequência temporal, top origens de erro
- [ ] Agrupamento de erros similares (clustering)
- [ ] Geração automática de insights textuais
- [ ] Relatórios em Markdown
- [ ] Relatórios em PDF
- [ ] API REST completa (upload, análise, relatórios)

## Arquitetura

Monolito modular — um único deployable, mas com fronteiras internas claras entre camadas, preparado para eventual extração de serviços caso o projeto cresça.

```
loglens/
    app/
        main.py                  # ponto de entrada da aplicação FastAPI
        core/
            config.py            # configurações centralizadas (pydantic-settings)
            database.py          # engine, session factory e dependency get_db()
            logging.py           # configuração de logging da aplicação
        api/
            router.py            # agregador de todas as rotas
            routes/
                upload.py         # POST /upload — recebe e persiste arquivos de log
                analysis.py       # rotas de análise de logs
                reports.py        # rotas de geração/download de relatórios
        analysis/
            parser.py            # interpreta linhas de log em LogEntry
            statistics.py        # cálculo de métricas agregadas
            clustering.py        # agrupamento de eventos/erros similares
            insights.py          # geração de conclusões automáticas
            timeline.py          # análise temporal (picos, frequência)
        storage/
            models.py            # modelos SQLAlchemy (LogFile, AnalysisRecord)
            queries.py            # repository pattern — toda lógica de acesso ao banco
        reports/
            markdown.py           # geração de relatório .md
            pdf.py                # geração de relatório .pdf
        schemas/
            request.py            # contratos Pydantic de entrada da API
            response.py           # contratos Pydantic de saída da API
        types/
            log_entry.py          # tipo interno: uma linha de log interpretada
            analysis_result.py    # tipo interno: resultado agregado de uma análise
        utils/
            datetime.py           # helpers de parsing/formatação de datas
            hashing.py             # cálculo de hash SHA-256 (deduplicação)
```

### Princípios de design

- **Separação tipos internos vs schemas de API**: `types/` (dataclasses) representa o domínio interno da aplicação; `schemas/` (Pydantic) representa o contrato público da API. Um nunca é exposto diretamente no lugar do outro.
- **Repository pattern**: toda query SQL vive em `storage/queries.py`. Rotas nunca acessam o banco diretamente — apenas chamam funções do repository.
- **Configuração centralizada**: nenhum valor de configuração (limites, paths, URLs) é hardcoded fora de `core/config.py`.
- **Idempotência de upload**: arquivos com conteúdo idêntico (mesmo hash SHA-256) não são duplicados — a API retorna o registro já existente.

## Stack

- **Python 3.11+**
- **FastAPI** — framework web assíncrono
- **SQLAlchemy 2.0** — ORM, com SQLite como banco de dados
- **Pydantic v2 / pydantic-settings** — validação de dados e configuração

## Como rodar

```bash
# Instalar dependências
pip install -r requirements.txt

# Rodar a aplicação
uvicorn app.main:app --reload

# Documentação interativa da API
# http://localhost:8000/docs
```

## Status do projeto

Em desenvolvimento ativo, como projeto de estudo de FastAPI, SQLAlchemy e arquitetura de aplicações Python. Construído incrementalmente, camada por camada, com foco em entender o "porquê" de cada decisão técnica — não apenas o "como".

---

*Projeto pessoal de aprendizado.*
