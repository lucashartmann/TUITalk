import os
from textual_serve.server import Server

port = int(os.environ.get('PORT', 8000))
server = Server(
    "python Main.py", 
    port=port, 
    host="0.0.0.0",
    public_url="https://f46867dadb6b.ngrok-free.app"
)
server.serve()