import sqlite3
import os

DB_NAME = "tourflow.db"

SQL_SCRIPT = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role_id INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (role_id) REFERENCES roles(id)
);

CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    last_name TEXT NOT NULL,
    first_name TEXT NOT NULL,
    middle_name TEXT,
    passport TEXT UNIQUE NOT NULL,
    phone TEXT NOT NULL,
    email TEXT UNIQUE,
    birth_date TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS partners (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('hotel', 'airline', 'guide', 'insurance', 'transport')),
    inn TEXT UNIQUE,
    phone TEXT,
    email TEXT,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
    rating REAL DEFAULT 0 CHECK (rating BETWEEN 0 AND 5),
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS tours (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    direction TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    price REAL NOT NULL CHECK (price >= 0),
    category TEXT CHECK (category IN ('standard', 'comfort', 'vip')),
    description TEXT,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('draft', 'active', 'archived')),
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS contracts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    partner_id INTEGER NOT NULL,
    number TEXT UNIQUE NOT NULL,
    sign_date TEXT NOT NULL,
    valid_until TEXT,
    terms TEXT,
    status TEXT NOT NULL DEFAULT 'active',
    FOREIGN KEY (partner_id) REFERENCES partners(id)
);

CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tour_id INTEGER NOT NULL,
    partner_id INTEGER NOT NULL,
    service_type TEXT NOT NULL CHECK (service_type IN ('hotel', 'flight', 'excursion', 'transfer')),
    booking_date TEXT NOT NULL DEFAULT (datetime('now')),
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'rejected')),
    external_id TEXT,
    FOREIGN KEY (tour_id) REFERENCES tours(id),
    FOREIGN KEY (partner_id) REFERENCES partners(id)
);

CREATE TABLE IF NOT EXISTS vouchers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    number TEXT UNIQUE NOT NULL,
    client_id INTEGER NOT NULL,
    tour_id INTEGER NOT NULL,
    issue_date TEXT NOT NULL DEFAULT (datetime('now')),
    total_price REAL NOT NULL CHECK (total_price >= 0),
    status TEXT NOT NULL DEFAULT 'issued' CHECK (status IN ('issued', 'paid', 'completed', 'cancelled')),
    FOREIGN KEY (client_id) REFERENCES clients(id),
    FOREIGN KEY (tour_id) REFERENCES tours(id)
);

CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    voucher_id INTEGER NOT NULL,
    amount REAL NOT NULL CHECK (amount > 0),
    method TEXT NOT NULL CHECK (method IN ('cash', 'card', 'transfer')),
    payment_date TEXT NOT NULL DEFAULT (datetime('now')),
    status TEXT NOT NULL DEFAULT 'success' CHECK (status IN ('success', 'failed', 'refund')),
    transaction_id TEXT,
    FOREIGN KEY (voucher_id) REFERENCES vouchers(id)
);

CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    tour_id INTEGER NOT NULL,
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    text TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (client_id) REFERENCES clients(id),
    FOREIGN KEY (tour_id) REFERENCES tours(id)
);

CREATE TABLE IF NOT EXISTS login_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    attempt_time TEXT NOT NULL,
    success INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS blocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    blocked_until TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_clients_passport ON clients(passport);
CREATE INDEX IF NOT EXISTS idx_tours_direction ON tours(direction);
CREATE INDEX IF NOT EXISTS idx_bookings_tour ON bookings(tour_id);
CREATE INDEX IF NOT EXISTS idx_vouchers_client ON vouchers(client_id);
CREATE INDEX IF NOT EXISTS idx_payments_voucher ON payments(voucher_id);
CREATE INDEX IF NOT EXISTS idx_reviews_tour ON reviews(tour_id);
"""


def init_database():
    """Создаёт базу и заполняет базовыми данными."""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Создание таблиц
    cur.executescript(SQL_SCRIPT)
    print("✓ Таблицы созданы")

    # Роли
    cur.execute("SELECT COUNT(*) FROM roles")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO roles (name, description) VALUES (?, ?)",
            [
                ("admin", "Администратор"),
                ("manager", "Менеджер"),
                ("financier", "Финансист"),
                ("client", "Клиент"),
            ]
        )
        print("✓ Роли добавлены")

    # Пользователь admin по умолчанию
    cur.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
    if cur.fetchone()[0] == 0:
        import hashlib
        pwd = hashlib.sha256("admin123".encode()).hexdigest()
        cur.execute(
            "INSERT INTO users (username, password_hash, role_id) VALUES (?, ?, ?)",
            ("admin", pwd, 1)
        )
        print("✓ Создан admin (пароль: admin123)")

    # Тестовые данные для туров
    cur.execute("SELECT COUNT(*) FROM tours")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            """INSERT INTO tours
               (title, direction, start_date, end_date, price, category, status)
               VALUES (?, ?, ?, ?, ?, ?, 'active')""",
            [
                ("Золотое кольцо", "Россия, Москва", "2026-05-01", "2026-05-07", 45000, "comfort"),
                ("Сочи — море", "Россия, Сочи", "2026-06-10", "2026-06-20", 65000, "standard"),
                ("Париж", "Франция, Париж", "2026-07-15", "2026-07-19", 120000, "vip"),
            ]
        )
        print("✓ Добавлены тестовые туры")

    # Тестовые партнёры
    cur.execute("SELECT COUNT(*) FROM partners")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            """INSERT INTO partners (name, type, inn, phone, email, rating)
               VALUES (?, ?, ?, ?, ?, ?)""",
            [
                ("Grand Hotel", "hotel", "7701234567", "+7 495 111-11-11", "hotel@grand.ru", 4.7),
                ("Aeroflot", "airline", "7712345678", "+7 495 222-22-22", "info@aeroflot.ru", 4.5),
                ("Гид-Сервис", "guide", "7723456789", "+7 495 333-33-33", "guide@msk.ru", 4.9),
            ]
        )
        print("✓ Добавлены тестовые партнёры")

    # Тестовый клиент
    cur.execute("SELECT COUNT(*) FROM clients")
    if cur.fetchone()[0] == 0:
        cur.execute(
            """INSERT INTO clients
               (last_name, first_name, passport, phone, email, birth_date)
               VALUES (?, ?, ?, ?, ?, ?)""",
            ("Иванов", "Иван", "4501 123456", "+7 999 111-22-33", "ivanov@mail.ru", "1990-05-15")
        )
        print("✓ Добавлен тестовый клиент")

    conn.commit()
    conn.close()
    print("\nГотово! База tourflow.db инициализирована.")


if __name__ == "__main__":
    if os.path.exists(DB_NAME):
        ans = input(f"Файл {DB_NAME} уже существует. Пересоздать? (y/n): ").strip().lower()
        if ans == "y":
            os.remove(DB_NAME)
            print("Старая БД удалена.")
        else:
            print("Отмена.")
            exit()

    init_database()