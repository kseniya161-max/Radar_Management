from openai import OpenAI

from app.core.config import settings


client = OpenAI(
    api_key=settings.OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)


def ask_ai(prompt:str):
    response = client.chat.completions.create(
        model="google/gemma-4-31b-it:free",
        messages=[
            {
                "role": "system",
                "content": "You are a strict B2B sales analyst. Return only JSON."
            },
            {
                "role": "user",
                "content": prompt,
            }
        ]
    )

    return response.choices[0].message.content