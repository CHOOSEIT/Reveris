from story.story import Story, ERRORCODE_NO_ERROR, ERRORCODE_STORY_COMPLETE
from typing import Tuple


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

    def generate_next_part(self) -> Tuple[int, dict]:
        if self.it == 0:
            part = [
                {"image": "out/img-5XkbU0ugs9hxI5G74gJz1pbG.png"},
                {
                    "text": "Once upon a time, in a world of dreams, there was a dreamer who was searching for the meaning of life."
                },
                {
                    "possible_choices": [
                        {"choice": "Continue dreaming"},
                        {"choice": "Wake up"},
                    ]
                },
            ]
        elif self.it == 1:
            part = [
                {"text": "The dreamer decided to continue dreaming."},
                {"image": "out/qemQ2o.jpg"},
                {"text": "The dreamer found himself in a beautiful forest."},
                {
                    "possible_choices": [
                        {"choice": "Continue dreaming 2"},
                        {"choice": "Wake up 2"},
                    ]
                },
            ]
        elif self.it == 2:
            part = [
                {"text": "The dreamer decided to continue dreaming. *again*"},
                {"image": "out/village.jpg"},
                {"text": "The dreamer found himself in a peaceful village."},
                {
                    "possible_choices": [
                        {"choice": "Continue dreaming 3"},
                        {"choice": "Wake up 3"},
                    ]
                },
            ]
        elif self.it == 3:
            part = [
                {"text": "The end"},
            ]
        else:
            return ERRORCODE_STORY_COMPLETE, None

        self._story_current_length += 1
        self.it += 1
        # Add the generated output to the formatted story
        self._formatted_story.extend(part)

        return ERRORCODE_NO_ERROR, part
