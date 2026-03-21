// SignalCheck - Service Worker MV3

console.log("🔥 SignalCheck: Service Worker Inicializado");

// Se ejecuta al instalar o actualizar la extensión
chrome.runtime.onInstalled.addListener(() => {
  console.log("✅ SignalCheck: Instalada/Actualizada");
});

// Listener de mensajes
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  
  // Test de vida (Ping)
  if (message.type === "ping") {
    sendResponse({ status: "alive", timestamp: Date.now() });
    return true; // Mantiene el canal abierto para respuestas asíncronas
  }

  // Aquí podrías centralizar llamadas a la API si en el futuro 
  // quieres que el análisis siga corriendo aunque cierres el popup.
});

// Manejo de errores globales en el worker
self.addEventListener("error", (event) => {
  console.error("❌ Error en Service Worker:", event.message);
});

// Mantiene el Service Worker activo durante procesos críticos
self.addEventListener("activate", (event) => {
  console.log("🚀 SignalCheck: Worker Activado");
  event.waitUntil(clients.claim());
});
