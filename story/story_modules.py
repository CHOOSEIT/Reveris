from typing import List
from agents.translationAgent import query_translation
from agents.voiceAgent import query_speech


class StoryModules:
    def __init__(self):
        pass

    def to_prompt_string(self):
        raise NotImplementedError


class HasDisplayableText:
    def __init__(self):
        self._displayed_text = None

    def get_text(self):
        raise NotImplementedError

    def is_displayed_text_set(self):
        return self._displayed_text is not None

    def get_displayed_text(self):
        if self._displayed_text is None:
            return self.get_text()
        return self._displayed_text

    def set_displayed_text(self, displayed_text):
        self._displayed_text = displayed_text


class isTranslatable:
    def __init__(self):
        pass

    def set_translation(self, target_lang: str):
        """
        Query the translation of the text and set it as the displayed text

        Args:
            target_lang (str): the language to translate the text (None -> English, Example: "FR" -> French)
        """
        raise NotImplementedError


class HasDisplayableAndIsTranslatableText(HasDisplayableText, isTranslatable):
    def __init__(self):
        super(HasDisplayableText, self).__init__()
        super(isTranslatable, self).__init__()

    def set_translation(self, target_lang: str):
        if target_lang is None:
            return

        translated_text = query_translation(
            text=self.get_displayed_text(), target_lang=target_lang
        )
        self.set_displayed_text(translated_text)


class canBeSpeechSynthesized:
    def __init__(self):
        self._speech_file_path = None
        pass

    def _get_speech_text(self):
        raise NotImplementedError

    def generate_speech(self):
        filename = query_speech(self._get_speech_text())
        self._speech_file_path = filename

    def has_speech_generated(self):
        return self._speech_file_path is not None

    def get_speech_file_path(self):
        return self._speech_file_path


class TextModule(
    StoryModules, HasDisplayableAndIsTranslatableText, canBeSpeechSynthesized
):
    """
    Text module

    Parameters:
        text (str): the text to display
        displayed_text (str): the text to display
    """

    def __init__(self, text: str, displayed_text: str = None):
        """
        Text module

        Args:
            text (str): the text to display
        """
        super(StoryModules, self).__init__()
        super(HasDisplayableAndIsTranslatableText, self).__init__()
        super(canBeSpeechSynthesized, self).__init__()
        self.text = text
        self.set_displayed_text(displayed_text)

    # Override from HasDisplayableText
    def get_text(self):
        return self.text

    # Override from StoryModules
    def to_prompt_string(self):
        return self.text

    # Override from canBeSpeechSynthesized
    def _get_speech_text(self):
        return self.get_displayed_text()


class ImageModule(StoryModules):
    """
    Image module

    Parameters:
        image_path (str): the path to the image
    """

    def __init__(self, image_path: str):
        """
        Image module

        Args:
            image_path (str): the path to the image
        """
        super(StoryModules, self).__init__()
        self.image_path = image_path

    def get_image_path(self):
        return self.image_path

    # Override from StoryModules
    def to_prompt_string(self):
        return ""


class ChoiceModule(StoryModules, HasDisplayableAndIsTranslatableText):
    """
    Choice module

    Parameters:
        choice (str): the choice text
        displayed_choice_text (str): the displayed choice text
    """

    def __init__(self, choice_text: str, displayed_choice_text: str = None):
        """
        Choice module

        Args:
            choice (str): the choice text
        """
        super(StoryModules, self).__init__()
        super(HasDisplayableAndIsTranslatableText, self).__init__()
        self.choice_text = choice_text
        self.set_displayed_text(displayed_choice_text)

    # Override from HasDisplayableText
    def get_text(self):
        return self.choice_text

    # Override from StoryModules
    def to_prompt_string(self):
        return "->" + self.choice_text

    def __eq__(self, other):
        if other is None:
            return False
        if isinstance(other, ChoiceModule):
            return self.choice_text == other.choice_text
        return False


class PossibleChoicesModule(StoryModules, isTranslatable):
    """
    Possible choices module

    Parameters:
        choices (list[ChoiceModule]): the list of choices
        selected (bool): whether the user has selected a choice
        selected_choice (ChoiceModule): the selected choice
    """

    def __init__(self, choices: List[ChoiceModule]):
        """
        Args:
            choices (list[ChoiceModule]): the list of choices
        """
        super(StoryModules, self).__init__()
        super(isTranslatable, self).__init__()
        self.choices = choices
        self.selected = False
        self.selected_choice = None

    def get_choices(self):
        return self.choices

    def has_selected_choice(self):
        """
        Get whether the user has selected a choice
        """
        return self.selected

    def get_selected_choice(self):
        """
        Get the selected choice

        Returns:
            ChoiceModule: the selected choice or None if no choice has been selected
        """
        if not self.has_selected_choice():
            return None
        return self.selected_choice

    def set_user_choice(self, user_choice):
        """
        Args:
            user_choice (ChoiceModule): the user choice
        """
        self.selected = True
        self.selected_choice = user_choice

    # Override from StoryModules
    def to_prompt_string(self):
        possible_choices_message = ""
        user_choice = self.selected_choice.to_prompt_string() if self.selected else ""

        return possible_choices_message + "\n" + user_choice

    # Override from isTranslatable
    def set_translation(self, target_lang: str):
        for choice in self.choices:
            choice.set_translation(target_lang)
