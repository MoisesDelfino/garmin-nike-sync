// popup.js - Lógica da interface da extensão

document.addEventListener('DOMContentLoaded', function() {
    const extractBtn = document.getElementById('extractBtn');
    const copyBtn = document.getElementById('copyBtn');
    const status = document.getElementById('status');
    const tokenDisplay = document.getElementById('tokenDisplay');
    const tokenValue = document.getElementById('tokenValue');

    let currentToken = '';

    // Extrai o token
    extractBtn.addEventListener('click', async function() {
        try {
            updateStatus('loading', '🔍 Procurando token...');
            
            // Busca cookies do Nike.com
            const cookies = await chrome.cookies.getAll({
                domain: '.nike.com'
            });

            // Procura pelo access_token
            let token = null;
            
            // Método 1: Procurar no cookie 'access_token'
            const accessTokenCookie = cookies.find(c => c.name === 'access_token');
            if (accessTokenCookie) {
                token = accessTokenCookie.value;
            }

            // Método 2: Procurar em outros cookies comuns da Nike
            if (!token) {
                const nikeCookies = cookies.filter(c => 
                    c.name.toLowerCase().includes('token') ||
                    c.name.toLowerCase().includes('bearer') ||
                    c.name.toLowerCase().includes('auth')
                );
                
                if (nikeCookies.length > 0) {
                    token = nikeCookies[0].value;
                }
            }

            // Método 3: Tentar extrair do localStorage via content script
            if (!token) {
                const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
                
                if (tab && tab.url && tab.url.includes('nike.com')) {
                    const response = await chrome.tabs.sendMessage(tab.id, { action: 'getToken' });
                    if (response && response.token) {
                        token = response.token;
                    }
                }
            }

            if (token && token.length > 20) {
                currentToken = token;
                tokenValue.textContent = token;
                tokenDisplay.classList.add('show');
                copyBtn.classList.add('show');
                updateStatus('success', '✅ Token extraído com sucesso!');
                
                // Salva no storage para uso futuro
                chrome.storage.local.set({ nikeToken: token });
            } else {
                throw new Error('Token não encontrado');
            }

        } catch (error) {
            console.error('Erro ao extrair token:', error);
            updateStatus('error', '❌ Erro: Faça login no Nike.com primeiro!');
            tokenDisplay.classList.remove('show');
            copyBtn.classList.remove('show');
        }
    });

    // Copia o token
    copyBtn.addEventListener('click', async function() {
        try {
            await navigator.clipboard.writeText(currentToken);
            
            // Feedback visual
            const originalText = copyBtn.innerHTML;
            copyBtn.innerHTML = '<span class="icon">✓</span> Copiado!';
            copyBtn.style.background = 'rgba(76, 175, 80, 0.3)';
            
            setTimeout(() => {
                copyBtn.innerHTML = originalText;
                copyBtn.style.background = '';
            }, 2000);
            
            updateStatus('success', '📋 Token copiado! Cole no aplicativo.');
            
        } catch (error) {
            console.error('Erro ao copiar:', error);
            updateStatus('error', '❌ Erro ao copiar. Selecione e copie manualmente.');
        }
    });

    // Verifica se já tem token salvo
    chrome.storage.local.get(['nikeToken'], function(result) {
        if (result.nikeToken) {
            currentToken = result.nikeToken;
            tokenValue.textContent = result.nikeToken;
            tokenDisplay.classList.add('show');
            copyBtn.classList.add('show');
            updateStatus('success', '✅ Token anterior carregado');
        }
    });

    function updateStatus(type, message) {
        status.className = `status ${type}`;
        status.innerHTML = message;
    }
});
