import os
import re
from pathlib import PurePath
from PyQt5.QtWidgets import (QApplication, QGroupBox, QWidget, QVBoxLayout, QComboBox, QGridLayout, QLabel,
                             QLineEdit, QPushButton, QFileDialog, QProgressBar, QTextBrowser, QMessageBox)
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl
from  gui_config import VALID_DOC_EXTENSIONS, INDEX_ROOT_DIR, APP_WIDTH, APP_HEIGHT, STYLES

import helpers.FileOperations.indexingthread as fidx


class IndexSearchApp(QWidget):
    """Interfaz gráfico para la plicación de indexación y búsqueda de archivos."""

    @staticmethod
    def replace_underscores(text: str) -> str:
        """Reemplaza cada primer '_' que encuentra por una '/' para convertir la cadena en un path"""
        return re.sub(r'_+', lambda m: '/' + '_' * (len(m.group()) - 1), text)

    @staticmethod
    def open_link_in_browser(url: QUrl) -> None:
        QDesktopServices.openUrl(url)

    @staticmethod
    def get_list_of_files(folder: str) -> []:
        return [os.path.join(root, file)
                for root, _, files in os.walk(folder)
                for file in files
                if file.lower().endswith(VALID_DOC_EXTENSIONS)]

    def __init__(self, index_root_dir: str = INDEX_ROOT_DIR):
        super().__init__()
        self.idx_root_folder = index_root_dir             # Normalmente toma el valor de INDEX_ROOT_DIR
        self.idx_subfolders = self._get_idx_subfolders()  # Lista de carpetas por debajo de la anterior
        self.all_files = [] # Lista de ficheros a indexar. Depende de la carpeta que seleccione el usuario

        self.init_ui()

    def _get_idx_subfolders(self):
        """Obtiene las carpetas ya indexadas."""
        return [d for d in os.listdir(self.idx_root_folder)
                if os.path.isdir(os.path.join(self.idx_root_folder, d))]

    def _set_initial_screen_size(self):
        screen_height = QApplication.desktop().screenGeometry().height()
        screen_width = QApplication.desktop().screenGeometry().width()
        height = min(APP_HEIGHT, int(screen_height*0.8))
        width = min(APP_WIDTH, int(screen_width*0.5))
        self.resize(width, height)

    def init_ui(self):
        """Inicializa los elementos de la interfaz gráfica."""
        self.setWindowTitle("Indexación y búsqueda dentro de archivos")
        self._set_initial_screen_size()

        # Configuración de los widgets
        self._setup_index_group()
        self._setup_search_group()
        self._setup_results_browser()
        self._setup_progress_bar()

        layout = QVBoxLayout()
        layout.addWidget(self.idx_group)
        layout.addWidget(self.search_group)
        layout.addWidget(self.results_browser)
        layout.addWidget(self.progress_label)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)
        self.setStyleSheet(self._get_stylesheet())

        self._setup_inital_state()

    def _setup_index_group(self):
        self.idx_group = QGroupBox('Índice de búsqueda')
        idx_group_layout = QGridLayout()
        self.idx_group.setLayout(idx_group_layout)

        self.idx_folders_combo = QComboBox()
        self.idx_folders_combo.addItems(self.idx_subfolders)

        self.idx_folder_button = QPushButton("Indexar carpeta")
        self.idx_folder_button.clicked.connect(self.index_new_folder)

        idx_group_layout.addWidget(self.idx_folders_combo, 0, 0)
        idx_group_layout.addWidget(self.idx_folder_button, 0, 1)

        idx_group_layout.setColumnStretch(0, 3)  # La columna del QComboBox ocupa más espacio
        idx_group_layout.setColumnStretch(1, 1)  # La columna del botón ocupa menos espacio

    def _setup_search_group(self):
        self.search_group = QGroupBox('Término a buscar')
        search_group_layout = QGridLayout()
        self.search_group.setLayout(search_group_layout)

        self.search_input = QLineEdit()
        self.search_input.returnPressed.connect(self.perform_search)
        self.search_button = QPushButton("Buscar")
        self.search_button.clicked.connect(self.perform_search)

        search_group_layout.addWidget(self.search_input, 0, 0)
        search_group_layout.addWidget(self.search_button, 0, 1)

        search_group_layout.setColumnStretch(0, 3)  # La columna del QLineEdit ocupa más espacio
        search_group_layout.setColumnStretch(1, 1)  # La columna del botón ocupa menos espacio

    def _setup_results_browser(self):
        self.results_browser = QTextBrowser()
        self.results_browser.setOpenLinks(False)
        self.results_browser.anchorClicked.connect(self.open_link_in_browser)

    def _setup_progress_bar(self):
        self.progress_label = QLabel("Progreso:")
        self.progress_label.setMinimumWidth(1)    # Para evitar que se expanda cuando el texto es muy largo
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)

    def _setup_inital_state(self):
        if len(self.idx_subfolders) == 0:
            self.search_button.setEnabled(False)
            self.search_input.setEnabled(False)
            self.idx_folder_button.setFocus()
        else:
            self.search_input.setFocus()


    # BEGIN INDEXING METHODS
    def index_new_folder(self):
        if folder:= QFileDialog.getExistingDirectory(self, "Seleccionar carpeta"):
            all_files = self.get_list_of_files(folder)
            if len(all_files) == 0:
                QMessageBox.warning(self, 'Aviso', f"No hay documentos para indexar en {folder}")
                return

            self.all_files = all_files
            path = PurePath(folder)
            new_list_item = (str(path.relative_to(path.anchor))
                             .replace('/', '_')
                             .replace('\\', '_')
                             )
            index_folder = f'{self.idx_root_folder}/{new_list_item}'

            self._update_index_subdirs(new_list_item)
            self._start_indexing_thread(folder, index_folder)

    def _update_index_subdirs(self, new_list_item):
        """Actualiza la lista de subdirectorios indexados y el combo box asociado."""
        self.idx_subfolders = sorted(list(set(self.idx_subfolders + [new_list_item])))
        self.idx_folders_combo.clear()
        self.idx_folders_combo.addItems(self.idx_subfolders)
        self.idx_folders_combo.setCurrentText(new_list_item)

    def _start_indexing_thread(self, folder_to_be_indexed, index_folder):
        """Inicia el hilo de indexación y actualiza la interfaz de usuario."""
        self.indexing_thread = fidx.IndexingThread(index_folder, self.all_files)
        self.indexing_thread.progress_updated.connect(self.progress_bar.setValue)
        self.indexing_thread.progress_updated.connect(self.on_indexing_progress)
        self.indexing_thread.indexing_complete.connect(self.on_indexing_complete)

        self._disable_controls_for_indexing(folder_to_be_indexed)
        self.progress_bar.setMaximum(len(self.all_files))
        self.indexing_thread.start()

    def _disable_controls_for_indexing(self, folder_to_be_indexed):
        """Desactiva los controles de la interfaz durante la indexación."""
        self.idx_folders_combo.setEnabled(False)
        self.idx_folder_button.setEnabled(False)
        self.search_input.setEnabled(False)
        self.search_button.setEnabled(False)
        self.progress_label.setText(f"Indexando: {folder_to_be_indexed}")
        self.progress_bar.setValue(0)

    def on_indexing_progress(self, i):
        """Se ejecuta cada vez que se indexa un nuevo fichero."""
        self.progress_label.setText(self.all_files[i])

    def on_indexing_complete(self):
        """Se ejecuta cuando la indexación se ha completado."""
        self.progress_label.setText("Indexación completada")
        self.progress_bar.setValue(self.progress_bar.maximum())
        self._enable_controls_after_indexing()

    def _enable_controls_after_indexing(self):
        """Reactiva los controles de la interfaz después de la indexación."""
        self.search_input.clear()
        self.results_browser.clear()
        self.idx_folders_combo.setEnabled(True)
        self.idx_folder_button.setEnabled(True)
        self.search_input.setEnabled(True)
        self.search_button.setEnabled(True)

    # END INDEXING METHODS


    def perform_search(self):
        """Realiza la búsqueda del término en el índice seleccionado."""
        query = self.search_input.text()
        if not query.strip():
            QMessageBox.warning(self, "Aviso", "Por favor, introduzca un término para buscar.")
            return

        index_folder = f'{self.idx_root_folder}/{self.idx_folders_combo.currentText()}'
        results = fidx.search_index(index_folder, query)
        self.results_browser.clear()

        if results:
            for file_path in results:
                file_name = file_path.split('/')[-1]
                self.results_browser.append(f"<a href='file://{file_path}'>{file_name}</a>")
        else:
            self.results_browser.append("<p>No se encontraron resultados.</p>")


    @staticmethod
    def _get_stylesheet():
        """Define el estilo personalizado para la aplicación."""
        return STYLES
