import os

from openaiAPI import query_openai_tts
from agents.utils.translateAgent import query_translation

def query_readme(text: str, id: str):
    """
    Read the story.
    """
    translated_text = query_translation("French", text)

    filename = os.path.join("out", f"readme_{id}.mp3")
    os.makedirs("out", exist_ok=True)

    query_openai_tts(text=translated_text, filename=filename)
    