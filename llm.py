import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

token = os.getenv("GITHUB_AI_TOKEN")
endpoint = "https://models.github.ai/inference"
model = "openai/gpt-4.1-mini"

client = OpenAI(
    base_url=endpoint,
    api_key=token,
)

response = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "",
        },
        {
            "role": "user",
            "content": "What is the capital of France?",
        }
    ],
    temperature=1,
    top_p=1,
    model=model
)

print(response.choices[0].message.content)