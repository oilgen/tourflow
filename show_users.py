import sqlite3

conn = sqlite3.connect("tourflow.db")
cur = conn.cursor()

cur.execute('''
    SELECT u.id, u.username, r.name, u.created_at
    FROM users u
    JOIN roles r ON u.role_id = r.id
    ORDER BY u.id
''')

rows = cur.fetchall()
conn.close()

if not rows:
    print("Пользователей нет.")
else:
    print(f"{'ID':<4} {'Логин':<20} {'Роль':<12} {'Создан'}")
    print("-" * 60)
    for uid, username, role, created in rows:
        print(f"{uid:<4} {username:<20} {role:<12} {created}")