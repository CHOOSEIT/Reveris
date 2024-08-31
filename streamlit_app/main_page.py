import streamlit as st
import os
import json

from story.story_type.custom_story import CustomStory
from story.story_type.ai_story import AIStory
from story.story_modules import TextModule
from datetime import datetime


# Should be bot available in the OpenAI TTS and DeepL API
AVAILABLE_LANGUAGES = [
    {"code": "EN", "name": "English"},
    {"code": "FR", "name": "French"},
]


def update_story_settings(
    need_illustration=None, generate_speeches=None, story_length=None, target_lang=None
):
    if need_illustration is not None:
        st.session_state.story_parameters["need_illustration"] = need_illustration
    if generate_speeches is not None:
        st.session_state.story_parameters["generate_speeches"] = generate_speeches
    if story_length is not None:
        st.session_state.story_parameters["story_length"] = story_length
    if target_lang is not None:
        st.session_state.story_parameters["target_lang"] = target_lang


def start_dreaming_with_settings(
    need_illustration,
    generate_speeches,
    story_length,
    target_lang,
    start_dreaming_function: callable,
):
    story = AIStory(
        need_illustration=need_illustration,
        generate_speeches=generate_speeches,
        story_length=story_length,
        target_lang=target_lang,
    )
    start_dreaming_function(story)


def load_story(story_path, start_dreaming_function: callable):
    story = AIStory.load_story(story_path)
    start_dreaming_function(story)


def get_story_infos():
    # Get the history of stories

    directory_path = "out/stories"

    # Get a list of folder names
    story_dirs = [
        os.path.join(directory_path, name)
        for name in os.listdir(directory_path)
        if os.path.isdir(os.path.join(directory_path, name))
    ]
    # Open the json
    stories_info = []
    for story_dir in story_dirs:
        story_file = os.path.join(story_dir, "story.json")
        if not os.path.exists(story_file):
            continue
        with open(story_file) as f:
            json_data = json.load(f)

        title_module = TextModule.from_dict(json_data["title"])
        title = title_module.get_displayed_text()

        saved_time = datetime.fromisoformat(json_data["saved_time"]).timestamp()

        lang = json_data["target_lang"]
        if lang == None:
            lang = "en"

        overview = json_data["overview"]

        stories_info.append(
            {
                "title": title,
                "datetime": saved_time,
                "overview": overview,
                "lang": lang,
                "path": story_dir,
            }
        )

    stories_info = sorted(stories_info, key=lambda x: x["datetime"], reverse=True)

    return stories_info


# Main functions


def set_display_parameters(page_title, page_icon):
    st.set_page_config(layout="centered", page_title=page_title, page_icon=page_icon)


def refresh_initial_state():
    if "story_parameters" not in st.session_state:
        st.session_state.story_parameters = {
            "need_illustration": True,
            "generate_speeches": True,
            "story_length": 3,
            "target_lang": "EN",
        }


def display(start_dreaming_function: callable):
    st.title("💭 Reveris 💭")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f"""
        <h4>⚙️ Story parameters ⚙️</h4>
        """,
            unsafe_allow_html=True,
        )

        def update_illustration():
            update_story_settings(
                need_illustration=st.session_state.checkbox_illustration
            )

        st.checkbox(
            "Generate illustrations",
            value=st.session_state.story_parameters["need_illustration"],
            key="checkbox_illustration",
            on_change=update_illustration,
        )

        def update_speeches():
            update_story_settings(generate_speeches=st.session_state.checkbox_speeches)

        st.checkbox(
            "Generate speeches",
            value=st.session_state.story_parameters["generate_speeches"],
            key="checkbox_speeches",
            on_change=update_speeches,
        )

    with col2:
        possible_choices = []
        lang_to_code = {}
        for lang in AVAILABLE_LANGUAGES:
            key = f"{lang['name']} ({lang['code']})"
            code = lang["code"]
            lang_to_code[key] = code

            if code == st.session_state.story_parameters["target_lang"]:
                possible_choices.insert(0, key)
            else:
                possible_choices.append(key)

        def update_language():
            update_story_settings(
                target_lang=lang_to_code[st.session_state.language_select_box]
            )

        st.selectbox(
            "Select your desired languagee:",
            possible_choices,
            key="language_select_box",
            label_visibility="visible",
            on_change=update_language,
        )

        def update_slider_value():
            update_story_settings(story_length=st.session_state.slider_story_length)

        st.slider(
            "Select the length of the story",
            min_value=1,
            max_value=10,
            value=st.session_state.story_parameters["story_length"],
            step=1,
            key="slider_story_length",
            on_change=update_slider_value,
        )

    story_settings = st.session_state.story_parameters
    st.button(
        r"$\Large\text{🌈 Start dreaming 🌈}$",
        on_click=start_dreaming_with_settings,
        args=(
            story_settings["need_illustration"],
            story_settings["generate_speeches"],
            story_settings["story_length"],
            story_settings["target_lang"],
            start_dreaming_function,
        ),
        use_container_width=True,
    )

    st.markdown(
        f"""
    <h3>📜 Stories history 📜</h3>
    """,
        unsafe_allow_html=True,
    )
    stories_info = get_story_infos()
    for story_info in stories_info:
        title = story_info["title"]
        lang = story_info["lang"]

        title_key = title.replace(" ", "_")
        latex_button = r"""$
                \Large\text{[TITLE]}
                $
                    """.replace(
            r"\n", ""
        ).replace(
            "[TITLE]", title
        )

        st.button(
            label=latex_button,
            on_click=load_story,
            args=(
                story_info["path"],
                start_dreaming_function,
            ),
            key=title_key,
            use_container_width=True,
        )
