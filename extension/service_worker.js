// service_worker.js
console.log("SignalCheck service worker initialized");

// ID de tu extensión (debe coincidir con ALLOWED_EXTENSIONS en app.py)
const EXTENSION_ID = "fijnjbaacmpnhaaconoafbmnholbmaig";

chrome.runtime.onInstalled.addListener(() => {
  console.log("SignalCheck extension installed/updated");
});

// Maneja mensajes del popup y content_script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  // Caso 1: Popup pide análisis
  if (request.action === "analyze") {
    // 📊 Loguear evento anónimo
    fetch("https://ge-signal-check-production.up.railway.app/event", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ 
        event_name: "verify_call",
        user_type: "free" 
      })
    }).catch(() => {});

    fetch("https://ge-signal-check-production.up.railway.app/v3/verify", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-extension-id": EXTENSION_ID
      },
      body: JSON.stringify({
        url: request.url || "https://example.com",
        text: request.text || ""
      })
    })
    .then(response => {
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return response.json();
    })
    .then(data => {
      console.log("API response:", data);
      sendResponse(data);
    })
    .catch(error => {
      console.error("API error:", error);
      sendResponse({ 
        error: "Análisis fallido", 
        details: error.message 
      });
    });
    return true; // Mantiene el puerto abierto para respuesta asíncrona
  }

  // Caso 2: Content script pide texto de la página
  if (request.action === "getText") {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs[0]?.id) {
        chrome.tabs.sendMessage(tabs[0].id, { action: "getText" }, (response) => {
          sendResponse(response || { text: "" });
        });
      } else {
        sendResponse({ text: "" });
      }
    });
    return true;
  }

  // Respuesta por defecto
  sendResponse({ status: "unknown_action" });
  return true;
});