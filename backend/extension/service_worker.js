// service_worker.js

// Worker mínimo para MV3.
// No ejecuta lógica pesada.
// Mantiene el contexto de la extensión activo.

console.log("SignalCheck service worker initialized");

chrome.runtime.onInstalled.addListener(() => {
  console.log("SignalCheck extension installed/updated");
});

chrome.runtime.onStartup.addListener(() => {
  console.log("SignalCheck extension startup");
});

// Listener preparado para comunicación futura
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {

  if (message.type === "ping") {
    sendResponse({ status: "alive" });
  }

});

// Evento de activación del worker
self.addEventListener("activate", () => {
  console.log("SignalCheck worker activated");
});