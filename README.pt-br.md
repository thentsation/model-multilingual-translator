# Multilingual Translator

[![Python CI](https://github.com/thentsation/model-multilingual-translator/actions/workflows/pipeline_python.yaml/badge.svg)](https://github.com/thentsation/model-multilingual-translator/actions/workflows/pipeline_python.yaml)
[![Docker CI/CD](https://github.com/thentsation/model-multilingual-translator/actions/workflows/pipeline_docker.yaml/badge.svg)](https://github.com/thentsation/model-multilingual-translator/actions/workflows/pipeline_docker.yaml)

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

O CI roda ruff, pytest (com piso de cobertura), mypy e pip-audit em todo push/PR, além de uma execução diária agendada. Imagens Docker são construídas, escaneadas com Trivy e publicadas no GHCR na `main`. O Dependabot mantém pip, imagem base do Docker e GitHub Actions atualizados, com bumps patch/minor mesclados automaticamente. Releases são versionados automaticamente com [python-semantic-release](https://python-semantic-release.readthedocs.io/).
