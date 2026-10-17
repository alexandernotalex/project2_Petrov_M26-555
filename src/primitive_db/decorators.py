import functools
import time

from prompt import string


def handle_db_errors(func):
    """Декоратор для централизованной обработки ошибок базы данных."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as e:
            print(
                f"Ошибка базы данных (KeyError):"
                f"Запрашиваемый элемент или таблица {e} не найдены."
            )
            return None
        except ValueError as e:
            print(f"Ошибка валидации данных (ValueError): {e}")
            return None
        except FileNotFoundError as e:
            print(
                f"Ошибка файловой системы (FileNotFoundError):"
                f"Не удалось найти файл базы данных ({e.filename})."
            )
            return None
        except Exception as e:
            print(f"Непредвиденная ошибка: {e}")
            return None

    return wrapper


def confirm_action(action_name):
    """Декоратор с аргументом для подтверждения опасных операций пользователя."""

    def decorator(func):
        # НАДО ЗДЕСЬ: сохраняем метаданные оригинальной функции core
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            confirmation = string(
                f"Вы уверены, что хотите выполнить '{action_name}'? [y/n]: "
            )

            if confirmation.strip().lower() != "y":
                print(f"Операция '{action_name}' отменена пользователем.")
                # Возвращаем первый переданный аргумент (metadata или table_data)
                return args[0] if args else None

            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_time(func):
    """Декоратор для замера и вывода времени выполнения функции."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Фиксируем время начала операции
        start_time = time.monotonic()

        # Выполняем основную функцию
        result = func(*args, **kwargs)

        # Вычисляем разницу во времени
        elapsed_time = time.monotonic() - start_time

        # Выводим результат в консоль с округлением до трех знаков после запятой
        print(f"Функция <{func.__name__}> выполнилась за {elapsed_time:.3f} секунд.")

        return result

    return wrapper


def create_cacher():
    """Реализует функцию с замыканием для кэширования результатов select."""
    cache_store = {}

    def cache_result(key, value_func):
        if key in cache_store:
            print(f"[КЭШ] Результат для запроса '{key}' взят из кэша.")
            return cache_store[key]
        print(f"[КЭШ] Запрос '{key}' не найден в кэше. Вычисляем значения...")
        result = value_func()
        cache_store[key] = result
        return result

    return cache_result
