""" This module contains the functions for generating and displaying a conversation
between two chatbots. """

import streamlit as st
import requests
import os
from src.utils import show_messages

# Set the backend server URL from environment variable or default to localhost
BACKEND_SERVER = os.environ.get('BACKEND_SERVER', 'http://localhost:8000')

# Define the maximum number of exchanges for different session lengths and
# learning modes
MAX_EXCHANGE_COUNTS = {
    'Short': {'Conversation': 4, 'Debate': 4},
    'Long': {'Conversation': 8, 'Debate': 8}
}

# Define avatar seed for consistent avatar generation
AVATAR_SEED = [123, 42]

# Define the engine to use for the chatbot
ENGINE = 'OpenAI'


def generate_conversation(role_dict, language, scenario, proficiency_level,
                          learning_mode, session_length):
    """
    Generates a conversation based on the provided parameters by sending a request to
      the backend server.

    Args:
        role_dict (dict): Dictionary containing role information for the conversation.
        language (str): Language of the conversation.
        scenario (str): Scenario for the conversation.
        proficiency_level (str): Proficiency level of the language learner.
        learning_mode (str): Learning mode, either 'Conversation' or 'Debate'.
        session_length (str): Length of the session, either 'Short' or 'Long'.

    Returns:
        dict: JSON response containing the generated conversation.

    Raises:
        requests.RequestException: If there is an error communicating with the
          backend server.
    """
    try:
        response = requests.post(f"{BACKEND_SERVER}/generate_conversation", json={
            "engine": ENGINE,
            "role_dict": role_dict,
            "language": language,
            "scenario": scenario,
            "proficiency_level": proficiency_level,
            "learning_mode": learning_mode,
            "session_length": session_length
        })
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error communicating with backend server: {str(e)}")
        return None


def setup_conversation(conversation_container, translate_col, original_col, audio_col,
                       learning_mode, role_dict, language, scenario, proficiency_level,
                       session_length, time_delay):
    """
    Sets up the conversation UI and handles the logic for generating and displaying the
      conversation.

    Args:
        conversation_container (streamlit.container): Streamlit container to display
          the conversation.
        translate_col (streamlit.column): Streamlit column for the translate button.
        original_col (streamlit.column): Streamlit column for the original text button.
        audio_col (streamlit.column): Streamlit column for the audio play button.
        learning_mode (str): Learning mode, either 'Conversation' or 'Debate'.
        role_dict (dict): Dictionary containing role information for the conversation.
        language (str): Language of the conversation.
        scenario (str): Scenario for the conversation.
        proficiency_level (str): Proficiency level of the language learner.
        session_length (str): Length of the session, either 'Short' or 'Long'.
        time_delay (int): Time delay between messages.
    """
    if st.sidebar.button('Generate'):
        # Reset the conversation on the backend
        requests.post(f"{BACKEND_SERVER}/reset_conversation")
        st.session_state["first_time_exec"] = True
        st.session_state['bot1_mesg'] = []
        st.session_state['bot2_mesg'] = []
        st.session_state['message_counter'] = 0

        with conversation_container:
            # Display the conversation or debate scenario
            if learning_mode == 'Conversation':
                st.write(
                    "#### The following conversation happens between\n"
                    f"{role_dict['role1']['name']} and "
                    f"{role_dict['role2']['name']} "
                    f"{scenario} 🎭"
                )
            else:
                st.write(f"""#### Debate 💬: {scenario}""")

            st.session_state['dual_chatbots'] = True
            # Generate and display the conversation
            with st.spinner('Generating conversation...'):
                for _ in range(MAX_EXCHANGE_COUNTS[session_length][learning_mode]):
                    result = generate_conversation(role_dict, language, scenario,
                                                   proficiency_level, learning_mode,
                                                   session_length)
                    if result:
                        output1, output2, translate1, translate2 = (
                            result["response1"],
                            result["response2"],
                            result["translate1"],
                            result["translate2"]
                        )
                        mesg_1 = {"role": role_dict['role1']['name'],
                                  "content": output1, "translation": translate1,
                                  "language": language}
                        mesg_2 = {"role": role_dict['role2']['name'],
                                  "content": output2, "translation": translate2,
                                  "language": language}
                        new_count = show_messages(mesg_1, mesg_2,
                                                  st.session_state["message_counter"],
                                                  time_delay=time_delay, batch=False,
                                                  audio=False, translation=False)
                        st.session_state["message_counter"] = new_count

                        st.session_state.bot1_mesg.append(mesg_1)
                        st.session_state.bot2_mesg.append(mesg_2)

    if 'dual_chatbots' in st.session_state:
        # Display buttons for translating, showing original text, and playing audio
        if translate_col.button('Translate to English'):
            st.session_state['translate_flag'] = True
            st.session_state['batch_flag'] = True

        if original_col.button('Show original'):
            st.session_state['translate_flag'] = False
            st.session_state['batch_flag'] = True

        if audio_col.button('Play audio'):
            st.session_state['audio_flag'] = True
            st.session_state['batch_flag'] = True

        # Use dictionary access instead of attribute access
        mesg1_list = st.session_state['bot1_mesg']
        mesg2_list = st.session_state['bot2_mesg']

        # Display the conversation history
        if st.session_state["first_time_exec"]:
            st.session_state['first_time_exec'] = False
        else:
            with conversation_container:
                if learning_mode == 'Conversation':
                    st.write(
                        f"#### {role_dict['role1']['name']} and "
                        f"{role_dict['role2']['name']} {scenario} 🎭"
                    )
                else:
                    st.write(f"#### Debate 💬: {scenario}")
                for mesg_1, mesg_2 in zip(mesg1_list, mesg2_list):
                    new_count = show_messages(
                        mesg_1,
                        mesg_2,
                        st.session_state["message_counter"],
                        time_delay=time_delay,
                        batch=st.session_state['batch_flag'],
                        audio=st.session_state['audio_flag'],
                        translation=st.session_state['translate_flag']
                    )
                    st.session_state["message_counter"] = new_count

        # Generate and display the learning summary
        summary_expander = st.expander('Key Learning Points')
        if "summary" not in st.session_state:
            with st.spinner('Generating summary...'):
                response = requests.post(f"{BACKEND_SERVER}/generate_summary", json={
                    "engine": ENGINE,
                    "role_dict": role_dict,
                    "language": language,
                    "scenario": scenario,
                    "proficiency_level": proficiency_level,
                    "learning_mode": learning_mode,
                    "session_length": session_length
                })
                if response.status_code == 200:
                    summary = response.json()["summary"]
                    st.session_state["summary"] = summary
                else:
                    st.error("Failed to generate summary")
                    summary = "Failed to generate summary"
        else:
            summary = st.session_state["summary"]

        with summary_expander:
            st.markdown("**Here is the learning summary:**")
            st.write(summary)
