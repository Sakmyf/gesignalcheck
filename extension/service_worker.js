const API_BASE = "http://127.0.0.1:8787";

// Escucha mensajes desde el popup o content_script
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === "VERIFY_PAGE") {
    // Ejecutamos la lógica sin bloquear la respuesta inmediata
    handleVerify(msg.payload).then(() => {
      // Opcional: notificar que terminó
    });
    sendResponse({ status: "started" });
    return true; // Indica respuesta asíncrona
  }
});

async function handleVerify(payload) {
  const cacheKey = `cv:${payload.url}`;
  
  try {
    // 1. Pedimos el texto de la página a la pestaña activa para enviarlo a la API
    // (Esto mejora la precisión si el usuario ya tiene la web abierta)
    let pageText = "";
    let pageTitle = "";
    
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tab && tab.id) {
      try {
        const response = await chrome.tabs.sendMessage(tab.id, { type: "GET_TEXT" });
        if (response) {
          pageText = response.text;
          pageTitle = response.title;
        }
      } catch (err) {
        console.log("No se pudo inyectar content script (quizás página protegida), usaremos solo URL.");
      }
    }

    // 2. Llamada al Backend (Tu Python)
    const reqBody = {
      url: payload.url,
      text: pageText || "",
      title: pageTitle || ""
    };

    const res = await fetch(`${API_BASE}/v1/verify`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(reqBody)
    });

    if (!res.ok) throw new Error(`API Error: ${res.status}`);

    const data = await res.json();

    // 3. Guardar resultado y actualizar ícono (Badge)
    await chrome.storage.local.set({ [cacheKey]: data });
    updateIcon(data.label, tab.id);

  } catch (e) {
    console.error("Error verificando:", e);
  }
}

function updateIcon(label, tabId) {
    if (!tabId) return;
    let text = "·";
    let color = "#999999";

    if (label === "respaldado") { text = "OK"; color = "#10B981"; }
    if (label === "en_debate") { text = "!"; color = "#F59E0B"; }
    if (label === "contradicho") { text = "X"; color = "#EF4444"; }

    chrome.action.setBadgeText({ text: text, tabId: tabId });
    chrome.action.setBadgeBackgroundColor({ color: color, tabId: tabId });
}