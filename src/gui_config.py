VALID_DOC_EXTENSIONS = ('.docx', '.pdf', '.txt', '.md')
INDEX_ROOT_DIR = 'indexdir'
APP_WIDTH = 750
APP_HEIGHT = 900
STYLES = """
            QWidget {
                font-family: Arial, sans-serif;
                font-size: 14px;
            }
            QGroupBox {
                border: 1px solid #3c3c3c;
                border-radius: 8px;
                margin-top: 20px;
                padding: 15px;
            }
            QPushButton {
                background-color: #0078D7;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #005A9E;
            }
            QLineEdit {
                border: 1px solid #3c3c3c;
                border-radius: 5px;
                padding: 5px;
            }
            QComboBox {
                border: 1px solid #3c3c3c;
                border-radius: 5px;
                padding: 5px;
            }
            QTextBrowser {
                border: 1px solid #3c3c3c;
                border-radius: 5px;
                padding: 5px;
            }
            QProgressBar {
                border: 1px solid #3c3c3c;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #0078D7;
            }
        """
