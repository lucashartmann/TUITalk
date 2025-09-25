# flask_server.py
from flask import Flask, jsonify, request

app = Flask(__name__)
redirect_url = "https://google.com"  # URL inicial

@app.route("/get_redirect")
def get_redirect():
    return jsonify({"url": redirect_url})

@app.route("/set_redirect", methods=["POST"])
def set_redirect():
    global redirect_url
    data = request.json
    if data and "url" in data:
        redirect_url = data["url"]
        return jsonify({"status": "ok", "new_url": redirect_url})
    return jsonify({"status": "error"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
