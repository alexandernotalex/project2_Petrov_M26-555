ALLOWED_TYPES = {'int', 'str', 'bool'}

def create_table(metadata, table_name, columns):
    """
    Создает новую таблицу в метаданных.
    
    :param metadata: текущий словарь метаданных
    :param table_name: имя создаваемой таблицы (str)
    :param columns: список или словарь столбцов с их типами
    :return: обновленный словарь metadata или исходный в случае ошибки
    """
    if table_name in metadata:
        print(f"Ошибка: таблица '{table_name}' уже существует.")
        return metadata

    for col_name, col_type in columns.items():
        if col_type not in ALLOWED_TYPES:
            print(
              f"Ошибка: недопустимый тип данных '{col_type}' для столбца '{col_name}'.")
            print("Разрешенные типы: int, str, bool.")
            return metadata

    new_table_columns = {}
    
    user_column_names = {col.lower() for col in columns.keys()}
    if "id" not in user_column_names:
        new_table_columns["id"] = "int"
        
    new_table_columns.update(columns)
    metadata[table_name] = {
        "columns": new_table_columns,
        "rows": []
    }

    print(f"Таблица '{table_name}' успешно создана.")
    return metadata

def drop_table(metadata, table_name):
    """
    Удаляет таблицу из метаданных.
    
    :param metadata: текущий словарь метаданных
    :param table_name: имя удаляемой таблицы (str)
    :return: обновленный словарь metadata
    """
    if table_name not in metadata:
        print(f"Ошибка: Таблицы '{table_name}' не существует.")
        return metadata

    del metadata[table_name]

    print(f"Таблица '{table_name}' успешно удалена.")
    return metadata

