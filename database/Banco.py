import io
import sqlite3
import os
import dbm
import shelve


def salvar(nome_arquivo, chave, dados):
    diretorio = "data"
    caminho = f"{diretorio}\\{nome_arquivo}"

    if not os.path.isdir(diretorio):
        os.makedirs(diretorio)

    with shelve.open(f"data/{nome_arquivo}") as db:
        db[chave] = dados


def carregar(nome_arquivo, chave):
    caminho = f"data\\{nome_arquivo}"
    try:
        with shelve.open(caminho, flag='r') as db:
            if chave in db:
                return db[chave]
            return None
    except dbm.error:
        return None


DB_PATH = f"{os.getcwd()}/data/banco.sqlite"


def _criar_tabela():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS frames (
                    tabela TEXT NOT NULL,
                    usuario TEXT NOT NULL,
                    frame BLOB,
                    PRIMARY KEY (tabela, usuario)
                )
            """)
        conn.commit()


def salvar_seguro(tabela, dados_novos):
    _criar_tabela()
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            for usuario, frame_io in dados_novos.items():
                frame_bytes = frame_io.getvalue() if isinstance(
                    frame_io, io.BytesIO) else frame_io
                cursor.execute("""
                        INSERT INTO frames (tabela, usuario, frame)
                        VALUES (?, ?, ?)
                        ON CONFLICT(tabela, usuario) DO UPDATE SET frame=excluded.frame
                    """, (tabela, usuario, frame_bytes))
            conn.commit()
    except Exception as e:
        print("Erro ao salvar no SQLite:", e)
