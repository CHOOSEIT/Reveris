from story.story import (
    Story,
    ERRORCODE_NO_ERROR,
    ERRORCODE_STORY_COMPLETE,
    ERRORCODE_WAITING_FOR_USER_INPUT,
    ERRORCODE_TEXT_GENERATION_ERROR,
)
from agents.writerAgent import (
    query_story_introduction,
    query_story_continuation,
    query_story_end,
)
from agents.illustratorAgent import query_suggested_illustrations, query_illustration
from agents.ideaAgent import generate_title_overview_story
from typing import Tuple


class AIStory(Story):
    def __init__(
        self, title=None, overview=None, need_illustration=True, story_length=3
    ):
        super().__init__(title, overview, need_illustration, story_length)

    def _generate_idea(self) -> bool:
        """
        Generate a new story idea.

        Returns:
            bool: True if no error occurred, False otherwise

        """
        if self._title is None or self._overview is None:
            print("Generating a new story idea...")
            title, overview = generate_title_overview_story()
            if title is None:
                print("Failed to generate the story idea.")
                return False

            self._title = title
            self._overview = overview

        return True

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
        if self._story_current_length > self._story_max_length:
            print("The story is already complete.")
            return ERRORCODE_STORY_COMPLETE, None

        if self.is_waiting_for_user_input():
            print("Waiting for user input.")
            return ERRORCODE_WAITING_FOR_USER_INPUT, None

        if self._title is None or self._overview is None:
            print("The story idea is missing (title and overview).")
            sucess = self._generate_idea()
            if not sucess:
                return ERRORCODE_TEXT_GENERATION_ERROR, None

        generated_part = []
        # We need to generate the introduction first
        if self._story_current_length == 0:
            ###
            # Generate the story introduction
            ###
            print("Generating the story introduction ...")
            introduction = query_story_introduction(self._overview)

            if introduction is None:
                print("Failed to generate the introduction.")
                return ERRORCODE_TEXT_GENERATION_ERROR, None

            generated_part.append({"text": introduction})

        story = self.get_story()

        if self._story_current_length < self._story_max_length:
            ###
            # Generate the story extension
            ###
            print("Generating the story ...")
            extension = query_story_continuation(
                self._overview,
                story,
                self._story_current_length + 1,
                self._story_max_length,
            )

            if extension is None:
                print("Failed to generate the extension.")
                return ERRORCODE_TEXT_GENERATION_ERROR, None

            generated_part.append({"text": extension["story_content"]})
            generated_part.append({"possible_choices": extension["choices"]})

        elif self._story_current_length == self._story_max_length:
            ###
            # Generate the end
            ###
            print("Generating the end of the story ...")
            end = query_story_end(self._overview, story)

            if end is None:
                print("Failed to generate the end.")
                return ERRORCODE_TEXT_GENERATION_ERROR, None

            generated_part.append({"text": end})

        self._story_current_length += 1

        return ERRORCODE_NO_ERROR, generated_part

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
        generated_output = []
        text_code_error, generated_parts = self._generate_text_next_part()

        if generated_parts is None:
            return text_code_error, None

        for part in generated_parts:
            if "possible_choices" in part:
                generated_output.append({"possible_choices": part["possible_choices"]})
            elif "text" in part:
                generated_text = part["text"]
                if self._need_illustration:
                    # Generate the illustrations

                    print("Generating the illustration suggestions ...")
                    suggested_illustrations = query_suggested_illustrations(
                        generated_text, max_illustrations=2
                    )
                    suggested_illustrations = sorted(
                        suggested_illustrations, key=lambda x: x["start_idx"]
                    )

                    current_start = 0

                    for suggested_illustration in suggested_illustrations:
                        end = suggested_illustration["start_idx"]
                        seperated = generated_text[current_start:end]

                        if len(seperated) != 0:
                            generated_output.append({"text": seperated})

                        # Generate the illustration
                        print("Generating an illustration ...")
                        url = query_illustration(
                            text=self.get_story(),
                            description=suggested_illustration["description"],
                            text_subpart=suggested_illustration["text"],
                        )

                        generated_output.append({"image": url})
                        current_start = end

                    final_separation = generated_text[current_start:]
                    generated_output.append({"text": final_separation})
                else:
                    generated_output.append({"text": generated_text})

        # Add the generated output to the formatted story
        self._formatted_story.extend(generated_output)

        return ERRORCODE_NO_ERROR, generated_output
