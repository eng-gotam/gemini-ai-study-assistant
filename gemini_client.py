
from google import genai
from google.genai import types

from config import (
    MODEL_NAME, 
    SYSTEM_INSTRUCTION,
    MAX_OUTPUT_TOKENS,
    REQUEST_TIMEOUT_MS,
)


def create_client(api_key):
    """Create the Gemini API client."""

    return genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(
            timeout=REQUEST_TIMEOUT_MS,
            retry_options=types.HttpRetryOptions(
                attempts=1
            )
        )
    )


def build_history(messages, history_limit):
    """Convert completed chat messages into Gemini content."""

    completed = []

    # Messages are stored as user/assistant pairs.
    for index in range(0, len(messages) - 1, 2):
        user = messages[index]
        assistant = messages[index + 1]

        if (
            user["role"] == "user"
            and assistant["role"] == "assistant"
        ):
            completed.append((user, assistant))

    selected = completed[-history_limit:]

    contents = []

    for user, assistant in selected:
        contents.append(
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(
                        text=user["content"]
                    )
                ]
            )
        )

        contents.append(
            types.Content(
                role="model",
                parts=[
                    types.Part.from_text(
                        text=assistant["content"]
                    )
                ]
            )
        )

    return contents


def stream_response(
    client,
    messages,
    user_message,
    history_limit
):
    """Stream a response using recent conversation history."""

    contents = build_history(
        messages,
        history_limit
    )

    contents.append(
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    text=user_message
                )
            ]
        )
    )

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        max_output_tokens=MAX_OUTPUT_TOKENS
    )

    stream = client.models.generate_content_stream(
        model=MODEL_NAME,
        contents=contents,
        config=config
    )

    for chunk in stream:
        yield chunk
