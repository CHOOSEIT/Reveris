from typing import List


class StoryModules:
    def __init__(self):
        pass

    def to_prompt_string(self):
        raise NotImplementedError


class TextModule(StoryModules):
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
        self.text = text
        self.displayed_text = displayed_text

    def get_text(self):
        return self.text

    def to_prompt_string(self):
        return self.text

    def get_displayed_text(self):
        if self.displayed_text is None:
            return self.text
        return self.displayed_text

    def set_displayed_text(self, displayed_text):
        self.displayed_text = displayed_text


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
        self.image_path = image_path

    def get_image_path(self):
        return self.image_path

    def to_prompt_string(self):
        return ""


class ChoiceModule(StoryModules):
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
        self.choice_text = choice_text
        self.displayed_choice_text = displayed_choice_text

    def get_choice_text(self):
        return self.choice_text

    def get_displayed_choice_text(self):
        if self.displayed_choice_text is None:
            return self.choice_text
        return self.displayed_choice_text

    def set_displayed_choice_text(self, displayed_choice_text):
        self.displayed_choice_text = displayed_choice_text

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

    def to_prompt_string(self):
        possible_choices_message = ""
        user_choice = self.selected_choice.to_prompt_string() if self.selected else ""

        return possible_choices_message + "\n" + user_choice

    def set_user_choice(self, user_choice):
        """
        Args:
            user_choice (ChoiceModule): the user choice
        """
        self.selected = True
        self.selected_choice = user_choice
