from openaiAPI import openai_show_usage, query_openai_image_generation
from agents.ideaAgent import query_idea, query_expand_story_idea
from agents.writerAgent import (
    query_story_introduction,
    query_story_continuation,
    query_story_end,
)
from agents.voiceAgent import query_readme
from agents.illustratorAgent import query_suggested_illustrations

# STORY_LENGTH = 3

# story_idea = query_idea()

# expanded_story_id = query_expand_story_idea(story_idea=story_idea)
# if expanded_story_id is None:
#     print("Failed to generate the story idea.")
#     exit(1)

# print("Story Idea:")
# print("Title: {}".format(expanded_story_id["title"]))
# print("Overview: {}".format(expanded_story_id["overview"]))
# print("--------")

# introduction = query_story_introduction(expanded_story_id["overview"])

# if introduction is None:
#     print("Failed to generate the introduction.")
#     exit(1)

# print(introduction)

# story = introduction

# success = True

# for i in range(STORY_LENGTH):
#     continuation = query_story_continuation(
#         expanded_story_id["overview"], story, i + 1, STORY_LENGTH
#     )
#     if continuation is None:
#         print("Failed to generate the continuation.")
#         success = False
#         break

#     story += "\n" + continuation
#     print(continuation)

#     # if i == 0:
#     #     query_readme(story, str(i))
#     # else:
#     #     query_readme(continuation, str(i))

#     answer = input("-> ")
#     story += "\n->" + answer

# if not success:
#     exit(1)

# # End the story
# end = query_story_end(expanded_story_id["overview"], story)
# if end is None:
#     print("Failed to generate the end.")
#     exit(1)

# query_readme(end, "end")


# print("Illustrations:")
# illustrations = query_suggested_illustrations(
#     """You stand at the edge of the Enchanted Forest, the air thick with the scent of pine and the distant sound of rustling leaves. In your hand, the magical compass glimmers, its needle spinning wildly before settling in a steady direction, pointing toward your deepest desires. The forest looms before you, a tapestry of vibrant colors and whispering secrets, inviting you to step into its embrace. As you take your first step, a sense of anticipation fills your heart, mingling with a hint of trepidation. The path ahead is unknown, but the compass promises revelations that could change everything. With each step, you feel the weight of your old life behind you, and the thrill of possibility ahead, as the journey of self-discovery begins to unfold.
# As you venture deeper into the Enchanted Forest, the trees seem to close in around you, their branches intertwining like the fingers of ancient giants. The compass in your hand begins to pulse with warmth, guiding you toward a clearing bathed in golden light. In the center stands a magnificent tree, its bark shimmering with iridescent hues, and at its base, a small, intricately carved box rests, beckoning you closer. You kneel down, heart racing, and open the box to reveal a shimmering crystal that radiates a soft glow. Just as you reach for it, a voice echoes through the clearing, startling you. "Only those who are truly ready may claim the crystal of their heart's desire. But beware, for it will reveal not just your dreams, but also your greatest fear." The air thickens with tension as you contemplate your next move. Will you take the crystal, risking the unveiling of your fears, or will you leave it behind and continue your journey unburdened? """
# )

# # Output the matches with their indices
# for i, match in enumerate(illustrations):
#     print(f"Illustration {i}:")
#     print("--------")

# print(illustrations)

final_url = query_openai_image_generation("A cat sitting on a table")
print(final_url)

openai_show_usage()
