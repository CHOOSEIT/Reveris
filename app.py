import streamlit as st
import time

from story.custom_story import CustomStory
from story.ai_story import AIStory
from streamlit_extras.stylable_container import stylable_container


def stream_data(text):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.05)


if "story" not in st.session_state:
    st.session_state.story = None
if "story_extension_requested" not in st.session_state:
    st.session_state.story_extension_requested = False
if "is_title_displayed" not in st.session_state:
    st.session_state.is_title_displayed = False


def display_parts(parts, new_parts):
    num_of_parts = len(parts)
    for i, part in enumerate(parts):
        if "text" in part:
            if new_parts:
                st.write(stream_data(part["text"]))
            else:
                st.write(part["text"])
        elif "image" in part:
            st.image(part["image"], use_column_width=True)
        elif "possible_choices" in part:
            disabled = i != num_of_parts - 1

            choices = [text["choice"] for text in part["possible_choices"]]
            made_choice = None
            if disabled:
                # This means that the user may have already made a choice
                next_part = parts[i + 1]
                if "user_choice" in next_part:
                    made_choice = next_part["user_choice"]

            create_button = lambda text: st.button(
                text,
                use_container_width=True,
                on_click=enter_user_input,
                args=(text,),
                disabled=disabled,
            )

            for text in choices:
                if made_choice == text:
                    with stylable_container(
                        key=f"selected_button_user_input_{i}",
                        css_styles="""
                        button {
                        border: solid green;
                        color: green;
                        }
                        """,
                    ):
                        create_button(text)
                else:
                    create_button(text)


def start_dreaming():
    st.session_state.story = AIStory(
        title="A village",
        overview="A big village that you explore",
        need_illustration=False,
        story_length=3,
    )
    st.session_state.story_extension_requested = True


def continue_dreaming():
    st.session_state.story_extension_requested = True


def stop_dreaming():
    st.session_state.story = None
    st.session_state.story_extension_requested = False
    st.session_state.is_title_displayed = False


def enter_user_input(text):
    story = st.session_state.story
    story.input_user_answer(text)

    continue_dreaming()


def display_story():
    story = st.session_state.story
    title = story.get_title()
    if title is not None:
        st.title(story.get_title())
        st.session_state.is_title_displayed = True
    display_parts(story.get_formatted_story(), False)


if st.session_state.story is None:
    st.title("💭 Reveris 💭")
    st.button(":rainbow: Start dreaming :rainbow:", on_click=start_dreaming)

else:
    display_story()
    if st.session_state.story_extension_requested:
        story = st.session_state.story
        with st.spinner("Dreaming..."):
            error_code, generated_part = story.generate_next_part()

        if error_code == 0:
            title = story.get_title()
            if title is not None and not st.session_state.is_title_displayed:
                st.title(story.get_title())
                st.session_state.is_title_displayed = True

            display_parts(generated_part, True)
        elif not (error_code == 1 or error_code == 2):
            st.error("An error occurred while generating the story.")
            st.error("Error code: " + str(error_code))

        st.session_state.story_extension_requested = False

    st.button("🚫 Quit", on_click=stop_dreaming)
