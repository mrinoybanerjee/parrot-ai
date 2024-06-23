# Parrot-AI 🦜🌍 

Parrot-AI is a Streamlit-based application that generates conversation or debate scripts to aid in language learning. It uses a local LLM (Mistral Instruct 7B) via llamafile to create interactive language practice scenarios.

## Features

- Supports multiple languages: English, Hindi, German, Spanish, French
- Two learning modes: Conversation and Debate
- Adjustable proficiency levels and session lengths
- Text-to-speech functionality
- Translation support

## Project Purpose

The main purpose of Parrot-AI is to provide language learners with an AI-powered tool to practice conversations and debates in their target language. By leveraging local Large Language Models, it offers a personalized and interactive learning experience without relying on external APIs.

## Motivation
Through my travels, I realized the importance of language to establish deep connections with locals. However, apps like Duolingo haven’t been fitting my learning style. I learn best when I can immerse myself into conversations and pick up ideas.

## Setup

### Prerequisites

- Python 3.8+
- [llamafile](https://github.com/Mozilla-Ocho/llamafile) (Mistral Instruct 7B)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-username/parrot-ai.git
   cd parrot-ai
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Download and set up llamafile (Mistral Instruct 7B):
   - Download the Mistral Instruct 7B llamafile from [here](https://github.com/Mozilla-Ocho/llamafile/releases)
   - Make the file executable: `chmod +x mistral-7b-instruct-v0.1-Q4_K_M-SERVER.llamafile`

## Usage

1. Start the llamafile server:
   ```
   ./mistral-7b-instruct-v0.1-Q4_K_M-SERVER.llamafile --server --host 0.0.0.0 --port 8080
   ```

2. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

3. Open your web browser and navigate to `http://localhost:8501`

4. Use the sidebar to configure your language learning session:
   - Select the learning mode (Conversation or Debate)
   - Choose the target language, proficiency level, and session length
   - For Conversation mode, input roles and actions
   - For Debate mode, input the debate topic

5. Click "Generate" to create the language learning script

6. Use the buttons to translate, show original text, or play audio

## Examples

### Conversation Mode

1. Set Learning Mode to "Conversation"
2. Input:
   - Role 1: Customer
   - Action 1: ordering food
   - Role 2: Waitstaff
   - Action 2: taking the order
   - Scenario: at a restaurant
   - Language: Spanish
   - Proficiency Level: Intermediate
   - Session Length: Short

3. Click "Generate" to create a Spanish conversation between a customer and waitstaff at a restaurant.

### Debate Mode

1. Set Learning Mode to "Debate"
2. Input:
   - Debate Topic: Climate change
   - Language: German
   - Proficiency Level: Advanced
   - Session Length: Long

3. Click "Generate" to create an advanced German debate about climate change.

## Project Structure

```
parrot-ai/
│
├── src/
│   ├── __init__.py
│   ├── chatbot.py
│   ├── conversation.py
│   └── utils.py
│
├── tests/
│   ├── __init__.py
│   ├── test_chatbot.py
│   ├── test_conversation.py
│   └── test_utils.py
│
├── app.py
├── conftest.py
├── pytest.ini
├── requirements.txt
├── README.md
└── Dockerfile
```

## Running Tests

To run the tests, use the following command:

```
python -m pytest
```

## CI/CD

This project uses GitHub Actions for continuous integration and continuous deployment. The workflow includes:

- Running tests
- Building a Docker container
- Ensuring the Docker image doesn't include the LLM

You can find the workflow configuration in the `.github/workflows/ci-cd.yml` file.

## Docker

To build and run the Docker container:

1. Build the image:
   ```
   docker build -t parrot-ai .
   ```

2. Run the container:
   ```
   docker run -p 8501:8501 parrot-ai
   ```

Note: The Docker image does not include the LLM. You need to run the llamafile server separately.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

