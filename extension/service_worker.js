// service_worker.js

// Worker mínimo para MV3.
// No hace fetch.
// Solo mantiene el contexto activo sin errores.

console.log("SignalCheck service worker initialized");

// Opcional: evento de instalación
chrome.runtime.onInstalled.addListener(() => {
  console.log("SignalCheck extension installed/updated");
});
