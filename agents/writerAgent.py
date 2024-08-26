from agents.utils.agent_utils import (
    AGENT_INTRODUCTION,
    extract_json_answer,
    query_llm_with_feedback,
)
from typing import Tuple


def query_story_introduction(story_overview: str):
    """
    Create the story introduction.

    Args:
        story_overview (str): the story overview

    Returns:
        str: introduction and idea of the story
    """

    JSON_FORMAT = """
{
    "story_content": "your answer here",
}
"""

    prompt = (
        AGENT_INTRODUCTION
        + """Write the beginning of story given its beginning overview. 
Tell the story assuming that I do not know the overview nor have any context about it.
It moreover should be short (1 paragraph maximum), and set the stage for the story. That will be completed later.

Do not start to make a transition for the following part (Do not ask question nor do not question the following part, just set the environment).
Your introduction can end abruptly, as it will be continued later. Do not try to engage the user in the story, just set the stage for the story.

Story beginning overview: [STORY_OVERVIEW]

Note that your introduction should not cover the entire story overview, but just set the stage for the story.

You answer must contains a single JSON object in the following format:
[FORMAT]
Make sure to have your answer in the JSON format.
""".replace(
            "[STORY_OVERVIEW]", story_overview
        ).replace(
            "[FORMAT]", JSON_FORMAT
        )
    )

    messages = [
        {"role": "system", "content": prompt},
    ]

    def feedback_function(answer: str) -> Tuple[bool, object]:
        json_answer = extract_json_answer(answer)
        if json_answer is None:
            return (
                False,
                "Failed to parse the answer. Please verify that your answer is in the right JSON format: {}".format(
                    JSON_FORMAT
                ),
            )

        if "story_content" not in json_answer:
            return (
                False,
                "The JSON answer is missing some keys. Please verify that your answer is in the right JSON format: {}".format(
                    JSON_FORMAT
                ),
            )

        return True, json_answer

    answer = query_llm_with_feedback(messages, feedback_function)
    if answer is None:
        return None
    return answer["story_content"]


def query_story_continuation(
    story_overview: str,
    story_state: str,
    story_part_number: int,
    story_number_of_parts: int,
):
    """
    Continue the story story.

    Returns:
        str: continuation of the story
    """

    JSON_FORMAT = """
{
    "story_content": "your answer here",
}
"""

    prompt = (
        AGENT_INTRODUCTION
        + """
Story State: [STORY_STATE]

Write the continuation of the story, given the beginning overview and the current state of the story.
The continuation should be short (1 paragraphs maximum). The story will be completed later, should write a single part of it.

Your part should contain a plot twist or a new element that will make the story more engaging.
End the part with a question or choice that the user should make as the person within the story in order to decide how the story will continue.
Craft the story such that the question you have 2 or 3 possible answers that have 2 or 3 radically different effects on the story. You have to see the story as a "story game".

Make sure that the continuation is engaging and have a clear path. You should advance in the story do not lose time as the story should be completed in [NUMBER_OF_PARTS] parts.
This part is the [PART_NUMBER]/[NUMBER_OF_PARTS].

Make sure to be close to the end of the story at the last part.

When writing your part, do not explicitly mention that your choices will have an effect on the story nor that you are in a story game. Just write the story as if it was a book and at the end provide the question with the choices.

Story beginning overview: [STORY_OVERVIEW]

You answer must contains a single JSON object in the following format:
[FORMAT]
Make sure to have your answer in the JSON format.
""".replace(
            "[STORY_OVERVIEW]", story_overview
        )
        .replace("[STORY_STATE]", story_state)
        .replace("[PART_NUMBER]", str(story_part_number))
        .replace("[NUMBER_OF_PARTS]", str(story_number_of_parts))
        .replace("[FORMAT]", JSON_FORMAT)
    )

    messages = [
        {"role": "system", "content": prompt},
    ]

    def feedback_function(answer: str) -> Tuple[bool, object]:
        json_answer = extract_json_answer(answer)
        if json_answer is None:
            return (
                False,
                "Failed to parse the answer. Please verify that your answer is in the right JSON format: {}".format(
                    JSON_FORMAT
                ),
            )

        if "story_content" not in json_answer:
            return (
                False,
                "The JSON answer is missing some keys. Please verify that your answer is in the right JSON format: {}".format(
                    JSON_FORMAT
                ),
            )

        return True, json_answer

    answer = query_llm_with_feedback(messages, feedback_function)
    if answer is None:
        return None
    return answer["story_content"]


def query_story_end(story_overview: str, story_state: str):
    """
    Finish the story story.

    Returns:
        str: end of the story
    """
    JSON_FORMAT = """
{
    "story_end": "your answer here",
}
"""

    prompt = (
        AGENT_INTRODUCTION
        + """
Story State: [STORY_STATE]

Write the end of the story, given the beginning overview and the current state of the story.
It is not necessary, but adding a moral or a clear idea to the story would add value to the story.

The end should be short (1 paragraphs maximum).

Make sure that the end follows the story and the choices made by the user in the previous parts.
Maybe reflect the choices made by the user in the story (not necessary but would be a nice touch if relevant).

Story beginning overview: [STORY_OVERVIEW]

You answer must contains a single JSON object in the following format:
[FORMAT]
Make sure to have your answer in the JSON format.
""".replace(
            "[STORY_OVERVIEW]", story_overview
        )
        .replace("[STORY_STATE]", story_state)
        .replace("[FORMAT]", JSON_FORMAT)
    )

    messages = [
        {"role": "system", "content": prompt},
    ]

    def feedback_function(answer: str) -> Tuple[bool, object]:
        json_answer = extract_json_answer(answer)
        if json_answer is None:
            return (
                False,
                "Failed to parse the answer. Please verify that your answer is in the right JSON format: {}".format(
                    JSON_FORMAT
                ),
            )

        if "story_end" not in json_answer:
            return (
                False,
                "The JSON answer is missing some keys. Please verify that your answer is in the right JSON format: {}".format(
                    JSON_FORMAT
                ),
            )

        return True, json_answer

    answer = query_llm_with_feedback(messages, feedback_function)
    if answer is None:
        return None
    return answer["story_end"]
