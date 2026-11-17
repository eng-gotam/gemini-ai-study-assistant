# Gemini AI Study Assistant 🤖

An AI-powered conversational learning assistant built with **Python, Streamlit, and Google Gemini API**.

## Overview

Gemini AI Study Assistant helps students understand programming, machine learning, deep learning, and artificial intelligence through interactive conversations.

The application supports follow-up questions, streaming responses, and beginner-friendly explanations in English and Roman Urdu.

## Key Features

- AI-powered question answering using Google Gemini
- Multi-turn conversation context
- Real-time streaming responses
- Custom system instructions
- Token usage tracking
- Configurable conversation history
- Conversation reset functionality
- API error handling
- Secure API key configuration

## Technology Stack

- **Language:** Python
- **Frontend:** Streamlit
- **LLM:** Google Gemini
- **SDK:** Google GenAI
- **Deployment:** Streamlit Community Cloud

## Application Architecture

User → Streamlit Interface → Python Backend → Gemini API → Generated Response

## Live Demo

[Launch AI Study Assistant](https://gemini-ai-study-assistant-tu8nbt3l59uereanqgfbxr.streamlit.app/)

## Local Installation

1. Clone the GitHub repository.
2. Create and activate a Python virtual environment.
3. Install dependencies using `pip install -r requirements.txt`.
4. Configure `GEMINI_API_KEY` in `.streamlit/secrets.toml`.
5. Run `streamlit run app.py`.

## What I Learned

- Integrating an LLM into a Python application
- Designing system instructions and prompts
- Managing conversation history
- Implementing streamed API responses
- Tracking model token usage
- Handling API errors
- Deploying AI applications securely

## Future Improvements

- Retrieval-Augmented Generation (RAG)
- PDF question answering
- Persistent conversation storage
- User authentication
- Automated evaluation and testing
