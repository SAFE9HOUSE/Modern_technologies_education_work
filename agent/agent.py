import os
import json
from pathlib import Path
from openai import OpenAI

client = OpenAI(
    api_key="ollama",
    base_url="http://localhost:11434/v1"
)

MODEL = "llama3.2:3b"
WORKSPACE = Path(__file__).parent / "workspace"
WORKSPACE.mkdir(exist_ok=True)
MAX_STEPS = 10

def list_files() -> str:
    try:
        files = [f.name for f in WORKSPACE.iterdir() if f.is_file()]
        return json.dumps(files, ensure_ascii=False)
    except Exception as e:
        return f"ОШИБКА: {e}"

def read_file(path: str) -> str:
    try:
        full_path = (WORKSPACE / path).resolve()
        if not str(full_path).startswith(str(WORKSPACE.resolve())):
            return "ОШИБКА: выход за пределы песочницы"
        if not full_path.exists():
            return f"ОШИБКА: файл '{path}' не найден"
        return full_path.read_text(encoding="utf-8")
    except Exception as e:
        return f"ОШИБКА: {e}"

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "Возвращает список файлов в рабочей папке проекта",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Читает содержимое файла из рабочей папки",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Имя файла, например README.md"}
                },
                "required": ["path"],
            },
        },
    },
]

def execute_tool(name: str, raw_args: str) -> str:
    try:
        args = json.loads(raw_args) if raw_args else {}
    except json.JSONDecodeError:
        return f"ОШИБКА: невалидный JSON в аргументах: {raw_args}"

    try:
        if name == "list_files":
            return list_files()
        elif name == "read_file":
            return read_file(args.get("path", ""))
        else:
            return f"ОШИБКА: неизвестный инструмент '{name}'"
    except Exception as e:
        return f"ОШИБКА: {e}"

def run_agent(messages: list) -> str:
    for step in range(MAX_STEPS):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
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







   


