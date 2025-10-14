import sqlite3
import io
import os

class Banco:
    DB_PATH = f"{os.getcwd()}/data/banco2.sqlite"

    @staticmethod
    def _criar_tabela():
        os.makedirs(os.path.dirname(Banco.DB_PATH), exist_ok=True)
        with sqlite3.connect(Banco.DB_PATH) as conn:
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

    @staticmethod
    def salvar_seguro(tabela, dados_novos):
        Banco._criar_tabela()
        try:
            with sqlite3.connect(Banco.DB_PATH) as conn:
                cursor = conn.cursor()
                for usuario, frame_io in dados_novos.items():
                    frame_bytes = frame_io.getvalue() if isinstance(frame_io, io.BytesIO) else frame_io
                    # Insert ou update
                    cursor.execute("""
                        INSERT INTO frames (tabela, usuario, frame)
                        VALUES (?, ?, ?)
                        ON CONFLICT(tabela, usuario) DO UPDATE SET frame=excluded.frame
                    """, (tabela, usuario, frame_bytes))
                conn.commit()
        except Exception as e:
            print("Erro ao salvar no SQLite:", e)

    @staticmethod
    def carregar(tabela):
        Banco._criar_tabela()
        resultado = {}
        try:
            with sqlite3.connect(Banco.DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT usuario, frame FROM frames WHERE tabela=?", (tabela,))
                for usuario, frame_bytes in cursor.fetchall():
                    resultado[usuario] = io.BytesIO(frame_bytes)
        except Exception as e:
            print("Erro ao carregar do SQLite:", e)
        return resultado
