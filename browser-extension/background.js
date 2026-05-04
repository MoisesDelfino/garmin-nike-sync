// background.js - Service worker da extensão

// Listener para mensagens
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'tokenAvailable') {
        console.log('Token disponível detectado:', request.key);
        
        // Salva no storage
        if (request.value && request.value.length > 20) {
            chrome.storage.local.set({ 
                nikeToken: request.value,
                lastUpdate: new Date().toISOString()
            });
        }
    }
});

// Notifica quando a extensão é instalada
chrome.runtime.onInstalled.addListener((details) => {
    if (details.reason === 'install') {
        console.log('Nike Token Extractor instalado com sucesso!');
        
        // Abre página de boas-vindas (opcional)
        // chrome.tabs.create({ url: 'https://garmin-nike-sync.onrender.com' });
    }
});

console.log('Nike Token Extractor - Background service worker loaded');
