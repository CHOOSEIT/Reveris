from openaiAPI import query_openai
from agents.utils.agent_utils import AGENT_INTRODUCTION, extract_json_answer

def query_translation(language: str, text: str) -> str:
    """
    Translate the story to a different language.
    
    Args:
        language (str): The language to translate the story to.

    Returns:
        str: The translated story
    """

    prompt = AGENT_INTRODUCTION + \
"""Translate in [LANGUAGE]

[TEXT]

You answer must contains a single JSON object in the following format:
{
    "translated_text": "Translated text",
}
Make sure to have your answer in the JSON format.
""".replace("[LANGUAGE]", language).replace("[TEXT]", text)

    messages = [
        {"role": "system", "content": prompt},
    ]

    answer = query_openai(messages)
    json_answer = extract_json_answer(answer)
    if json_answer is None:
        return None
    else:
        return json_answer["translated_text"]

    

