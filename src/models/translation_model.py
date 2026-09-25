from typing import ClassVar

from transformers import MarianMTModel, MarianTokenizer


class TranslationModel:
    _model_cache: ClassVar[dict[str, "TranslationModel"]] = {}

    @classmethod
    def load_model(cls, model_name: str) -> "TranslationModel":
        if model_name not in cls._model_cache:
            tokenizer = MarianTokenizer.from_pretrained(model_name)
            model = MarianMTModel.from_pretrained(model_name)
            cls._model_cache[model_name] = cls(tokenizer, model)
        return cls._model_cache[model_name]

    def __init__(self, tokenizer: MarianTokenizer, model: MarianMTModel) -> None:
        self.tokenizer = tokenizer
        self.model = model
