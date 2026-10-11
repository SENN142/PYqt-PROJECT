import sys
from PyQt5.QtWidgets import QApplication
from windows import MainWindow
import db_manager
from logger import app_logger


def main():
    app_logger.info("=== ЗАПУСК ПРИЛОЖЕНИЯ ===")

    # Инициализация базы данных
    db_manager.init_db()

    app = QApplication(sys.argv)

    # Блок стилей (QSS) для придания профессионального вида
    style_sheet = """
    QMainWindow, QDialog {
        background-color: #f4f5f7;
    }
    QPushButton {
        background-color: #0078D7;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 8px 16px;
        font-family: "Segoe UI", Arial, sans-serif;
        font-size: 14px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #005A9E;
    }
    QPushButton:pressed {
        background-color: #004578;
    }
    QTableWidget {
        background-color: #ffffff;
        alternate-background-color: #f9f9f9;
        gridline-color: #e0e0e0;
        border: 1px solid #d0d0d0;
        border-radius: 4px;
        font-family: "Segoe UI", Arial, sans-serif;
        font-size: 13px;
        color: #333333;
        selection-background-color: #cce8ff;
        selection-color: #000000;
    }
    QHeaderView::section {
        background-color: #e1dfdd;
        color: #333333;
        padding: 6px;
        border: 1px solid #d0d0d0;
        font-weight: bold;
        font-size: 13px;
    }
    QLineEdit, QSpinBox, QComboBox {
        background-color: #ffffff;
        border: 1px solid #cccccc;
        border-radius: 4px;
        padding: 6px;
        font-size: 14px;
        color: #333333;
    }
    QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
        border: 1px solid #0078D7;
    }
    QLabel {
        font-family: "Segoe UI", Arial, sans-serif;
        font-size: 14px;
        color: #333333;
    }
    QLabel#label_image {
        background-color: #e0e0e0;
        border: 2px dashed #aaaaaa;
        border-radius: 8px;
        color: #777777;
        font-weight: bold;
    }
    """
    app.setStyleSheet(style_sheet)

    window = MainWindow()
    window.show()

    # Корректное завершение работы приложения
    exit_code = app.exec_()
    app_logger.info(f"=== ПРИЛОЖЕНИЕ ЗАКРЫТО (Код: {exit_code}) ===")
    sys.exit(exit_code)


if __name__ == '__main__':
    main()