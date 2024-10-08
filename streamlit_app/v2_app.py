import streamlit as st
import random
import string
import time

from story.story_modules import (
    ImageModule,
    TextModule,
    ChoiceModule,
    PossibleChoicesModule,
    canBeSpeechSynthesized,
)
from streamlit_extras.stylable_container import stylable_container
from streamlit_app.streamlit_utils import (
    stream_data,
    isinstance_story_modules_streamlit,
)
from typing import List
from pygame import mixer
from openaiAPI import openai_show_usage

### Main functions


def continue_dreaming():
    st.session_state.story_extension_requested = True
    stop_playing_audio()


def stop_dreaming():
    st.session_state.story = None
    st.session_state.story_extension_requested = False
    st.session_state.is_title_displayed = False
    stop_audio()


def enter_user_input(choice: ChoiceModule):
    story = st.session_state.story
    story.input_user_answer(choice)

    continue_dreaming()


### Display functions


def display_module(module, is_new):
    """
    Display a story module.

    Args:
        module (StoryModules): the module to display
        is_new (bool): whether the module is new
    """
    unique_key = "".join(random.choices(string.ascii_letters + string.digits, k=6))
    if isinstance_story_modules_streamlit(module, TextModule):
        choice_text = module.get_displayed_text()
        displayed_text = stream_data(choice_text) if is_new else choice_text

        st.write(displayed_text)
    elif isinstance_story_modules_streamlit(module, PossibleChoicesModule):
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
        st.markdown(
            f"<h1 style='text-align: center; black: grey;'>{title_module.get_displayed_text()}</h1>",
            unsafe_allow_html=True,
        )


def _split_pages(modules) -> List[dict]:
    page_list = []
    started_page = []
    found_image = None
    for module in modules:
        if (
            isinstance_story_modules_streamlit(module, ImageModule)
            and module.has_image_path()
        ):
            if found_image is not None:
                page_list.append(
                    {"image": found_image, "modules": started_page, "displayed": False}
                )
                started_page = []

            found_image = module

        else:
            started_page.append(module)

    page_list.append(
        {"image": found_image, "modules": started_page, "displayed": False}
    )

    return page_list


def _display_page(page, is_new):
    display_story_title()

    def display_buttons():
        b1, b2, b3 = st.columns(3)
        with b1:
            st.button(
                "⬅️",
                on_click=change_page,
                args=(-1,),
                disabled=st.session_state.displayed_page_index == 0
                or st.session_state.story_audio_requested,
                use_container_width=True,
            )
        audio_disabled = not _has_speech_available_page()
        logo = "🔇" if st.session_state.story_audio_requested else "🔊"
        action = stop_audio if st.session_state.story_audio_requested else start_audio
        with b2:
            st.button(
                logo,
                on_click=action,
                disabled=audio_disabled,
                use_container_width=True,
            )
        with b3:
            st.button(
                "➡️",
                on_click=change_page,
                args=(+1,),
                disabled=st.session_state.displayed_page_index
                == len(st.session_state.pages) - 1
                or st.session_state.story_audio_requested,
                use_container_width=True,
            )
        st.button("🚫 Quit", on_click=stop_dreaming, use_container_width=True)

    number_of_modules = len(page["modules"])
    if page["image"] is None:
        _, col, _ = st.columns([0.25, 0.5, 0.25], gap="medium")
        with col:
            display_modules(page["modules"], is_new)
            display_buttons()
        pass
    else:
        col1, col2 = st.columns([0.7, 0.3], gap="medium")

        with col1:
            st.image(page["image"].get_image_path(), use_column_width=True)
            display_buttons()

        with col2:
            display_modules(page["modules"], is_new)


def display_page():
    page_number = st.session_state.displayed_page_index
    page = st.session_state.pages[page_number]
    _display_page(page, not st.session_state.pages[page_number]["displayed"])
    st.session_state.pages[page_number]["displayed"] = True


def change_page(delta):
    st.session_state.displayed_page_index += delta


def start_audio():
    st.session_state.story_audio_requested = True
    st.session_state.pages[st.session_state.displayed_page_index]["displayed"] = True


def stop_audio():
    stop_playing_audio()
    st.session_state.story_audio_requested = False


def stop_playing_audio():
    if mixer.music.get_busy():
        mixer.music.stop()


def _next_audio_page():
    page_index = st.session_state.displayed_page_index
    if page_index != len(st.session_state.pages) - 1:
        page_index += 1
        st.session_state.displayed_page_index = page_index
        st.session_state.pages[page_index]["displayed"] = True
        st.rerun()


def _has_speech_available_page():
    page_number = st.session_state.displayed_page_index
    page = st.session_state.pages[page_number]
    for module in page["modules"]:
        if (
            isinstance_story_modules_streamlit(module, canBeSpeechSynthesized)
            and module.has_speech_generated()
        ):
            return True
    return False


def play_audio():
    if st.session_state.story_audio_requested:
        page_number = st.session_state.displayed_page_index
        page = st.session_state.pages[page_number]
        num_modules = len(page["modules"])

        index = 0
        while index < num_modules and st.session_state.story_audio_requested:
            module = page["modules"][index]
            if (
                isinstance_story_modules_streamlit(module, canBeSpeechSynthesized)
                and module.has_speech_generated()
            ):
                mixer.music.load(module.get_speech_file_path())
                mixer.music.play()

                while mixer.music.get_busy():  # wait for speech to finish playing
                    time.sleep(1)
            index += 1

        if st.session_state.story_audio_requested:
            _next_audio_page()


# Main


def set_display_parameters(page_title, page_icon):
    st.set_page_config(layout="wide", page_title=page_title, page_icon=page_icon)


def refresh_initial_state():
    mixer.init()
    if "story_extension_requested" not in st.session_state:
        st.session_state.story_extension_requested = False
    if "is_title_displayed" not in st.session_state:
        st.session_state.is_title_displayed = False
    if "pages" not in st.session_state:
        st.session_state.pages = []
    if "displayed_page_index" not in st.session_state:
        st.session_state.displayed_page_index = -1
    if "story_audio_requested" not in st.session_state:
        st.session_state.story_audio_requested = False


def start_dreaming():
    st.session_state.story_extension_requested = True
    st.session_state.story_audio_requested = False
    st.session_state.displayed_page_index = -1
    st.session_state.pages = []


def display():
    if st.session_state.story_extension_requested:
        story = st.session_state.story
        with st.spinner("Dreaming..."):
            error_code, generated_parts = story.generate_next_parts()

        openai_show_usage()

        if error_code == 3 or error_code == 4:
            st.error("An error occurred while generating the story.")
            st.error("Error code: " + str(error_code))
        elif error_code == 0:
            added_page = False
            for generated_part in generated_parts:
                pages = _split_pages(generated_part.get_modules())
                if len(pages) > 0:
                    added_page = True
                    st.session_state.pages.extend(pages)

            if added_page:
                st.session_state.displayed_page_index += 1

        st.session_state.story_extension_requested = False
        if st.session_state.story_audio_requested:
            st.session_state.pages[st.session_state.displayed_page_index][
                "displayed"
            ] = True

    display_page()

    play_audio()
