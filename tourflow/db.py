import sqlite3
import hashlib
from datetime import datetime, timedelta


DB_NAME = "tourflow.db"

MAX_ATTEMPTS = 3
BLOCK_MINUTES = 3


def get_connection():
    """Соединение с БД."""
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ============================================================
# ХЕШИРОВАНИЕ
# ============================================================

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


# ============================================================
# ПОЛЬЗОВАТЕЛИ
# ============================================================

def get_role_id(role_name: str) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM roles WHERE name = ?", (role_name,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else 1


def user_exists(username: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM users WHERE username = ?", (username,))
    r = cur.fetchone()
    conn.close()
    return r is not None


def create_user(username: str, password: str, role_name: str = "client") -> bool:
    if user_exists(username):
        return False
    role_id = get_role_id(role_name)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (username, password_hash, role_id) VALUES (?, ?, ?)",
        (username, hash_password(password), role_id)
    )
    conn.commit()
    conn.close()
    return True


def check_credentials(username: str, password: str):
    """Возвращает (role_name, user_id) или (None, None)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT u.password_hash, u.id, r.name
        FROM users u
        JOIN roles r ON u.role_id = r.id
        WHERE u.username = ?
    ''', (username,))
    row = cur.fetchone()
    conn.close()
    if row is None:
        return None, None
    if row[0] != hash_password(password):
        return None, None
    return row[2], row[1]


# ============================================================
# ПОПЫТКИ ВХОДА И БЛОКИРОВКА
# ============================================================

def log_attempt(username, success):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO login_attempts (username, attempt_time, success) VALUES (?, ?, ?)",
        (username, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1 if success else 0)
    )
    conn.commit()
    conn.close()


def count_failed_attempts(username):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT COUNT(*) FROM login_attempts
        WHERE username = ? AND success = 0
    ''', (username,))
    n = cur.fetchone()[0]
    conn.close()
    return n


def block_user(username):
    until = (datetime.now() + timedelta(minutes=BLOCK_MINUTES)).strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO blocks (username, blocked_until) VALUES (?, ?)
        ON CONFLICT(username) DO UPDATE SET blocked_until = excluded.blocked_until
    ''', (username, until))
    conn.commit()
    conn.close()


def is_blocked(username):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT blocked_until FROM blocks WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return False, 0
    until = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
    now = datetime.now()
    if now >= until:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM blocks WHERE username = ?", (username,))
        conn.commit()
        conn.close()
        return False, 0
    return True, int((until - now).total_seconds())


def clear_attempts(username):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM login_attempts WHERE username = ?", (username,))
    conn.commit()
    conn.close()


# ============================================================
# ТУРЫ
# ============================================================

def list_tours(only_active=True):
    conn = get_connection()
    cur = conn.cursor()
    if only_active:
        cur.execute("SELECT id, title, direction, start_date, end_date, price, category FROM tours WHERE status = 'active'")
    else:
        cur.execute("SELECT id, title, direction, start_date, end_date, price, category FROM tours")
    rows = cur.fetchall()
    conn.close()
    return rows


def add_tour(title, direction, start, end, price, category, description=""):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO tours (title, direction, start_date, end_date, price, category, description, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'active')
    ''', (title, direction, start, end, price, category, description))
    conn.commit()
    conn.close()


def delete_tour(tour_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM tours WHERE id = ?", (tour_id,))
    conn.commit()
    conn.close()


# ============================================================
# КЛИЕНТЫ
# ============================================================

def list_clients():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, last_name, first_name, phone, email FROM clients")
    rows = cur.fetchall()
    conn.close()
    return rows


def add_client(last_name, first_name, passport, phone, email="", birth_date=""):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO clients (last_name, first_name, passport, phone, email, birth_date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (last_name, first_name, passport, phone, email, birth_date))
    conn.commit()
    conn.close()


# ============================================================
# БРОНИРОВАНИЯ
# ============================================================

def list_bookings():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT b.id, t.title, p.name, b.service_type, b.status
        FROM bookings b
        JOIN tours t ON b.tour_id = t.id
        JOIN partners p ON b.partner_id = p.id
        ORDER BY b.id DESC
    ''')
    rows = cur.fetchall()
    conn.close()
    return rows


def create_booking(tour_id, partner_id, service_type):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO bookings (tour_id, partner_id, service_type, status)
        VALUES (?, ?, ?, 'pending')
    ''', (tour_id, partner_id, service_type))
    conn.commit()
    conn.close()


def confirm_booking(booking_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE bookings SET status = 'confirmed' WHERE id = ?", (booking_id,))
    conn.commit()
    conn.close()


# ============================================================
# ПУТЁВКИ
# ============================================================

def list_vouchers():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT v.id, v.number, c.last_name || ' ' || c.first_name,
               t.title, v.total_price, v.status
        FROM vouchers v
        JOIN clients c ON v.client_id = c.id
        JOIN tours t ON v.tour_id = t.id
        ORDER BY v.id DESC
    ''')
    rows = cur.fetchall()
    conn.close()
    return rows


def create_voucher(client_id, tour_id, total_price):
    number = f"V-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO vouchers (number, client_id, tour_id, total_price, status)
        VALUES (?, ?, ?, ?, 'issued')
    ''', (number, client_id, tour_id, total_price))
    conn.commit()
    conn.close()
    return number


# ============================================================
# ОПЛАТЫ
# ============================================================

def list_payments():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT p.id, v.number, p.amount, p.method, p.payment_date, p.status
        FROM payments p
        JOIN vouchers v ON p.voucher_id = v.id
        ORDER BY p.id DESC
    ''')
    rows = cur.fetchall()
    conn.close()
    return rows


def add_payment(voucher_id, amount, method):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO payments (voucher_id, amount, method, status)
        VALUES (?, ?, ?, 'success')
    ''', (voucher_id, amount, method))
    cur.execute("UPDATE vouchers SET status = 'paid' WHERE id = ?", (voucher_id,))
    conn.commit()
    conn.close()


# ============================================================
# ОТЗЫВЫ
# ============================================================

def list_reviews():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT r.id, c.last_name || ' ' || c.first_name,
               t.title, r.rating, r.text, r.created_at
        FROM reviews r
        JOIN clients c ON r.client_id = c.id
        JOIN tours t ON r.tour_id = t.id
        ORDER BY r.id DESC
    ''')
    rows = cur.fetchall()
    conn.close()
    return rows


def add_review(client_id, tour_id, rating, text):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO reviews (client_id, tour_id, rating, text)
        VALUES (?, ?, ?, ?)
    ''', (client_id, tour_id, rating, text))
    conn.commit()
    conn.close()


# ============================================================
# ПАРТНЁРЫ
# ============================================================

def list_partners():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, type, rating FROM partners WHERE status = 'active'")
    rows = cur.fetchall()
    conn.close()
    return rows


def add_partner(name, type_, inn, phone, email, rating=0.0):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO partners (name, type, inn, phone, email, rating)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, type_, inn, phone, email, rating))
    conn.commit()
    conn.close()