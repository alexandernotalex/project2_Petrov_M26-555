import functools

def handle_db_errors(func):
    """
    Декоратор для централизованной обработки ошибок базы данных.
    Перехватывает KeyError, ValueError, FileNotFoundError и выводит сообщение.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as e:
            print(f"Ошибка базы данных (KeyError):" \
                  "Запрашиваемый элемент или таблица {e} не найдены.")
            return None
        except ValueError as e:
            print(f"Ошибка валидации данных (ValueError): {e}")
            return None
        except FileNotFoundError as e:
            print(f"Ошибка файловой системы (FileNotFoundError):" \
                  "Не удалось найти файл базы данных ({e.filename}).")
            return None
        except Exception as e:
            print(f"Непредвиденная ошибка: {e}")
            return None
            
    return wrapper
