from agents.writerAgent import (
    query_story_introduction,
    query_story_continuation,
    query_story_end,
)
from agents.illustratorAgent import query_suggested_illustrations, query_illustration
from agents.ideaAgent import generate_title_overview_story
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
        self.title = title
        self.overview = overview
        self.story_max_length = story_length
        self.story_current_length = 0
        self.story_parts = []
        self.wait_for_user_input = False
        self.need_illustration = need_illustration

    def _generate_idea(self) -> bool:
        """
        Generate a new story idea.

        Returns:
            bool: True if no error occurred, False otherwise

        """
        if self.title is None or self.overview is None:
            print("Generating a new story idea...")
            title, overview = generate_title_overview_story()
            if title is None:
                print("Failed to generate the story idea.")
                return False

            self.title = title
            self.overview = overview

        return True

    def set_need_illustration(self, need_illustration: bool):
        """
        Set if the story needs an illustration.

        Args:
            need_illustration (bool): True if the story needs an illustration, False otherwise
        """
        self.need_illustration = need_illustration

    def input_user_answer(self, user_choice: str):
        self.story_parts.append("-> " + user_choice)
        self.wait_for_user_input = False

    def is_waiting_for_user_input(self) -> bool:
        return self.wait_for_user_input

    def _generate_text_next_part(self) -> Tuple[int, str]:
        """
        Generate the next part of the story.

        Returns:
            int: error code:
                - 0 if no error,
                - 1 waiting for user input
                - 2 the story is already complete
                - 3 generation error
            str: The generated part of the story
        """
        if self.story_current_length > self.story_max_length:
            print("The story is already complete.")
            return ERRORCODE_STORY_COMPLETE, None

        if self.wait_for_user_input:
            print("Waiting for user input.")
            return ERRORCODE_WAITING_FOR_USER_INPUT, None

        if self.title is None or self.overview is None:
            print("The story idea is missing (title and overview).")
            sucess = self._generate_idea()
            if not sucess:
                return ERRORCODE_TEXT_GENERATION_ERROR, None

        generated_part = ""
        # We need to generate the introduction first
        if self.story_current_length == 0:
            ###
            # Generate the story introduction
            ###
            print("Generating the story introduction ...")
            introduction = query_story_introduction(self.overview)

            if introduction is None:
                print("Failed to generate the introduction.")
                return ERRORCODE_TEXT_GENERATION_ERROR, None

            self.story_parts.append(introduction)
            generated_part += introduction + "\n"

        story = self.get_story()

        if self.story_current_length < self.story_max_length:
            ###
            # Generate the story extension
            ###
            print("Generating the story ...")
            extension = query_story_continuation(
                self.overview,
                story,
                self.story_current_length + 1,
                self.story_max_length,
            )

            if extension is None:
                print("Failed to generate the extension.")
                return ERRORCODE_TEXT_GENERATION_ERROR, None

            self.story_parts.append(extension)
            generated_part += extension + "\n"
            self.wait_for_user_input = True

        elif self.story_current_length == self.story_max_length:
            ###
            # Generate the end
            ###
            print("Generating the end of the story ...")
            end = query_story_end(self.overview, story)

            if end is None:
                print("Failed to generate the end.")
                return ERRORCODE_TEXT_GENERATION_ERROR, None

            self.story_parts.append(end)
            generated_part += end + "\n"

        self.story_current_length += 1

        return ERRORCODE_NO_ERROR, generated_part

    def get_story(self) -> str:
        """
        Get the generated story.

        Returns:
            str: the generated story
        """
        return "\n".join(self.story_parts)

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

            dict: The generated part of the story under the following format:
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
                ]
        """
        generated_output = []
        text_code_error, generated_text = self._generate_text_next_part()
        if generated_text is None:
            return text_code_error, None

        if self.need_illustration:
            # Generate the illustrations
            print("Generating the illustration suggestions ...")
            suggested_illustrations = query_suggested_illustrations(
                generated_text, max_illustrations=3
            )
            suggested_illustrations = sorted(
                suggested_illustrations, key=lambda x: x["start_idx"]
            )

            print(len(suggested_illustrations))

            current_start = 0
            final_formatting = []

            for suggested_illustration in suggested_illustrations:
                end = suggested_illustration["start_idx"]
                seperated = generated_text[current_start:end]

                if len(seperated) != 0:
                    final_formatting.append({"text": seperated})

                # Generate the illustration
                print("Generating an illustration ...")
                url = query_illustration(
                    text=generated_text,
                    description=suggested_illustration["description"],
                    text_subpart=suggested_illustration["text"],
                )

                final_formatting.append({"image": url})

                current_start = end

            final_separation = generated_text[current_start:]
            final_formatting.append({"text": final_separation})
            generated_output = final_formatting

        else:
            generated_output.append({"text": generated_text})

        return ERRORCODE_NO_ERROR, generated_output
