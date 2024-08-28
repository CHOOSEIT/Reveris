import os
import deepl

from dotenv import load_dotenv

load_dotenv()

_deepl_key = os.environ.get("DEEPL_KEY")
_deepl_client = deepl.Translator(_deepl_key)


def query_translation(text: str, target_lang: str) -> str:
    """
    Query the DeepL API to translate text.

    Args:
        text (str): The text to translate
        target_lang (str): The target language to translate to
    """
    response = _deepl_client.translate_text(
        text, target_lang=target_lang, source_lang="EN"
    )
    return response.text
