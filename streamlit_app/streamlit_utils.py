import time
from story.story_modules import StoryModules


def stream_data(text):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.05)


def istype_module_streamlit(module: StoryModules, module_type: type):
    """
    Check if a module is of a certain type.

    Args:
        module (StoryModules): the module to check (Ex: a module)
        module_type (StoryModules): the type to check for (Ex: TextModule)
    """
    # Fix for the issue: isinstance(module, module_type) does not work when 'rerunning' the script
    return module.__class__.__name__ == module_type.__name__
