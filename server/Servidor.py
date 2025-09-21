import os
from textual_serve.server import Server

port = int(os.environ.get('PORT', 8000))
server = Server(
    "python Main.py",
    port=port,
    host="0.0.0.0",
    public_url="https://b663d8809f44.ngrok-free.app"
)

if __name__ == "__main__":
    if os.path.exists("data"):
        if len(os.listdir("data")) > 0:
            for arquivo in os.listdir("data"):
                os.remove(f"data/{arquivo}")
    server.serve()
