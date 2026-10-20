from db import (
    user_exists, create_user, check_credentials,
    log_attempt, count_failed_attempts, block_user,
    is_blocked, clear_attempts, MAX_ATTEMPTS, BLOCK_MINUTES
)


def register(username: str, password: str, role: str = "client"):
    """Регистрация. Роль по умолчанию — client."""
    username = username.strip()
    password = password.strip()

    if not username or not password:
        return False, "Логин и пароль не могут быть пустыми."
    if len(username) < 3:
        return False, "Логин минимум 3 символа."
    if len(password) < 4:
        return False, "Пароль минимум 4 символа."
    if user_exists(username):
        return False, f"Пользователь «{username}» уже существует."

    if create_user(username, password, role):
        return True, f"Пользователь «{username}» зарегистрирован (роль: {role})."
    return False, "Не удалось создать пользователя."


def login(username: str, password: str):
    """Возвращает (role, user_id, message)."""
    username = username.strip()
    password = password.strip()

    if not username or not password:
        return None, None, "Введите логин и пароль."

    blocked, sec = is_blocked(username)
    if blocked:
        return None, None, f"Аккаунт заблокирован. Осталось: {sec // 60} мин {sec % 60} сек."

    role, user_id = check_credentials(username, password)
    if role:
        log_attempt(username, True)
        clear_attempts(username)
        return role, user_id, f"Добро пожаловать, {username}!"

    log_attempt(username, False)
    failed = count_failed_attempts(username)
    remaining = MAX_ATTEMPTS - failed

    if remaining <= 0:
        block_user(username)
        return None, None, f"Превышено попыток ({MAX_ATTEMPTS}). Блокировка на {BLOCK_MINUTES} минуты."

    return None, None, f"Неверный логин или пароль. Осталось попыток: {remaining}."