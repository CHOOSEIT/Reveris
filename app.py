import streamlit as st
import time

from story import Story
from streamlit_extras.stylable_container import stylable_container

# ### FAKE GENERATION
# ### FAKE GENERATION
# ### FAKE GENERATION
# if "statestory_parts" not in st.session_state:
#     st.session_state.statestory_parts = []
# if "it" not in st.session_state:
#     st.session_state.it = 0


# def fake_generation():
#     if st.session_state.it == 0:
#         part = [
#             {"image": "out/img-5XkbU0ugs9hxI5G74gJz1pbG.png"},
#             {
#                 "text": "As you continue walking, the trees begin to thin, and in the distance, you spot a small village nestled in a valley. The rooftops of the cottages glisten under the sun, and a thin column of smoke rises from a chimney, suggesting warmth and life within."
#             },
#             {
#                 "possible_choices": [
#                     {"choice": "Continue exploring the forest"},
#                     {"choice": "Approach the village"},
#                 ]
#             },
#         ]
#     elif st.session_state.it == 1:
#         part = [
#             {
#                 "text": "You approach the village and step onto the cobblestone path leading into its heart. The houses are quaint, with thatched roofs and flower boxes under the windows. Villagers are going about their day, tending to chores, and you can hear the faint sound of laughter and conversation from within the homes."
#             }
#         ]
#     elif st.session_state.it == 2:
#         part = [
#             {
#                 "text": "In the center of the village, you notice a large, inviting tavern with a wooden sign swinging gently in the breeze. The sign reads 'The Wandering Bard.' The aroma of roasted meat and fresh bread wafts through the open door, and you can hear the lively chatter of patrons inside."
#             }
#         ]
#     elif st.session_state.it == 3:
#         part = [
#             {
#                 "text": "You decide to enter the tavern. As you push open the heavy wooden door, a wave of warmth and light greets you. The interior is cozy, with a crackling fire in the hearth and wooden tables scattered around. The tavern is bustling with activity—villagers are gathered in groups, sharing stories, and a bard in the corner is playing a soft melody on a lute."
#             }
#         ]
#     else:
#         part = []

#     st.session_state.it = st.session_state.it + 1
#     st.session_state.statestory_parts.extend(part)
#     return part


# ### FAKE GENERATION
# ### FAKE GENERATION
# ### FAKE GENERATION

########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################


def stream_data(text):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.002)


if "story" not in st.session_state:
    st.session_state.story = None
if "story_extension_requested" not in st.session_state:
    st.session_state.story_extension_requested = False


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
    st.session_state.story = Story(
        "The story", "The overview", need_illustration=False, story_length=3
    )
    st.session_state.story_extension_requested = True


def continue_dreaming():
    st.session_state.story_extension_requested = True


def stop_dreaming():
    st.session_state.story = None
    st.session_state.story_extension_requested = False

    # ### FAKE GENERATION
    # st.session_state.statestory_parts = []
    # st.session_state.it = 0
    # ### FAKE GENERATION


def enter_user_input(text):
    story = st.session_state.story
    story.input_user_answer(text)

    # ### FAKE GENERATION
    # st.session_state.statestory_parts.append({"user_choice": text})
    # ### FAKE GENERATION

    continue_dreaming()


def display_story():
    story = st.session_state.story
    st.title(story.get_title())
    display_parts(story.get_formatted_story(), False)


if st.session_state.story is None:
    st.title("💭 Reveris 💭")
    st.button(":rainbow: Start dreaming :rainbow:", on_click=start_dreaming)

else:
    display_story()
    if st.session_state.story_extension_requested:
        story = st.session_state.story
        with st.spinner("Dreaming..."):
            # ### FAKE GENERATION
            # time.sleep(0.1)
            # generated_part = fake_generation()
            # ### FAKE GENERATION
            error_code, generated_part = story.generate_next_part()

        if error_code == 0:
            display_parts(generated_part, True)
        elif not (error_code == 1 or error_code == 2):
            st.error("An error occurred while generating the story.")
            st.error("Error code: " + str(error_code))

        st.session_state.story_extension_requested = False

    st.button("🚫 Quit", on_click=stop_dreaming)
