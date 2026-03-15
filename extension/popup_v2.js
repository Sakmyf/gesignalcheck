const API_URL = "https://gesignalcheck-production-8e78.up.railway.app/v3/verify";

window.API_DEBUG = API_URL;
console.log("POPUP CARGADO:", API_URL);

document.addEventListener("DOMContentLoaded", () => {

  const analyzeBtn = document.getElementById("analyzeBtn");
  const scoreValue = document.getElementById("scoreValue");
  const confidenceBar = document.getElementById("confidenceBar");
  const signalsList = document.getElementById("signalsList");
  const labelBadge = document.getElementById("labelBadge");
  const errorDiv = document.getElementById("error");

  const scoreContainer = scoreValue.parentElement;

  // ======================================================
  // RESET UI
  // ======================================================

  function resetUI() {
    errorDiv.style.display = "none";
    errorDiv.textContent = "";

    labelBadge.textContent = "Analizando...";
    labelBadge.className = "signal-label";

    scoreContainer.style.display = "block";
    scoreValue.textContent = "0.00";

    confidenceBar.style.width = "0%";
    confidenceBar.className = "confidence-bar";

    signalsList.innerHTML = "<li>Procesando...</li>";
  }

  // ======================================================
  // MAIN CLICK
  // ======================================================

  analyzeBtn.addEventListener("click", async () => {
    resetUI();

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

  // ======================================================
  // TAB
  // ======================================================

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
  // TEXT EXTRACTION
  // ======================================================

  async function getPageText(tab) {

    await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      files: ["content_script.js"]
    });

    await new Promise(resolve => setTimeout(resolve, 800));

    return new Promise((resolve, reject) => {

      chrome.tabs.sendMessage(
        tab.id,
        { action: "extractText" },
        (response) => {

          if (chrome.runtime.lastError) {
            reject(new Error(chrome.runtime.lastError.message));
            return;
          }

          if (!response) {
            reject(new Error("Sin respuesta del content script"));
            return;
          }

          resolve(response);
        }
      );

    });
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
        text: extracted.text
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
  // UPDATE UI
  // ======================================================

  function updateUI(data) {

    if (!data.analysis || !data.analysis.level) {
      showError("Respuesta inválida del servidor.");
      return;
    }

    const level = data.analysis.level;
    const indicators = data.analysis.indicators || [];
    const plan = (data.meta?.plan || "free").toLowerCase();
    const risk = data.analysis.structural_index ?? 0;

    confidenceBar.style.width = (risk * 100) + "%";
    confidenceBar.className = "confidence-bar";
    labelBadge.className = "signal-label";
<<<<<<< HEAD

    signalsList.innerHTML = "";

    // ================= FREE =================

=======
    signalsList.innerHTML = "";

    // ================= FREE =================
>>>>>>> 60b46bb (Reconstruccion completa SignalCheck)
    if (plan === "free") {

      scoreContainer.style.display = "none";
      setLevelVisual(level);

      indicators.slice(0, 3).forEach(signal => {
        const li = document.createElement("li");
        li.textContent = signal.title;
        signalsList.appendChild(li);
      });

      addUpgradeBox(
        "Plan FREE activo",
        "Mostrando análisis básico estructural.",
        "Actualizá a PRO para ver score numérico y más señales.",
        "https://gesignalcheck.com/upgrade"
      );

      return;
    }

    // ================= PRO =================
<<<<<<< HEAD

=======
>>>>>>> 60b46bb (Reconstruccion completa SignalCheck)
    if (plan === "pro") {

      scoreContainer.style.display = "block";
      scoreValue.textContent = risk.toFixed(2);
      setLevelVisual(level);

      indicators.slice(0, 5).forEach(signal => {
        const li = document.createElement("li");
        li.textContent = signal.title;
        signalsList.appendChild(li);
      });

      addUpgradeBox(
        "Plan PRO activo",
        "Acceso a score estructural extendido.",
        "Actualizá a PREMIUM para análisis técnico completo.",
        "https://gesignalcheck.com/upgrade"
      );

      return;
    }

    // ================= PREMIUM =================
<<<<<<< HEAD

=======
>>>>>>> 60b46bb (Reconstruccion completa SignalCheck)
    if (plan === "premium") {

      scoreContainer.style.display = "block";
      scoreValue.textContent = risk.toFixed(3);
      setLevelVisual(level);

      indicators.forEach(signal => {
        const li = document.createElement("li");
        li.textContent = signal.title;
        signalsList.appendChild(li);
      });

      addUpgradeBox(
        "Plan PREMIUM activo",
        "Snapshot estructural disponible.",
        "Modo EXPERT habilita auditoría institucional avanzada.",
        "https://gesignalcheck.com/upgrade"
      );

      return;
    }

    // ================= EXPERT =================
<<<<<<< HEAD

=======
>>>>>>> 60b46bb (Reconstruccion completa SignalCheck)
    if (plan === "expert") {

      scoreContainer.style.display = "block";
      scoreValue.textContent = risk.toFixed(4);
      setLevelVisual(level);

      indicators.forEach(signal => {
        const li = document.createElement("li");
        li.textContent = signal.title;
        signalsList.appendChild(li);
      });

      const expertBox = document.createElement("div");
      expertBox.style.marginTop = "14px";
      expertBox.style.padding = "12px";
      expertBox.style.borderRadius = "10px";
      expertBox.style.background = "rgba(0,255,150,0.08)";
      expertBox.style.fontSize = "0.85rem";
      expertBox.innerHTML =
        "<strong>Modo Auditoría Profesional Activo</strong><br>Informe estructural trazable y consistente.";

      signalsList.appendChild(expertBox);

      return;
    }
  }

  // ======================================================
  // HELPERS
  // ======================================================

  function setLevelVisual(level) {
    if (level === "bajo") {
      labelBadge.textContent = "Riesgo Bajo";
      labelBadge.classList.add("risk-low");
      confidenceBar.classList.add("bar-low");
    } else if (level === "medio") {
      labelBadge.textContent = "Riesgo Medio";
      labelBadge.classList.add("risk-medium");
      confidenceBar.classList.add("bar-medium");
    } else {
      labelBadge.textContent = "Riesgo Alto";
      labelBadge.classList.add("risk-high");
      confidenceBar.classList.add("bar-high");
    }
  }

  function addUpgradeBox(title, line1, line2, upgradeUrl) {

    const box = document.createElement("div");
    box.style.marginTop = "14px";
    box.style.padding = "12px";
    box.style.borderRadius = "10px";
    box.style.background = "rgba(255,255,255,0.04)";
    box.style.fontSize = "0.85rem";
    box.style.lineHeight = "1.4";

    const button = document.createElement("button");
    button.textContent = "Actualizar plan";
    button.style.marginTop = "8px";
    button.style.padding = "6px 10px";
    button.style.fontSize = "0.8rem";
    button.style.borderRadius = "6px";
    button.style.border = "none";
    button.style.cursor = "pointer";
    button.style.background = "#2e7dff";
    button.style.color = "#fff";

    button.addEventListener("click", () => {
      chrome.tabs.create({ url: upgradeUrl });
    });

    box.innerHTML = `
      <strong>${title}</strong><br>
      ${line1}<br>
      <span style="opacity:0.7">${line2}</span>
    `;

    box.appendChild(button);
    signalsList.appendChild(box);
  }

  function showError(message) {
    errorDiv.textContent = message;
    errorDiv.style.display = "block";
    labelBadge.textContent = "Error";
    confidenceBar.style.width = "0%";
    signalsList.innerHTML = "";
  }

});
