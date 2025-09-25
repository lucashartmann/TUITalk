from flask import Flask, request, jsonify
import os

app = Flask(__name__)

current_url = None


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


if __name__ == '__main__':
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

    print(f"Iniciando Flask na porta {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
