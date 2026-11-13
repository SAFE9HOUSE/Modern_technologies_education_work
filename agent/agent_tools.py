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
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Записывает текст в файл в рабочей папке. Требует подтверждения пользователя.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Имя файла, например TODO.md"},
                    "content": {"type": "string", "description": "Текст для записи"},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_workout",
            "description": "Создаёт день тренировки с описанием. Используй, когда пользователь просит создать новый день (например, 'День спины').",
            "parameters": {
                "type": "object",
                "properties": {
                    "day": {"type": "string", "description": "Название дня, например 'вторник'"},
                    "description": {"type": "string", "description": "Описание, например 'День спины и плеч'"},
                },
                "required": ["day", "description"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_exercise",
            "description": "Добавляет упражнение в день тренировки: название, вес, повторения, подходы. "
                           "Используй, когда пользователь просит добавить упражнение или зафиксировать результат.",
            "parameters": {
                "type": "object",
                "properties": {
                    "day": {"type": "string", "description": "День тренировки, например 'вторник'"},
                    "name": {"type": "string", "description": "Название упражнения, например 'жим лёжа'"},
                    "weight": {"type": "number", "description": "Вес в кг"},
                    "reps": {"type": "integer", "description": "Количество повторений"},
                    "sets": {"type": "integer", "description": "Количество подходов"},
                },
                "required": ["day", "name", "weight", "reps", "sets"],
            },
        },
    },
]