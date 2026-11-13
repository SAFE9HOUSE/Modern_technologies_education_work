import json
from pathlib import Path

WORKSPACE = Path(__file__).parent / "workspace"
WORKSPACE.mkdir(exist_ok=True)

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

def write_file(path: str, content: str) -> str:
    try:
        full_path = (WORKSPACE / path).resolve()
        if not str(full_path).startswith(str(WORKSPACE.resolve())):
            return "ОШИБКА: выход за пределы песочницы"

        answer = input(f"\n[ПОДТВЕРЖДЕНИЕ] Записать в '{path}'? [y/N]: ").strip().lower()
        if answer != "y":
            return "ОТКАЗ: пользователь не разрешил запись"

        full_path.write_text(content, encoding="utf-8")
        return f"OK: файл '{path}' записан ({len(content)} символов)"
    except Exception as e:
        return f"ОШИБКА: {e}"

def create_workout(day: str, description: str) -> str:
    try:
        path = (WORKSPACE / "workouts.json").resolve()
        if not str(path).startswith(str(WORKSPACE.resolve())):
            return "ОШИБКА: выход за пределы песочницы"

        data = {}
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                data = {}

        data.setdefault("_workouts", {})[day] = description
        data.setdefault(day, [])

        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return f"OK: создана тренировка '{day}' — {description}"
    except Exception as e:
        return f"ОШИБКА: {e}"

def create_exercise(day: str, name: str, weight: float, reps: int, sets: int) -> str:
    try:
        path = (WORKSPACE / "workouts.json").resolve()
        if not str(path).startswith(str(WORKSPACE.resolve())):
            return "ОШИБКА: выход за пределы песочницы"

        data = {}
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                data = {}

        data.setdefault(day, []).append({
            "name": name,
            "weight": weight,
            "reps": reps,
            "sets": sets,
        })

        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return f"OK: добавлено '{name}' ({weight} кг × {reps} × {sets} подходов) в '{day}'"
    except Exception as e:
        return f"ОШИБКА: {e}"

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
        elif name == "write_file":
            return write_file(args.get("path", ""), args.get("content", ""))
        elif name == "create_workout":
            return create_workout(
                args.get("day", ""),
                args.get("description", ""),
            )
        elif name == "create_exercise":
            return create_exercise(
                args.get("day", ""),
                args.get("name", ""),
                float(args.get("weight", 0)),
                int(args.get("reps", 0)),
                int(args.get("sets", 0)),
            )
        else:
            return f"ОШИБКА: неизвестный инструмент '{name}'"
    except Exception as e:
        return f"ОШИБКА: {e}"

