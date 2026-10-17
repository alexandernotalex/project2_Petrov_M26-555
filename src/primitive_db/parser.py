def parse_kv_pair(pair_str):
    """
    Разбирает одну пару вида 'key = value' и возвращает (key, typed_value).
    Поддерживает типы: int, bool (True/False) и str (обязательно в кавычках).
    """
    if "=" not in pair_str:
        raise ValueError(f"Отсутствует знак равенства '=' в выражении: '{pair_str}'")

    # Разделяем по первому знаку '=' и убираем лишние пробелы по краям
    key, val_str = pair_str.split("=", 1)
    key = key.strip()
    val_str = val_str.strip()

    if not key or not val_str:
        raise ValueError(f"Некорректный формат выражения: '{pair_str}'")

    # 1. Проверяем, является ли значение строкой в кавычках
    if (val_str.startswith('"') and val_str.endswith('"')) or (
        val_str.startswith("'") and val_str.endswith("'")
    ):
        return key, val_str[1:-1]  # Возвращаем строку без внешних кавычек

    # 2. Проверяем булевы значения
    if val_str.lower() == "true":
        return key, True
    if val_str.lower() == "false":
        return key, False

    # 3. Проверяем целые числа
    try:
        return key, int(val_str)
    except ValueError:
        pass

    # Если ни один тип не подошел и кавычек не было — выдаем ошибку
    raise ValueError(
        f"Не удалось определить тип значения для '{key}'. "
        f"Если это текстовая строка, обязательно оберните её в кавычки "
        f'(например: name = "Иван")'
    )


def parse_clause(clause_str):
    """
    Разбирает выражения условий для WHERE или SET.
    Поддерживает одиночные условия "age = 28" или множественные через запятую:
    "name = 'Alex', age = 20".
    Возвращает словарь вида {'age': 28} или {'name': 'Alex', 'age': 20}.
    """
    if not clause_str or not clause_str.strip():
        return {}

    result = {}
    # Разделяем условия по запятым (позволяет делать множественные UPDATE или фильтры)
    pairs = clause_str.split(",")

    for pair in pairs:
        pair = pair.strip()
        if not pair:
            continue
        key, typed_value = parse_kv_pair(pair)
        result[key] = typed_value

    return result
