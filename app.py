
from pathlib import Path

import streamlit as st
from google.genai import errors

from config import (
    MODEL_NAME,
    DEFAULT_HISTORY_LIMIT,
    MAX_HISTORY_LIMIT,
    MAX_INPUT_CHARACTERS,
)
from gemini_client import create_client, stream_response


# -----------------------------------
# Page setup
# -----------------------------------

st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="🤖",
    layout="centered"
)

css_file = Path(__file__).parent / "styles.css"

if css_file.exists():
    st.html(
        f"<style>{css_file.read_text(encoding='utf-8')}</style>"
    )


# -----------------------------------
# Secure API configuration
# -----------------------------------

try:
    api_key = st.secrets["GEMINI_API_KEY"]
except (KeyError, FileNotFoundError):
    st.error("Gemini API key is not configured.")
    st.stop()


# -----------------------------------
# Initialize session state
# -----------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "usage" not in st.session_state:
    st.session_state.usage = {
        "input": 0,
        "output": 0,
        "total": 0,
        "requests": 0
    }

if "history_limit" not in st.session_state:
    st.session_state.history_limit = DEFAULT_HISTORY_LIMIT

if "client" not in st.session_state:
    st.session_state.client = create_client(api_key)


# -----------------------------------
# Sidebar
# -----------------------------------

with st.sidebar:

    st.title("🤖 AI Study Assistant")
    st.caption("Powered by Google Gemini")

    st.divider()

    st.subheader("Model")
    st.code(MODEL_NAME)

    st.subheader("Conversation Settings")

    history_limit = st.slider(
        "Previous conversation turns",
        min_value=1,
        max_value=MAX_HISTORY_LIMIT,
        key="history_limit"
    )

    st.caption(
        "Controls how many previous completed "
        "exchanges Gemini receives."
    )

    st.divider()

    st.subheader("Token Usage")

    usage = st.session_state.usage

    st.metric(
        "Input Tokens",
        f"{usage['input']:,}"
    )

    st.metric(
        "Output Tokens",
        f"{usage['output']:,}"
    )

    st.metric(
        "Total Tokens",
        f"{usage['total']:,}"
    )

    st.caption(
        f"Successful requests: {usage['requests']}"
    )

    st.divider()

    if st.button(
        "🗑️ Clear Conversation",
        use_container_width=True
    ):
        st.session_state.messages = []

        st.session_state.usage = {
            "input": 0,
            "output": 0,
            "total": 0,
            "requests": 0
        }

        st.rerun()


# -----------------------------------
# Main interface
# -----------------------------------

st.title("AI Study Assistant")

st.caption(
    "Learn Python, Machine Learning, "
    "Deep Learning, and Generative AI."
)

if not st.session_state.messages:
    st.info(
        "Welcome! Ask a question to start learning."
    )


# -----------------------------------
# Display existing messages
# -----------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# -----------------------------------
# User input
# -----------------------------------

user_input = st.chat_input(
    "Ask a question about AI..."
)

if user_input:

    if len(user_input) > MAX_INPUT_CHARACTERS:
        st.warning(
            f"Please keep your message under "
            f"{MAX_INPUT_CHARACTERS} characters."
        )
        st.stop()

    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate streamed assistant response
    with st.chat_message("assistant"):

        response_chunks = []
        usage_metadata = None

        def text_generator():
            nonlocal_placeholder = None

            # The generator yields only text to Streamlit.
            # Usage is captured in the outer mutable list.
            for chunk in stream_response(
                client=st.session_state.client,
                messages=st.session_state.messages,
                user_message=user_input,
                history_limit=history_limit
            ):

                if chunk.usage_metadata:
                    usage_holder.append(
                        chunk.usage_metadata
                    )

                if chunk.text:
                    response_chunks.append(chunk.text)
                    yield chunk.text

        usage_holder = []

        try:
            with st.spinner("Generating response..."):
                answer = st.write_stream(
                    text_generator()
                )

            if not isinstance(answer, str):
                raise ValueError(
                    "Unexpected response format."
                )

            if not answer.strip():
                raise ValueError(
                    "Gemini returned an empty response."
                )

            # Commit only after successful completion.
            st.session_state.messages.extend([
                {
                    "role": "user",
                    "content": user_input
                },
                {
                    "role": "assistant",
                    "content": answer
                }
            ])

            # Update token usage
            if usage_holder:
                metadata = usage_holder[-1]

                st.session_state.usage["input"] += (
                    metadata.prompt_token_count or 0
                )

                st.session_state.usage["output"] += (
                    metadata.candidates_token_count or 0
                )

                st.session_state.usage["total"] += (
                    metadata.total_token_count or 0
                )

            st.session_state.usage["requests"] += 1

        except errors.APIError as error:

            if error.code == 429:
                st.error(
                    "API quota or rate limit reached. "
                    "Please try again later."
                )

            elif error.code == 503:
                st.error(
                    "Gemini is temporarily unavailable. "
                    "Please try again later."
                )

            elif error.code == 404:
                st.error(
                    "The selected model is unavailable."
                )

            elif error.code in (401, 403):
                st.error(
                    "API authentication or permission error."
                )

            else:
                st.error(
                    "The Gemini API request failed."
                )

        except Exception:
            st.error(
                "The response could not be completed. "
                "Please try again."
            )

