# Multilingual Translator

[![Python CI](https://github.com/thentsation/model-multilingual-translator/actions/workflows/pipeline_python.yaml/badge.svg)](https://github.com/thentsation/model-multilingual-translator/actions/workflows/pipeline_python.yaml)
[![Docker CI/CD](https://github.com/thentsation/model-multilingual-translator/actions/workflows/pipeline_docker.yaml/badge.svg)](https://github.com/thentsation/model-multilingual-translator/actions/workflows/pipeline_docker.yaml)

> Leia em [português](README.pt-br.md).

A Streamlit app that translates text between English, Spanish, French and German using pre-trained [Helsinki-NLP MarianMT](https://huggingface.co/Helsinki-NLP) models from Hugging Face's Transformers library.

An in-depth write-up of the productization of this project is available in [ARTIGO.md](ARTIGO.md) (pt-br) / [ARTIGO.en-us.md](ARTIGO.en-us.md) (en-us).

## Features

- Translation between English↔Spanish, English↔French, English↔German.
- Saves every translation to `translations.txt`.
- Logs translation activity (and failures) through the standard `logging` module.
- Lets the user flag whether a translation was helpful.

## Project structure

```text
src/
├── app.py                        # thin Streamlit UI, not unit-tested (excluded from coverage)
├── logger.py
├── models/translation_model.py    # MarianMT model loading + in-process cache
├── services/
│   ├── text_sanitizer.py
│   ├── translation_service.py     # supported languages + inference call
│   └── translation_workflow.py    # sanitize -> translate -> persist, used by app.py and tested directly
└── storage/file_storage.py
```

`app.py` only wires Streamlit widgets to `translation_workflow.process_translation`, which is what's actually tested — running real translation models in CI would mean downloading gigabytes of PyTorch weights per run, so `translation_service`/`translation_model` tests mock the Hugging Face calls instead.

## Getting started

```bash
make install    # creates .venv and installs deps (torch + transformers, this takes a while)
make run        # streamlit run src/app.py
```

Run with Docker instead:

```bash
make docker-build
make docker-run
```

## Development

```bash
make test        # pytest
make coverage     # pytest with coverage report
make lint         # ruff check
make format       # ruff format
make typecheck    # mypy
```

CI runs ruff, pytest (coverage gate), mypy and pip-audit on every push/PR, plus a scheduled daily run. Docker images are built, scanned with Trivy, and published to GHCR on `main`. Dependabot keeps pip, the Docker base image, and GitHub Actions up to date, with patch/minor bumps auto-merged. Releases are tagged automatically with [python-semantic-release](https://python-semantic-release.readthedocs.io/).
