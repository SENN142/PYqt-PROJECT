import os
import sys
import csv
from PyQt5.QtWidgets import (QMainWindow, QDialog, QFileDialog, QMessageBox,
                             QTableWidgetItem, QHeaderView)
from PyQt5.QtGui import QPixmap, QKeyEvent, QMouseEvent
from PyQt5.QtCore import Qt
from PyQt5 import uic
import db_manager
from logger import app_logger


def resource_path(relative_path):
    """Получает абсолютный путь к ресурсу, работает для обычной среды и для .exe"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class MainWindow(QMainWindow):
    """
    Главное окно приложения.
    Отображает список медиа в виде таблицы, предоставляет инструменты
    для добавления, удаления, поиска и экспорта данных.
    """

    def __init__(self):
        super().__init__()
        uic.loadUi(resource_path('ui/main_window.ui'), self)
        self.setWindowTitle("Каталог Медиа")

        # Настройка таблицы
        self.table_media.setColumnCount(4)
        self.table_media.setHorizontalHeaderLabels(["ID", "Название", "Категория", "Рейтинг"])
        header = self.table_media.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_media.setSortingEnabled(True)  # Включаем сортировку по клику на заголовок

        # Подключение кнопок к функциям
        self.btn_add.clicked.connect(self.open_add_dialog)
        self.btn_refresh.clicked.connect(self.load_data)
        self.btn_delete.clicked.connect(self.delete_selected_record)

        # Подключение новых кнопок
        self.btn_search.clicked.connect(self.search_data)
        self.btn_export.clicked.connect(self.export_to_csv)
        self.btn_stats.clicked.connect(self.show_statistics)

        # Загрузка данных при старте
        self.load_data()
        app_logger.info("Главное окно успешно загружено.")

    def load_data(self, records=None):
        """
        Метод загрузки данных из БД в виджет QTableWidget.
        Если передан список records, загружает его (для поиска).
        """
        self.table_media.setSortingEnabled(False)  # Отключаем сортировку на время заполнения
        if records is None:
            records = db_manager.get_all_media()

        self.table_media.setRowCount(0)

        for row_number, row_data in enumerate(records):
            self.table_media.insertRow(row_number)

            id_item = QTableWidgetItem(str(row_data[0]))
            # Делаем ячейки недоступными для прямого редактирования
            id_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.table_media.setItem(row_number, 0, id_item)

            title_item = QTableWidgetItem(str(row_data[1]))
            title_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.table_media.setItem(row_number, 1, title_item)

            cat_item = QTableWidgetItem(str(row_data[2]))
            cat_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.table_media.setItem(row_number, 2, cat_item)

            rating_item = QTableWidgetItem(str(row_data[3]))
            rating_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.table_media.setItem(row_number, 3, rating_item)

        self.table_media.setSortingEnabled(True)

    def search_data(self):
        """Обрабатывает поиск по названию."""
        keyword = self.line_search.text().strip()
        if not keyword:
            self.load_data()  # Если строка пустая, грузим всё
            return

        records = db_manager.search_media(keyword)
        self.load_data(records)

    def export_to_csv(self):
        """
        Экспортирует текущее содержимое таблицы в CSV-файл.
        Открывает стандартный диалог сохранения файла.
        """
        path, _ = QFileDialog.getSaveFileName(self, "Экспорт в CSV", "", "CSV Files (*.csv)")
        if not path:
            return

        try:
            with open(path, 'w', newline='', encoding='utf-8') as stream:
                writer = csv.writer(stream)
                # Записываем заголовки
                writer.writerow(["ID", "Название", "Категория", "Рейтинг"])
                # Записываем данные
                for row in range(self.table_media.rowCount()):
                    rowdata = []
                    for column in range(self.table_media.columnCount()):
                        item = self.table_media.item(row, column)
                        rowdata.append(item.text() if item is not None else "")
                    writer.writerow(rowdata)

            QMessageBox.information(self, "Успех", f"Данные успешно экспортированы в:\n{path}")
            app_logger.info(f"База данных экспортирована в файл {path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось экспортировать файл: {e}")
            app_logger.error(f"Ошибка экспорта CSV: {e}")

    def show_statistics(self):
        """Отображает диалоговое окно со статистикой каталога."""
        stats = db_manager.get_statistics()
        msg = f"Всего записей в каталоге: {stats['total']}\n"
        msg += f"Средний рейтинг медиа: {stats['avg_rating']} / 10"
        QMessageBox.information(self, "Статистика", msg)
        app_logger.info("Просмотрена статистика каталога.")

    def open_add_dialog(self):
        """Открывает диалог добавления."""
        self.dialog = EditDialog(self)
        self.dialog.exec_()
        self.load_data()

    def delete_selected_record(self):
        """Удаляет выбранную в таблице запись с подтверждением."""
        current_row = self.table_media.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Внимание", "Пожалуйста, выберите запись для удаления!")
            return

        record_id = self.table_media.item(current_row, 0).text()
        title = self.table_media.item(current_row, 1).text()

        reply = QMessageBox.question(self, 'Подтверждение',
                                     f'Вы действительно хотите удалить "{title}"?',
                                     QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            db_manager.delete_media_record(record_id)
            self.load_data()

    def keyPressEvent(self, event: QKeyEvent):
        """Обработка нажатий клавиатуры (Требование 3f)."""
        if event.key() == Qt.Key_Delete:
            self.delete_selected_record()
        elif event.key() == Qt.Key_Escape:
            self.line_search.clear()
            self.load_data()
        super().keyPressEvent(event)


class EditDialog(QDialog):
    """
    Диалоговое окно для добавления новой записи.
    Обрабатывает валидацию данных и загрузку изображений.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(resource_path('ui/edit_dialog.ui'), self)
        self.setWindowTitle("Добавление новой записи")

        self.image_path = ""
        self.category_mapping = {}

        self.spin_rating.setRange(1, 10)
        self.load_categories()

        self.btn_choose_image.clicked.connect(self.choose_image)
        self.btn_save.clicked.connect(self.save_record)
        app_logger.info("Открыто окно добавления записи.")

    def load_categories(self):
        """Загружает категории из базы в выпадающий список QComboBox."""
        categories = db_manager.get_categories()
        for cat_id, cat_name in categories:
            self.combo_category.addItem(cat_name)
            self.category_mapping[cat_name] = cat_id

    def choose_image(self):
        """Открывает файловый диалог для выбора картинки."""
        file_name, _ = QFileDialog.getOpenFileName(self, "Выберите постер", "", "Images (*.png *.jpg *.jpeg)")
        if file_name:
            self.image_path = file_name
            pixmap = QPixmap(file_name)
            scaled_pixmap = pixmap.scaled(self.label_image.width(), self.label_image.height(), Qt.KeepAspectRatio)
            self.label_image.setPixmap(scaled_pixmap)
            app_logger.info(f"Выбрано изображение: {file_name}")

    def save_record(self):
        """Считывает данные с формы, валидирует их и сохраняет в БД."""
        title = self.line_title.text().strip()

        # Строгая валидация (проверка на пустые значения)
        if not title:
            QMessageBox.warning(self, "Ошибка валидации", "Название не может быть пустым!")
            app_logger.warning("Попытка сохранить запись с пустым названием.")
            return

        cat_name = self.combo_category.currentText()
        cat_id = self.category_mapping[cat_name]
        rating = self.spin_rating.value()

        db_manager.add_media_record(title, cat_id, rating, self.image_path)
        QMessageBox.information(self, "Успешно", "Запись успешно добавлена в каталог!")
        self.close()

    def mousePressEvent(self, event: QMouseEvent):
        """Обработка кликов мыши (Требование 3g)."""
        if event.button() == Qt.LeftButton:
            self.setFocus()
        super().mousePressEvent(event)