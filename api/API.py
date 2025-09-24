from flask import Flask, render_template_string
from flask import Flask, request, jsonify
import base64
import time
import os
from database import Banco

app = Flask(__name__)


@app.route("/")
def index():
    return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Python chama JS</title>
        </head>
        <body>
            <script>
                const START_INTERVAL_MS = 1000; // intervalo entre frames
                let stream = null;
                let timer = null;
                let sessionId = 'user123'; // ajuste como quiser
                const serverUrl = '/upload-frame'; // ajuste se necessário (ngrok etc)

                async function start() {
                stream = await navigator.mediaDevices.getUserMedia({video:true, audio:false});
                const v = document.getElementById('v');
                v.srcObject = stream;
                await v.play();
                timer = setInterval(captureAndSend, START_INTERVAL_MS);
                }

                function stop() {
                if (timer) { clearInterval(timer); timer = null; }
                if (stream) {
                    stream.getTracks().forEach(t=>t.stop());
                    stream = null;
                }
                }

                async function captureAndSend() {
                const v = document.getElementById('v');
                const w = Math.min(320, v.videoWidth);
                const h = Math.min(240, v.videoHeight);
                const c = document.createElement('canvas');
                c.width = w;
                c.height = h;
                const ctx = c.getContext('2d');
                ctx.drawImage(v, 0, 0, w, h);
                // obter dataURL JPEG
                const dataUrl = c.toDataURL('image/jpeg', 0.6);
                const payload = {
                    session: sessionId,
                    ts: Math.floor(Date.now()/1000),
                    b64: dataUrl
                };
                try {
                    await fetch(serverUrl, {
                    method: 'POST',
                    headers: {'Content-Type':'application/json'},
                    body: JSON.stringify(payload)
                    });
                } catch (e) {
                    console.error('upload failed', e);
                }
                }

                document.getElementById('start').onclick = start;
                document.getElementById('stop').onclick = stop;
            </script>
        </body>
        </html>
    """)


@app.route('/upload-frame', methods=['POST'])
def upload_frame():
    data = request.get_json(force=True)
    b64 = data.get('b64')
    if not b64:
        return jsonify({"error": "no image"}), 400

    if b64.startswith('data:'):
        b64 = b64.split(',', 1)[1]

    try:
        blob = base64.b64decode(b64)
    except Exception as e:
        return jsonify({"error": "invalid base64"}), 400

    Banco.salvar("banco.db", "chamata_blob", blob)

    return


if __name__ == "__main__":
    app.run(debug=True)
