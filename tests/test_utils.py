import pytest
from src.utils import show_messages, initialize_session_state
from io import BytesIO
from gtts import gTTS
import streamlit as st

def test_initialize_session_state():
    # Mock Streamlit session state for testing
    if "bot1_mesg" in st.session_state:
        del st.session_state["bot1_mesg"]
    if "bot2_mesg" in st.session_state:
        del st.session_state["bot2_mesg"]
    initialize_session_state()
    assert "bot1_mesg" in st.session_state
    assert "bot2_mesg" in st.session_state

def test_show_messages():
    mesg_1 = {"role": "Customer", "content": "नमस्ते", "translation": "Hello", "language": "Hindi"}
    mesg_2 = {"role": "Waitstaff", "content": "स्वागत है", "translation": "Welcome", "language": "Hindi"}
    message_counter = show_messages(mesg_1, mesg_2, message_counter=0, time_delay=1, batch=False, audio=False, translation=False)
    assert isinstance(message_counter, int)

def test_text_to_speech():
    tts = gTTS(text="नमस्ते", lang="hi")
    sound_file = BytesIO()
    tts.write_to_fp(sound_file)
    assert isinstance(sound_file, BytesIO)
