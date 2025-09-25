from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)

CORS(app, origins=["https://textual-message.vercel.app"])

redirect_url = "https://google.com"

@app.route("/get_redirect", methods=["GET"])
def get_redirect():
    return jsonify({"url": redirect_url})

@app.route("/set_redirect", methods=["POST"])
def set_redirect():
    global redirect_url
    data = request.get_json(silent=True)
    if not data or "url" not in data:
        return jsonify({"status": "error", "message": "missing 'url'"}), 400
    redirect_url = data["url"]
    return jsonify({"status": "ok", "new_url": redirect_url})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
