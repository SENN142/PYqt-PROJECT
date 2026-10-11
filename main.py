import sys
from PyQt5.QtWidgets import QApplication
from windows import MainWindow
import db_manager


def main():
    # Создаем таблицы при первом запуске
    db_manager.init_db()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()