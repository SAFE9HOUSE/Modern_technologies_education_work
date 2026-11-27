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

STRATEGY = os.getenv("STRATEGY", "summarize") # "trim" | "summarize"
print(f"[РЕЖИМ] STRATEGY={STRATEGY}\n")

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)

MODEL = "nvidia/nemotron-3.5-lightning:free"
MAX_STEPS = 50
CONTEXT_BUDGET = 100000

def ensure_context_budget(messages: list) -> list:
    if estimate_tokens(messages) <= CONTEXT_BUDGET:
        return messages

    system = messages[0]
    rest = messages[1:]

    # уже накопленная память (если есть) — не суммируем её повторно
    memory_msg = None
    if rest and rest[0].get("role") == "system":
        c = rest[0].get("content", "")
        if "[память диалога]" in c or "[memory dialogue]" in c:
            memory_msg = rest[0]
            rest = rest[1:]

    removed_all = []

    while rest and estimate_tokens(
        [system] + ([memory_msg] if memory_msg else []) + rest
    ) > CONTEXT_BUDGET:
        end = 1
        while end < len(rest) and rest[end].get("role") != "user":
            end += 1
        removed = rest[:end]
        rest = rest[end:]
        removed_all.extend(removed)
        print(f"\nTRIM:removed {len(removed)} messages: "
              f"{[m.get('role') for m in removed]}\n")

    result = [system]

    if removed_all:
        if STRATEGY == "summarize":
            if memory_msg:
                removed_all = [memory_msg] + removed_all
            summary = summarize_messages(removed_all)
            if summary and len(summary) > 20:
                print(f"SUMMARY: {summary[:150]}...")
                result.append({"role": "system",
                    "content": summary + "\nНЕ повторяй уже выполненные действия."})
            else:
                # fallback на trim, если модель не справилась
                print("SUMMARY: пустой/короткий ответ, fallback на trim")
                if memory_msg:
                    result.append(memory_msg)
        elif memory_msg:
            result.append(memory_msg)

    return result + rest

def summarize_messages(removed: list) -> str:
    """Сжимает удалённый хвост в одно сообщение [память диалога]."""
    lines = []
    for m in removed:
        role = m.get("role")
        content = (m.get("content") or "").strip()
        if role == "user":
            lines.append(f"Пользователь: {content[:300]}")
        elif role == "assistant":
            if m.get("tool_calls"):
                names = [tc["function"]["name"] for tc in m["tool_calls"]]
                lines.append(f"Ассистент вызвал: {', '.join(names)}")
            elif content:
                lines.append(f"Ассистент: {content[:300]}")
        elif role == "tool":
            lines.append(f"Результат: {content[:200]}")

    text = "\n".join(lines)

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content":
                "Сожми диалог в короткую память. Отвечай ТОЛЬКО на русском языке. "
                "Формат строго: [память диалога] Пользователя зовут... Ранее сделано: ... Открытые задачи: ... "
                "Максимум 5 предложений, без лишних слов."},
                {"role": "user", "content": text},
            ],
            # tools НЕ передаём — суммаризация без инструментов
        )
        summary = (response.choices[0].message.content or "").strip()
        
        if not summary.startswith("[память диалога]"):
            summary = "[память диалога] " + summary

        print(f"SUMMARY: usage prompt={response.usage.prompt_tokens}, "
              f"completion={response.usage.completion_tokens}")
        return summary
    except Exception as e:
        print(f"SUMMARY: ошибка модели: {e}")
        return ""

def load_session(session_id: str) -> list:
    path = SESSIONS_DIR / f"{session_id}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return []

def save_session(session_id: str, messages: list):
    path = SESSIONS_DIR / f"{session_id}.json"
    path.write_text(json.dumps(messages, ensure_ascii=False, indent=2), encoding="utf-8")

def estimate_tokens(messages: list) -> int:
    return sum(len(str(m)) // 4 for m in messages) + len(json.dumps(TOOLS)) // 4

def run_agent(messages: list) -> str:
    for step in range(MAX_STEPS):
        messages = ensure_context_budget(messages)
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







   


