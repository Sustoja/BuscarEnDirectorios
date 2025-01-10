import hashlib
import pickle
from pathlib import Path


CHUNK_SIZE = 8192  # Tamaño de bloque para leer archivos


def compute_hash(file_path: Path, include_path_in_hash: bool = False) -> str:
    """
    Calcula el hash de un fichero. Puede incluir su ruta en el cálculo para detectar cambios
    en su localización.
    """
    if not file_path.exists() or not file_path.is_file():
        raise FileNotFoundError(f"El archivo '{file_path}' no existe o no es un archivo válido.")

    hash_func = hashlib.sha256()

    # Para detectar si el fichero se mueve de carpeta aunque el contenido no varíe.
    if include_path_in_hash:
        hash_func.update(str(file_path).encode('utf-8'))

    # Hash del contenido del fichero
    with file_path.open('rb') as f:
        while chunk := f.read(CHUNK_SIZE):
            hash_func.update(chunk)

    return hash_func.hexdigest()


def save_hashes_and_filenames(file_path: Path, files_hashes: dict) -> None:
    """
    Guarda en disco un diccionario de tipo {<ruta_al_fichero> : <hash_del_fichero>}
    """
    try:
        with file_path.open('wb') as f:
            pickle.dump(files_hashes, f)
    except Exception as e:
        raise IOError(f"Error al guardar el archivo de hashes '{file_path}': {e}")


def read_hashes_and_filenames(file_path: Path) -> dict:
    """
    Lee desde disco un diccionario de tipo {<ruta_al_fichero> : <hash_del_fichero>}
    """
    if not file_path.exists():
        raise IOError(f"No existe el archivo '{file_path}'")

    try:
        with file_path.open('rb') as f:
            return pickle.load(f)
    except Exception as e:
        raise IOError(f"Error al leer el archivo de hashes '{file_path}': {e}")
