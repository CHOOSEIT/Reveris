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
        self,
        need_illustration=True,
        generate_speeches=False,
        target_lang=None,
        story_length=3,
    ):
        super().__init__(
            title=None,
            overview=None,
            need_illustration=need_illustration,
            generate_speeches=generate_speeches,
            target_lang=target_lang,
            story_length=story_length,
            id="custom_story",
        )

    def _generate_idea(self) -> bool:
        self.set_title("The story of a dreamer")
        self.overview = "A dreamer who is searching for the meaning of life."

        return True

    def _generate_next_modules(self) -> Tuple[int, List[StoryModules]]:
        if self.get_title_module() is None or self._overview is None:
            self._generate_idea()

        current_story_length = self._get_story_part_index()
        if current_story_length == 0:
            textAndSpeech = TextModule(
                "Once upon a time, in a world of dreams, there was a dreamer who was searching for the meaning of life."
            )
            textAndSpeech._speech_file_path = "demo_story/tts_8D115s.mp3"
            part = [
                ImageModule("demo_story/img-5XkbU0ugs9hxI5G74gJz1pbG.png"),
                textAndSpeech,
                PossibleChoicesModule(
                    [
                        ChoiceModule("Continue dreaming"),
                        ChoiceModule("Wake up"),
                    ]
                ),
            ]
        elif current_story_length == 1:
            textAndSpeech1 = TextModule("The dreamer decided to continue dreaming.")
            textAndSpeech1._speech_file_path = "demo_story/tts_tlOtNh.mp3"
            textAndSpeech2 = TextModule("The dreamer decided to continue dreaming.")
            textAndSpeech2._speech_file_path = "demo_story/tts_qS5R6s.mp3"
            part = [
                textAndSpeech1,
                ImageModule("demo_story/qemQ2o.jpg"),
                ImageModule("demo_story/lb33UI.jpg"),
                TextModule("This is a market"),
                textAndSpeech2,
                PossibleChoicesModule(
                    [
                        ChoiceModule("Continue dreaming 2"),
                        ChoiceModule("Wake up 2"),
                    ]
                ),
            ]
        elif current_story_length == 2:
            part = [
                ImageModule("demo_story/village.jpg"),
                TextModule("The dreamer found himself in a peaceful village."),
                PossibleChoicesModule(
                    [
                        ChoiceModule("Continue dreaming 3"),
                        ChoiceModule("Wake up 3"),
                    ]
                ),
            ]
        elif current_story_length == 3:
            part = [TextModule("The end")]
        else:
            return ERRORCODE_STORY_COMPLETE, None

        return ERRORCODE_NO_ERROR, part

    # Override from Story
    def save_to_file(self):
        # Prevent saving the story
        return
