from agents.agent_utils import (
    AGENT_INTRODUCTION,
    query_llm_with_feedback_json,
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

Write the introduction of the story. Describe the environment, the main characters, and the current situation.
    You should for example describe the setting of the characters, the time, the place, and the main characters and how it end up in the current situation (the plot of the story).
You must explain how to main character ended up in the current situation before starting the story.

Your instroduction should be short (2 paragraphs maximum) and you should talk about the main character as the second person (you).

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
    answer = query_llm_with_feedback_json(
        message_history=messages,
        list_json_parent_key=["story_content"],
        json_format=JSON_FORMAT,
    )
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
    "choices": [
        {
            "choice": "Choice 1",
        },
        {
            "choice": "Choice 2",
        },
        ...
    ]
}
"""

    prompt = (
        AGENT_INTRODUCTION
        + """
Story State: [STORY_STATE]

Write the continuation of the story, given the beginning overview and the current state of the story.
The continuation should be short (2 paragraphs maximum). The story will be completed later, should write a single part of it.

Your part should contain a plot twist or a new element that will make the story more engaging.
Whenever a new character or place is introduced, make sure to describe them smoothly in the story.

End the part with a question or choice that the user should make as the person within the story in order to decide how the story will continue.
Craft the story such that the question you have 2 to 4 possible answers that have 2 to 4 radically different effects on the story. You have to see the story as a "story game".

Make sure that the continuation is engaging and have a clear path. You should advance in the story do not lose time as the story should be completed in [NUMBER_OF_PARTS] parts.
This part is the [PART_NUMBER]/[NUMBER_OF_PARTS].

The story extension should lead to different paths and ending that each of them can be good or bad depending on the previous and future decisions.
Make sure to really transport the player in an unique adventure. Note that you should not base the entire story on "choices that will define your future". You should really write a story and at one point, stop and ask the user to make a choice.

Make sure to be close to the end of the story at the last part.

When writing your part, do not explicitly mention that your choices will have an effect on the story nor that you are in a story game. Just write the story as if it was a book and at the end provide the question with the choices.

The choices should be explained in the part, but do not enumerate them at the end of the part. You should list them inside the JSON object.

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

    def feedback_json_function(
        json_answer: dict, is_final_feedback: bool
    ) -> Tuple[bool, object]:
        if len(json_answer["choices"]) < 2:
            return (
                False,
                "The JSON answer should contain at least 2 choices. Please verify that your answer is in the right JSON format and contain all the choices: {}".format(
                    JSON_FORMAT
                ),
            )

        for choice in json_answer["choices"]:
            if "choice" not in choice:
                return (
                    False,
                    "The JSON of a choice is missing some keys ({}). Please verify that your answer is in the right JSON format: {}".format(
                        choice, JSON_FORMAT
                    ),
                )

        return True, json_answer

    answer = query_llm_with_feedback_json(
        message_history=messages,
        list_json_parent_key=["story_content", "choices"],
        json_format=JSON_FORMAT,
        feedback_function=feedback_json_function,
    )

    if answer is None:
        return None

    return answer


def query_story_end(story_overview: str, story: str):
    """
    Finish the story story.

    Args:
        story_overview (str): the story overview
        story_state (str): the story

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

The end should be short (2 paragraphs maximum).

Make sure that the end follows the story and the choices made by the user in the previous parts.
Maybe reflect the choices made by the user in the story (not necessary but would be a nice touch if relevant).

Story beginning overview: [STORY_OVERVIEW]

You answer must contains a single JSON object in the following format:
[FORMAT]
Make sure to have your answer in the JSON format.
""".replace(
            "[STORY_OVERVIEW]", story_overview
        )
        .replace("[STORY_STATE]", story)
        .replace("[FORMAT]", JSON_FORMAT)
    )

    messages = [
        {"role": "system", "content": prompt},
    ]

    answer = query_llm_with_feedback_json(
        message_history=messages,
        list_json_parent_key=["story_end"],
        json_format=JSON_FORMAT,
    )
    if answer is None:
        return None
    return answer["story_end"]
