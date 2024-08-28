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


class StoryPart:
    def __init__(self, modules: List[StoryModules]):
        self._modules = modules

    def to_prompt_string(self) -> str:
        return "\n".join([module.to_prompt_string() for module in self._modules])

    def __getitem__(self, index):
        return self._modules[index]

    def __len__(self):
        return len(self._modules)


class Story:
    def __init__(
        self, title=None, overview=None, need_illustration=True, story_length=3
    ):
        self._title = title
        self._overview = overview
        self._story_max_length = story_length
        self._need_illustration = need_illustration
        self._story_parts = []

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
        if self.is_waiting_for_user_input():
            possible_choices = self._story_parts[-1][-1]
            possible_choices.set_user_choice(user_choice)

    def is_waiting_for_user_input(self) -> bool:
        """
        Return whether the story is waiting for user input.
        """
        if len(self._story_parts) == 0:
            return False
        last_module = self._story_parts[-1][-1]
        if isinstance(last_module, PossibleChoicesModule):
            return not last_module.has_selected_choice()
        return False

    def get_title(self) -> str:
        """
        Get the title of the story.

        Returns:
            str: the title of the story
        """
        return self._title

    def get_prompt_story(self) -> str:
        """
        Get the generated story.

        Returns:
            str: the generated story
        """
        return "\n".join([part.to_prompt_string() for part in self._story_parts])

    def get_story_parts(self) -> List[StoryPart]:
        """
        Get the formatted story.

        Returns:
            list of modules that compose the story
        """
        return self._story_parts

    def _get_story_current_length(self) -> int:
        """
        Get the current length of the story.

        Returns:
            int: the current length of the story
        """
        return len(self._story_parts)

    def _add_part_to_story(self, part: List[StoryModules]):
        """
        Add a part to the story.

        Args:
            list[StoryModule]: the part to add to the story
        """
        if len(part) == 0:
            return
        self._story_parts.append(StoryPart(part))

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
