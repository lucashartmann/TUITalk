export default function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method === 'POST') {
    const { url } = req.body;

    if (!url) {
      return res.status(400).json({ error: 'URL não fornecida' });
    }

    try {
      global.currentUrl = url;
      global.urlTimestamp = Date.now();

      console.log('URL do ngrok recebida e salva:', url);
      console.log('global.currentUrl:', global.currentUrl);
      console.log('global.urlTimestamp:', global.urlTimestamp);

      res.status(200).json({ status: 'ok', url: url });
    } catch (error) {
      console.error('Erro ao salvar URL:', error);
      res.status(500).json({ error: 'Erro interno do servidor' });
    }
  } else {
    res.status(405).json({ error: 'Method not allowed' });
  }
}
