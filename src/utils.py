import streamlit as st
from streamlit_chat import message
from gtts import gTTS
from io import BytesIO
import time

AUDIO_SPEECH = {
    'English': 'en',
    'Hindi': 'hi',
    'German': 'de',
    'Spanish': 'es',
    'French': 'fr'
}
AVATAR_SEED = [123, 42]

def initialize_session_state():
    if "bot1_mesg" not in st.session_state:
        st.session_state["bot1_mesg"] = []

    if "bot2_mesg" not in st.session_state:
        st.session_state["bot2_mesg"] = []

    if 'batch_flag' not in st.session_state:
        st.session_state["batch_flag"] = False

    if 'translate_flag' not in st.session_state:
        st.session_state["translate_flag"] = False

    if 'audio_flag' not in st.session_state:
        st.session_state["audio_flag"] = False

    if 'message_counter' not in st.session_state:
        st.session_state["message_counter"] = 0

def show_messages(mesg_1, mesg_2, message_counter,
                  time_delay, batch=False, audio=False,
                  translation=False):
    """Display conversation exchanges. This helper function supports
    displaying original texts, translated texts, and audio speech."""

    for i, mesg in enumerate([mesg_1, mesg_2]):
        # Show original exchange
        message(f"{mesg['content']}", is_user=i==1, avatar_style="bottts", 
                seed=AVATAR_SEED[i],
                key=message_counter)
        message_counter += 1
        
        # Mimic time interval between conversations
        if not batch:
            time.sleep(time_delay)

        # Show translated exchange
        if translation:
            message(f"{mesg['translation']}", is_user=i==1, avatar_style="bottts", 
                    seed=AVATAR_SEED[i], 
                    key=message_counter)
            message_counter += 1

        # Append audio to the exchange
        if audio:
            tts = gTTS(text=mesg['content'], lang=AUDIO_SPEECH[mesg_1['language']])  
            sound_file = BytesIO()
            tts.write_to_fp(sound_file)
            st.audio(sound_file)

    return message_counter
