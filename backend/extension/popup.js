// ==========================================
// SIGNALCHECK POPUP.JS v2.2 - FULL STABLE
// Mantiene lógica PRO + Railway + Seguridad XSS
// ==========================================

console.log("🔥 POPUP JS CARGADO v2.2 - MODO ESTABLE");

const API_URL = "https://gesignalcheck-production-8e78.up.railway.app/v3/verify";
const PRO_URL = "https://gesignalcheck.com/analysis";

let currentMeta = null;

document.addEventListener("DOMContentLoaded", async () => {

  // Referencias a la UI
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

  // Recuperar token guardado
  const stored = await chrome.storage.local.get("pro_token");
  let storedToken = stored.pro_token || "";

  // Evento: Activar PRO
  if (activateBtn && tokenInput) {
    activateBtn.addEventListener("click", () => {
      const token = tokenInput.value.trim();
      if (!token) return;
      chrome.storage.local.set({ pro_token: token }, () => {
        storedToken = token;
        alert("✅ PRO activado correctamente.");
        runAnalysis(); // Re-analizar automáticamente
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
    if (proSection) proSection.classList.add("locked");
    if (upgradeBtn) upgradeBtn.style.display = "none";
    _resetProFields();
    currentMeta = null;
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

  // Comunicación con el Content Script
  function sendExtractMessage(tabId, attempts = 3) {
    return new Promise((resolve) => {
      function attempt(n) {
        chrome.tabs.sendMessage(tabId, { action: "extractText" }, (res) => {
          if (chrome.runtime.lastError || !res) {
            if (n > 1) setTimeout(() => attempt(n - 1), 300);
            else resolve(null);
          } else {
            resolve(res);
          }
        });
      }
      attempt(attempts);
    });
  }

  async function runAnalysis() {
    startScanUI();
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (!tab?.id || tab.url.startsWith("chrome://")) return showError("Página no compatible.");

      // Inyectar content script dinámicamente si es necesario
      try {
        await chrome.scripting.executeScript({ target: { tabId: tab.id }, files: ["content_script.js"] });
      } catch (e) { /* Ya inyectado o error menor */ }

      await new Promise(r => setTimeout(r, 200));
      const extracted = await sendExtractMessage(tab.id, 3);
      if (!extracted) return showError("No se pudo leer la página.");

      const text = extracted.text || "";
      if (text.length < 30) return showError("Texto insuficiente.");

      // Fetch a tu API de Railway
      const res = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-extension-id": chrome.runtime.id,
          "x-pro-token": storedToken
        },
        body: JSON.stringify({ text, url: extracted.url || tab.url })
      });

      if (!res.ok) {
        if (res.status === 401) return showError("Token PRO inválido.");
        return showError("Error en servidor Railway.");
      }

      const data = await res.json();
      renderResult(data);

    } catch (err) { 
      console.error(err);
      showError("Error de conexión."); 
    }
  }

  function renderResult(data) {
    const analysis = data?.analysis || data;
    if (!analysis) return showError("Sin datos de análisis.");

    const plan  = data?.meta?.plan || "free";
    const level = (analysis.level || "green").toLowerCase();

    // Configuración visual de los badges
    const BADGE = {
      green:  { text: "● Bajo riesgo",     bg: "rgba(34,197,94,0.15)",  color: "#4ade80" },
      yellow: { text: "● Riesgo moderado", bg: "rgba(250,204,21,0.15)", color: "#facc15" },
      red:    { text: "● Alto riesgo",     bg: "rgba(239,68,68,0.15)",  color: "#f87171" },
    };
    const badge = BADGE[level] || BADGE.green;
    
    labelBadge.textContent      = badge.text;
    labelBadge.style.background = badge.bg;
    labelBadge.style.color      = badge.color;

    const score = analysis.score ?? 0;
    const conf  = Math.round((analysis.confidence || 0) * 100);
    scoreEl.textContent = score;
    confEl.textContent  = conf;

    summaryBox.textContent = analysis.insight || analysis.message || "Análisis completado.";
    summaryBox.classList.remove("hidden");

    currentMeta = { score, level, confidence: conf };

    // Alerta visual de riesgo
    if (proWarning) {
      if (level !== "green" || score > 15) proWarning.classList.remove("hidden");
      else proWarning.classList.add("hidden");
    }

    // Lógica PRO vs FREE
    if (plan === "pro") {
      proSection.classList.remove("locked");
      if (upgradeBtn) upgradeBtn.style.display = "none";
      if (analysis.pro) _renderProData(analysis.pro);
    } else {
      proSection.classList.add("locked");
      if (upgradeBtn) upgradeBtn.style.display = "block";
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
      if (!el || !dim) continue;
      
      // Seguridad XSS: Usamos textContent y manipulamos el estilo aparte
      el.textContent = `${dim.label}: ${dim.score}/100`;
      el.style.fontWeight = "600";
      el.style.color = dim.score >= 70 ? "#f87171" : dim.score >= 40 ? "#facc15" : "#4ade80";
    }

    const patEl = document.getElementById("pro-pattern");
    if (patEl && pro.dominant_pattern) {
      patEl.textContent = `${pro.dominant_pattern.label}: ${pro.dominant_pattern.explanation}`;
    }

    const recEl = document.getElementById("pro-recommendation");
    if (recEl && pro.recommendation) {
      recEl.textContent = pro.recommendation.text;
    }
  }

  // Manejo de clicks globales
  document.addEventListener("click", (e) => {
    if (e.target.id === "upgradeBtn") {
      if (!currentMeta) return;
      chrome.tabs.create({ url: `${PRO_URL}?score=${currentMeta.score}&level=${currentMeta.level}` });
    }
    if (e.target.id === "analyzeBtn") runAnalysis();
  });

  // Ejecución inicial
  runAnalysis();
});