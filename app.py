import streamlit as st
import streamlit_app.v1_app as v1_app
import streamlit_app.v2_app as v2_app
import os
import json
import time


from story.story_type.custom_story import CustomStory
from story.story_type.ai_story import AIStory
from story.story_modules import TextModule
from datetime import datetime


def get_display_app(display_version):
    display_app = None
    if display_version == 1:
        display_app = v1_app
    else:
        display_app = v2_app

    # Streamlit does not seems to like state initialization in multiple files.
    if display_app is not None:
        display_app.refresh_initial_state()
    return display_app


### Variable initialization

if "story" not in st.session_state:
    st.session_state.story = None
if "previous_placeholder" not in st.session_state:
    st.session_state.previous_placeholder = None


def start_dreaming(
    _story=None,
):
    if _story is None:
        _story = AIStory(
            need_illustration=True,
            generate_speeches=True,
            story_length=3,
        )

    st.session_state.story = _story

    display_app = get_display_app(DISPLAY_VERSION)
    display_app.start_dreaming()


def load_story(story_path):
    story = AIStory.load_story(story_path)
    start_dreaming(story)


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


### Main
DISPLAY_VERSION = 2

if st.session_state.story is not None:
    get_display_app(DISPLAY_VERSION).set_display_parameters()
else:
    st.set_page_config(layout="centered")

# This is a workaround to clear the previous page
# (this prevent the previous page to be displayed as shadow)
if st.session_state.previous_placeholder is not None:
    st.session_state.previous_placeholder.empty()
    time.sleep(0.1)

st.session_state.previous_placeholder = st.empty()
with st.session_state.previous_placeholder.container():

    if st.session_state.story is None:
        st.title("💭 Reveries 💭")
        st.button(
            r"$\Large\text{🌈 Start dreaming 🌈}$",
            on_click=start_dreaming,
            args=(None,),
            use_container_width=True,
        )

        st.markdown(
            f"""
        <h4>📜 Stories history 📜</h4>
        """,
            unsafe_allow_html=True,
        )
        stories_info = get_story_infos()
        for story_info in stories_info:
            title = story_info["title"]
            lang = story_info["lang"]
            datetime = story_info["datetime"]
            overview = story_info["overview"][:50] + "..."

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
                args=(story_info["path"],),
                key=title_key,
                use_container_width=True,
            )

    else:
        display_app = get_display_app(DISPLAY_VERSION)
        display_app.display()
