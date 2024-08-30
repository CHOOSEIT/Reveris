import json
import os

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
from typing import Tuple, List
from story.story_modules import (
    StoryModules,
    ImageModule,
    TextModule,
    ChoiceModule,
    PossibleChoicesModule,
)
from story.story_part import StoryPart


class AIStory(Story):
    def __init__(
        self,
        title=None,
        overview=None,
        need_illustration=True,
        generate_speeches=False,
        target_lang=None,
        story_length=3,
        id=None,
    ):
        super().__init__(
            title=title,
            overview=overview,
            need_illustration=need_illustration,
            generate_speeches=generate_speeches,
            target_lang=target_lang,
            story_length=story_length,
            id=id,
        )

    def _generate_idea(self) -> bool:
        if self.get_title_module() is None or self._overview is None:
            print("Generating a new story idea...")
            title, overview = generate_title_overview_story()
            if title is None:
                print("Failed to generate the story idea.")
                return False

            self.set_title(title)
            self._overview = overview

        return True

    def _generate_text_next_part(self) -> Tuple[int, List[StoryModules]]:
        current_story_length = self._get_story_part_index()
        if current_story_length > self._story_max_length:
            print("The story is already complete.")
            return ERRORCODE_STORY_COMPLETE, None

        if self.is_waiting_for_user_input():
            print("Waiting for user input.")
            return ERRORCODE_WAITING_FOR_USER_INPUT, None

        if self.get_title_module() is None or self._overview is None:
            print("The story idea is missing (title and overview).")
            sucess = self._generate_idea()
            if not sucess:
                return ERRORCODE_TEXT_GENERATION_ERROR, None

        generated_part = []
        # We need to generate the introduction first
        if current_story_length == 0:
            ###
            # Generate the story introduction
            ###
            print("Generating the story introduction ...")
            introduction = query_story_introduction(self._overview)

            if introduction is None:
                print("Failed to generate the introduction.")
                return ERRORCODE_TEXT_GENERATION_ERROR, None

            generated_part.append(TextModule(introduction))

        story = self.get_prompt_story()

        if current_story_length < self._story_max_length:
            ###
            # Generate the story extension
            ###
            print("Generating the story ...")
            extension = query_story_continuation(
                self._overview,
                story,
                current_story_length + 1,
                self._story_max_length,
            )

            if extension is None:
                print("Failed to generate the extension.")
                return ERRORCODE_TEXT_GENERATION_ERROR, None

            list_of_choices = []
            for choice in extension["choices"]:
                list_of_choices.append(ChoiceModule(choice["choice"]))

            generated_part.append(TextModule(extension["story_content"]))
            generated_part.append(PossibleChoicesModule(list_of_choices))

        elif current_story_length >= self._story_max_length:
            ###
            # Generate the end
            ###
            print("Generating the end of the story ...")
            end = query_story_end(self._overview, story)

            if end is None:
                print("Failed to generate the end.")
                return ERRORCODE_TEXT_GENERATION_ERROR, None

            generated_part.append(TextModule(end))

        return ERRORCODE_NO_ERROR, generated_part

    def _generate_next_modules(self) -> Tuple[int, List[StoryModules]]:
        generated_modules = []
        text_code_error, generated_output = self._generate_text_next_part()

        if generated_output is None:
            return text_code_error, None

        for module in generated_output:
            if isinstance(module, TextModule):
                generated_text = module.get_text()
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
                            generated_modules.append(TextModule(seperated))

                        # Generate the illustration
                        print("Generating an illustration ...")
                        url = query_illustration(
                            text=self.get_prompt_story(),
                            description=suggested_illustration["description"],
                            text_subpart=suggested_illustration["text"],
                            working_folder=self.get_working_folder(),
                        )

                        generated_modules.append(ImageModule(url))
                        current_start = end

                    final_separation = generated_text[current_start:]
                    generated_modules.append(TextModule(final_separation))
                else:
                    generated_modules.append(module)
            else:
                generated_modules.append(module)

        return ERRORCODE_NO_ERROR, generated_modules

    @staticmethod
    def load_story(directory: str):
        """
        Load a story from a directory.

        Args:
            directory (str): the directory of the story (Example: "out/stories/story_id")

        Returns:
            Story: the loaded story or None if the story does not exist
        """
        if not os.path.exists(directory):
            return None

        filename = os.path.join(directory, "story.json")
        with open(filename, "r") as file:
            story_dict = json.load(file)
            story = AIStory(
                title="Title",
                overview=story_dict["overview"],
                need_illustration=story_dict["need_illustration"],
                generate_speeches=story_dict["generate_speeches"],
                target_lang=story_dict["target_lang"],
                story_length=story_dict["story_length"],
                id=story_dict["id"],
            )
            story._title_module = TextModule.from_dict(story_dict["title"])
            story._story_parts = [
                StoryPart([StoryModules.from_dict(module) for module in part])
                for part in story_dict["story_parts"]
            ]
            return story
