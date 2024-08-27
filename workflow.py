from story import Story
from openaiAPI import openai_show_usage
from openaiAPI import query_openai_image_generation

# story = Story(need_illustration=False, story_length=3)
# code_error = 0
# while code_error == 0 or code_error == 1:
#     code_error, parts = story.generate_next_part()

#     print("The code error is: ", code_error)
#     if code_error == 0:
#         for p in parts:
#             print(p)

#     if story.is_waiting_for_user_input():
#         user_input = input("-> ")
#         story.input_user_answer(user_input)

# print(query_openai_image_generation("Generate an image of a village"))

openai_show_usage()
