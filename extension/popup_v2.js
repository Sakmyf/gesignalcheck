document.addEventListener("DOMContentLoaded", () => {

  const analyzeBtn = document.getElementById("analyzeBtn");
  const scoreValue = document.getElementById("scoreValue");
  const confidenceBar = document.getElementById("confidenceBar");
  const signalsList = document.getElementById("signalsList");
  const labelBadge = document.getElementById("labelBadge");
  const errorDiv = document.getElementById("error");

  // ✅ URL CORREGIDA: SIN ESPACIOS AL FINAL
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

      if (!extracted || !extracted.text) {
        showError("No se pudo extraer texto significativo.");
        return;
      }

      const result = await callBackend(extracted);
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
    const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tabs.length) throw new Error("No se encontró pestaña activa.");

    const tab = tabs[0];
    if (!tab.id) throw new Error("ID de pestaña inválido.");
    if (!tab.url) throw new Error("No se pudo obtener la URL.");

    const blockedProtocols = [
      "chrome://", "chrome-extension://", "edge://", "about:", "file://"
    ];
    if (blockedProtocols.some(p => tab.url.startsWith(p))) {
      throw new Error("No se puede analizar esta página.");
    }

    return tab;
  }

  // ======================================================
  // TEXT EXTRACTION (robusto para SPA como iProfesional)
  // ======================================================

  async function getPageText(tab) {
    try {
      return await chrome.tabs.sendMessage(tab.id, { action: "getText" });
    } catch (err) {
      console.log("ℹ Reintentando con fallback...");
      await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        files: ["content_script.js"]
      });
      await new Promise(resolve => setTimeout(resolve, 1200));
      return await chrome.tabs.sendMessage(tab.id, { action: "getText" });
    }
  }

  // ======================================================
  // BACKEND CALL
  // ======================================================

  async function callBackend(extracted) {
    const extensionId = chrome.runtime.id;
    if (!extensionId) throw new Error("No se pudo obtener ID de extensión.");

    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-extension-id": extensionId
      },
      body: JSON.stringify({
        url: extracted.url,
        text: extracted.text.substring(0, 15000)
      })
    });

    if (!response.ok) {
      const errorMsg = await response.text();
      console.error("❌ HTTP ERROR:", response.status, errorMsg);
      throw new Error(`Error del servidor (${response.status})`);
    }

    return await response.json();
  }

  // ======================================================
  // UI UPDATE
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
    if (!data.level || typeof data.level !== "string") {
      showError("Respuesta inválida del servidor.");
      return;
    }

    let risk = 0;
    if (data.level === "bajo") risk = 0.2;
    else if (data.level === "medio") risk = 0.5;
    else if (data.level === "alto") risk = 0.8;

    scoreValue.textContent = risk.toFixed(2);
    confidenceBar.style.width = (risk * 100) + "%";

    labelBadge.className = "signal-label";
    confidenceBar.className = "confidence-bar";

    signalsList.innerHTML = "";

    const indicators = data.indicators || [];
    if (indicators.length > 0) {
      indicators.slice(0, 5).forEach(signal => {
        const li = document.createElement("li");
        li.textContent = signal;
        signalsList.appendChild(li);
      });
    } else {
      signalsList.innerHTML = "<li>No se detectaron señales relevantes</li>";
    }

    if (data.level === "bajo") {
      labelBadge.textContent = "Riesgo Bajo";
      labelBadge.classList.add("risk-low");
      confidenceBar.classList.add("bar-low");
    } else if (data.level === "medio") {
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