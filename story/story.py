import random
import string
import os
import json

from typing import Tuple, List
from story.story_modules import (
    StoryModules,
    ChoiceModule,
    PossibleChoicesModule,
    isTranslatable,
    TextModule,
    canBeSpeechSynthesized,
)
from agents.agent_utils import query_in_parallel
from story.story_part import StoryPart
from datetime import datetime
from openaiAPI import API_BATCH_DELAY, API_MAX_BATCH_SPEECHES

ERRORCODE_NO_ERROR = 0
ERRORCODE_WAITING_FOR_USER_INPUT = 1
ERRORCODE_STORY_COMPLETE = 2
ERRORCODE_TEXT_GENERATION_ERROR = 3
ERRORCODE_IMAGE_GENERATION_ERROR = 4

WORKING_FOLDER = "out/stories/"


class Story:
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
        """
        Story class.

        Args:
            title (str): the title of the story
            overview (str): the overview of the story
            need_illustration (bool): True if the story needs an illustration, False otherwise
            generate_speeches (bool): True if the story needs to generate speeches, False otherwise
            target_lang (str): the language of the story (None -> english, Example: "FR")
            story_length (int): the number of parts of the story
            id (str): the id of the story
        """
        self._overview = overview
        self._story_max_length = story_length
        self._need_illustration = need_illustration
        self._generate_speeches = generate_speeches
        self._story_parts = []
        self._story_part_index = 0

        if target_lang is not None and target_lang.lower() == "en":
            target_lang = None
        self._target_lang = target_lang

        self.set_title(title)

        if id is None:
            generated_id = self._generate_id()
            if generated_id is None:
                raise Exception("Failed to generate the story ID.")
            self.id = generated_id
        else:
            self.id = id

    def _generate_id(self):
        for _ in range(10):
            _id = "".join(random.choices(string.ascii_letters + string.digits, k=10))
            if not os.path.exists(WORKING_FOLDER + _id):
                return _id
        return None

    def get_working_folder(self) -> str:
        working_folder = WORKING_FOLDER + self.id
        return working_folder

    def set_title(self, title: str):
        """
        Set the title of the story.

        Args:
            title (str): the title of the story
        """
        if title is None:
            self._title_module = None
            return
        _title_module = TextModule(title)
        _title_module.set_translation(target_lang=self._target_lang)
        self._title_module = _title_module

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

    def get_title_module(self) -> TextModule:
        """
        Get the title of the story.

        Returns:
            TextModule: the module that contains the title of the story
        """
        return self._title_module

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

    def _get_story_part_index(self) -> int:
        """
        Get the current length of the story.

        Returns:
            int: the current length of the story
        """
        return self._story_part_index

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

    def _generate_next_modules(self) -> Tuple[int, List[StoryModules]]:
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

            list[StoryModules]: The generated modules of the story.
        """
        raise NotImplementedError

    def generate_next_parts(self) -> Tuple[int, List[StoryPart]]:
        """
        Generate the next parts of the story.

        Returns:
            int: error code:
                - 0 if no error,

                (text generation)
                - 1 waiting for user input
                - 2 the story is already complete
                - 3 text generation error

                (image generation)
                - 4 image generation error

            List[StoryPart]: The generated part of the story.
        """
        resulting_parts = None
        if self._get_story_part_index() >= len(self._story_parts):
            error_code, modules = self._generate_next_modules()

            if error_code == ERRORCODE_NO_ERROR:
                # Translate the necessary modules
                if self._target_lang is not None:
                    print("Translating the story...")
                    for module in modules:
                        if isinstance(module, isTranslatable):
                            module.set_translation(target_lang=self._target_lang)

                def generate_module_speech(module: canBeSpeechSynthesized):
                    module.generate_speech(working_folder=self.get_working_folder())

                need_speech_generation = []
                # Generate the speeches
                if self._generate_speeches:
                    print("Generating the speeches...")
                    for module in modules:
                        if isinstance(module, canBeSpeechSynthesized):
                            need_speech_generation.append(module)

                args = [[module] for module in need_speech_generation]
                query_in_parallel(
                    function=generate_module_speech,
                    args_list=args,
                    max_parallel_queries=API_MAX_BATCH_SPEECHES,
                    time_between_queries=API_BATCH_DELAY,
                )

                resulting_parts = [StoryPart(modules)]
                self._story_parts.extend(resulting_parts)

            self.save_to_file()
            self._story_part_index += 1
        else:
            len_generated_story = len(self._story_parts)

            resulting_parts = self._story_parts[
                self._story_part_index : len_generated_story
            ]
            self._story_part_index = len_generated_story
            error_code = ERRORCODE_NO_ERROR

        return error_code, resulting_parts

    def save_to_file(self):
        """
        Save the story to file.
        """
        directory = self.get_working_folder()
        os.makedirs(directory, exist_ok=True)

        filename = directory + "/story.json"
        story_dict = self.to_dict()
        with open(filename, "w") as file:
            json.dump(story_dict, file, indent=4)

    def to_dict(self) -> dict:
        """
        Convert the story to a dictionary.

        Returns:
            dict: the dictionary that represents the story
        """
        story_dict = {
            "id": self.id,
            "saved_time": datetime.now().isoformat(),
            "title": (
                self._title_module.to_dict() if self._title_module is not None else None
            ),
            "overview": self._overview,
            "need_illustration": self._need_illustration,
            "generate_speeches": self._generate_speeches,
            "target_lang": self._target_lang,
            "story_length": self._story_max_length,
            "story_parts": [part.to_dict() for part in self._story_parts],
        }
        return story_dict

    @staticmethod
    def load_story(directory: str):
        raise NotImplementedError
