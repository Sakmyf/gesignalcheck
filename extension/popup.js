const API_BASE = "http://127.0.0.1:8787";

// Colores y textos para la interfaz
const UI_MAP = {
  respaldado: { cls: "bg-respaldado", text: "CONFIABLE", color: "#10B981" },
  en_debate: { cls: "bg-en_debate", text: "EN DEBATE", color: "#F59E0B" },
  especulativo: { cls: "bg-especulativo", text: "RUMOR", color: "#9CA3AF" },
  contradicho: { cls: "bg-contradicho", text: "ALERTA", color: "#EF4444" },
  desconocido: { cls: "bg-especulativo", text: "ANALIZANDO", color: "#6B7280" }
};

document.addEventListener('DOMContentLoaded', async () => {
  // 1. Obtenemos la pestaña actual
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab) return;

  const cacheKey = `cv:${tab.url}`;
  const badgeEl = document.getElementById("status-badge");
  const summaryEl = document.getElementById("summary");
  const claimsListEl = document.getElementById("claims-list");

  // Función para dibujar en pantalla
  const render = (data) => {
    const ui = UI_MAP[data.label] || UI_MAP.desconocido;
    
    // Actualizar Badge
    badgeEl.className = `badge ${ui.cls}`;
    badgeEl.textContent = ui.text;

    // Actualizar Resumen
    summaryEl.textContent = data.summary || "Sin información detallada.";

    // Actualizar Evidencias (Claims)
    claimsListEl.innerHTML = "";
    if (data.claims && data.claims.length > 0) {
      data.claims.forEach(claim => {
        const item = document.createElement("div");
        item.className = "claim-item";
        
        // Determinar color del puntito según el riesgo de la evidencia
        let dotColor = "#9CA3AF"; // Gris por defecto
        if (claim.label === "respaldado") dotColor = "#10B981";
        if (claim.label === "contradicho") dotColor = "#EF4444";
        if (claim.label === "en_debate") dotColor = "#F59E0B";

        item.innerHTML = `
          <div class="claim-dot" style="background-color: ${dotColor}"></div>
          <div>${claim.text}</div>
        `;
        claimsListEl.appendChild(item);
      });
    } else {
      claimsListEl.innerHTML = "<div style='color:#999; font-size:11px; font-style:italic;'>No se detectaron frases clave específicas.</div>";
    }
  };

  // 2. Flujo Principal
  try {
    // A. Revisar caché local (para velocidad)
    const stored = await chrome.storage.local.get(cacheKey);
    if (stored[cacheKey]) {
      console.log("Cargado desde caché");
      render(stored[cacheKey]);
      return; 
    }

    // B. Si no hay caché, pedir análisis al Service Worker
    badgeEl.textContent = "SCAN...";
    
    // Enviamos mensaje al background para que coordine el fetch
    chrome.runtime.sendMessage({ type: "VERIFY_PAGE", payload: { url: tab.url } }, (response) => {
      if (chrome.runtime.lastError) {
        summaryEl.textContent = "Error de conexión con la extensión.";
        return;
      }
      // Esperamos un poco a que el service worker guarde los datos
      setTimeout(async () => {
        const fresh = await chrome.storage.local.get(cacheKey);
        if (fresh[cacheKey]) {
          render(fresh[cacheKey]);
        } else {
          summaryEl.textContent = "Esperando respuesta del servidor...";
          // Re-intentar en 2 segundos (polling simple)
          setTimeout(async () => {
            const retry = await chrome.storage.local.get(cacheKey);
            if(retry[cacheKey]) render(retry[cacheKey]);
            else {
               badgeEl.textContent = "ERROR";
               badgeEl.className = "badge bg-contradicho";
               summaryEl.textContent = "El servidor no respondió a tiempo. Asegurate de que 'app.py' esté corriendo.";
            }
          }, 2000);
        }
      }, 500);
    });

  } catch (e) {
    console.error(e);
    summaryEl.textContent = "Error interno de la extensión.";
  }
});