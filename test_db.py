from openai import OpenAI

from app.core.config import settings


client = OpenAI(
    api_key=settings.OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

response = client.chat.completions.create(
    model="google/gemma-4-31b-it:free",
    messages=[
        {
            "role": "user",
            "content": "What is 6+2?"
        }
    ]
)

print(response.choices[0].message.content)