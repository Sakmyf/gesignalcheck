document.addEventListener("DOMContentLoaded", () => {

  const analyzeBtn = document.getElementById("analyzeBtn");
  const scoreValue = document.getElementById("scoreValue");
  const confidenceBar = document.getElementById("confidenceBar");
  const signalsList = document.getElementById("signalsList");
  const labelBadge = document.getElementById("labelBadge");
  const errorDiv = document.getElementById("error");

  const API_URL = "https://ge-signal-check-production.up.railway.app/v3/verify";

  // ======================================================
  // MAIN CLICK HANDLER
  // ======================================================

  analyzeBtn.addEventListener("click", async () => {

    resetUI();
    console.log("🔎 Analizando página...");

    try {

      const tab = await getActiveTab();
      const extracted = await getPageText(tab);

      if (!extracted || !extracted.text || extracted.text.length < 50) {
        showError("No se pudo extraer texto significativo.");
        return;
      }

      const result = await callBackend(extracted);

      if (!result) {
        showError("Respuesta inválida del servidor.");
        return;
      }

      updateUI(result);

    } catch (err) {
      console.error("🔥 ERROR GENERAL:", err);
      showError(err?.message || "Error inesperado");
    }

  });

// =====================================================
// TAB
// =====================================================

async function getActiveTab() {

  const tabs = await chrome.tabs.query({
    active: true,
    currentWindow: true
  });

  if (!tabs || tabs.length === 0) {
    throw new Error("No se encontró pestaña activa.");
  }

  const tab = tabs[0];

  if (!tab.id) {
    throw new Error("ID de pestaña inválido.");
  }

  if (!tab.url) {
    throw new Error("No se pudo obtener la URL.");
  }

  // 🚫 Bloquear páginas donde no se puede inyectar
  const blockedProtocols = [
    "chrome://",
    "chrome-extension://",
    "edge://",
    "about:",
    "file://"
  ];

  if (blockedProtocols.some(protocol => tab.url.startsWith(protocol))) {
    throw new Error("No se puede analizar esta página.");
  }

  return tab;
}

  // ======================================================
  // TEXT EXTRACTION
  // ======================================================

  async function getPageText(tab) {

    try {
      return await chrome.tabs.sendMessage(tab.id, { action: "extractText" });
    } catch (err) {

      console.log("ℹ Reiniciando conexión con la página...");

      // Inyección manual (MV3 fallback)
      await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        files: ["content_script.js"]
      });

      // pequeño delay para asegurar registro del listener
      await new Promise(resolve => setTimeout(resolve, 150));

      return await chrome.tabs.sendMessage(tab.id, { action: "extractText" });
    }
  }

  // ======================================================
  // BACKEND CALL
  // ======================================================

  async function callBackend(extracted) {

    const extensionId = chrome.runtime.id;

    if (!extensionId) {
      throw new Error("No se pudo obtener ID de extensión.");
    }

    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-extension-id": extensionId
      },
      body: JSON.stringify({
        url: extracted.url,
        text: extracted.text
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error("❌ HTTP ERROR:", response.status, errorText);
      throw new Error("Error del servidor (" + response.status + ")");
    }

    return await response.json();
  }

  // ======================================================
  // UI
  // ======================================================

  function resetUI() {

    errorDiv.style.display = "none";
    errorDiv.textContent = "";

    labelBadge.textContent = "Analizando...";
    labelBadge.className = "signal-label";

    scoreValue.textContent = "0.00";

    confidenceBar.style.width = "0%";
    confidenceBar.className = "confidence-bar";

    signalsList.innerHTML = "<li>Procesando...</li>";
  }

  function updateUI(data) {

    if (typeof data.risk_index !== "number") {
      showError("Respuesta inválida del servidor.");
      return;
    }

    const risk = Math.max(0, Math.min(1, data.risk_index));

    scoreValue.textContent = risk.toFixed(2);
    confidenceBar.style.width = (risk * 100) + "%";

    labelBadge.className = "signal-label";
    confidenceBar.className = "confidence-bar";

    signalsList.innerHTML = "";

    // Recolectar señales
    const allSignals = [
      ...(data?.details?.structural_signals || []),
      ...(data?.details?.rhetorical_signals || []),
      ...(data?.details?.narrative_signals || []),
      ...(data?.details?.source_signals || [])
    ];

    if (allSignals.length > 0) {
      allSignals.forEach(signal => {
        const li = document.createElement("li");
        li.textContent = signal;
        signalsList.appendChild(li);
      });
    } else {
      signalsList.innerHTML = "<li>No se detectaron señales relevantes</li>";
    }

    // Advertencia contextual prioritaria
    if (data.context_warning) {

      labelBadge.textContent = "Advertencia Contextual";
      labelBadge.classList.add("risk-medium");
      confidenceBar.classList.add("bar-medium");

      const warningLi = document.createElement("li");
      warningLi.textContent = "⚠ " + data.context_warning;
      warningLi.style.fontWeight = "bold";

      signalsList.prepend(warningLi);
      return;
    }

    // Escala normal
    if (risk < 0.35) {
      labelBadge.textContent = "Riesgo Bajo";
      labelBadge.classList.add("risk-low");
      confidenceBar.classList.add("bar-low");

    } else if (risk < 0.65) {
      labelBadge.textContent = "Riesgo Medio";
      labelBadge.classList.add("risk-medium");
      confidenceBar.classList.add("bar-medium");

    } else {
      labelBadge.textContent = "Riesgo Alto";
      labelBadge.classList.add("risk-high");
      confidenceBar.classList.add("bar-high");
    }
  }

  function showError(message) {

    errorDiv.textContent = message;
    errorDiv.style.display = "block";

    labelBadge.textContent = "Error";
    labelBadge.className = "signal-label";

    confidenceBar.style.width = "0%";
    confidenceBar.className = "confidence-bar";

    signalsList.innerHTML = "";
  }

});
