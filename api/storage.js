export default async function handler(req, res) {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS');
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

            console.log('URL salva no storage:', url);

            res.status(200).json({ status: 'ok', url: url });
        } catch (error) {
            console.error('Erro ao salvar URL:', error);
            res.status(500).json({ error: 'Erro interno do servidor' });
        }
    } else if (req.method === 'GET') {
        try {
            const currentUrl = global.currentUrl;

            console.log('URL lida do storage:', currentUrl);

            if (currentUrl) {
                res.status(200).json({ redirect: currentUrl });
            } else {
                res.status(200).json({ redirect: null });
            }
        } catch (error) {
            console.error('Erro ao ler URL:', error);
            res.status(200).json({ redirect: null });
        }
    } else if (req.method === 'DELETE') {
        try {
            global.currentUrl = null;
            global.urlTimestamp = null;

            console.log('URL removida do storage');

            res.status(200).json({ status: 'ok', message: 'URL removida' });
        } catch (error) {
            console.error('Erro ao remover URL:', error);
            res.status(500).json({ error: 'Erro interno do servidor' });
        }
    } else {
        res.status(405).json({ error: 'Method not allowed' });
    }
}
