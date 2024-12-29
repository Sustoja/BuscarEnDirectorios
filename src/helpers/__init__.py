"""
Al importar este módulo se importa automáticamente el objeto "logger" que permite registrar
eventos por consola y en el fichero "eventos.log". Su funcionalidad se define en la clase
"MyLogger" del módulo "logger".
"""
import logging
from src.helpers.logger import MyLogger

logger = MyLogger(logging.WARNING)
