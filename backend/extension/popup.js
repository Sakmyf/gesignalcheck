// ==========================================
// SIGNALCHECK POPUP.JS v2.0
// Schema alineado con engine v13.8 + PRO real
// ==========================================

console.log("🔥 POPUP JS CARGADO v2.0");

const API_URL = "https://gesignalcheck-production-8e78.up.railway.app/v3/verify";
const PRO_URL = "https://gesignalcheck.com/analysis";

let currentMeta = null;

document.addEventListener("DOMContentLoaded", async () => {

  const scanLine   = document.getElementById("scanLine");
  const labelBadge = document.getElementById("labelBadge");
  const summaryBox = document.getElementById("summary");
  const scoreEl    = document.getElementById("scoreValue");
  const confEl     = document.getElementById("confidenceValue");
  const proSection = document.getElementById("proSection");

  const tokenInput  = document.getElementById("proTokenInput");
  const activateBtn = document.getElementById("activateProBtn");

  // 🔐 TOKEN PRO
  const stored = await chrome.storage.local.get("pro_token");
  let storedToken = stored.pro_token || "";

  if (activateBtn && tokenInput) {
    activateBtn.addEventListener("click", () => {
      const token = tokenInput.value.trim();
      if (!token) return;
      chrome.storage.local.set({ pro_token: token }, () => {
        storedToken = token;
        alert("✅ PRO activado. Reanalizá la página.");
      });
    });
  }

  // =====================
  // UI STATES
  // =====================

  function startScanUI() {
    if (scanLine) scanLine.classList.add("active");
    labelBadge.textContent       = "Analizando contenido...";
    labelBadge.style.background  = "#1e293b";
    labelBadge.style.color       = "#94a3b8";
    summaryBox.classList.add("hidden");
    scoreEl.textContent = "--";
    confEl.textContent  = "--";
    proSection.classList.add("locked");
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

  // =====================
  // ANÁLISIS
  // =====================

  async function runAnalysis() {
    startScanUI();

    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

      if (!tab?.id || tab.url.startsWith("chrome://")) {
        return showError("Página no compatible.");
      }

      try {
        await chrome.scripting.executeScript({
          target: { tabId: tab.id },
          files: ["content_script.js"]
        });
      } catch {}

      await new Promise(r => setTimeout(r, 150));

      chrome.tabs.sendMessage(tab.id, { action: "extractText" }, async (extracted) => {

        if (!extracted) return showError("No se pudo leer la página.");

        const text = extracted.text || "";
        if (text.length < 30) return showError("Texto insuficiente.");

        try {
          const res = await fetch(API_URL, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "x-extension-id": chrome.runtime.id,
              "x-pro-token": storedToken || ""
            },
            body: JSON.stringify({ text, url: extracted.url || tab.url })
          });

          if (!res.ok) return showError("Error servidor.");

          const data = await res.json();
          renderResult(data);

        } catch {
          showError("Error de conexión.");
        }
      });

    } catch {
      showError("Error inesperado.");
    }
  }

  // =====================
  // RENDER
  // =====================

  function renderResult(data) {

    // El engine devuelve el análisis directo o dentro de data.analysis
    const analysis = data?.analysis || data;
    if (!analysis) return showError("Sin datos.");

    const plan = data?.meta?.plan || "free";

    // — Badge nivel —
    // engine devuelve: "green" | "yellow" | "red"
    const level = (analysis.level || "green").toLowerCase();
    const BADGE = {
      green:  { text: "● Bajo riesgo",      bg: "rgba(34,197,94,0.15)",  color: "#4ade80" },
      yellow: { text: "● Riesgo moderado",  bg: "rgba(250,204,21,0.15)", color: "#facc15" },
      red:    { text: "● Alto riesgo",      bg: "rgba(239,68,68,0.15)",  color: "#f87171" },
    };
    const badge = BADGE[level] || BADGE.green;
    labelBadge.textContent      = badge.text;
    labelBadge.style.background = badge.bg;
    labelBadge.style.color      = badge.color;

    // — Score (ya viene 0-100 entero desde engine v13.8) —
    const score = analysis.score ?? 0;
    const conf  = Math.round((analysis.confidence || 0) * 100);

    scoreEl.textContent = score;
    confEl.textContent  = conf;

    // — Insight / mensaje —
    const msg = analysis.insight || analysis.message || "Análisis completado.";
    summaryBox.textContent = msg;
    summaryBox.classList.remove("hidden");

    currentMeta = { score, level, confidence: conf };

    // — Señal PRO freemium —
    const proWarning = document.getElementById("proWarning");
    if (proWarning) {
      if (level !== "green" || score > 15) {
        proWarning.textContent = "⚠ Hay señales más profundas que no estás viendo\nEste contenido puede influir en cómo lo interpretás";
        proWarning.classList.remove("hidden");
      } else {
        proWarning.classList.add("hidden");
      }
    }

    // =========================
    // PRO REAL
    // =========================
    if (plan === "pro" && analysis.pro) {
      _renderPro(analysis.pro);
      proSection.classList.remove("locked");
      const upgradeBtn = document.getElementById("upgradeBtn");
      if (upgradeBtn) upgradeBtn.style.display = "none";
    } else {
      proSection.classList.add("locked");
      _resetProFields();
      const upgradeBtn = document.getElementById("upgradeBtn");
      if (upgradeBtn) upgradeBtn.style.display = "block";
    }

    stopScanUI();
  }

  function _renderPro(pro) {
    const dims = pro.dimensions || {};

    // Dimensiones con barra visual
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
      const color = dim.score >= 70 ? "#f87171" : dim.score >= 40 ? "#facc15" : "#4ade80";
      el.innerHTML = `
        <span style="color:${color}; font-weight:600">${dim.label}</span>
        <span style="color:#475569; font-size:11px"> ${dim.score}/100</span>
      `;
    }

    // Patrón dominante
    const patEl = document.getElementById("pro-pattern");
    if (patEl && pro.dominant_pattern) {
      const p = pro.dominant_pattern;
      patEl.innerHTML = `
        <span style="font-weight:600; color:#e2e8f0">${p.label}</span><br>
        <span style="font-size:11px; color:#64748b">${p.explanation}</span>
      `;
    }

    // Recomendación
    const recEl = document.getElementById("pro-recommendation");
    if (recEl && pro.recommendation) {
      recEl.textContent = pro.recommendation.text;
    }
  }

  // =====================
  // EVENTOS
  // =====================

  document.addEventListener("click", (e) => {

    if (e.target.id === "upgradeBtn") {
      if (!currentMeta) return;
      const url = `${PRO_URL}?score=${currentMeta.score}&level=${currentMeta.level}&conf=${currentMeta.confidence}`;
      chrome.tabs.create({ url });
    }

    if (e.target.id === "analyzeBtn") {
      runAnalysis();
    }
  });

  runAnalysis();
});