import logging
import os
from pathlib import Path


# Colores para el texto por pantalla.
COLORS = {
    'WHITE': '\033[97m',
    'RED': '\033[91m',
    'GREEN': '\033[92m',
}


class TerminalFilter(logging.Filter):
    """
    Filtro para procesar mensajes antes de que se escriban en el terminal.
    Colorea el texto según el nivel de criticidad.
    """

    def filter(self, record):
        if os.name == 'posix':
            color = COLORS["RED"] if record.levelno > logging.INFO else COLORS["WHITE"]
            record.msg = f'{color}{record.msg}{COLORS["WHITE"]}'

        return True # Permite que el mensaje continúe al manejador


class FileFilter(logging.Filter):
    """
    Filtro para procesar mensajes antes de que se escriban en el archivo de registro.
    Elimina los códigos de color para el terminal ya que no tienen sentido en un fichero txt.
    """

    def filter(self, record):
        for color in COLORS.values():
            record.msg = record.msg.replace(color, "")
        return True  # Permite que el mensaje continúe al manejador


class MyLogger:

    @property
    def log_path(self) -> Path:
        for handler in self.log.handlers:
            if hasattr(handler, "baseFilename"):
                return Path(getattr(handler, 'baseFilename'))

    @property
    def log_size(self) -> int:
        return self.log_path.stat().st_size if self.log_path else 0

    def _setup_handlers(self):
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        terminal_formatter = logging.Formatter(f'{COLORS["WHITE"]}%(message)s')
        stream_handler.setFormatter(terminal_formatter)
        stream_handler.addFilter(TerminalFilter())

        file_handler = logging.FileHandler('eventos.log')
        file_handler.setLevel(logging.DEBUG)
        file_handler.addFilter(FileFilter())

        self.log.addHandler(stream_handler)
        self.log.addHandler(file_handler)

    def __init__(self, log_level = logging.DEBUG):
        self.log = logging.getLogger(__name__)
        self._setup_handlers()
        self.log.setLevel(log_level)
