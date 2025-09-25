const FLASK_URL = "https://MEU-FLASK-SERVER.com"; // coloque o URL público do Flask

async function redirectToFlask() {
    try {
        const res = await fetch(`${FLASK_URL}/get_redirect`);
        const data = await res.json();
        if (data.url) {
            window.location.href = data.url;
        }
    } catch (e) {
        console.error("Erro ao buscar URL do Flask:", e);
    }
}

redirectToFlask();

document.getElementById("btn").addEventListener("click", redirectToFlask);