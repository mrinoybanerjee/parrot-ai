""" This script defines the Streamlit app for the Parrot-AI project. """

import os
import streamlit as st
from src.conversation import setup_conversation
from src.utils import initialize_session_state

# Get the backend server URL from environment variables
BACKEND_SERVER = os.environ.get('BACKEND_SERVER', 'http://localhost:8000')

# Set the title of the app
st.set_page_config(page_title='Parrot AI', page_icon='🦜', layout='centered')
st.title('Parrot AI')

# Set the description of the app
st.markdown("Practice a conversation or debate in your target language. "
            "Choose your settings, then select Generate.")
st.caption("Generation uses your configured model server. Play audio sends text to Google TTS.")

# Define the language learning settings
LANGUAGES = ['English', 'Hindi', 'German', 'Spanish', 'French']
SESSION_LENGTHS = ['Short', 'Long']
PROFICIENCY_LEVELS = ['Beginner', 'Intermediate', 'Advanced']

# Add a selectbox for learning mode
learning_mode = st.sidebar.selectbox('Learning mode', ('Conversation', 'Debate'))

# Configure settings based on the selected learning mode
if learning_mode == 'Conversation':
    role1 = st.sidebar.text_input('First role', 'Customer')
    action1 = st.sidebar.text_input('First action', 'ordering food')
    role2 = st.sidebar.text_input('Second role', 'Waitstaff')
    action2 = st.sidebar.text_input('Second action', 'taking the order')
    scenario = st.sidebar.text_input('Scenario', 'at a restaurant')
    time_delay = 2

    # Configure role dictionary
    role_dict = {
        'role1': {'name': role1, 'action': action1},
        'role2': {'name': role2, 'action': action2}
    }

else:
    scenario = st.sidebar.text_input('Debate topic', 'Climate change')

    # Configure role dictionary
    role_dict = {
        'role1': {'name': 'Proponent'},
        'role2': {'name': 'Opponent'}
    }
    time_delay = 5

# Add selectboxes for language, session length, and proficiency level
language = st.sidebar.selectbox('Language', LANGUAGES)
session_length = st.sidebar.selectbox('Session length', SESSION_LENGTHS)
proficiency_level = st.sidebar.selectbox('Proficiency', PROFICIENCY_LEVELS)

# Initialize session states
initialize_session_state()

# Define the button layout at the beginning
translate_col, original_col, audio_col = st.columns(3)

# Create the conversation container
conversation_container = st.container()

# Set up the conversation with the provided settings
setup_conversation(conversation_container, translate_col, original_col, audio_col,
                   learning_mode, role_dict, language, scenario, proficiency_level,
                   session_length, time_delay)
