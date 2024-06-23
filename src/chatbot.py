""" Module for chatbot interaction system. """

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
    Class definition for a single chatbot.
    
    Attributes:
        client (OpenAI): The OpenAI client for interacting with the language model.
        memory (list): A list to store the conversation history.
        prompt (str): The system prompt for the chatbot.
    """

    def __init__(self, engine):
        """
        Select backbone large language model.
        
        Args:
            engine (str): The language model to use.
        """
        # Instantiate llm
        if engine == "OpenAI":
            self.client = OpenAI(
                base_url=f"{LLM_SERVER}/v1",
                api_key="sk-no-key-required"
            )
        else:
            raise KeyError("Currently unsupported language model type!")
        # Initialize conversation memory
        self.memory = []
        self.prompt = None

    def instruct(self, role, oppo_role, language, scenario,
                 session_length, proficiency_level,
                 learning_mode, starter=False):
        """
        Determine the context of chatbot interaction.
        
        Args:
            role (dict): The role of the chatbot.
            oppo_role (dict): The role of the conversation partner.
            language (str): The language to use in the conversation.
            scenario (str): The scenario for the conversation.
            session_length (str): The length of the conversation session.
            proficiency_level (str): The proficiency level of the language learners.
            learning_mode (str): The mode of learning (Conversation or Debate).
            starter (bool): Whether the chatbot is starting the conversation.
            
        Raises:
            KeyError: If the proficiency level is not supported.
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
            KeyError: If the proficiency level is not supported.
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
            lang_requirement = """use basic and simple vocabulary and
            sentence structures. Avoid idioms, slang, and complex grammatical constructs."""
        elif self.proficiency_level == 'Intermediate':
            lang_requirement = """use a moderate range of vocabulary and varied sentence structures. 
            You can include some common idioms and colloquial expressions,
            but avoid highly technical language or complex literary expressions."""
        elif self.proficiency_level == 'Advanced':
            lang_requirement = """use sophisticated vocabulary, complex sentence structures, idioms,
            colloquial expressions, and technical language where appropriate."""
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
        Generate a response to the given input text.
        
        Args:
            input_text (str): The input text to generate a response.
            
        Returns:
            str: The generated response.
        """
        if self.prompt is None:
            raise ValueError("Chatbot has not been instructed. Call instruct() before generate_response().")
        messages = [
            {"role": "system", "content": self.prompt},
        ]

        # Add only the last few messages to stay within the token limit
        max_tokens = 4096 - 500  # Reserve tokens for response and prompt
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
        # Remove </s> from the response
        return response.choices[0].message.content.replace("</s>", "").strip()

    def step(self, input_text):
        """ 
        Generate a response to the given input text and update the conversation history.
        
        Args:
            input_text (str): The input text to generate a response.
            
        Returns:
            str: The generated response.
        """
        response = self.generate_response(input_text)
        self.memory.append({"role": self.role['name'], "text": response})
        translate = self.translate(response)
        return response, translate

    def translate(self, message):
        """
        Translate the given message to the target language.
        
        Args:
            message (str): The message to translate.
        
        Returns:
            str: The translated message.
        
        Raises:
            ValueError: If the language is not supported.
        """
        if self.language == 'English':
            translation = 'Translation: ' + message
        else:
            instruction = f"Translate the following sentence from {self.language} to English: {message}"
            translation = self.generate_response(instruction)
        return translation

    def text_to_speech(self, message):
        """
        Convert the given text to speech.
        
        Args:
            message (str): The text to convert to speech.
            
        Returns:
            BytesIO: The audio file in BytesIO format.
        
        Raises:
            ValueError: If the language is not supported.
        """
        tts = gTTS(text=message, lang=AUDIO_SPEECH[self.language])
        sound_file = BytesIO()
        tts.write_to_fp(sound_file)
        return sound_file

    def _reset_conversation_history(self):
        """
        Reset the conversation history.
        
        Raises:
            ValueError: If the chatbot has not been instructed.
        """
        self.memory = []


class DualChatbot:
    """
    Class definition for a dual chatbot system.
    
    Attributes:
        engine (str): The language model to use.
        proficiency_level (str): The proficiency level of the language learners.
        language (str): The language to use in the conversation.
        chatbots (dict): A dictionary of two chatbots.
        session_length (str): The length of the conversation session.
        conversation_history (list): A list to store the conversation history.
        input1 (str): The input text for the first chatbot.
        input2 (str): The input text for the second chatbot.
    """

    def __init__(self, engine, role_dict, language, scenario, proficiency_level,
                 learning_mode, session_length):
        """
        Initialize the dual chatbot system.
        
        Args:
            engine (str): The language model to use.
            role_dict (dict): A dictionary of two chatbots.
            language (str): The language to use in the conversation.
            scenario (str): The scenario for the conversation.
            proficiency_level (str): The proficiency level of the language learners.
            learning_mode (str): The mode of learning (Conversation or Debate).
            session_length (str): The length of the conversation
            
        Raises:
            KeyError: If the language model is not supported.
        """
        self.engine = engine
        self.proficiency_level = proficiency_level
        self.language = language
        self.chatbots = role_dict
        for k in role_dict.keys():
            self.chatbots[k].update({'chatbot': Chatbot(engine)})

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
        self._reset_conversation_history()


    def step(self):
        """
        Generate a response for the dual chatbot system.
        
        Returns:
            str: The generated response for the first chatbot.
            str: The generated response for the second chatbot.
            str: The translation of the response for the first chatbot.
            str: The translation of the response for the second chatbot.
            
        Raises:
            ValueError: If the chatbots have not been instructed.
        """
        response1, translate1 = self.chatbots['role1']['chatbot'].step(self.input1)
        self.conversation_history.append({"bot": self.chatbots['role1']['name'], "text": response1})

        response2, translate2 = self.chatbots['role2']['chatbot'].step(response1)
        self.conversation_history.append({"bot": self.chatbots['role2']['name'], "text": response2})

        self.input1 = response2

        return response1, response2, translate1, translate2

    def _reset_conversation_history(self):
        """
        Reset the conversation history.
        
        Raises:
            ValueError: If the chatbots have not been instructed.
        """
        self.conversation_history = []
        self.input1 = "Start the conversation."
        self.input2 = ""

    def summary(self):
        """
        Generate a summary of the conversation.
        
        Returns:
            str: The summary of the conversation.
            
        Raises:
            ValueError: If the conversation history is empty.
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
