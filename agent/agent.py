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

messages = [
    {"role": "system", "content": "Ты полезный ассистент. Отвечай кратко."}
]

print("Чат запущен. Введите 'exit' для выхода.\n")

while True:
    user_input = input("Вы: ")

    if user_input.lower() == "exit":
        print("Пока!")
        break

    messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="nvidia/nemotron-3.5-lightning:free",  
        messages=messages)

    answer = response.choices[0].message.content
    print(f"\nАссистент: {answer}\n")

    # STEP №1
    # print(f"{'-' * 70}\nFINISH_REASON: {response.choices[0].finish_reason}\n\nUSAGE: {response.usage}\n{'-' * 70}\n")

    # STEP №2
    # messages.append({"role": "assistant", "content": answer})



