import os

from openaiAPI import query_openai_tts


def query_speech(text: str, working_folder: str = "out") -> str:
    """
    Read the story.

    Args:
        text (str): the text to read

    Returns:
        str: the file path of the generated speech
    """
    return query_openai_tts(text=text, working_folder=working_folder)
