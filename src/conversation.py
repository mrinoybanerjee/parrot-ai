import streamlit as st
from src.chatbot import DualChatbot
from src.utils import show_messages
import time

MAX_EXCHANGE_COUNTS = {
    'Short': {'Conversation': 8, 'Debate': 4},
    'Long': {'Conversation': 16, 'Debate': 8}
}
AVATAR_SEED = [123, 42]
engine = 'OpenAI'

def setup_conversation(conversation_container, translate_col, original_col, audio_col, learning_mode,
                       role_dict, language, scenario, proficiency_level, session_length, time_delay):
    if 'dual_chatbots' not in st.session_state:
        generate_button = st.sidebar.button('Generate')
        if generate_button:
            st.session_state["first_time_exec"] = True
            st.session_state['bot1_mesg'] = []
            st.session_state['bot2_mesg'] = []
            st.session_state['message_counter'] = 0

            with conversation_container:
                if learning_mode == 'Conversation':
                    conversation_container.write(f"""#### The following conversation happens between 
                                {role_dict['role1']['name']} and {role_dict['role2']['name']} {scenario} 🎭""")
                else:
                    conversation_container.write(f"""#### Debate 💬: {scenario}""")

                dual_chatbots = DualChatbot(engine, role_dict, language, scenario,
                                            proficiency_level, learning_mode, session_length)
                st.session_state['dual_chatbots'] = dual_chatbots

                for _ in range(MAX_EXCHANGE_COUNTS[session_length][learning_mode]):
                    output1, output2, translate1, translate2 = dual_chatbots.step()

                    mesg_1 = {"role": dual_chatbots.chatbots['role1']['name'], 
                            "content": output1, "translation": translate1, "language": language}
                    mesg_2 = {"role": dual_chatbots.chatbots['role2']['name'], 
                            "content": output2, "translation": translate2, "language": language}
                    
                    new_count = show_messages(mesg_1, mesg_2, 
                                            st.session_state["message_counter"],
                                            time_delay=time_delay, batch=False,
                                            audio=False, translation=False)
                    st.session_state["message_counter"] = new_count

                    st.session_state.bot1_mesg.append(mesg_1)
                    st.session_state.bot2_mesg.append(mesg_2)
                    

    if 'dual_chatbots' in st.session_state:
        if translate_col.button('Translate to English'):
            st.session_state['translate_flag'] = True
            st.session_state['batch_flag'] = True

        if original_col.button('Show original'):
            st.session_state['translate_flag'] = False
            st.session_state['batch_flag'] = True

        if audio_col.button('Play audio'):
            st.session_state['audio_flag'] = True
            st.session_state['batch_flag'] = True

        if 'bot1_mesg' not in st.session_state:
            st.session_state['bot1_mesg'] = []
        if 'bot2_mesg' not in st.session_state:
            st.session_state['bot2_mesg'] = []

        mesg1_list = st.session_state['bot1_mesg']
        mesg2_list = st.session_state['bot2_mesg']
        dual_chatbots = st.session_state['dual_chatbots']

        if st.session_state["first_time_exec"]:
            st.session_state['first_time_exec'] = False
        else:
            with conversation_container:
                if learning_mode == 'Conversation':
                    st.write(f"""#### {role_dict['role1']['name']} and {role_dict['role2']['name']} {scenario} 🎭""")
                else:
                    st.write(f"""#### Debate 💬: {scenario}""")
                
                for mesg_1, mesg_2 in zip(mesg1_list, mesg2_list):
                    new_count = show_messages(mesg_1, mesg_2, 
                                              st.session_state["message_counter"],
                                              time_delay=time_delay,
                                              batch=st.session_state['batch_flag'],
                                              audio=st.session_state['audio_flag'],
                                              translation=st.session_state['translate_flag'])
                    st.session_state["message_counter"] = new_count

        summary_expander = st.expander('Key Learning Points')
        if "summary" not in st.session_state:
            summary = dual_chatbots.summary()
            st.session_state["summary"] = summary
        else:
            summary = st.session_state["summary"]

        with summary_expander:
            st.markdown(f"**Here is the learning summary:**")
            st.write(summary)
