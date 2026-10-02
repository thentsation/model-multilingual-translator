# Multilingual Translator

> Read in [English](README.md).

Um app Streamlit que traduz texto entre inglês, espanhol, francês e alemão usando modelos pré-treinados [Helsinki-NLP MarianMT](https://huggingface.co/Helsinki-NLP) da biblioteca Transformers da Hugging Face.

Um artigo detalhado sobre a produtização deste projeto está disponível em [ARTIGO.md](ARTIGO.md) (pt-br) / [ARTIGO.en-us.md](ARTIGO.en-us.md) (en-us).

## Funcionalidades

- Tradução entre inglês↔espanhol, inglês↔francês, inglês↔alemão.
- Salva cada tradução em `translations.txt`.
- Loga a atividade de tradução (e falhas) via o módulo `logging` padrão.
- Permite que o usuário indique se a tradução foi útil.

## Estrutura do projeto

```text
src/
├── app.py                        # UI Streamlit fina, sem teste unitário direto (excluída da cobertura)
├── logger.py
├── models/translation_model.py    # carregamento do MarianMT + cache em processo
├── services/
│   ├── text_sanitizer.py
│   ├── translation_service.py     # idiomas suportados + chamada de inferência
│   └── translation_workflow.py    # sanitiza -> traduz -> persiste, usado pelo app.py e testado direto
└── storage/file_storage.py
```

`app.py` só conecta os widgets do Streamlit ao `translation_workflow.process_translation`, que é o que realmente é testado — rodar modelos de tradução de verdade no CI significaria baixar gigabytes de pesos do PyTorch a cada execução, então os testes de `translation_service`/`translation_model` mockam as chamadas à Hugging Face.

## Como rodar

```bash
make install    # cria o .venv e instala as deps (torch + transformers, demora um pouco)
make run        # streamlit run src/app.py
```

Rodando com Docker:

```bash
make docker-build
make docker-run
```

## Desenvolvimento

```bash
make test        # pytest
make coverage     # pytest com relatório de cobertura
make lint         # ruff check
make format       # ruff format
make typecheck    # mypy
```

CI e deploy rodam no Jenkins da plataforma (`Jenkinsfile` → `appPipeline` da Shared Library `platform`, repo devops-platform), disparados por webhooks. Sem GitHub Actions.

- **PRs e branches** — validação do contrato; `docker build --target test` (`ruff check`, `ruff format --check`, `mypy`, `pytest` com cobertura ≥90% em Python 3.11 e 3.12, versões das ferramentas no `config/requirements-dev.txt`); `pip-audit` no `config/requirements.lock`; Trivy (CRITICAL/HIGH) na imagem de runtime.
- **main** — tudo acima e depois build, smoke test, push para o OCIR, deploy atrás do Traefik em https://translator.137-131-175-7.sslip.io com rollback automático, release com o python-semantic-release (versão, CHANGELOG, tag e release no GitHub) e rebuild do portfolio. Também é reconstruída toda segunda para pegar patches de segurança.
- **Dependências** — Renovate (job `platform/renovate` no Jenkins, `renovate.json` → preset do devops-platform): atualizações diárias, manutenção semanal do lockfile, issue "Dependency Dashboard" e auto-merge de patch/minor depois que o Jenkins aprova.
