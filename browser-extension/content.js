// content.js - Script que roda nas páginas do Nike.com

// Listener para mensagens da popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'getToken') {
        try {
            // Tenta extrair token do localStorage
            let token = null;
            
            // Método 1: localStorage
            if (window.localStorage) {
                // Nike armazena tokens de diferentes formas
                const possibleKeys = [
                    'access_token',
                    'nike_access_token',
                    'auth_token',
                    'bearer_token',
                    'user_token'
                ];
                
                for (const key of possibleKeys) {
                    const value = localStorage.getItem(key);
                    if (value && value.length > 20) {
                        token = value;
                        break;
                    }
                }
                
                // Procura em objetos JSON no localStorage
                if (!token) {
                    for (let i = 0; i < localStorage.length; i++) {
                        const key = localStorage.key(i);
                        const value = localStorage.getItem(key);
                        
                        try {
                            const parsed = JSON.parse(value);
                            if (parsed.access_token || parsed.token || parsed.accessToken) {
                                token = parsed.access_token || parsed.token || parsed.accessToken;
                                break;
                            }
                        } catch (e) {
                            // Não é JSON, continua
                        }
                    }
                }
            }
            
            // Método 2: sessionStorage
            if (!token && window.sessionStorage) {
                const possibleKeys = [
                    'access_token',
                    'nike_access_token',
                    'auth_token'
                ];
                
                for (const key of possibleKeys) {
                    const value = sessionStorage.getItem(key);
                    if (value && value.length > 20) {
                        token = value;
                        break;
                    }
                }
            }
            
            // Método 3: Procura em variáveis globais
            if (!token && window.__NEXT_DATA__) {
                // Next.js apps da Nike podem ter dados aqui
                const data = JSON.stringify(window.__NEXT_DATA__);
                const tokenMatch = data.match(/access_token["']?\s*:\s*["']([^"']+)["']/);
                if (tokenMatch) {
                    token = tokenMatch[1];
                }
            }
            
            sendResponse({ token: token });
        } catch (error) {
            console.error('Erro ao extrair token:', error);
            sendResponse({ token: null, error: error.message });
        }
    }
    
    return true; // Mantém o canal aberto para resposta assíncrona
});

// Detecta quando o usuário faz login
window.addEventListener('storage', function(e) {
    if (e.key && (e.key.includes('token') || e.key.includes('auth'))) {
        // Notifica que um token pode estar disponível
        chrome.runtime.sendMessage({ 
            action: 'tokenAvailable',
            key: e.key,
            value: e.newValue 
        });
    }
});

console.log('Nike Token Extractor - Content script loaded');
