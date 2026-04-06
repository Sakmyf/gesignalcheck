// ==========================================
// SIGNALCHECK POPUP.JS v2.3 - FULL STABLE
// Sincronizado con Backend Local y Railway
// ==========================================

console.log("🔥 POPUP JS CARGADO v2.3 - MODO ESTABLE");

const API_URL = "https://gesignalcheck-production-8e78.up.railway.app/v3/verify";
const PRO_URL = "https://gesignalcheck.com/analysis";

let currentMeta = null;

document.addEventListener("DOMContentLoaded", async () => {

  const scanLine    = document.getElementById("scanLine");
  const labelBadge  = document.getElementById("labelBadge");
  const summaryBox  = document.getElementById("summary");
  const scoreEl     = document.getElementById("scoreValue");
  const confEl      = document.getElementById("confidenceValue");
  const proSection  = document.getElementById("proSection");
  const upgradeBtn  = document.getElementById("upgradeBtn");
  const tokenInput  = document.getElementById("proTokenInput");
  const activateBtn = document.getElementById("activateProBtn");
  const proWarning  = document.getElementById("proWarning");

  const stored = await chrome.storage.local.get("pro_token");
  let storedToken = stored.pro_token || "";

  if (activateBtn && tokenInput) {
    activateBtn.addEventListener("click", () => {
      const token = tokenInput.value.trim();
      if (!token) return;
      chrome.storage.local.set({ pro_token: token }, () => {
        storedToken = token;
        alert("✅ PRO activado correctamente.");
        runAnalysis();
      });
    });
  }

  function startScanUI() {
    if (scanLine) scanLine.classList.add("active");
    labelBadge.textContent      = "Analizando contenido...";
    labelBadge.style.background = "#1e293b";
    labelBadge.style.color      = "#94a3b8";
    if (summaryBox) summaryBox.classList.add("hidden");
    if (scoreEl) scoreEl.textContent = "--";
    if (confEl) confEl.textContent  = "--";
    _resetProFields();
  }

  function stopScanUI() {
    if (scanLine) scanLine.classList.remove("active");
  }

  function showError(msg) {
    stopScanUI();
    labelBadge.textContent      = "Error";
    labelBadge.style.background = "#471b1b";
    labelBadge.style.color      = "#f87171";
    summaryBox.textContent      = msg;
    summaryBox.classList.remove("hidden");
  }

  function _resetProFields() {
    ["pro-emocional","pro-narrativo","pro-credibilidad",
     "pro-cientifico","pro-comercial","pro-pattern","pro-recommendation"]
      .forEach(id => {
        const el = document.getElementById(id);
        if (el) el.textContent = "🔒";
      });
  }

  async function runAnalysis() {
    startScanUI();
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (!tab?.id || tab.url.startsWith("chrome://")) return showError("Página no compatible.");

      chrome.tabs.sendMessage(tab.id, { action: "extractText" }, async (res) => {
        if (chrome.runtime.lastError || !res) return showError("No se pudo leer la página.");

        const text = res.text || "";
        if (text.length < 30) return showError("Texto insuficiente.");

        const response = await fetch(API_URL, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "x-extension-id": chrome.runtime.id,
            "x-pro-token": storedToken
          },
          body: JSON.stringify({ text, url: res.url || tab.url })
        });

        if (!response.ok) return showError("Error en servidor.");

        const data = await response.json();
        renderResult(data);
      });

    } catch (err) { 
      showError("Error de conexión."); 
    }
  }

  function renderResult(data) {
    // Sincronización con la nueva estructura del app.py
    const analysis = data?.analysis;
    if (!analysis) return showError("Datos corruptos.");

    const plan  = data?.meta?.plan || "free";
    const level = (analysis.level || "green").toLowerCase();

    const BADGE = {
      green:  { text: "● Bajo riesgo",     bg: "rgba(34,197,94,0.15)",  color: "#4ade80" },
      yellow: { text: "● Riesgo moderado", bg: "rgba(250,204,21,0.15)", color: "#facc15" },
      red:    { text: "● Alto riesgo",     bg: "rgba(239,68,68,0.15)",  color: "#f87171" },
    };
    const badge = BADGE[level] || BADGE.green;
    
    labelBadge.textContent      = badge.text;
    labelBadge.style.background = badge.bg;
    labelBadge.style.color      = badge.color;

    scoreEl.textContent = analysis.score ?? 0;
    confEl.textContent  = Math.round((analysis.confidence || 0) * 100);

    summaryBox.textContent = analysis.message || "Análisis completado.";
    summaryBox.classList.remove("hidden");

    currentMeta = { score: analysis.score, level };

    if (plan === "pro") {
      proSection.classList.remove("locked");
      if (analysis.pro) _renderProData(analysis.pro);
    } else {
      proSection.classList.add("locked");
    }

    stopScanUI();
  }

  function _renderProData(pro) {
    const dims = pro.dimensions || {};
    const dimMap = {
      "pro-emocional":    dims.emocional,
      "pro-narrativo":    dims.narrativo,
      "pro-credibilidad": dims.credibilidad,
      "pro-cientifico":   dims.cientifico,
      "pro-comercial":    dims.comercial,
    };

    for (const [id, dim] of Object.entries(dimMap)) {
      const el = document.getElementById(id);
      if (el && dim) el.textContent = `${dim.label}: ${dim.score}/100`;
    }
  }

  document.addEventListener("click", (e) => {
    if (e.target.id === "upgradeBtn" && currentMeta) {
      chrome.tabs.create({ url: `${PRO_URL}?score=${currentMeta.score}&level=${currentMeta.level}` });
    }
    if (e.target.id === "analyzeBtn") runAnalysis();
  });

  runAnalysis();
});