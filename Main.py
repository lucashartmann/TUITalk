from view.App import App
import sys
import os

comando = sys.argv[1:]

if "python" in comando or "textual" in comando:
    comando = sys.argv[comando.index("Main.py"):]

if __name__ == "__main__":
    app = App()
    
    if os.environ.get("TEXTUAL_RUN") == "1":
        app.servidor = True
        
    if comando:
        app.tela = "tela_servidor"
   
    app.run()
