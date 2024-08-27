from story import Story
from agents.illustratorAgent import query_suggested_illustrations
from openaiAPI import openai_show_usage

story = Story(need_illustration=False, story_length=1)
code_error = 0
while code_error == 0 or code_error == 1:
    code_error, parts = story.generate_next_part()

    print("The code error is: ", code_error)
    if code_error == 0:
        for p in parts:
            print(p)

    if story.is_waiting_for_user_input():
        user_input = input("-> ")
        story.input_user_answer(user_input)

openai_show_usage()

print("Final formatted story")
print(story.get_formatted_story())

print("Final story")
print(story.get_story())
