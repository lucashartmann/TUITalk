import os
from textual_serve.server import Server
import sys

comando = sys.argv[1:]


cert_path = f"{os.getcwd()}/data/cert.pem"
key_path = f"{os.getcwd()}/data/key.pem"


if "http" in comando or "https" in comando:

    servidor = Server(
        command="python Main.py",
        port=8000,
        host="0.0.0.0",
        public_url=comando[-1]
    )

else:
    try:
        servidor = Server(
            command="python Main.py",
            host=comando[-1],
            port=8000,
            ssl_cert=cert_path,
            ssl_key=key_path
        )
    except:
        servidor = Server(
            command="python Main.py",
            host=comando[-1],
            port=8000,
        )

servidor.serve()
