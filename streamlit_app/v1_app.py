import streamlit as st
import random
import string

from story.story import Story
from story.story_modules import (
    ImageModule,
    TextModule,
    ChoiceModule,
    PossibleChoicesModule,
)
from streamlit_extras.stylable_container import stylable_container
from streamlit_app.streamlit_utils import stream_data, isinstance_streamlit

### Display functions


def display_module(module, is_new):
    """
    Display a story module.

    Args:
        module (StoryModules): the module to display
        is_new (bool): whether the module is new
    """
    unique_key = "".join(random.choices(string.ascii_letters + string.digits, k=6))
    if isinstance_streamlit(module, TextModule):
        choice_text = module.get_displayed_text()
        displayed_text = stream_data(choice_text) if is_new else choice_text
        if module.has_speech_generated():
            st.audio(module.get_speech_file_path(), format="audio/mp3")

        st.write(displayed_text)
    elif isinstance_streamlit(module, ImageModule):
        st.image(module.get_image_path(), use_column_width=True)
    elif isinstance_streamlit(module, PossibleChoicesModule):
        disabled = module.has_selected_choice()
        made_choice = module.get_selected_choice()
        choices = [choice for choice in module.get_choices()]

        create_button = lambda choice: st.button(
            choice.get_displayed_text(),
            key=f"button_user_input_{unique_key}_{i}",
            use_container_width=True,
            on_click=enter_user_input,
            args=(choice,),
            disabled=disabled,
        )

        for i, choice_text in enumerate(choices):
            if made_choice == choice_text:
                with stylable_container(
                    key=f"selected_button_user_input_{unique_key}_{i}",
                    css_styles="""
                    button {
                    border: solid green;
                    color: green;
                    }
                    """,
                ):
                    create_button(choice_text)
            else:
                create_button(choice_text)


def display_modules(modules, new_modules):
    for module in modules:
        display_module(module, new_modules)


def display_story_title():
    story = st.session_state.story
    title_module = story.get_title_module()
    if title_module is not None:
        st.title(title_module.get_displayed_text())
        st.session_state.is_title_displayed = True


def display_story():
    story = st.session_state.story
    display_story_title()

    story_parts = story.get_story_parts()
    for story_part in story_parts:
        display_modules(story_part, False)


### Main functions


def continue_dreaming():
    st.session_state.story_extension_requested = True


def stop_dreaming():
    st.session_state.story = None
    st.session_state.story_extension_requested = False
    st.session_state.is_title_displayed = False


def enter_user_input(choice: ChoiceModule):
    story = st.session_state.story
    story.input_user_answer(choice)

    continue_dreaming()


# Main


def refresh_initial_state():
    if "story_extension_requested" not in st.session_state:
        st.session_state.story_extension_requested = False
    if "is_title_displayed" not in st.session_state:
        st.session_state.is_title_displayed = False


def start_dreaming():
    st.session_state.story_extension_requested = True


def display():
    st.set_page_config(layout="centered")
    display_story()
    if st.session_state.story_extension_requested:
        story = st.session_state.story
        with st.spinner("Dreaming..."):
            error_code, generated_part = story.generate_next_part()

        if error_code == 0:
            if not st.session_state.is_title_displayed:
                display_story_title()

            display_modules(generated_part, True)
        elif not (error_code == 1 or error_code == 2):
            st.error("An error occurred while generating the story.")
            st.error("Error code: " + str(error_code))

        st.session_state.story_extension_requested = False

    st.button("🚫 Quit", on_click=stop_dreaming)
