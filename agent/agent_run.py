from openai import OpenAI
from agent_tools import TOOLS
from agent_func import execute_tool
import json
import sys
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

SESSIONS_DIR = Path(__file__).parent / "sessions"
SESSIONS_DIR.mkdir(exist_ok=True)

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)

MODEL = "nvidia/nemotron-3.5-lightning:free"
MAX_STEPS = 10

def load_session(session_id: str) -> list:
    path = SESSIONS_DIR / f"{session_id}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return []

def save_session(session_id: str, messages: list):
    path = SESSIONS_DIR / f"{session_id}.json"
    path.write_text(json.dumps(messages, ensure_ascii=False, indent=2), encoding="utf-8")

def estimate_tokens(messages: list) -> int:
    return sum(len(str(m)) // 4 for m in messages)

def run_agent(messages: list) -> str:
    for step in range(MAX_STEPS):
        print(f"\n[ОЦЕНКА] ~{estimate_tokens(messages)} токенов")
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

        messages.append(msg.model_dump())

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
    session_id = sys.argv[1] if len(sys.argv) > 1 else "default"
    messages = load_session(session_id)
    
    if not messages:
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
            print("\nПока!")
            break

        messages.append({"role": "user", "content": user_input})
        answer = run_agent(messages)
        print(f"\nАссистент: {answer}\n")
        messages.append({"role": "assistant", "content": answer})
        
        save_session(session_id, messages)







   


