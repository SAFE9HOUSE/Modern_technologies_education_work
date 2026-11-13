from openai import OpenAI
from agent_tools import TOOLS
from agent_func import execute_tool

client = OpenAI(
    api_key="ollama",
    base_url="http://localhost:11434/v1"
)

MODEL = "qwen3:8b"
MAX_STEPS = 10

def run_agent(messages: list) -> str:
    for step in range(MAX_STEPS):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            extra_body={"think": False}
        )

        msg = response.choices[0].message
        print(f"\n[ШАГ {step + 1}] finish_reason={response.choices[0].finish_reason}")
        print(f"[ШАГ {step + 1}] usage: prompt={response.usage.prompt_tokens}, "
              f"completion={response.usage.completion_tokens}")

        if not msg.tool_calls:
            return msg.content or "(пустой ответ)"

        messages.append(msg)

        for tool_call in msg.tool_calls:
            name = tool_call.function.name
            args = tool_call.function.arguments
            print(f"[ШАГ {step + 1}] ВЫЗОВ: {name}({args})")

            result = execute_tool(name, args)
            print(f"[ШАГ {step + 1}] РЕЗУЛЬТАТ: {result[:200]}...")

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })

    return f"ОШИБКА: достигнут лимит шагов ({MAX_STEPS})"

if __name__ == "__main__":

    messages = [
        {"role": "system", "content": 
        "Я разработчик. Пишу проект FitTracker (приложение по контролю физических тренировок). "
        "Ты агент, который мне помогает с разработкой этого приложения. "
        "Я обучил тебя инструментам, используй их только тогда, когда уверен, что они помогут в поиске ответе именно по моему проекту. "
        "На все остальные вопросы отвечай сам."}
    ]

    print("Агент запущен. Введите 'exit' для выхода.\n")

    while True:
        user_input = input("Вы: ")
        if user_input.lower() == "exit":
            print("Пока!")
            break

        messages.append({"role": "user", "content": user_input})
        answer = run_agent(messages)
        print(f"\nАссистент: {answer}\n")
        messages.append({"role": "assistant", "content": answer})







   


