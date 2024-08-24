import json

from openaiAPI import query_openai
from agents.agent_utils import AGENT_INTRODUCTION, extract_json_answer
from datetime import datetime

def query_expand_story_idea(story_idea) -> dict:
    """
    Create the story introduction and ideas.

    Returns:
        dict: introduction and ideas
    """

    prompt = AGENT_INTRODUCTION + \
"""Make sure that the story idea is clear. You should not open to a vague story.

Story Idea: [STORY_IDEA]

Start by giving the list of theme that you want to explore in the story.
Give me main places, characters, and objects that you want to include and explore in the story.

Give a quick overview of the main plot of the story and the idea behind it. 
The story should be able to be told in a few paragraphs.
Make sure that the story has a clear goal. Make sure to outline this goal.

Moreover make sure to be clear about the places, characters, objects and goal that you want to include in the story.

You should create a story overview that has a clear beginning and middle.
Make sure to express the moral or idea that you want to convey in the story.

But remember that you should only give the overview containing a moral or idea and not the entire story.

You answer must contains a single JSON object in the following format:
{
    "themes": ["theme1", "theme2", "theme3"],
    "places": ["place1", "place2", "place3"],
    "characters": ["character1", "character2", "character3"],
    "objects": ["object1", "object2", "object3"],
    "goal": "The goal of the story",
    "title": "The story Title",
    "overview": "A quick overview of the story plot containing a moral or idea."
}
Make sure to have your answer in the JSON format.
""".replace("[STORY_IDEA]", story_idea)

    messages = [
        {"role": "system", "content": prompt},
    ]

    answer = query_openai(messages)
    return extract_json_answer(answer)


PREVIOUS_IDEAS_FILE = "previous_ideas.json"
def query_idea() -> dict:
    """
    Create a story idea.

    Returns:
        str: The story idea
    """
    try:
        with open(PREVIOUS_IDEAS_FILE, "r") as f:
            ideas = json.load(f)
    except:
        ideas = []

    ideas = ideas[-40:]

    prompt = """
Generate a 3 lines long story idea. The story should be seen as a first person story that I will be living and play as a story game.

Note that your previously generated ideas are:
[STORIES]

Make sure that your new idea is not similar or close to the previous ones. Make it truly unique.

You answer must contains a single JSON object in the following format:
{
    "idea": "The story idea",
}
Make sure to have your answer in the JSON format.

    """.replace("[STORIES]", "\n".join(ideas))

    messages = [
        {"role": "system", "content": prompt},
    ]

    answer = query_openai(messages, temperature=0)
    idea = extract_json_answer(answer)["idea"]

    ideas.append(idea)

    with open(PREVIOUS_IDEAS_FILE, "w") as f:
        json.dump(ideas, f)

    return idea



    

