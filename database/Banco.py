import io
import sqlite3
import os


class Banco:

    def __init__(self):
        diretorio = "data"
        if not os.path.isdir(diretorio):
            os.makedirs(diretorio)
        self.init_tabelas()

    def init_tabelas(self):
        with sqlite3.connect(f"/data/Banco.db") as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Mensagem (
                    id_mensagem AUTOINCREMENT,
                    autor TEXT,
                    arquivo BLOB,
                    tipo TEXT,
                    hash TEXT,
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Frame (
                    id_frame AUTOINCREMENT,
                    tabela TEXT NOT NULL,
                    usuario TEXT NOT NULL,
                    frame BLOB,
                    PRIMARY KEY (tabela, usuario)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Url (
                    id_url AUTOINCREMENT,
                    url TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Chave (
                    id_chave AUTOINCREMENT,
                    chave TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Acao (
                    id_acao AUTOINCREMENT,
                    acao TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Usuario (
                    id_usuario AUTOINCREMENT,
                    foto BLOB, 
                    cor TEXT PRIMARY KEY, 
                    status TEXT, 
                    nome TEXT, 
                    tempo TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Chamada (
                    caller TEXT, 
                    receiver TEXT, 
                    FOREIGN KEY (caller) REFERENCES Usuario (cor),
                    FOREIGN KEY (receiver) REFERENCES Usuario (cor),
                )
            """)

    def atualizar(self, tabela, tipo_dado, condicao, novo_valor):
        with sqlite3.connect(f"data/Biblioteca.db") as conexao:
            cursor = conexao.cursor()
            try:
                sql_update_query = f"""
                UPDATE {tabela}
                SET {tipo_dado} = ?
                WHERE id = ?;
                """
                dados = (novo_valor, condicao)
                cursor.execute(sql_update_query, dados)
                conexao.commit()
                return True
            except Exception as e:
                print("ERRO ao atualizar leitor", e)
                return False

    def salvar_usuario(self, usuario):
        with sqlite3.connect(f"data/Biblioteca.db") as conexao:
            cursor = conexao.cursor()
            try:
                cursor.execute(
                    f'INSERT INTO Leitor (foto, cor, status, nome, tempo) VALUES (?, ?)', (usuario.get_foto(), usuario.get_cor(), usuario.get_status(), usuario.get_nome(), usuario.get_tempo()))
                conexao.commit()
                return True
            except Exception as e:
                print("ERRO ao adicionar leitor", e)
                return False

    def salvar_mensagem(dados_novos):
        if "autor" in dados_novos.keys():
            autor = dados_novos["autor"]
        else:
            autor = ""
        if "arquivo" in dados_novos.keys():
            arquivo = dados_novos["arquivo"]
        else:
            arquivo = ""
        if "tipo" in dados_novos.keys():
            tipo = dados_novos["tipo"]
        else:
            tipo = ""
        if "hash" in dados_novos.keys():
            hash = dados_novos["hash"]
        else:
            hash = ""

        try:
            with sqlite3.connect(f"/data/Banco.db") as conn:
                cursor = conn.cursor()
                cursor.execute("""
                            INSERT INTO mensagem (autor, arquivo, tipo, hash)
                            VALUES (?, ?, ?)
                        """, (autor, arquivo, tipo, hash))
                conn.commit()
                return True
        except Exception as e:
            print("Erro ao salvar_mensagem no SQLite:", e)
            return False

    def salvar_um(self, tabela, dado):
        with sqlite3.connect(f"data/Banco.db") as conexao:
            cursor = conexao.cursor()
            try:
                cursor.execute(
                    f'INSERT INTO {tabela} (?) VALUES (?)', (dado))
                conexao.commit()
                return True
            except Exception as e:
                print("ERRO ao salvar_chave no SQLite", e)
                return False

    def carregar_um(self, tabela):
        try:
            with sqlite3.connect(f"/data/Banco.db") as conn:
                cursor = conn.cursor()
                cursor.execute(f"""SELECT * from {tabela}""",)
                chave = cursor.fetchone()

                if chave:
                    return chave
                else:
                    return None

        except Exception as e:
            print("Erro ao carregar_chave no SQLite:", e)
            return None

    def carregar_usuarios():
        try:
            with sqlite3.connect(f"/data/Banco.db") as conn:
                cursor = conn.cursor()
                cursor.execute("""SELECT * from Usuario""",)
                usuarios = cursor.fetchall()

            if usuarios:
                dicionario_usuarios = {}
                for usuario in usuarios:
                    dicionario_usuarios["id"] = usuario[0]
                    dicionario_usuarios["foto"] = usuario[1]
                    dicionario_usuarios["cor"] = usuario[2]
                    dicionario_usuarios["status"] = usuario[4]
                    dicionario_usuarios["nome"] = usuario[5]
                    dicionario_usuarios["tempo"] = usuario[6]
                return dicionario_usuarios
            else:
                return []
        except Exception as e:
            print("Erro ao carregar_mensagens no SQLite:", e)
            return []

    def carregar_mensagens():
        try:
            with sqlite3.connect(f"/data/Banco.db") as conn:
                cursor = conn.cursor()
                cursor.execute("""SELECT * from Mensagem""",)
                mensagens = cursor.fetchall()

            if mensagens:
                dicionario_mensagens = {}
                for mensagem in mensagens:
                    dicionario_mensagens["autor"] = mensagem[1]
                    dicionario_mensagens["arquivo"] = mensagem[2]
                    dicionario_mensagens["tipo"] = mensagem[3]
                    dicionario_mensagens["hash"] = mensagem[4]
                return dicionario_mensagens
            else:
                return []
        except Exception as e:
            print("Erro ao carregar_mensagens no SQLite:", e)
            return []

    def carregar_frames():
        resultado = {}
        try:
            with sqlite3.connect(Banco.DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT usuario, frame FROM Frame")
                for usuario, frame_bytes in cursor.fetchall():
                    resultado[usuario] = io.BytesIO(frame_bytes)
        except Exception as e:
            print("Erro ao carregar do SQLite:", e)
        return resultado

    def salvar_seguro_chamada(dados_novos):
        try:
            with sqlite3.connect(f"/data/Banco.db") as conn:
                cursor = conn.cursor()
                for usuario, frame_io in dados_novos.items():
                    frame_bytes = frame_io.getvalue() if isinstance(
                        frame_io, io.BytesIO) else frame_io
                    cursor.execute("""
                            INSERT INTO Frame (usuario, frame)
                            VALUES (?, ?, ?)
                            ON CONFLICT(usuario) DO UPDATE SET frame=excluded.frame
                        """, (usuario, frame_bytes))
                conn.commit()
                return True
        except Exception as e:
            print("Erro ao salvar_seguro_chamada no SQLite:", e)
            return False
