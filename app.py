import streamlit as st
import streamlit_app.v1_app as v1_app
import streamlit_app.v2_app as v2_app
import streamlit_app.main_page as main_page
import time


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


# Variable initialization
if "story" not in st.session_state:
    st.session_state.story = None
if "previous_placeholder" not in st.session_state:
    st.session_state.previous_placeholder = None


def start_dreaming(
    _story,
):
    st.session_state.story = _story

    display_app = get_display_app(DISPLAY_VERSION)
    display_app.start_dreaming()


### Main
DISPLAY_VERSION = 2
if st.session_state.story is not None:
    get_display_app(DISPLAY_VERSION).set_display_parameters()
else:
    main_page.set_display_parameters()

# This is a workaround to clear the previous page
# (this prevent the previous page to be displayed as shadow)
if st.session_state.previous_placeholder is not None:
    st.session_state.previous_placeholder.empty()
    time.sleep(0.1)

st.session_state.previous_placeholder = st.empty()
with st.session_state.previous_placeholder.container():

    if st.session_state.story is None:
        main_page.refresh_initial_state()
        main_page.display(start_dreaming)

    else:
        display_app = get_display_app(DISPLAY_VERSION)
        display_app.display()
