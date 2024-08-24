import os

from dotenv import load_dotenv
from openai import OpenAI
from random import randint

load_dotenv()

###############################################################################################
# openAI
###############################################################################################

_openai_key = os.environ.get("OPENAI_KEY")
_openai_model = "gpt-4o-mini-2024-07-18"
_openai_client = OpenAI(api_key=_openai_key)
_openai_model_tts = "tts-1"
_price_per_token = {"prompt": 0.00000015, "completion": 0.0000006, "text_to_speech_per_character": 0.000015}


###############################################################################################
# Query OpenAI Chat
###############################################################################################
def query_openai(messages: list, temperature=0.0) -> str:
    """
    Query the OpenAI API with the current conversation.

    Args:
        messages (dict): The message history to query
        temperature (float): The temperature to use for the query (0 to 2 range)
        output_format (class): The output format to use for the query
    """
    response: dict = _openai_client.chat.completions.create(
        messages=messages,
        model=_openai_model,
        temperature=temperature,
        seed=randint(0, 1000000),
    ).model_dump()

    # Save usage
    openai_add_usage(response["usage"])

    return response["choices"][0]["message"]["content"]

###############################################################################################
# Query OpenAI Text to Speech
###############################################################################################

def query_openai_tts(text: str, filename: str):
    """
    Query the OpenAI API with the current conversation.

    Args:
        text (str): The text to convert to speech
    """
    openai_add_text_to_speech_usage(len(text))

    with _openai_client.audio.speech.with_streaming_response.create(
        model=_openai_model_tts,
        voice="nova",
        input=text,
    ) as response:
        response.stream_to_file(filename)
    print("Text to speech saved to {}".format(filename))

###############################################################################################
# OpenAI Usage
###############################################################################################
_usage_dict = {"total_input_tokens": 0, "total_output_tokens": 0, "text_to_speech_characters": 0, "estimated_cost": 0.0}
def openai_add_usage(usage: dict) -> None:
    _usage_dict["total_input_tokens"] += usage["prompt_tokens"]
    _usage_dict["total_output_tokens"] += usage["completion_tokens"]
    _usage_dict["estimated_cost"] += (usage["prompt_tokens"] * _price_per_token["prompt"] +
                                     usage["completion_tokens"] * _price_per_token["completion"])

def openai_add_text_to_speech_usage(characters_number: int) -> None:
    _usage_dict["text_to_speech_characters"] += characters_number
    _usage_dict["estimated_cost"] += characters_number * _price_per_token["text_to_speech_per_character"]

def openai_show_usage() -> None:
    print("############################################")
    print("OpenAI Usage:")
    print("Total input tokens: {}".format(_usage_dict["total_input_tokens"]))
    print("Total output tokens: {}".format(_usage_dict["total_output_tokens"]))
    print("Text to speech characters: {}".format(_usage_dict["text_to_speech_characters"]))
    print("Estimated cost: ${}".format(_usage_dict["estimated_cost"]))
    print("############################################")