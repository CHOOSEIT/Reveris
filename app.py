import streamlit as st
import time

from story.custom_story import CustomStory
from story.ai_story import AIStory
from streamlit_extras.stylable_container import stylable_container
from story.story_modules import (
    StoryModules,
    ImageModule,
    TextModule,
    ChoiceModule,
    PossibleChoicesModule,
)


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


def display_modules(modules, new_modules):
    for i, module in enumerate(modules):
        if isinstance(module, TextModule):
            choice = module.get_text()
            displayed_text = stream_data(choice) if new_modules else choice
            st.write(displayed_text)
        elif isinstance(module, ImageModule):
            st.image(module.get_image_path(), use_column_width=True)
        elif isinstance(module, PossibleChoicesModule):
            disabled = module.has_selected_choice()
            made_choice = module.get_selected_choice()
            choices = [choice for choice in module.get_choices()]

            create_button = lambda choice: st.button(
                choice.get_choice_text(),
                use_container_width=True,
                on_click=enter_user_input,
                args=(choice,),
                disabled=disabled,
            )

            for choice in choices:
                if made_choice == choice:
                    with stylable_container(
                        key=f"selected_button_user_input_{i}",
                        css_styles="""
                        button {
                        border: solid green;
                        color: green;
                        }
                        """,
                    ):
                        create_button(choice)
                else:
                    create_button(choice)


def start_dreaming():
    st.session_state.story = CustomStory(
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


def enter_user_input(choice: ChoiceModule):
    story = st.session_state.story
    story.input_user_answer(choice)

    continue_dreaming()


def display_story():
    story = st.session_state.story
    title = story.get_title()
    if title is not None:
        st.title(story.get_title())
        st.session_state.is_title_displayed = True
    display_modules(story.get_formatted_story(), False)


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

            display_modules(generated_part, True)
        elif not (error_code == 1 or error_code == 2):
            st.error("An error occurred while generating the story.")
            st.error("Error code: " + str(error_code))

        st.session_state.story_extension_requested = False

    st.button("🚫 Quit", on_click=stop_dreaming)
