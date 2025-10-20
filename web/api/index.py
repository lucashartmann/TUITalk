from flask import Flask, request, jsonify
from flask_cors import CORS
import queue

app = Flask(__name__)

current_url = None

CORS(app)


@app.route("/set_url", methods=["POST"])
def set_url():
    global current_url
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({"status": "error", "message": "URL não fornecida"}), 400

        current_url = data.get("url")
        print(f"URL do ngrok recebida: {current_url}")
        return jsonify({"status": "ok", "url": current_url})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/url", methods=["GET"])
def get_url():
    if current_url:
        return jsonify({"redirect": current_url})
    return jsonify({"redirect": None})


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "url": current_url})


def run_flask():
    app.run(port=5000)


if __name__ == "__main__":
    run_flask()
