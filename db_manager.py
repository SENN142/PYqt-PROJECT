import sqlite3
import os

# Константы
DB_NAME = 'media_catalog.db'

def init_db():
    """
    Инициализирует базу данных.
    Создает две связанные таблицы: categories (категории) и media (медиа-файлы).
    Выполняет требование по работе с БД (не менее двух таблиц).
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Создание таблицы категорий
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')

    # Создание основной таблицы каталога
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS media (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category_id INTEGER,
            rating INTEGER,
            image_path TEXT,
            FOREIGN KEY(category_id) REFERENCES categories(id)
        )
    ''')

    # Предзаполнение категорий, если таблица пуста
    cursor.execute("SELECT COUNT(*) FROM categories")
    if cursor.fetchone()[0] == 0:
        categories = [('Фильм',), ('Сериал',), ('Игра',), ('Книга',)]
        cursor.executemany("INSERT INTO categories (name) VALUES (?)", categories)

    conn.commit()
    conn.close()

def get_categories():
    """
    Получает список всех категорий из базы данных.
    Возвращает список кортежей (id, name).
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM categories")
    result = cursor.fetchall()
    conn.close()
    return result

def add_media_record(title, category_id, rating, image_path):
    """
    Добавляет новую запись в таблицу media.
    (Запись в БД)
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO media (title, category_id, rating, image_path)
        VALUES (?, ?, ?, ?)
    ''', (title, category_id, rating, image_path))
    conn.commit()
    conn.close()

def get_all_media():
    """
    Получает все записи из базы данных, объединяя таблицы media и categories.
    (Чтение из БД)
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT m.id, m.title, c.name, m.rating, m.image_path 
        FROM media m
        JOIN categories c ON m.category_id = c.id
    ''')
    result = cursor.fetchall()
    conn.close()
    return result

def delete_media_record(record_id):
    """
    Удаляет запись из базы данных по её ID.
    (Изменение/Удаление из БД)
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM media WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()