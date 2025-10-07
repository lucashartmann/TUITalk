from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
import cv2
import numpy as np
import queue
from threading import Thread
import os

app = Flask(__name__)

current_url = None

button_clicked = False

CORS(app)

frame_queue = queue.Queue(maxsize=10)


@app.route('/video_frame', methods=['POST'])
def receive_frame():
    if 'frame' not in request.files:
        return {'error': 'No frame'}, 400

    file = request.files['frame']

    img_bytes = file.read()
    nparr = np.frombuffer(img_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    try:
        frame_queue.put_nowait(frame)
    except queue.Full:
        try:
            frame_queue.get_nowait()
            frame_queue.put_nowait(frame)
        except:
            pass

    return {'status': 'ok'}, 200


@app.route("/ping")
def ping():
    return "pong", 200


def get_latest_frame():
    try:
        return frame_queue.get_nowait()
    except queue.Empty:
        return None


@app.route(f'/check-button', methods=['GET'])
def check_button():
    global button_clicked
    if button_clicked:
        button_clicked = False
        return jsonify({"start": True})
    return jsonify({"start": False})


@app.route("/upload-data", methods=["POST"])
def upload_data():
    if "frame" not in request.files:
        return jsonify({"error": "Nenhum frame recebido"}), 400

    frame = request.files["frame"]

    save_path = os.path.join("frames", frame.filename)
    os.makedirs("frames", exist_ok=True)
    frame.save(save_path)

    print(f"🖼️ Frame salvo em: {save_path}")
    return jsonify({"status": "ok"})


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
    app.run(port=5000)
