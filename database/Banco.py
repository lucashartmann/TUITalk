import dbm
import shelve
import os


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


def deletar(nome_arquivo, chave):
    with shelve.open(f"data\\{nome_arquivo}") as db:
        del db[chave]


def iterar(nome_arquivo):
    with shelve.open(f"data\\{nome_arquivo}") as db:
        for chave in db:
            print(chave, db[chave])