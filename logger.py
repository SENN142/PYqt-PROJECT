import logging
import os
from datetime import datetime

def setup_logger():
    """
    Настраивает систему логирования для приложения.
    Все важные события (запуск, добавление, удаление, ошибки)
    будут записываться в файл app.log с указанием точного времени.
    Это повышает надежность приложения и упрощает отладку.
    """
    # Создаем директорию для логов, если её нет
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Формируем имя файла лога
    log_file = os.path.join(log_dir, 'app.log')

    # Создаем объект логгера
    logger = logging.getLogger('MediaCatalogLogger')
    logger.setLevel(logging.DEBUG)

    # Формат записи: [Дата Время] [Уровень] Сообщение
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # Обработчик для записи в файл
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Обработчик для вывода в консоль
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Добавляем обработчики к логгеру
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger

# Инициализируем глобальный логгер для использования в других модулях
app_logger = setup_logger()