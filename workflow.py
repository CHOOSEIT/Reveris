from openaiAPI import openai_show_usage
from agents.ideaAgent import query_idea, query_expand_story_idea
from agents.writerAgent import query_story_introduction, query_story_continuation, query_story_end
from agents.voiceAgent import query_readme

STORY_LENGTH = 3

story_idea = query_idea()

expanded_story_id = query_expand_story_idea(story_idea=story_idea)

print("Story Idea:")
print("Title: {}".format(expanded_story_id["title"]))
print("Overview: {}".format(expanded_story_id["overview"]))

introduction = query_story_introduction(expanded_story_id["overview"])

if introduction is None:
    print("Failed to generate the introduction.")
    exit(1)

print("\n Introduction:")
print(introduction)

story = introduction

success = True

for i in range(STORY_LENGTH):
    continuation = query_story_continuation(expanded_story_id["overview"], story, i+1, STORY_LENGTH)
    if continuation is None:
        print("Failed to generate the continuation.")
        success = False
        break

    story += "\n" + continuation
    print(continuation)

    if i == 0:
        query_readme(story, str(i))
    else:
        query_readme(continuation, str(i))

    answer = input("-> ")
    story += "\n->" + answer

if not success:
    exit(1)

# End the story
end = query_story_end(expanded_story_id["overview"], story)
if end is None:
    print("Failed to generate the end.")
    exit(1)

query_readme(end, "end")

openai_show_usage()