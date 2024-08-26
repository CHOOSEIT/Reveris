import json

from openaiAPI import query_openai

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


def query_llm_with_feedback(
    message_history: list,
    feedback_function: callable,
    loop_times=3,
    temperature=0,
) -> object:
    """
    Query the LLM until the feedback function returns a success or the loop times is reached.

    Args:
        message_history (list): the message history
        feedback_function (callable([str, bool] -> [bool, object])): the feedback function
            -> function that accepts a string and a boolean (is final feedback) and return a boolean and an object. If the boolean is False, the object is the error message else it is the final answer

    Returns:
        str: the answer or None if the query failed

    """
    for i in range(loop_times):
        answer = query_openai(message_history, temperature=temperature)

        error_code, output = feedback_function(answer, i == loop_times - 1)
        if error_code:
            return output

        print("Feedback: {}".format(output))
        message_history.append({"role": "system", "content": output})

    return None
