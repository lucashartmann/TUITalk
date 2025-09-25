const FLASK_URL = "https://textual-message.vercel.app";

async function redirectToFlask() {
  const res = await fetch(`${FLASK_URL}/get_redirect`);
  const data = await res.json();
  if (data.url) {
    if (/^https?:\/\//i.test(data.url)) {
      window.location.href = data.url;
    }
  }

}

redirectToFlask();
