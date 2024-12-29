
import os
from PyQt5.QtWidgets import QApplication
from gui import IndexSearchApp, INDEX_ROOT_DIR


def main():
    if not os.path.exists(INDEX_ROOT_DIR):
        os.mkdir(INDEX_ROOT_DIR)
    app = QApplication([])
    window = IndexSearchApp()
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()