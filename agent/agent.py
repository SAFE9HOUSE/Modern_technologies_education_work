import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import httpx

load_dotenv(Path(__file__).parent / ".env")

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
    http_client=httpx.Client(proxy=os.getenv("PROXY_URL"), verify=False) 
)

response = client.chat.completions.create(
    model="nvidia/nemotron-3.5-lightning:free",
    messages=[{"role": "user", "content": "Что такое токен?"}],
)

message = response.choices[0].message
print("CONTENT:", message.content)
print("FINISH_REASON:", response.choices[0].finish_reason)
print("USAGE:", response.usage)