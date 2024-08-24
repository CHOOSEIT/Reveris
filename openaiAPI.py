import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

###############################################################################################
# openAI
###############################################################################################

_openai_key = os.environ.get("OPENAI_KEY")
_openai_model = "gpt-4o-mini-2024-07-18"
_openai_client = OpenAI(api_key=_openai_key)
_price_per_token = {"prompt": 0.00000015, "completion": 0.0000006}

###############################################################################################
# Query OpenAI Chat
###############################################################################################
_usage_dict = {"total_input_tokens": 0, "total_output_tokens": 0, "estimated_cost": 0.0}

def query_openai_with_history(messages: list, temperature=0.0) -> str:
    """
    Query the OpenAI API with the current conversation.

    Args:
        messages (dict): The message history to query
        temperature (float): The temperature to use for the query (0 to 2 range)
    """
    response: dict = _openai_client.chat.completions.create(
        messages=messages,
        model=_openai_model,
        temperature=temperature,
    ).model_dump()

    # Save usage
    openai_add_usage(response["usage"])

    return response["choices"][0]["message"]["content"]

def openai_add_usage(usage: dict) -> None:
    _usage_dict["total_input_tokens"] += usage["prompt_tokens"]
    _usage_dict["total_output_tokens"] += usage["completion_tokens"]
    _usage_dict["estimated_cost"] += (usage["prompt_tokens"] * _price_per_token["prompt"] +
                                     usage["completion_tokens"] * _price_per_token["completion"])

def openai_show_usage() -> None:
    print("############################################")
    print("OpenAI Usage:")
    print("Total input tokens: {}".format(_usage_dict["total_input_tokens"]))
    print("Total output tokens: {}".format(_usage_dict["total_output_tokens"]))
    print("Estimated cost: ${}".format(_usage_dict["estimated_cost"]))
    print("############################################")