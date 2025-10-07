from textual_serve.server import Server
import sys

comando = sys.argv[1:]

servidor = Server(
    command="python Main.py",
    port=8000,
    host="0.0.0.0",
    public_url=comando[-1]
)

servidor.serve() 
