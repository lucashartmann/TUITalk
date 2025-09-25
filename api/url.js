export default function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
  res.setHeader('Pragma', 'no-cache');
  res.setHeader('Expires', '0');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method === 'GET') {
    try {
      let currentUrl = null;
      
      currentUrl = global.currentUrl;
      
      if (!currentUrl) {
        try {
          const fs = require('fs');
          if (fs.existsSync('/tmp/current_url.json')) {
            const data = JSON.parse(fs.readFileSync('/tmp/current_url.json', 'utf8'));
            currentUrl = data.url;
            console.log('URL lida do arquivo temporário:', currentUrl);
          }
        } catch (fileError) {
          console.log('Erro ao ler arquivo (usando apenas globais):', fileError.message);
        }
      }
      
      console.log('GET /api/url - currentUrl final:', currentUrl);
      console.log('global.currentUrl:', global.currentUrl);
      console.log('global.urlTimestamp:', global.urlTimestamp);
      
      if (currentUrl) {
        res.status(200).json({ redirect: currentUrl });
      } else {
        res.status(200).json({ redirect: null });
      }
    } catch (error) {
      console.error('Erro ao ler URL:', error);
      res.status(200).json({ redirect: null });
    }
  } else {
    res.status(405).json({ error: 'Method not allowed' });
  }
}
