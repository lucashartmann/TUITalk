from view.App import App
import os
import sys

if __name__ == "__main__":
    if os.path.exists("data"):
        if len(os.listdir("data")) > 0:
            for arquivo in os.listdir("data"):
                os.remove(f"data/{arquivo}")

    app = App()
    if os.environ.get("TEXTUAL_RUN") == "1":
        app.tela = "tela_login"
    os.environ["TEXTUAL_RUN"] = "0"
    app.run()
