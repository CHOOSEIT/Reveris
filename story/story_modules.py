from typing import List


class StoryModules:
    def __init__(self):
        pass

    def to_prompt_string(self):
        raise NotImplementedError


class TextModule(StoryModules):
    """
    Text module

    Args:
        text (str): the text to display
    """

    def __init__(self, text: str):
        self.text = text

    def get_text(self):
        return self.text

    def to_prompt_string(self):
        return self.text


class ImageModule(StoryModules):
    """
    Image module

    Args:
        image_path (str): the path to the image
    """

    def __init__(self, image_path: str):
        self.image_path = image_path

    def get_image_path(self):
        return self.image_path

    def to_prompt_string(self):
        return ""


class ChoiceModule(StoryModules):
    """
    Choice module

    Args:
        choice (str): the choice text
    """

    def __init__(self, choice_text: str):
        self.choice_text = choice_text

    def get_choice_text(self):
        return self.choice_text

    def to_prompt_string(self):
        return "->" + self.choice_text

    def __eq__(self, other):
        if other is None:
            return False
        if isinstance(other, ChoiceModule):
            return self.choice_text == other.choice_text
        return False


class PossibleChoicesModule(StoryModules):
    """
    Possible choices module

    Args:
        choices (list[Choice]): the list of choices
    """

    def __init__(self, choices: List[ChoiceModule]):
        self.choices = choices

    def get_choices(self):
        return self.choices

    def to_prompt_string(self):
        return ""
