import sqlite3
from logger import app_logger

# Константы
DB_NAME = 'media_catalog.db'


def init_db():
    """
    Инициализирует базу данных. Создает таблицы, если они отсутствуют.
    """
    app_logger.info("Инициализация базы данных...")
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        ''')

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

        # Предзаполнение категорий
        cursor.execute("SELECT COUNT(*) FROM categories")
        if cursor.fetchone()[0] == 0:
            categories = [('Фильм',), ('Сериал',), ('Игра',), ('Книга',)]
            cursor.executemany("INSERT INTO categories (name) VALUES (?)", categories)
            app_logger.info("Добавлены базовые категории в БД.")

        conn.commit()
        conn.close()
        app_logger.info("База данных успешно загружена.")
    except Exception as e:
        app_logger.error(f"Ошибка при инициализации БД: {e}")


def get_categories():
    """Получает список всех категорий из базы данных."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM categories")
    result = cursor.fetchall()
    conn.close()
    return result


def add_media_record(title, category_id, rating, image_path):
    """Добавляет новую запись в каталог."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO media (title, category_id, rating, image_path)
            VALUES (?, ?, ?, ?)
        ''', (title, category_id, rating, image_path))
        conn.commit()
        conn.close()
        app_logger.info(f"Добавлена новая запись: '{title}', Рейтинг: {rating}")
    except Exception as e:
        app_logger.error(f"Ошибка при добавлении записи '{title}': {e}")


def get_all_media():
    """Получает все записи из базы данных."""
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
    """Удаляет запись из базы данных по её ID."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM media WHERE id = ?", (record_id,))
        conn.commit()
        conn.close()
        app_logger.info(f"Запись с ID={record_id} успешно удалена.")
    except Exception as e:
        app_logger.error(f"Ошибка при удалении записи ID={record_id}: {e}")


def search_media(keyword):
    """Ищет записи в базе данных по совпадению в названии."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    query = '''
        SELECT m.id, m.title, c.name, m.rating, m.image_path 
        FROM media m
        JOIN categories c ON m.category_id = c.id
        WHERE m.title LIKE ?
    '''
    cursor.execute(query, ('%' + keyword + '%',))
    result = cursor.fetchall()
    conn.close()
    app_logger.info(f"Выполнен поиск по ключевому слову: '{keyword}'. Найдено: {len(result)}")
    return result


def get_statistics():
    """Собирает статистику по каталогу (количество, средний рейтинг)."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    stats = {}
    cursor.execute("SELECT COUNT(*) FROM media")
    stats['total'] = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(rating) FROM media")
    avg_rating = cursor.fetchone()[0]
    stats['avg_rating'] = round(avg_rating, 2) if avg_rating else 0

    conn.close()
    return stats