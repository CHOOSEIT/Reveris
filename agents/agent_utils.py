import json

AGENT_INTRODUCTION = """You are a story writer. Your goal create an engaging story idea that will be remembered by the user.
The story is lived by the user, so it should be in the user's perspective but told as the second person.

Additionally, the story should be straightforward and concrete. Focus on making it clear and relatable, avoiding abstract concepts and overly complex ideas such as decisions about feelings. It should be engaging and easy to follow.
Note that the story should be lived as a "story game" by the user.

Do not write explicitly that we are in a "story game", do not write that the choice of the user will be involve. Write the story as if it was a book.
"""

def extract_json_answer(answer: str) -> dict:
    """
    Extract the JSON answer from the OpenAI API response.

    Returns:
        dict: the JSON answer
    """
    try:
        return json.loads(answer)
    except:
        print("Failed to parse answer:")
        print(answer)
        return None