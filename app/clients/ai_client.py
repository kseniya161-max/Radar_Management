from app.core.config import settings
from app.exceptions.ai import AiAPIError
from openai import (
    OpenAI,
    RateLimitError,
    APIConnectionError,
    APITimeoutError,
    APIStatusError,
)

client = OpenAI(
    api_key=settings.OPENROUTER_API_KEY, base_url="https://openrouter.ai/api/v1"
)


def ask_ai(prompt: str):
    try:
        response = client.chat.completions.create(
            model="google/gemma-4-31b-it:free",
            messages=[
                {
                    "role": "system",
                    "content": "You are a strict B2B sales analyst. Return only JSON.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        return response.choices[0].message.content
    except RateLimitError:
        raise AiAPIError("AI rate limit exceeded")
    except APIConnectionError:
        raise AiAPIError("No connection with api")
    except APITimeoutError:
        raise AiAPIError("AI API timeout")
    except APIStatusError:
        raise AiAPIError("AI API returned an error")
