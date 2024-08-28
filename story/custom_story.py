from story.story import Story, ERRORCODE_NO_ERROR, ERRORCODE_STORY_COMPLETE
from typing import Tuple, List
from story.story_modules import (
    StoryModules,
    ImageModule,
    TextModule,
    ChoiceModule,
    PossibleChoicesModule,
)


class CustomStory(Story):
    def __init__(
        self, title=None, overview=None, need_illustration=True, story_length=3
    ):
        super().__init__(
            title=title,
            overview=overview,
            need_illustration=need_illustration,
            story_length=story_length,
        )
        self.it = 0

    def _generate_idea(self) -> bool:
        self.title = "The story of a dreamer"
        self.overview = "A dreamer who is searching for the meaning of life."

        return True

    def generate_next_part(self) -> Tuple[int, List[StoryModules]]:
        if self.it == 0:
            part = [
                ImageModule("out/img-5XkbU0ugs9hxI5G74gJz1pbG.png"),
                TextModule(
                    "Once upon a time, in a world of dreams, there was a dreamer who was searching for the meaning of life."
                ),
                PossibleChoicesModule(
                    [
                        ChoiceModule("Continue dreaming"),
                        ChoiceModule("Wake up"),
                    ]
                ),
            ]
        elif self.it == 1:
            part = [
                TextModule("The dreamer decided to continue dreaming."),
                ImageModule("out/qemQ2o.jpg"),
                TextModule("The dreamer found himself in a beautiful forest."),
                PossibleChoicesModule(
                    [
                        ChoiceModule("Continue dreaming 2"),
                        ChoiceModule("Wake up 2"),
                    ]
                ),
            ]
        elif self.it == 2:
            part = [
                TextModule("The dreamer decided to continue dreaming. *again*"),
                ImageModule("out/village.jpg"),
                TextModule("The dreamer found himself in a peaceful village."),
                PossibleChoicesModule(
                    [
                        ChoiceModule("Continue dreaming 3"),
                        ChoiceModule("Wake up 3"),
                    ]
                ),
            ]
        elif self.it == 3:
            part = [TextModule("The end")]
        else:
            return ERRORCODE_STORY_COMPLETE, None

        self.it += 1
        self._add_part_to_story(part)
        return ERRORCODE_NO_ERROR, part
