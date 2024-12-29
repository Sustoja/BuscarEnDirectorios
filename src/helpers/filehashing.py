import hashlib
import pickle


def compute_hash(filepath: str) -> str:
    """
    Calcula el hash del fichero teniendo en cuenta su contenido y su ruta completa
    para detectar si cambia de contenido y/o de carpeta en el disco.
    """
    hash_func = hashlib.sha256()

    # Incluir el filepath en el cálculo del hash
    hash_func.update(filepath.encode('utf-8'))

    # Procesar el contenido del fichero para el cálculo
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            hash_func.update(chunk)
    return hash_func.hexdigest()


def save_hash_file(filepath: str, hashes: {}) -> None:
    with open(filepath, 'wb') as f:
        pickle.dump(hashes, f)

def read_hash_file(filepath: str) -> {}:
    try:
        with open(filepath, 'rb') as f:
            return dict(pickle.load(f))
    except FileNotFoundError:
        return {}
