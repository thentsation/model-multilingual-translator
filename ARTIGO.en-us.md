[🇧🇷 Português](ARTIGO.md) | 🇺🇸 English

# A Streamlit app that promised logs that never existed

This project's README said: "Logs user actions and errors to a log file (`log.txt`)." There wasn't a single `import logging` anywhere in the code. That kind of gap — documentation describing behavior the code never had — became the throughline of the whole productization: the app "worked" (it ran, translated, saved to `translations.txt`), but the distance between what it claimed to do and what it actually did was too wide for me to sign off on.

## What I had

A multilingual translation Streamlit app using MarianMT (Hugging Face Transformers), with reasonably separated layers — `TranslationModel` (per-name model cache), `TranslationService` (language map + inference call), `TextSanitizer` (regex), `FileStorage` (writes to `translations.txt`) — all orchestrated inside the Streamlit `main()`. No tests, no CI, no Docker, no type hints, an unpinned `requirements.txt`, and no real logging despite what the README claimed.

## The real risk wasn't the code, it was how to test it without downloading 2GB of weights

`TranslationService.translate_text` downloads and runs real MarianMT models via Hugging Face — each language pair is a hundreds-of-MB download on first call. Testing this "for real" on every CI push would be slow and flaky (depends on network, on Hugging Face Hub rate limits). I followed the same rule I've applied on the other projects: mock when the dependency is expensive and non-deterministic in reaching outside the process; don't mock when it's fast and deterministic.

So: `TextSanitizer` and `FileStorage` are tested against the real thing (regex and file I/O are cheap). `TranslationModel.load_model` and `TranslationService.translate_text` are tested with `unittest.mock.patch` in place of `MarianTokenizer`/`MarianMTModel`, verifying the right model gets loaded and cached, and that the tokenizer's output is decoded correctly — without ever touching the network.

## Pulling the logic out of Streamlit's `main()`

The original `main()` did sanitization, translation, persistence, and UI rendering all together, inside one broad `try/except`. That's exactly the kind of code you can't test without simulating widget clicks. I extracted the orchestration into a pure function, `process_translation(text, language, logger)`, in `services/translation_workflow.py`:

```python
def process_translation(text: str, language: str, logger=None) -> str:
    sanitized_text = TextSanitizer.sanitize_text(text)
    if not sanitized_text:
        raise EmptyTextError("Please enter a valid text to translate.")

    translated_text = TranslationService.translate_text(sanitized_text, language)
    FileStorage.save_translation(sanitized_text, translated_text, language)
    logger.info("Translated text (language: %s)", language)
    return translated_text
```

`app.py` is now reduced to Streamlit widgets calling this function and translating the result (or the `EmptyTextError`) into `st.success`/`st.warning`/`st.error`. It's little enough code that it isn't worth testing directly — which is why `src/app.py` is excluded from coverage (`[tool.coverage.run] omit`), the same treatment I gave the `@bentoml.service` wrapper in the Iris project.

## Closing the README gap: real logging

I added `src/logger.py` (the same pattern used across the other projects in the org) and wired it into `process_translation` and into `app.py`'s `except` block (`logger.exception("Translation failed")`). What the README promises is now what the code does.

## Packaging and the rest of the pattern

`FileStorage.save_translation` got a `path` parameter defaulting to `"translations.txt"`, just so it could be tested with `tmp_path` instead of writing into the real repo. I pinned `streamlit`, `transformers`, `sentencepiece`, and `torch` in `config/requirements.txt`, generated the lockfile with `uv pip compile` (clean per `pip-audit`), and the Dockerfile is multi-stage with a `HEALTHCHECK` against Streamlit's own health endpoint (`/_stcore/health`) — used both by Docker and by the manual smoke test in `deploy.yaml`.

## The same Trivy lesson learned from the other two projects

While putting together this project's Docker pipeline I already knew about a problem I'd only discovered after productizing the previous two: Trivy scans `pip/_vendor/msgpack` — a vendored copy `pip` carries for its own internal use, not a real project dependency — and blocks the build over a CVE that isn't reachable at runtime. `skip-dirs: usr/local/lib/python*/site-packages/pip/_vendor` on the Trivy step avoids this recurring false positive, already configured here from the very first commit.
