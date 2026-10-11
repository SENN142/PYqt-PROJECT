from PyQt5.QtWidgets import QMainWindow, QDialog, QFileDialog, QMessageBox, QTableWidgetItem, QHeaderView
from PyQt5.QtGui import QPixmap, QKeyEvent, QMouseEvent
from PyQt5.QtCore import Qt
from PyQt5 import uic
import db_manager
import os
import sys
def resource_path(relative_path):
    """ Получает абсолютный путь к ресурсу, работает для обычной среды и для .exe """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class MainWindow(QMainWindow):
    """
    Главное окно приложения.
    Отображает список медиа в виде таблицы и предоставляет кнопки управления.
    """

    def __init__(self):
        super().__init__()
        # Загрузка первой формы
        uic.loadUi(resource_path('ui/main_window.ui'), self)
        self.setWindowTitle("Каталог Медиа")

        # Настройка таблицы
        self.table_media.setColumnCount(4)
        self.table_media.setHorizontalHeaderLabels(["ID", "Название", "Категория", "Рейтинг"])
        # Растягиваем столбцы по ширине окна
        header = self.table_media.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)

        # Подключение кнопок к функциям
        self.btn_add.clicked.connect(self.open_add_dialog)
        self.btn_refresh.clicked.connect(self.load_data)
        self.btn_delete.clicked.connect(self.delete_selected_record)

        # Загрузка данных при старте
        self.load_data()

    def load_data(self):
        """
        Метод загрузки данных из БД в виджет QTableWidget.
        """
        records = db_manager.get_all_media()
        self.table_media.setRowCount(0)  # Очистка таблицы

        for row_number, row_data in enumerate(records):
            self.table_media.insertRow(row_number)
            # ID
            self.table_media.setItem(row_number, 0, QTableWidgetItem(str(row_data[0])))
            # Название
            self.table_media.setItem(row_number, 1, QTableWidgetItem(str(row_data[1])))
            # Категория
            self.table_media.setItem(row_number, 2, QTableWidgetItem(str(row_data[2])))
            # Рейтинг
            self.table_media.setItem(row_number, 3, QTableWidgetItem(str(row_data[3])))

    def open_add_dialog(self):
        """
        Открывает вторую форму (диалог добавления).
        """
        self.dialog = EditDialog(self)
        self.dialog.exec_()  # exec_ замораживает главное окно, пока диалог открыт
        self.load_data()  # Обновляем таблицу после закрытия диалога

    def delete_selected_record(self):
        """
        Удаляет выбранную в таблице запись.
        """
        current_row = self.table_media.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для удаления!")
            return

        record_id = self.table_media.item(current_row, 0).text()

        # Использование стандартного диалога (Требование 3c)
        reply = QMessageBox.question(self, 'Подтверждение',
                                     'Вы уверены, что хотите удалить эту запись?',
                                     QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            db_manager.delete_media_record(record_id)
            self.load_data()

    def keyPressEvent(self, event: QKeyEvent):
        """
        Требование 3f: Обработка нажатий клавиш клавиатуры.
        Если пользователь нажимает клавишу Delete, вызывается удаление строки.
        """
        if event.key() == Qt.Key_Delete:
            self.delete_selected_record()
        super().keyPressEvent(event)


class EditDialog(QDialog):
    """
    Диалоговое окно для добавления новой записи в каталог.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        # Загрузка второй формы
        uic.loadUi(resource_path('ui/edit_dialog.ui'), self)
        self.setWindowTitle("Добавление записи")

        self.image_path = ""
        self.category_mapping = {}  # Словарь для связи ID категории и текста

        # Настройка виджетов
        self.spin_rating.setRange(1, 10)
        self.load_categories()

        # Подключение кнопок
        self.btn_choose_image.clicked.connect(self.choose_image)
        self.btn_save.clicked.connect(self.save_record)

    def load_categories(self):
        """
        Загружает категории из БД в выпадающий список (QComboBox).
        """
        categories = db_manager.get_categories()
        for cat_id, cat_name in categories:
            self.combo_category.addItem(cat_name)
            self.category_mapping[cat_name] = cat_id

    def choose_image(self):
        """
        Открывает стандартный диалог выбора файла (Требование 3c).
        Отображает выбранную картинку (Требование 3d - мультимедиа).
        """
        file_name, _ = QFileDialog.getOpenFileName(self, "Выберите постер", "", "Images (*.png *.jpg *.jpeg)")
        if file_name:
            self.image_path = file_name
            pixmap = QPixmap(file_name)
            # Масштабируем картинку под размер Label
            scaled_pixmap = pixmap.scaled(self.label_image.width(), self.label_image.height(), Qt.KeepAspectRatio)
            self.label_image.setPixmap(scaled_pixmap)

    def save_record(self):
        """
        Сохраняет введенные данные в базу данных.
        """
        title = self.line_title.text().strip()
        if not title:
            QMessageBox.warning(self, "Ошибка", "Название не может быть пустым!")
            return

        cat_name = self.combo_category.currentText()
        cat_id = self.category_mapping[cat_name]
        rating = self.spin_rating.value()

        db_manager.add_media_record(title, cat_id, rating, self.image_path)
        QMessageBox.information(self, "Успех", "Запись успешно добавлена!")
        self.close()

    def mousePressEvent(self, event: QMouseEvent):
        """
        Требование 3g: Обработка нажатий клавиш мыши.
        При клике левой кнопкой мыши по пустому пространству формы,
        фокус ввода снимается с текстовых полей.
        """
        if event.button() == Qt.LeftButton:
            self.setFocus()
        super().mousePressEvent(event)