from typing import Tuple, List
from story.story_modules import (
    StoryModules,
    ChoiceModule,
    PossibleChoicesModule,
)

ERRORCODE_NO_ERROR = 0
ERRORCODE_WAITING_FOR_USER_INPUT = 1
ERRORCODE_STORY_COMPLETE = 2
ERRORCODE_TEXT_GENERATION_ERROR = 3
ERRORCODE_IMAGE_GENERATION_ERROR = 4


class Story:
    def __init__(
        self, title=None, overview=None, need_illustration=True, story_length=3
    ):
        self._title = title
        self._overview = overview
        self._story_max_length = story_length
        self._story_current_length = 0
        self._need_illustration = need_illustration
        self._formatted_story = []

    def set_need_illustration(self, need_illustration: bool):
        """
        Set if the story needs an illustration.

        Args:
            need_illustration (bool): True if the story needs an illustration, False otherwise
        """
        self._need_illustration = need_illustration

    def input_user_answer(self, user_choice: ChoiceModule):
        """
        Input the user choice in the story.
        """
        self._formatted_story.append(user_choice)

    def is_waiting_for_user_input(self) -> bool:
        """
        Return whether the story is waiting for user input.
        """
        if len(self._formatted_story) == 0:
            return False
        last_module = self._formatted_story[-1]
        return isinstance(last_module, PossibleChoicesModule)

    def get_title(self) -> str:
        """
        Get the title of the story.

        Returns:
            str: the title of the story
        """
        return self._title

    def get_story(self) -> str:
        """
        Get the generated story.

        Returns:
            str: the generated story
        """
        return "\n".join([part.to_prompt_string() for part in self._formatted_story])

    def get_formatted_story(self) -> List[StoryModules]:
        """
        Get the formatted story.

        Returns:
            list of modules that compose the story
        """
        return self._formatted_story

    def _add_part_to_story(self, part: List[StoryModules]):
        """
        Add a part to the story.

        Args:
            list[StoryModule]: the part to add to the story
        """
        self._story_current_length += 1
        # Add the generated output to the formatted story
        self._formatted_story.extend(part)

    def _generate_idea(self) -> bool:
        """
        Generate a new story idea.
        It generate and set the title and overview of the story.

        Returns:
            bool: True if no error occurred, False otherwise

        """
        raise NotImplementedError

    def _generate_text_next_part(self) -> Tuple[int, List[StoryModules]]:
        """
        Generate the next part of the story.

        Returns:
            int: error code:
                - 0 if no error,
                - 1 waiting for user input
                - 2 the story is already complete
                - 3 generation error
            list[StoryModules]: The generated part of the story.
        """
        raise NotImplementedError

    def generate_next_part(self) -> Tuple[int, List[StoryModules]]:
        """
        Generate the next part of the story.

        Returns:
            int: error code:
                - 0 if no error,

                (text generation)
                - 1 waiting for user input
                - 2 the story is already complete
                - 3 text generation error

                (image generation)
                - 4 image generation error

            list[StoryModules]: The generated part of the story.
        """
        raise NotImplementedError
