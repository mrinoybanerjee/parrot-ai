"""
Module for chatbot interaction system.
"""

import os
from io import BytesIO
from openai import OpenAI
from dotenv import load_dotenv
from gtts import gTTS

# Load environment variables
load_dotenv()
LLM_SERVER = os.environ.get('LLM_SERVER', 'http://localhost:8080')

# Define language codes for speech synthesis
AUDIO_SPEECH = {
    'English': 'en',
    'Hindi': 'hi',
    'German': 'de',
    'Spanish': 'es',
    'French': 'fr'
}


class Chatbot:
    """
    A class to represent a chatbot using OpenAI's language model.

    Attributes:
        client (OpenAI): The OpenAI client for interacting with the language 
        model.
        memory (list): The conversation history.
        prompt (str): The system prompt for the chatbot.
    """

    def __init__(self, engine, llm_server):
        """
        Initialize the Chatbot with a specific engine.

        Args:
            engine (str): The type of engine to use for the chatbot.
        
        Raises:
            KeyError: If the engine type is unsupported.
        """
        if engine == "OpenAI":
            self.client = OpenAI(
                base_url=f"{llm_server}/v1",
                api_key="sk-no-key-required"
            )
        else:
            raise KeyError("Currently unsupported language model type!")
        self.memory = []
        self.prompt = None

    def instruct(self, role, oppo_role, language, scenario, session_length, 
                 proficiency_level, learning_mode, starter=False):
        """
        Instruct the chatbot with specific conversation parameters.

        Args:
            role (dict): The role of the chatbot.
            oppo_role (dict): The role of the opponent chatbot.
            language (str): The language of the conversation.
            scenario (str): The scenario of the conversation.
            session_length (str): The length of the session
              ('Short' or 'Long').
            proficiency_level (str): The proficiency level of the language
            learner.
            learning_mode (str): The learning mode
            ('Conversation' or 'Debate').
            starter (bool, optional): Whether the chatbot starts the
            conversation. Defaults to False.
        """
        self.role = role
        self.oppo_role = oppo_role
        self.language = language
        self.scenario = scenario
        self.session_length = session_length
        self.proficiency_level = proficiency_level
        self.learning_mode = learning_mode
        self.starter = starter
        self.prompt = self._specify_system_message()

    def _specify_system_message(self):
        """
        Specify the system message based on the chatbot context.

        Returns:
            str: The system message for the chatbot.

        Raises:
            KeyError: If the proficiency level or learning mode is unsupported.
        """
        exchange_counts_dict = {
            'Short': {'Conversation': 4, 'Debate': 4},
            'Long': {'Conversation': 8, 'Debate': 8}
        }
        exchange_counts = exchange_counts_dict[self.session_length][self.learning_mode]

        argument_num_dict = {
            'Beginner': 4,
            'Intermediate': 6,
            'Advanced': 8
        }

        # Define language requirements based on proficiency level
        if self.proficiency_level == 'Beginner':
            lang_requirement = "use basic and simple vocabulary and sentence structures. Avoid idioms, slang, and complex grammatical constructs."
        elif self.proficiency_level == 'Intermediate':
            lang_requirement = "use a moderate range of vocabulary and varied sentence structures. You can include some common idioms and colloquial expressions, but avoid highly technical language or complex literary expressions."
        elif self.proficiency_level == 'Advanced':
            lang_requirement = "use sophisticated vocabulary, complex sentence structures, idioms, colloquial expressions, and technical language where appropriate."
        else:
            raise KeyError('Currently unsupported proficiency level!')

        # Define the prompt for Conversation mode
        if self.learning_mode == 'Conversation':
            prompt = f"""You are an AI assistant participating in a role-playing conversation.
            Your role: {self.role['name']} {self.role['action']}
            Your conversation partner's role: {self.oppo_role['name']} {self.oppo_role['action']}
            Scenario: {self.scenario}

            Important instructions:
            1. Respond ONLY as your character ({self.role['name']}).
            2. Generate ONLY ONE response at a time.
            3. Do NOT generate responses for your conversation partner.
            4. Keep your responses concise and relevant to the ongoing conversation.
            5. Use ONLY {self.language}. Do not translate or use any other language.
            6. {lang_requirement}
            7. Ensure your responses are natural and typical for this scenario in {self.language}-speaking cultures.
            8. The entire conversation should not exceed {exchange_counts} exchanges.

            Remember: You are helping language learners practice {self.language} at a {self.proficiency_level} level.
            Wait for your conversation partner's input before responding."""

        # Define the prompt for Debate mode
        elif self.learning_mode == 'Debate':
            prompt = f"""You are an AI assistant participating in a debate.
            Your role: {self.role['name']}
            Debate topic: {self.scenario}

            Important instructions:
            1. Argue ONLY from your perspective as {self.role['name']}.
            2. Generate ONLY ONE response at a time.
            3. Do NOT generate arguments for your opponent.
            4. Keep your responses focused and relevant to the debate topic.
            5. Use ONLY {self.language}. Do not translate or use any other language.
            6. {lang_requirement}
            7. Limit each of your responses to no more than {argument_num_dict[self.proficiency_level]} sentences.
            8. The entire debate should not exceed {exchange_counts} exchanges.

            Remember: You are helping language learners practice {self.language} at a {self.proficiency_level} level.
            Wait for your opponent's argument before responding."""

        else:
            raise KeyError('Currently unsupported learning mode!')

        if self.starter:
            prompt += "\nYou are starting the conversation. Make an appropriate opening statement or question."
        else:
            prompt += f"\nWait for the {self.oppo_role['name']}'s statement before responding."

        return prompt

    def generate_response(self, input_text):
        """
        Generate a response based on the input text.

        Args:
            input_text (str): The input text from the user.

        Returns:
            str: The generated response from the chatbot.

        Raises:
            ValueError: If the chatbot has not been instructed.
        """
        if self.prompt is None:
            raise ValueError("Chatbot has not been instructed. Call instruct() before generate_response().")
        messages = [
            {"role": "system", "content": self.prompt},
        ]

        max_tokens = 4096 - 500
        context_tokens = 0
        for mem in reversed(self.memory):
            context_tokens += len(mem['text'].split())
            if context_tokens > max_tokens:
                break
            messages.append({"role": "user" if mem['role'] != self.role['name'] else "assistant", "content": mem['text']})

        messages.append({"role": "user", "content": input_text})

        response = self.client.chat.completions.create(
            model="LLaMA_CPP",
            messages=messages
        )
        return response.choices[0].message.content.replace("</s>", "").strip()

    def step(self, input_text):
        """
        Perform a conversation step with the chatbot.

        Args:
            input_text (str): The input text from the user.

        Returns:
            tuple: The response from the chatbot and its translation.
        """
        response = self.generate_response(input_text)
        self.memory.append({"role": self.role['name'], "text": response})
        translate = self.translate(response)
        return response, translate

    def translate(self, message):
        """
        Translate a message from the chatbot's language to English.

        Args:
            message (str): The message to translate.

        Returns:
            str: The translated message.
        """
        if self.language == 'English':
            translation = 'Translation: ' + message
        else:
            instruction = f"Translate the following sentence from {self.language} to English: {message}"
            translation = self.generate_response(instruction)
        return translation

    def text_to_speech(self, message):
        """
        Convert a text message to speech.

        Args:
            message (str): The message to convert to speech.

        Returns:
            BytesIO: The audio file of the speech.
        """
        tts = gTTS(text=message, lang=AUDIO_SPEECH[self.language])
        sound_file = BytesIO()
        tts.write_to_fp(sound_file)
        return sound_file

    def _reset_conversation_history(self):
        """Reset the conversation history."""
        self.memory = []


