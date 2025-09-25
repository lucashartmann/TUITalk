from flask import Flask, redirect, request

app = Flask(__name__)

redirect_url = "https://google.com"

@app.route("/")
def home():
    return redirect(redirect_url, code=302)

@app.route("/set_redirect", methods=["POST"])
def set_redirect():
    global redirect_url
    new_url = request.json.get("url")
    if new_url:
        redirect_url = new_url
        return {"status": "ok", "new_url": redirect_url}
    return {"status": "error", "message": "URL inválida"}, 400
