const FLASK_URL = "https://textual-message.vercel.app"; 

async function redirectToFlask() {
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 5000);
    const res = await fetch(`${FLASK_URL}/get_redirect`, { signal: controller.signal });
    clearTimeout(timeout);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    if (data.url) {
      if (/^https?:\/\//i.test(data.url)) {
        window.location.href = data.url;
      } else {
        console.error("Invalid redirect URL:", data.url);
      }
    } else {
      console.error("No url in response:", data);
    }
  } catch (e) {
    console.error("Erro ao buscar URL do Flask:", e);
    const status = document.getElementById("status");
    if (status) status.textContent = "Erro ao contatar servidor.";
  }
}

redirectToFlask();
