import json

from openaiAPI import query_openai
from typing import Tuple, List

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
    message_history: List[dict],
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
        loop_times (int): the number of times to loop
        temperature (int): the temperature to use for the query

    Returns:
        str: the answer or None if the query failed

    """
    for i in range(loop_times):
        answer = query_openai(message_history, temperature=temperature)

        error_code, output = feedback_function(answer, i == loop_times - 1)
        if error_code:
            return output

        print("    LLM error feedback: {}".format(output))
        message_history.append({"role": "system", "content": output})

    return None


def query_llm_with_feedback_json(
    message_history: List[dict],
    list_json_parent_key: List[str],
    json_format: str,
    feedback_function: callable = None,
    loop_times=3,
    temperature=0,
):
    """
    Query the LLM until the feedback function returns a success or the loop times is reached.

    Args:
        message_history (list): the message history
        list_json_parent_key (list): the list of keys that should be present in the JSON answer
        json_format (str): the JSON format that the answer should respect
        feedback_function (callable([dict, bool] -> [bool, object])): the feedback function
            -> function that accepts a json dictionary and a boolean (is final feedback) and return a boolean and an object. If the boolean is False, the object is the error message else it is the final answer
        loop_times (int): the number of times to loop
        temperature (int): the temperature to use for the query

    Returns:
        dict: the answer or None if the query failed

    """

    def json_feedback(answer: str, is_final_feedback: bool) -> Tuple[bool, object]:
        json_answer = extract_json_answer(answer)
        if json_answer is None:
            return (
                False,
                "Failed to parse the answer. Please verify that your answer is in the right JSON format: {}".format(
                    json_format
                ),
            )

        if list_json_parent_key is not None:
            for key in list_json_parent_key:
                if key not in json_answer:
                    return (
                        False,
                        "The JSON answer is missing some keys. Please verify that your answer is in the right JSON format: {}".format(
                            json_format
                        ),
                    )

        if feedback_function is not None:
            return feedback_function(json_answer, is_final_feedback)
        return True, json_answer

    return query_llm_with_feedback(
        message_history=message_history,
        feedback_function=json_feedback,
        loop_times=loop_times,
        temperature=temperature,
    )