class DualChatbot:
    """
    A class to represent a dual chatbot system for role-playing conversations.

    Attributes:
        engine (str): The type of engine to use for the chatbots.
        proficiency_level (str): The proficiency level of the language learner.
        language (str): The language of the conversation.
        chatbots (dict): The dictionary containing the chatbots for each role.
        session_length (str): The length of the session ('Short' or 'Long').
        conversation_history (list): The conversation history.
        current_speaker (str): The current speaker ('role1' or 'role2').
    """

    def __init__(self, engine, role_dict, language, scenario, proficiency_level, learning_mode, session_length, llm_server):
        """
        Initialize the DualChatbot with specific conversation parameters.

        Args:
            engine (str): The type of engine to use for the chatbots.
            role_dict (dict): The dictionary containing the roles for each chatbot.
            language (str): The language of the conversation.
            scenario (str): The scenario of the conversation.
            proficiency_level (str): The proficiency level of the language learner.
            learning_mode (str): The learning mode ('Conversation' or 'Debate').
            session_length (str): The length of the session ('Short' or 'Long').
        """
        self.engine = engine
        self.proficiency_level = proficiency_level
        self.language = language
        self.chatbots = role_dict
        for k in role_dict.keys():
            self.chatbots[k].update({'chatbot': Chatbot(engine, llm_server)})

        self.chatbots['role1']['chatbot'].instruct(role=self.chatbots['role1'],
                                                   oppo_role=self.chatbots['role2'],
                                                   language=language, scenario=scenario,
                                                   session_length=session_length,
                                                   proficiency_level=proficiency_level,
                                                   learning_mode=learning_mode, starter=True)

        self.chatbots['role2']['chatbot'].instruct(role=self.chatbots['role2'],
                                                   oppo_role=self.chatbots['role1'],
                                                   language=language, scenario=scenario,
                                                   session_length=session_length,
                                                   proficiency_level=proficiency_level,
                                                   learning_mode=learning_mode, starter=False)

        self.session_length = session_length
        self.conversation_history = []
        self.current_speaker = 'role1'

    def step(self):
        """
        Perform a conversation step for the dual chatbot system.

        Returns:
            tuple: The responses and translations from both chatbots.
        """
        if not self.conversation_history:
            input_text = "Start the conversation."
        else:
            input_text = self.conversation_history[-1]['text']

        current_chatbot = self.chatbots[self.current_speaker]['chatbot']
        response, translate = current_chatbot.step(input_text)

        self.conversation_history.append({
            "bot": self.chatbots[self.current_speaker]['name'],
            "text": response
        })

        self.current_speaker = 'role2' if self.current_speaker == 'role1' else 'role1'

        next_chatbot = self.chatbots[self.current_speaker]['chatbot']
        response2, translate2 = next_chatbot.step(response)

        self.conversation_history.append({
            "bot": self.chatbots[self.current_speaker]['name'],
            "text": response2
        })

        self.current_speaker = 'role2' if self.current_speaker == 'role1' else 'role1'

        return response, response2, translate, translate2

    def summary(self):
        """
        Generate a summary of the conversation.

        Returns:
            str: The summary of the conversation.
        """
        script = "\n".join([f"{entry['bot']}: {entry['text']}" for entry in self.conversation_history])
        instruction = f"""The following text is a simulated conversation in
        {self.language}. The goal of this text is to aid {self.language} learners to learn
        real-life usage of {self.language}. Therefore, your task is to summarize the key
        learning points based on the given text. Specifically, you should summarize
        the key vocabulary, grammar points, and function phrases that could be important
        for students learning {self.language}. Your summary should be conducted in English, but
        use examples from the text in the original language where appropriate.
        Remember your target students have a proficiency level of
        {self.proficiency_level} in {self.language}. Your summarization must match with their
        proficiency level.

        The conversation is: \n{script}"""

        summary = self.chatbots['role1']['chatbot'].generate_response(instruction)
        return summary