import time
from story.story_modules import *


def stream_data(text):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.05)


# This is a workaround for the Streamlit execution module (object and type caching)
# https://github.com/streamlit/streamlit/issues/6765
def isinstance_story_modules_streamlit(module: StoryModules, module_type: type):
    """
    Check if a module is of a certain type.

    Args:
        module (StoryModules): the module to check (Ex: a module)
        module_type (StoryModules): the type to check for (Ex: TextModule)
    """

    if isinstance(module, module_type):
        return True

    try:
        module_obj_type = globals()[module.__class__.__name__]
        module = module_obj_type(module)
        return isinstance(module, module_type)
    except:
        return False
