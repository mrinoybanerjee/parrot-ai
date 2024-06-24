"""This module contains helper functions to initialize session state and display messages."""

from io import BytesIO
import time
import streamlit as st
from streamlit_chat import message
from gtts import gTTS

# Define language codes for speech synthesis
AUDIO_SPEECH = {
    'English': 'en',
    'Hindi': 'hi',
    'German': 'de',
    'Spanish': 'es',
    'French': 'fr'
}

# Define avatar seeds for consistent avatar generation
AVATAR_SEED = [123, 42]

def initialize_session_state():
    """
    Initialize the session state variables for the Streamlit application.
    Ensures that all required session state variables are set.
    """
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
    """
    Display conversation exchanges. This helper function supports
    displaying original texts, translated texts, and audio speech.
    
    Args:
        mesg_1 (dict): The message dictionary for the first speaker.
        mesg_2 (dict): The message dictionary for the second speaker.
        message_counter (int): The message counter for the conversation.
        time_delay (int): The time delay between messages.
        batch (bool): Whether to show the messages in batch.
        audio (bool): Whether to show the audio speech.
        translation (bool): Whether to show the translated messages.
        
    Returns:
        int: The updated message counter.
    """
    for i, mesg in enumerate([mesg_1, mesg_2]):
        # Show original exchange
        message(f"{mesg['content']}", is_user=i==1, avatar_style="bottts",
                seed=AVATAR_SEED[i],
                key=message_counter)
        message_counter += 1

        # Mimic time interval between conversations
        if not batch:
            time.sleep(time_delay)

        # Show translated exchange if translation flag is set
        if translation:
            message(f"{mesg['translation']}", is_user=i==1, avatar_style="bottts",
                    seed=AVATAR_SEED[i], 
                    key=message_counter)
            message_counter += 1

        # Append audio to the exchange if audio flag is set
        if audio:
            tts = gTTS(text=mesg['content'], lang=AUDIO_SPEECH[mesg_1['language']])
            sound_file = BytesIO()
            tts.write_to_fp(sound_file)
            st.audio(sound_file)

    return message_counter

def text_to_speech(text, lang):
    """
    Convert the given text to speech using Google Text-to-Speech (gTTS).

    Args:
        text (str): The text to be converted to speech.
        lang (str): The language code for the speech synthesis.

    Returns:
        BytesIO: A BytesIO object containing the audio data.
    """
    tts = gTTS(text=text, lang=lang)
    sound_file = BytesIO()
    tts.write_to_fp(sound_file)
    return sound_file
