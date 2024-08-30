import re

from typing import Tuple, List
from agents.agent_utils import query_llm_with_feedback_json
from openaiAPI import query_openai_image_generation


def _get_valid_illustrations(
    text: str, illustrations: List[dict], JSON_FORMAT: str
) -> Tuple[list, str]:
    """
    Given a text and a list of illustrations, will return the list of valid illustrations that should be included in the story.

    Args:
        text (str): the text
        illustrations (list): the list of illustrations
        JSON_FORMAT (str): the JSON format for the illustrations

    Returns:
        list: the list of valid illustrations in the following format:
        [
            {
                "description": "Description for the illustration",
                "text": "Text reference that should be illustrated"
                "start_idx": "start index of the text reference",
                "end_idx": "end index of the text reference"
            },
            ...
        ]
        str: the message error if there is any
    """
    valid_matches = []
    error_message = ""
    for i, illustration in enumerate(illustrations):
        if (
            "description" not in illustration
            or "text_beginning" not in illustration
            or "text_end" not in illustration
        ):
            error_message += f"Requested illustration {i+1} is missing some keys. Please verify that your answer is in the right JSON format: {JSON_FORMAT} \n"
        else:
            start = illustration["text_beginning"]
            end = illustration["text_end"]
            pattern = rf"{re.escape(start)}.*?{re.escape(end)}"

            matches = [
                (match.start(), match.end(), match.group())
                for match in re.finditer(pattern, text, re.DOTALL | re.IGNORECASE)
            ]

            # Check if there are any matches
            if len(matches) == 0:
                error_message += f"Requested illustration {i+1} text reference does not match any part of the text ({str(illustration)}). Please provide in 'text_beginning' and 'text_end' the beginning and end of the text reference that should be illustrated respectively. \n"
            elif len(matches) > 1:
                error_message += f"Requested illustration {i+1} text reference is too broad and matches multiple parts of the text ({str(illustration)}). Please provide a more specific text reference. \n"
            else:

                # Check that there is no overlapping
                final_match = matches[0]

                for j, previous_match in enumerate(valid_matches):
                    start_idx = previous_match["start_idx"]
                    end_idx = previous_match["end_idx"]
                    if final_match[0] < end_idx and final_match[1] > start_idx:
                        error_message += f"Requested illustration {i+1} text reference overlaps with illustration {j+1}. Please provide a non-overlapping text reference or remove the illustration \n"

                if error_message == "":
                    valid_matches.append(
                        {
                            "description": illustration["description"],
                            "text": final_match[2],
                            "start_idx": final_match[0],
                            "end_idx": final_match[1],
                        }
                    )
    return valid_matches, error_message


def query_suggested_illustrations(text: str, max_illustrations: int = 2) -> List[dict]:
    """
    Given a text will return the list of illustrations that should be included in the story.

    Args:
        text (str): the text
        max_illustrations (int): the maximum number of illustrations

    Returns:
        list: the list of illustrations in the following format:
        [
            {
                "description": "Description for the illustration",
                "text": "Text reference that should be illustrated"
                "start_idx": "start index of the text reference",
                "end_idx": "end index of the text reference"
            },
            ...
        ]
    """
    JSON_FORMAT = """
{
    "illustrations": [
        {
            "description": "Description for the illustration",
            "text_beginning": "Beginning of the text reference",
            "text_end": "End of the text reference"
        },
        {
            "description": "Description for the illustration",
            "text_beginning": "Beginning of the text reference",
            "text_end": "End of the text reference"
        },
        ...
    ]

}
"""

    prompt = (
        """
You have written a story. Now, you need to illustrate the story.
Given the story that you have written, provide a list of illustrations that should be included in the story.
Make sure to include only the most important and valuable illustrations that will help the reader understand the story better.
Make sure to request a small number of illustrations ([MAX_ILLUSTRATION] maximum).

Text:
[TEXT]


To request an illustration from your illustrator, provide the instruction and the text reference for each illustration.
'description' should be a consise description of what the illustration should depict.
'text_beginning' and 'text_end' are the beginning and end of the text reference that should be illustrated respectively that you should copy from the text (Do not add any '...', only give the few words for the beginning and the end).
    -> Make sure to include the exact words and ponctuation to refer to the text. Moreover if the reference text does not end with a . or any ponctuation , you should not add one.

Make sure that the text reference do not overlap and are not too long.

Your answer must contain a list of illustrations in the following format:
[FORMAT]
""".replace(
            "[FORMAT]", JSON_FORMAT
        )
        .replace("[TEXT]", text)
        .replace("[MAX_ILLUSTRATION]", str(max_illustrations))
    )

    messages = [
        {"role": "system", "content": prompt},
    ]

    def feedback_json_function(
        json_answer: dict, is_final_feedback: bool
    ) -> Tuple[bool, object]:
        # Get the valid illustrations and the error message
        illustrations = json_answer["illustrations"]
        valid_matches, error_message = _get_valid_illustrations(
            text, illustrations, JSON_FORMAT
        )
        valid_matches = valid_matches[:max_illustrations]

        # If it is the final feedback, output only the valid matches
        # We don't want to stop the process if there is an error message. If the still have valid matches, we should output them.
        if is_final_feedback:
            return True, valid_matches

        # Check if there is an error message
        if error_message != "":
            return False, error_message

        return True, valid_matches

    return query_llm_with_feedback_json(
        message_history=messages,
        list_json_parent_key=["illustrations"],
        json_format=JSON_FORMAT,
        feedback_function=feedback_json_function,
    )


def query_illustration(
    text: str, description: str, text_subpart: str, working_folder: str = "out"
) -> str:
    """
    Generate an illustration using the OpenAI API.

    Args:
        text (str): The entire text to generate the illustration
        description (str): The description of the illustration
        text_subpart (str): The text subpart that should be illustrated.
        working_folder (str): The working folder to save the illustration

    Returns:
        str: path to the generated image
    """

    JSON_FORMAT = """
{
    "image_description": "Description of the image",
}
"""

    prompt = (
        """
I have written a story and would like to illustrate it with multiple images.

The story is: [TEXT]

For this task, I have selected a specific part of the story to illustrate. Your goal is to generate a detailed image description for the illustrator.

The specific text from the story to be illustrated is: [TEXT_SUBPART]

Additionally, I am providing a brief description of the image I envision. Based on both the text subpart and the brief description, please generate a precise and detailed image description.
My description is: [DESCRIPTION]

Make sure to keep the theme and the style of the story intact.
Make sure to add in the image description a style. You should provide a style that is close the natural or realistic style.

Provide the image description in the following format:
[FORMAT]
""".replace(
            "[TEXT]", text
        )
        .replace("[TEXT_SUBPART]", text_subpart)
        .replace("[FORMAT]", JSON_FORMAT)
        .replace("[DESCRIPTION]", description)
    )

    messages = [
        {"role": "system", "content": prompt},
    ]

    answer = query_llm_with_feedback_json(
        message_history=messages,
        list_json_parent_key=["image_description"],
        json_format=JSON_FORMAT,
    )
    if answer is None:
        return None
    image_description = answer["image_description"]
    return query_openai_image_generation(
        image_description, style="vivid", working_folder=working_folder
    )


def get_text_illustrations(text: str, max_illustrations: int = 2) -> List[str]:
    urls = []
    illustrations = query_suggested_illustrations(
        text, max_illustrations=max_illustrations
    )
    for i, match in enumerate(illustrations):
        print("Generating illustration: ", i + 1)
        url = query_illustration(
            text=text, description=match["description"], text_subpart=match["text"]
        )
        urls.append(url)
    return urls
