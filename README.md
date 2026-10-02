# Multilingual Translator

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

CI and deploy run on the platform's Jenkins (`Jenkinsfile` → `appPipeline` from the `platform` Shared Library, repo devops-platform), triggered by webhooks; there are no GitHub Actions.

- **PRs and branches** — contract validation; `docker build --target test` (`ruff check`, `ruff format --check`, `mypy`, `pytest` with ≥90% coverage on Python 3.11 and 3.12, tool versions from `config/requirements-dev.txt`); `pip-audit` on `config/requirements.lock`; Trivy (CRITICAL/HIGH) on the runtime image.
- **main** — all of the above, then build, smoke test, push to OCIR, deploy behind Traefik at https://translator.137-131-175-7.sslip.io with automatic rollback, release with python-semantic-release (version, CHANGELOG, tag and GitHub release) and a rebuild of the portfolio. Also rebuilt every Monday to pick up security patches.
- **Dependencies** — Renovate (Jenkins job `platform/renovate`, `renovate.json` → devops-platform preset): daily updates, weekly lockfile maintenance, Dependency Dashboard issue and auto-merge of patch/minor after Jenkins passes.
