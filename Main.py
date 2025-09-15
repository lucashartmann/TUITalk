from view.App import App
import os


if __name__ == "__main__":
    if os.path.exists("data"):
        if len(os.listdir("data")) > 0:
            for arquivo in os.listdir("data"):
                os.remove(f"data/{arquivo}")

    app = App()
    app.run()
