import json
import os

from agents.agent_utils import (
    AGENT_INTRODUCTION,
    query_llm_with_feedback_json,
)


def query_expand_story_idea(story_idea) -> dict:
    """
    Create the story introduction and ideas.

    Returns:
        dict: introduction and ideas
    """

    JSON_FORMAT = """
{
    "themes": ["theme1", "theme2", "theme3"],
    "places": ["place1", "place2", "place3"],
    "characters": ["character1", "character2", "character3"],
    "objects": ["object1", "object2", "object3"],
    "goal": "The goal of the story",
    "title": "The story Title",
    "overview": "A quick overview of the story plot containing a moral or idea."
}
"""

    prompt = (
        AGENT_INTRODUCTION
        + """Make sure that the story idea is clear. You should not open to a vague story.

Story Idea: [STORY_IDEA]

Start by giving the list of theme that you want to explore in the story.
Give me main places, characters, and objects that you want to include and explore in the story.

Give a quick overview of the main plot of the story and the idea behind it. 
The story should be able to be told in a few paragraphs.
Make sure that the story has a clear goal. Make sure to outline this goal.

Moreover make sure to be clear about the places, characters, objects and goal that you want to include in the story.

You should create a story overview that has a clear beginning and middle.
Make sure to express the moral or idea that you want to convey in the story.

The story that you create should have a real story and structure with arcs and a clear goal. But note that you should precise in the overview how the stories may end (as it is wrote along the way) depending on the choices made by the player.
The story should have clear different paths and ending that each of them can be good or bad depending on the player decisions.

But remember that you should only give the overview containing a moral or idea and not the entire story.

You answer must contains a single JSON object in the following format:
[FORMAT]
Make sure to have your answer in the JSON format.
""".replace(
            "[STORY_IDEA]", story_idea
        ).replace(
            "[FORMAT]", JSON_FORMAT
        )
    )

    messages = [
        {"role": "system", "content": prompt},
    ]

    return query_llm_with_feedback_json(
        message_history=messages,
        list_json_parent_key=[
            "themes",
            "places",
            "characters",
            "objects",
            "goal",
            "title",
            "overview",
        ],
        json_format=JSON_FORMAT,
    )


PREVIOUS_IDEAS_FILE_PATH = "out/previous_ideas.json"


def query_idea() -> dict:
    """
    Create a story idea.

    Returns:
        str: The story idea
    """
    base_path = os.path.dirname(PREVIOUS_IDEAS_FILE_PATH)
    os.makedirs(base_path, exist_ok=True)
    try:
        with open(PREVIOUS_IDEAS_FILE_PATH, "r") as f:
            ideas = json.load(f)
    except:
        ideas = []

    ideas = ideas[-40:]

    JSON_FORMAT = """
{
    "idea": "The story idea",
}
"""

    prompt = """
Generate a 3 lines long story idea. The story should be seen as a first person story that I will be living and play as a story game.

Note that your previously generated ideas are:
[STORIES]

Make sure that your new idea is not similar or close to the previous ones. Make it truly unique.
Try to not use the same places, themes, characters, objects, and goals that you have used in the previous ideas.

The story that you create should have a real story and structure with arcs and a clear goal. But note that you should precise in the overview how the stories may end (as it is wrote along the way) depending on the choices made by the player.
The story should have clear different paths and ending that each of them can be good or bad depending on the player decisions.

You answer must contains a single JSON object in the following format:
[FORMAT]
Make sure to have your answer in the JSON format.

    """.replace(
        "[STORIES]", "\n".join(ideas) if len(ideas) > 0 else "None"
    ).replace(
        "[FORMAT]", JSON_FORMAT
    )

    messages = [
        {"role": "system", "content": prompt},
    ]

    answer = query_llm_with_feedback_json(
        message_history=messages,
        list_json_parent_key=["idea"],
        json_format=JSON_FORMAT,
    )
    if answer is None:
        return None

    idea = answer["idea"]

    ideas.append(idea)

    with open(PREVIOUS_IDEAS_FILE_PATH, "w") as f:
        json.dump(ideas, f)

    return idea


def generate_title_overview_story():
    """
    Generate the title and overview of the story.

    Returns:
        str: The title of the story or None if the story could not be generated
        str: The overview of the story or None if the story could not be generated
    """
    story_idea = query_idea()
    if story_idea is None:
        return None, None

    expanded_story_id = query_expand_story_idea(story_idea=story_idea)
    if expanded_story_id is None:
        return None, None

    title = expanded_story_id["title"]
    overview = expanded_story_id["overview"]
    return title, overview
