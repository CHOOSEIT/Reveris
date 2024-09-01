import os
import io, base64
import random
import string
import time

from dotenv import load_dotenv
from openai import OpenAI
from random import randint
from PIL import Image
from threading import Lock

load_dotenv()

###############################################################################################
# openAI
###############################################################################################

_openai_key = os.environ.get("OPENAI_KEY")
_openai_model = "gpt-4o-mini-2024-07-18"
_openai_client = OpenAI(api_key=_openai_key)
_openai_model_tts = "tts-1"
_openai_model_image_model = "dall-e-3"
_openai_model_image_resolution = "1792x1024"
_openai_model_image_quality = "hd"
_api_prices = {
    "per_token_input": 0.00000015,
    "per_token_output": 0.0000006,
    "text_to_speech_per_character": 0.000015,
    "image_generation": 0.120,
}
# Allow multi-threading calls
API_MAX_BATCH_IMAGES = 5
API_MAX_BATCH_SPEECHES = 5
API_BATCH_DELAY = 60  # seconds
# Add a delay to API request to avoid rate limiting
# (+ recommended: set API_MAX_BATCH_IMAGES and API_MAX_BATCH_SPEECHES to 1)
_api_request_delay = 0  # seconds


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
    time.sleep(_api_request_delay)
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

speech_dir_checking_lock = Lock()


def query_openai_tts(text: str, working_folder: str = "out") -> str:
    """
    Query the OpenAI API with the current conversation.

    Args:
        text (str): The text to convert to speech
        working_folder (str): The working folder to save the speech
    """
    time.sleep(_api_request_delay)
    openai_add_text_to_speech_usage(len(text))

    filename = (
        f"{working_folder}/tts_"
        + "".join(random.choices(string.ascii_letters + string.digits, k=6))
        + ".mp3"
    )

    with speech_dir_checking_lock:
        os.makedirs(os.path.dirname(filename), exist_ok=True)

    with _openai_client.audio.speech.with_streaming_response.create(
        model=_openai_model_tts,
        voice="nova",
        input=text,
    ) as response:
        response.stream_to_file(filename)
    print("Text to speech saved to {}".format(filename))

    return filename


###############################################################################################
# Query OpenAI Image Generation
###############################################################################################

image_dir_checking_lock = Lock()


def query_openai_image_generation(
    prompt: str, style="vivid", working_folder: str = "out"
) -> str:
    """
    Generate an image using the OpenAI API.

    Args:
        prompt (str): The prompt to generate the image
        style (str): The style of the image (standard or vivid)
        working_folder (str): The working folder to save the image

    Returns:
        str: file path of the generated image
    """
    if prompt is None:
        return None

    time.sleep(_api_request_delay)
    response = _openai_client.images.generate(
        model=_openai_model_image_model,
        prompt=prompt,
        size=_openai_model_image_resolution,
        quality=_openai_model_image_quality,
        style=style,
        response_format="b64_json",
        n=1,
    )
    openai_add_image_generation(1)

    image_obj = response.data[0].b64_json
    image_obj = Image.open(io.BytesIO(base64.b64decode(image_obj)))

    filename = (
        f"{working_folder}/"
        + "".join(random.choices(string.ascii_letters + string.digits, k=6))
        + ".jpg"
    )
    with image_dir_checking_lock:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
    image_obj.save(filename, quality=100, subsampling=0)
    print("Image saved to {}".format(filename))
    return filename


###############################################################################################
# OpenAI Usage
###############################################################################################
_usage_dict = {
    "total_input_tokens": 0,
    "total_output_tokens": 0,
    "text_to_speech_characters": 0,
    "generated_images": 0,
    "estimated_cost": 0.0,
}
chat_completion_lock = Lock()
text_to_speech_lock = Lock()
image_generation_lock = Lock()


def openai_add_usage(usage: dict) -> None:
    with chat_completion_lock:
        _usage_dict["total_input_tokens"] += usage["prompt_tokens"]
        _usage_dict["total_output_tokens"] += usage["completion_tokens"]
        _usage_dict["estimated_cost"] += (
            usage["prompt_tokens"] * _api_prices["per_token_input"]
            + usage["completion_tokens"] * _api_prices["per_token_output"]
        )


def openai_add_text_to_speech_usage(characters_number: int) -> None:
    with text_to_speech_lock:
        _usage_dict["text_to_speech_characters"] += characters_number
        _usage_dict["estimated_cost"] += (
            characters_number * _api_prices["text_to_speech_per_character"]
        )


def openai_add_image_generation(image_number: int) -> None:
    with image_generation_lock:
        _usage_dict["generated_images"] += image_number
        _usage_dict["estimated_cost"] += image_number * _api_prices["image_generation"]


def openai_show_usage() -> None:
    print("############################################")
    print("OpenAI Usage:")
    print("Total input tokens: {}".format(_usage_dict["total_input_tokens"]))
    print("Total output tokens: {}".format(_usage_dict["total_output_tokens"]))
    print(
        "Text to speech characters: {}".format(_usage_dict["text_to_speech_characters"])
    )
    print("Generated images: {}".format(_usage_dict["generated_images"]))
    print("Estimated cost: ${}".format(_usage_dict["estimated_cost"]))
    print("############################################")
