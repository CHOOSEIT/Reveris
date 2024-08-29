import streamlit as st
import streamlit_app.v1_app as v1_app

from story.custom_story import CustomStory
from story.ai_story import AIStory


def get_display_app(display_version):
    display_app = None
    if display_version == 1:
        display_app = v1_app

    # Streamlit does not seems to like state initialization in multiple files.
    if display_app is not None:
        display_app.refresh_initial_state()
    return display_app


### Variable initialization

if "story" not in st.session_state:
    st.session_state.story = None


def start_dreaming(display_version):
    st.session_state.story = CustomStory(
        need_illustration=False,
        generate_speeches=False,
        story_length=3,
    )
    display_app = get_display_app(display_version)
    display_app.start_dreaming()


### Main
DISPLAY_VERSION = 1

if st.session_state.story is None:
    st.title("💭 Reveries 💭")
    st.button(
        ":rainbow: Start dreaming :rainbow:",
        on_click=lambda: start_dreaming(DISPLAY_VERSION),
    )

else:
    display_app = get_display_app(DISPLAY_VERSION)
    display_app.display()
