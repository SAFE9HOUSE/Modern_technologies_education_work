from openai import OpenAI

client = OpenAI(
    api_key="ollama",
    base_url="http://localhost:11434/v1"
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
        model="llama3.2:3b",  
        messages=messages)

    answer = response.choices[0].message.content
    print(f"\nАссистент: {answer}\n")

    # STEP №1
    # print(f"{'-' * 70}\nFINISH_REASON: {response.choices[0].finish_reason}\n\nUSAGE: {response.usage}\n{'-' * 70}\n")

    # STEP №2
    messages.append({"role": "assistant", "content": answer})



