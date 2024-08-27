from typing import Tuple

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

    def input_user_answer(self, user_choice: str):
        """
        Input the user choice in the story.
        """
        self._formatted_story.append({"user_choice": user_choice})

    def is_waiting_for_user_input(self) -> bool:
        """
        Return whether the story is waiting for user input.
        """
        if len(self._formatted_story) == 0:
            return False
        return "possible_choices" in self._formatted_story[-1]

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
        story = ""
        for part in self._formatted_story:
            if "text" in part:
                story += part["text"] + "\n"
            elif "user_choice" in part:
                story += "-> " + part["user_choice"] + "\n"
        return story

    def get_formatted_story(self) -> list:
        """
        Get the formatted story.

        Returns:
            list: the formatted parts of the story under the following format:
                [
                    {
                        "text": "Generated text"
                    },
                    {
                        "image": "Generated image"
                    },
                    {
                        "text": "Generated text"
                    },
                    {
                        "possible_choices": [
                            {
                                "choice": "Choice 1",

                            },
                            {
                                "choice": "Choice 2",
                            },
                            ...
                        ]
                    },
                    {
                        "user_choice": "User choice"
                    },
                    {
                        "text": "Generated text"
                    },
                    ...
                ]
        """
        return self._formatted_story

    def _generate_idea(self) -> bool:
        """
        Generate a new story idea.

        Returns:
            bool: True if no error occurred, False otherwise

        """
        raise NotImplementedError

    def _generate_text_next_part(self) -> Tuple[int, str]:
        """
        Generate the next part of the story.

        Returns:
            int: error code:
                - 0 if no error,
                - 1 waiting for user input
                - 2 the story is already complete
                - 3 generation error
            str: The generated part of the story under the following format:
                [
                    {
                        "text": "Generated text"
                    },
                    {
                        "possible_choices": [
                            {
                                "choice": "Choice 1",

                            },
                            {
                                "choice": "Choice 2",
                            },
                            ...
                        ]
                    },
                ]
        """
        raise NotImplementedError

    def generate_next_part(self) -> Tuple[int, dict]:
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

            dict: The generated part of the story under the formatted format.
        """
        raise NotImplementedError
