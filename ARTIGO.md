🇧🇷 Português | [🇺🇸 English](ARTIGO.en-us.md)

# Um app Streamlit que prometia logs que nunca existiram

O README deste projeto dizia: "Logs user actions and errors to a log file (`log.txt`)." Não existia uma única linha de `import logging` no código. Esse tipo de gap — documentação descrevendo um comportamento que o código nunca teve — foi o fio condutor da produtização inteira: o app "funcionava" (rodava, traduzia, salvava em `translations.txt`), mas a distância entre o que ele dizia fazer e o que ele fazia de fato era grande demais pra eu assinar embaixo.

## O que eu tinha em mãos

Um app Streamlit de tradução multilíngue usando MarianMT (Hugging Face Transformers), com camadas razoavelmente separadas — `TranslationModel` (cache de modelo por nome), `TranslationService` (mapa de idiomas + chamada de inferência), `TextSanitizer` (regex), `FileStorage` (grava em `translations.txt`) — tudo orquestrado dentro do `main()` do Streamlit. Sem testes, sem CI, sem Docker, sem type hints, `requirements.txt` sem versão pinada, e nenhum log real apesar do que o README afirmava.

## O maior risco não era o código, era como testar sem baixar 2GB de pesos

`TranslationService.translate_text` baixa e roda modelos MarianMT reais via Hugging Face — cada par de idioma é um download de centenas de MB na primeira chamada. Testar isso "de verdade" a cada push do CI seria lento e frágil (depende de rede, de rate limit do Hugging Face Hub). Segui a mesma régua que já apliquei nos outros projetos: mockar quando a dependência é cara e não-determinística goes external; não mockar quando é rápida e determinística.

Então: `TextSanitizer` e `FileStorage` são testados contra a coisa real (regex e I/O de arquivo são baratos). `TranslationModel.load_model` e `TranslationService.translate_text` são testados com `unittest.mock.patch` no lugar de `MarianTokenizer`/`MarianMTModel`, verificando que o modelo certo é carregado e cacheado, e que o resultado do tokenizer é decodificado corretamente — sem nunca tocar a rede.

## Extraindo a lógica de dentro do `main()` do Streamlit

O `main()` original fazia sanitização, tradução, persistência e renderização de UI tudo junto, dentro de um `try/except` genérico. Isso é exatamente o tipo de código que não dá pra testar sem simular cliques em widgets Streamlit. Extraí a orquestração para uma função pura, `process_translation(text, language, logger)`, em `services/translation_workflow.py`:

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

`app.py` ficou reduzido a widgets do Streamlit chamando essa função e traduzindo o resultado (ou a `EmptyTextError`) em `st.success`/`st.warning`/`st.error`. É pouco código, não vale a pena testar diretamente — por isso `src/app.py` está excluído da cobertura (`[tool.coverage.run] omit`), o mesmo tratamento que dei ao wrapper `@bentoml.service` no projeto do Iris.

## Fechando o gap do README: logging de verdade

Adicionei `src/logger.py` (o mesmo padrão dos outros projetos da organização) e conectei no `process_translation` e no `except` do `app.py` (`logger.exception("Translation failed")`). Agora o que o README promete é o que o código faz.

## Empacotamento e o resto do padrão

`FileStorage.save_translation` ganhou um parâmetro `path` com default `"translations.txt"`, só pra poder testar com `tmp_path` sem escrever no repositório de verdade. Pinei `streamlit`, `transformers`, `sentencepiece` e `torch` em `config/requirements.txt`, gerei o lockfile com `uv pip compile` (limpo no `pip-audit`), e o Dockerfile ficou multi-stage com HEALTHCHECK no endpoint nativo do Streamlit (`/_stcore/health`) — usado tanto pelo Docker quanto pelo smoke test manual do `deploy.yaml`.

## O mesmo cuidado com o Trivy que aprendi nos outros dois projetos

Ao montar o pipeline Docker deste projeto eu já sabia de um problema que só descobri depois de produtizar os dois anteriores: o Trivy escaneia `pip/_vendor/msgpack` — uma cópia vendorizada que o próprio `pip` carrega para uso interno, não uma dependência real do projeto — e bloqueia o build por uma CVE que não é alcançável em tempo de execução. `skip-dirs: usr/local/lib/python*/site-packages/pip/_vendor` no step do Trivy evita esse falso positivo recorrente, aqui já configurado desde o primeiro commit.
