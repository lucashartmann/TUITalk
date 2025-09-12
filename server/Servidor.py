import os
from textual_serve.server import Server

port = int(os.environ.get('PORT', 8000))
server = Server(
    "python Main.py",
    port=port,
    host="0.0.0.0",
    public_url="https://55849bcfb94e.ngrok-free.app"
)

if __name__ == "__main__":
    if os.path.isdir("data/banco.db"):
        os.remove("data/banco.db")
    if os.path.isdir("data/banco.db-shm"):
        os.remove("data/banco.db-shm")
    if os.path.isdir("data/banco.db-wal"):
        os.remove("data/banco.db-wal")
    server.serve()
