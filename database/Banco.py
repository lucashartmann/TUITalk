import io
import sqlite3
import os
from model.Usuario import Usuario


class Banco:

    def __init__(self):
        diretorio = "data"
        if not os.path.isdir(diretorio):
            os.makedirs(diretorio)
        self.init_tabelas()

    def init_tabelas(self):
        with sqlite3.connect("data/Banco.db") as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Mensagem (
                    id_mensagem INTEGER PRIMARY KEY AUTOINCREMENT,
                    autor TEXT,
                    arquivo BLOB,
                    tipo TEXT,
                    hash TEXT,
                    nome TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Frame (
                        usuario TEXT PRIMARY KEY,
                        frame BLOB
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Url (
                    id_url INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Chave (
                    id_chave INTEGER PRIMARY KEY AUTOINCREMENT,
                    chave TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Acao (
                    id_acao INTEGER PRIMARY KEY AUTOINCREMENT,
                    acao TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Usuario (
                    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
                    foto BLOB,
                    cor TEXT UNIQUE,
                    status TEXT,
                    nome TEXT,
                    tempo TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Chamada (
                    caller TEXT,
                    receiver TEXT
                )
            """)  # TODO: arrumar FOREIGN KEY (receiver) REFERENCES Usuario (cor)
            conexao.commit()

    def deletar(self, tabela):
        try:
            with sqlite3.connect("data/Banco.db") as conn:
                cursor = conn.cursor()
                cursor.execute(f"DELETE FROM {tabela}")
                conn.commit()
                return True
        except Exception as e:
            print("Erro ao deletar chamada:", e)
            return False

    def salvar_chamada(self, chamada):
        with sqlite3.connect("data/Banco.db") as conexao:
            cursor = conexao.cursor()
            try:
                cursor.execute(
                    "INSERT INTO Chamada (caller, receiver) VALUES (?, ?)",
                    (chamada["caller"], chamada["receiver"])
                )
                conexao.commit()
                return True
            except Exception as e:
                print("ERRO ao salvar_chamada no SQLite:", e)
                return False

    def carregar_chamada(self):
        try:
            with sqlite3.connect("data/Banco.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM Chamada")
                chave = cursor.fetchone()
                if chave:
                    dicionario_chamada = {
                        "caller": chave[0],
                        "receiver": chave[1]
                    }
                    return dicionario_chamada
                else:
                    return None
        except Exception as e:
            print("ERRO ao carregar_chamada no SQLite:", e)
            return None

    def atualizar(self, tabela, coluna, coluna_condicao, valor_novo, valor_condicao):
        with sqlite3.connect("data/Banco.db") as conexao:
            cursor = conexao.cursor()
            try:
                sql_update_query = f"""
                    UPDATE {tabela}
                    SET {coluna} = ?
                    WHERE {coluna_condicao} = ?;
                """
                cursor.execute(sql_update_query, (valor_novo, valor_condicao))
                conexao.commit()
                return True
            except Exception as e:
                print(f"ERRO ao atualizar tabela '{tabela}':", e)
                return False

    def salvar_usuario(self, usuario):
        with sqlite3.connect("data/Banco.db") as conexao:
            cursor = conexao.cursor()
            try:
                cursor.execute(
                    """
                    INSERT INTO Usuario (foto, cor, status, nome, tempo)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        usuario.get_foto(),
                        usuario.get_cor(),
                        usuario.get_status(),
                        usuario.get_nome(),
                        usuario.get_tempo(),
                    )
                )
                conexao.commit()
                return True
            except Exception as e:
                print("ERRO ao adicionar usuario:", e)
                return False

    def salvar_mensagem(self, dados_novos):
        autor = dados_novos.get("autor", "")
        arquivo = dados_novos.get("arquivo", "")
        tipo = dados_novos.get("tipo", "")
        hash_valor = dados_novos.get("hash", "")
        nome = dados_novos.get("nome", "")

        try:
            with sqlite3.connect("data/Banco.db") as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO Mensagem (autor, arquivo, tipo, hash, nome)
                    VALUES (?, ?, ?, ?, ?)
                """, (autor, arquivo, tipo, hash_valor, nome))
                conn.commit()
                return True
        except Exception as e:
            print("Erro ao salvar_mensagem no SQLite:", e)
            return False

    def salvar_um(self, tabela, coluna, dado):
        with sqlite3.connect("data/Banco.db") as conexao:
            cursor = conexao.cursor()
            try:
                cursor.execute(
                    f"INSERT INTO {tabela} ({coluna}) VALUES (?)", (dado,)
                )
                conexao.commit()
                return True
            except Exception as e:
                print("ERRO ao salvar dado no SQLite:", e)
                return False

    def carregar_um(self, tabela):
        try:
            with sqlite3.connect("data/Banco.db") as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT * FROM {tabela}")
                chave = cursor.fetchone()

                if chave:
                    return chave
                else:
                    return None

        except Exception as e:
            print(f"Erro ao carregar dados da tabela {tabela} no SQLite:", e)
            return None

    def carregar_usuarios(self):
        try:
            with sqlite3.connect("data/Banco.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM Usuario")
                usuarios = cursor.fetchall()

            if usuarios:
                lista_usuarios = []
                for usuario in usuarios:
                    usuarioo = Usuario()
                    usuarioo.set_id(int(usuario[0]))
                    usuarioo.set_foto(usuario[1])
                    usuarioo.set_cor(usuario[2])
                    usuarioo.set_status(usuario[3])
                    usuarioo.set_nome(usuario[4])
                    usuarioo.set_tempo(int(usuario[5]))

                    lista_usuarios.append(usuarioo)
                return lista_usuarios
            else:
                return []
        except Exception as e:
            print("Erro ao carregar_usuarios no SQLite:", e)
            return []

    def carregar_mensagens(self):
        try:
            with sqlite3.connect("data/Banco.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM Mensagem")
                mensagens = cursor.fetchall()

            if mensagens:
                lista_mensagens = []
                for mensagem in mensagens:
                    dicionario = {
                        "id": mensagem[0],
                        "autor": mensagem[1],
                        "arquivo": mensagem[2],
                        "tipo": mensagem[3],
                        "hash": mensagem[4],
                        "nome": mensagem[5]
                    }
                    lista_mensagens.append(dicionario)
                return lista_mensagens
            else:
                return []
        except Exception as e:
            print("Erro ao carregar_mensagens no SQLite:", e)
            return []

    def carregar_frames(self):
        resultado = {}
        try:
            with sqlite3.connect("data/Banco.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT usuario, frame FROM Frame")
                for usuario, frame_bytes in cursor.fetchall():
                    resultado[usuario] = io.BytesIO(frame_bytes)
        except Exception as e:
            print("Erro ao carregar frames do SQLite:", e)
        return resultado

    def salvar_seguro_chamada(self, dados_novos):
        try:
            with sqlite3.connect("data/Banco.db") as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS Frame (
                        usuario TEXT PRIMARY KEY,
                        frame BLOB
                    )
                """)
                for usuario, frame_io in dados_novos.items():
                    frame_bytes = frame_io.getvalue() if isinstance(
                        frame_io, io.BytesIO) else frame_io
                    cursor.execute("""
                        INSERT OR REPLACE INTO Frame (usuario, frame)
                        VALUES (?, ?)
                    """, (usuario, frame_bytes))
                conn.commit()
                return True
        except Exception as e:
            print("Erro ao salvar_seguro_chamada no SQLite:", e)
            return False
