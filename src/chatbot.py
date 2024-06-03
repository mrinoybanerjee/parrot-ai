import os
from openai import OpenAI

AUDIO_SPEECH = {
    'English': 'en',
    'German': 'de',
    'Spanish': 'es',
    'French': 'fr',
    'Hindi': 'hi'
}

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

class Chatbot:
    """Class definition for a single chatbot."""
    
    def __init__(self, engine):
        """Select backbone large language model."""
        
        # Instantiate llm
        if engine == "OpenAI":
            self.client = OpenAI()
        else:
            raise KeyError("Currently unsupported language model type!")
        # Initialize conversation memory
        self.memory = []

    def instruct(self, role, oppo_role, language, scenario, 
                 session_length, proficiency_level, 
                 learning_mode, starter=False):
        """Determine the context of chatbot interaction."""
        
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
        """Specify the behavior of the chatbot."""
        
        exchange_counts_dict = {
            'Short': {'Conversation': 8, 'Debate': 4},
            'Long': {'Conversation': 16, 'Debate': 8}
        }
        exchange_counts = exchange_counts_dict[self.session_length][self.learning_mode]
        
        argument_num_dict = {
            'Beginner': 4,
            'Intermediate': 6,
            'Advanced': 8
        }
        
        if self.proficiency_level == 'Beginner':
            lang_requirement = """use as basic and simple vocabulary and
            sentence structures as possible. Must avoid idioms, slang, 
            and complex grammatical constructs."""
        elif self.proficiency_level == 'Intermediate':
            lang_requirement = """use a wider range of vocabulary and a variety of sentence structures. 
            You can include some idioms and colloquial expressions, 
            but avoid highly technical language or complex literary expressions."""
        elif self.proficiency_level == 'Advanced':
            lang_requirement = """use sophisticated vocabulary, complex sentence structures, idioms, 
            colloquial expressions, and technical language where appropriate."""
        else:
            raise KeyError('Currently unsupported proficiency level!')
    
        if self.learning_mode == 'Conversation':
            prompt = f"""You are an AI that is good at role-playing. 
            You are simulating a typical conversation happened {self.scenario}. 
            In this scenario, you are playing as a {self.role['name']} {self.role['action']}, speaking to a 
            {self.oppo_role['name']} {self.oppo_role['action']}.
            Your conversation should only be conducted in {self.language}. Do not translate.
            This simulated {self.learning_mode} is designed for {self.language} language learners to learn real-life 
            conversations in {self.language}. You should assume the learners' proficiency level in 
            {self.language} is {self.proficiency_level}. Therefore, you should {lang_requirement}.
            You should finish the conversation within {exchange_counts} exchanges with the {self.oppo_role['name']}. 
            Make your conversation with {self.oppo_role['name']} natural and typical in the considered scenario in 
            {self.language} cultural."""
        
        elif self.learning_mode == 'Debate':
            prompt = f"""You are an AI that is good at debating. 
            You are now engaged in a debate with the following topic: {self.scenario}. 
            In this debate, you are taking on the role of a {self.role['name']}. 
            Always remember your stances in the debate.
            Your debate should only be conducted in {self.language}. Do not translate.
            This simulated debate is designed for {self.language} language learners to 
            learn {self.language}. You should assume the learners' proficiency level in {self.language} 
            is {self.proficiency_level}. Therefore, you should {lang_requirement}.
            You will exchange opinions with another AI (who plays the {self.oppo_role['name']} role) 
            {exchange_counts} times. 
            Everytime you speak, you can only speak no more than 
            {argument_num_dict[self.proficiency_level]} sentences."""
        
        else:
            raise KeyError('Currently unsupported learning mode!')
        
        if self.starter:
            prompt += f"You are leading the {self.learning_mode}. \n"
        else:
            prompt += f"Wait for the {self.oppo_role['name']}'s statement."
        
        return prompt

    def generate_response(self, input_text):
        """Generate a response from the model based on the input text."""
        response = self.client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": self.prompt
            },
            {
                "role": "user",
                "content": input_text
            }
        ]
        )
        return response.choices[0].message.content
        

    def step(self, input_text):
        """Make one exchange round between two chatbots."""
        # Generate response from role1
        response1 = self.generate_response(input_text)
        self.memory.append({"role": self.role['name'], "text": response1})
        
        # Generate response from role2 based on role1's response
        response2 = self.generate_response(response1)
        self.memory.append({"role": self.oppo_role['name'], "text": response2})

        translate1 = self.translate(response1)
        translate2 = self.translate(response2)

        return response1, response2, translate1, translate2

    def translate(self, message):
        """Translate the generated script into target language."""
        if self.language == 'English':
            translation = 'Translation: ' + message
        else:
            instruction = f"Translate the following sentence from {self.language} to English: {message}"
            translation = self.generate_response(instruction)
        return translation

    def summary(self, script):
        """Distill key language learning points from the generated scripts."""
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
        
        summary = self.generate_response(instruction)
        return summary

    def _reset_conversation_history(self):
        """Reset the conversation history."""
        self.memory = []


class DualChatbot:
    """Class definition for dual-chatbots interaction system."""

    def __init__(self, engine, role_dict, language, scenario, proficiency_level, 
                 learning_mode, session_length):
        """Initialize two chatbots with the given parameters."""
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
        """Make one exchange round between two chatbots."""
        response1 = self.chatbots['role1']['chatbot'].generate_response(self.input1)
        self.conversation_history.append({"bot": self.chatbots['role1']['name'], "text": response1})
        
        self.input2 = response1
        
        response2 = self.chatbots['role2']['chatbot'].generate_response(self.input2)
        self.conversation_history.append({"bot": self.chatbots['role2']['name'], "text": response2})
        
        self.input1 = response2

        translate1 = self.chatbots['role1']['chatbot'].translate(response1)
        translate2 = self.chatbots['role2']['chatbot'].translate(response2)

        return response1, response2, translate1, translate2

    def _reset_conversation_history(self):
        """Reset the conversation history."""
        self.conversation_history = []
        self.input1 = "Start the conversation."
        self.input2 = "" 

