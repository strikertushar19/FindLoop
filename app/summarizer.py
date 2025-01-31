import openai
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)


def summarize_text(text):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": f"Summarize the following text:\n{text[:4000]}"}]
    )
    return response.choices[0].message.content
