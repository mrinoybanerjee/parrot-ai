# Parrot-AI🦜🌍: AI-Powered Language Learning Conversation Generator

Parrot-AI is a Streamlit-based application that leverages local Large Language Models to generate conversation or debate scripts for language learning. It offers a personalized and interactive experience without relying on external APIs.

## 🎯 Project Purpose

The main purpose of Parrot-AI is to provide language learners with an AI-powered tool to practice conversations and debates in their target language. By leveraging local Large Language Models, it offers a personalized and interactive learning experience without relying on external APIs.

## 💡 Motivation

Through my travels, I realized the importance of language to establish deep connections with locals. However, apps like Duolingo haven't been fitting my learning style. I learn best when I can immerse myself into conversations and pick up ideas. Parrot-AI was born out of this need for a more immersive and conversational approach to language learning.

## 🌟 Features

- 🌍 Supports multiple languages: English, Hindi, German, Spanish, French
- 💬 Two learning modes: Conversation and Debate
- 📊 Adjustable proficiency levels and session lengths
- 🔊 Text-to-speech functionality
- 🔄 Translation support

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- [llamafile](https://github.com/Mozilla-Ocho/llamafile) (Mistral Instruct 7B)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/parrot-ai.git
   cd parrot-ai
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Download and set up llamafile (Mistral Instruct 7B):
   - Download from [llamafile releases](https://github.com/Mozilla-Ocho/llamafile/releases)
   - Make it executable:
     ```bash
     chmod +x mistral-7b-instruct-v0.2.Q4_0.llamafile
     ```

## 🖥️ Usage

1. Start the llamafile server:
   ```bash
   ./mistral-7b-instruct-v0.2.Q4_0.llamafile --server --host 0.0.0.0 --port 8080
   ```

2. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

3. Open your web browser and navigate to `http://localhost:8501`

4. Configure your session in the sidebar:
   - Choose learning mode (Conversation or Debate)
   - Select target language, proficiency level, and session length
   - For Conversation mode: input roles and actions
   - For Debate mode: input the debate topic

5. Click "Generate" to create your language learning script

6. Use the provided buttons to translate, show original text, or play audio

## 🧪 Running Tests

Execute the test suite with:

```bash
python -m pytest
```

## 🐳 Docker Support

Build the Docker image:

```bash
docker build -t parrot-ai .
```

Run the container:

```bash
docker run -p 8501:8501 --add-host=host.docker.internal:host-gateway parrot-ai
```

Note: The Docker image doesn't include the LLM. Run the llamafile server separately on your host machine.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io/) for the awesome web app framework
- [llamafile](https://github.com/Mozilla-Ocho/llamafile) for the local LLM support

## 📬 Contact

mrinoybanerjee@gmail.com
