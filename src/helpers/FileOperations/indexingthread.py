import os
from pathlib import Path
from PyQt5.QtCore import QThread, pyqtSignal
from whoosh.analysis import StemmingAnalyzer, CharsetFilter
from whoosh.fields import Schema, TEXT, ID
from whoosh.index import create_in, open_dir
from whoosh.qparser import MultifieldParser
from whoosh.support.charset import accent_map
from whoosh.writing import AsyncWriter

from .filehashing import compute_hash, save_hashes_and_filenames, read_hashes_and_filenames
from .textextractor import extract_content
from ..Logger import mylogger


ARCHIVO_HASHES = 'hashes.pickle'


def create_schema() -> Schema:
    analyzer = StemmingAnalyzer() | CharsetFilter(accent_map)
    return Schema(
        title=TEXT(stored=True, analyzer=analyzer),
        path=ID(stored=True, unique=True), # Debe ser de tipo "ID" porque luego lo usamos como clave para borrar
        content=TEXT(analyzer=analyzer),
    )


def process_document(file_path: str) -> {}:
    content = extract_content(file_path, mylogger)
    title = os.path.splitext(os.path.basename(file_path))[0]
    return {
        "title": title,
        "path": file_path,
        "content": content,
    }


class IndexingThread(QThread):
    progress_updated = pyqtSignal(int)  # Señal para actualizar el progreso
    indexing_complete = pyqtSignal()   # Señal para indicar que la indexación ha finalizado

    def __init__(self, index_folder: str, docs_list: [str]):
        super().__init__()
        self.index_folder = index_folder
        self.docs_list = docs_list


    def run(self):
        """ Indexa los documentos en un hilo separado y emite señales para actualizar la barra de progreso."""
        schema = create_schema()
        if not os.path.exists(self.index_folder):
            os.mkdir(self.index_folder)
            idx = create_in(self.index_folder, schema)
            old_hashes = {}
        else:
            idx = open_dir(self.index_folder)
            hash_file = Path(self.index_folder) / ARCHIVO_HASHES
            try:
                old_hashes = read_hashes_and_filenames(hash_file)
            except IOError:
                old_hashes = {}

        writer = AsyncWriter(idx)
        new_hashes = {}

        for i, file_path in enumerate(self.docs_list):
            current_hash = compute_hash(Path(file_path), True)
            new_hashes[current_hash] = file_path

            if (current_hash not in old_hashes) or (old_hashes[current_hash] != file_path):
                content = extract_content(file_path)
                mylogger.log.info(f"Añadiendo al índice: {file_path}")
                writer.update_document(
                    title=os.path.splitext(os.path.basename(file_path))[0],
                    path=file_path,
                    content=content,
                )
            self.progress_updated.emit(i)

        deleted_hashes = set(old_hashes.keys()) - set(new_hashes.keys())
        if deleted_hashes:
            for deleted_hash in deleted_hashes:
                deleted_path = old_hashes[deleted_hash]
                writer.delete_by_term('path', deleted_path)  # Usamos la ruta completa como identificador
                mylogger.log.info(f"Eliminando del índice: {deleted_path}")

        writer.commit()
        hash_file = Path(self.index_folder) / ARCHIVO_HASHES
        save_hashes_and_filenames(hash_file, new_hashes)
        self.indexing_complete.emit()


def search_index(index_dir: str, query_string: str):
    idx = open_dir(index_dir)
    with idx.searcher() as searcher:
        parser = MultifieldParser(["content", "title"], schema=idx.schema)
        query = parser.parse(query_string)
        results = searcher.search(query, limit=None)

        html_content = ("<!DOCTYPE html>\n<html lang='es'>\n<head><meta charset='UTF-8'>"
                        "<title>Resultados de Búsqueda</title></head><body>")
        html_content += f"<h1>Resultados de Búsqueda para '{query_string}'</h1><ul>"

        devolver = []
        for result in results:
            file_path = result['path']
            file_name = result['title']
            devolver.append(file_path)
            html_content += f"<li><a href='file://{file_path}'>{file_name}</a></li>\n"

        html_content += "</ul></body></html>"

        with open("../search_results.html", "w", encoding="utf-8") as f:
            f.write(html_content)

        return devolver
