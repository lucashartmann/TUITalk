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
                CREATE TABLE IF NOT EXISTS Usuario (
                    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
                    foto BLOB,
                    cor TEXT UNIQUE,
                    status TEXT,
                    nome TEXT,
                    tempo TEXT
                )
            """)
            conexao.commit()

    def salvar_mensagem(self, autor, arquivo, tipo, hash, nome):
        with sqlite3.connect("data/Banco.db") as conexao:
            cursor = conexao.cursor()
            if isinstance(arquivo, io.BytesIO):
                arquivo = arquivo.getvalue()
            try:
                cursor.execute(
                    "INSERT INTO Mensagem (autor, arquivo, tipo, hash, nome) VALUES (?, ?, ?, ?, ?)",
                    (autor, arquivo, tipo, hash, nome)
                )
                conexao.commit()
                return True
            except Exception as e:
                print("ERRO ao salvar_mensagem no SQLite:", e)
                return False

    def salvar_usuario(self, usuario):
        with sqlite3.connect("data/Banco.db") as conexao:
            cursor = conexao.cursor()
            try:
                cursor.execute(
                    "INSERT INTO Usuario (foto, cor, status, nome, tempo) VALUES (?, ?, ?, ?, ?)",
                    (usuario.get_foto(), usuario.get_cor(), usuario.get_status(), usuario.get_nome(), usuario.get_tempo())
                )
                conexao.commit()
                return True
            except Exception as e:
                print("ERRO ao salvar_usuario no SQLite:", e)
                return False

    def atualizar(self, tabela, coluna, coluna_condicao, valor_novo, valor_condicao):
        with sqlite3.connect("data/Banco.db") as conexao:
            cursor = conexao.cursor()
            try:
                cursor.execute(f"UPDATE {tabela} SET {coluna} = ? WHERE {coluna_condicao} = ?", (valor_novo, valor_condicao))
                conexao.commit()
                return True
            except Exception as e:
                print(f"ERRO ao atualizar {tabela} no SQLite:", e)
                return False

    def salvar_um(self, tabela, valor):
        with sqlite3.connect("data/Banco.db") as conexao:
            cursor = conexao.cursor()
            try:
                cursor.execute(f"DELETE FROM {tabela}")
                cursor.execute(f"INSERT INTO {tabela} ({tabela.lower()}) VALUES (?)", (valor,))
                conexao.commit()
                return True
            except Exception as e:
                print(f"ERRO ao salvar_um no SQLite:", e)
                return False

    def carregar_um(self, tabela):
        try:
            with sqlite3.connect("data/Banco.db") as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT * FROM {tabela}")
                chave = cursor.fetchone()
                if chave:
                    return chave[1]
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