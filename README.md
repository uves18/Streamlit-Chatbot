# Streamlit AI Chat Assistant

A simple Streamlit chatbot that uses an open-source Hugging Face model via the OpenAI-compatible `openai` client.

## Features

- Chat interface with history saved in session state
- Multiple conversations available in a sidebar like ChatGPT
- Streaming assistant response display
- Session memory for short-term context
- File upload support for displaying text content
- Download chat history as JSON

## Requirements

- Python 3.8+
- `streamlit`
- `huggingface_hub`
- `python-dotenv`
- `openai`

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the project folder with your Hugging Face API key:

```env
hf_api_key=YOUR_HUGGINGFACE_API_KEY
```

3. Run the app:

```bash
streamlit run main.py
```

## Usage

- Use the sidebar to create a new chat or switch between existing chats.
- Type your prompt in the chat input box.
- The assistant response will stream back as it is generated.
- Clear the current chat or reset memory from the sidebar.

## Notes

- The app currently uses the Hugging Face router endpoint with an OpenAI-compatible client.
- If you want to switch models, update `HF_MODEL` in the environment or modify the model candidates in `main.py`.

## Demo link
https://drive.google.com/file/d/1zC0OAEKJkw82YwQFG87FLQ6KB0UgQTvf/view?usp=drive_link
