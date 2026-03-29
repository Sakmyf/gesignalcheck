// ==========================================
// SIGNALCHECK POPUP.JS - FUNNEL READY
// ==========================================

console.log("🔥 POPUP JS CARGADO");

// 👉 TU BACKEND (no tocar)
const API_URL = "https://gesignalcheck-production-8e78.up.railway.app/v3/verify";

// 👉 ID EXTENSIÓN
const EXT_ID  = "dpgnanocamaeieplhgnapgcannjcpghn";

// 👉 NUEVA LANDING (IMPORTANTE)
const PRO_URL = "https://gesignalcheck.com/analysis";

let currentProData = null;
let currentMeta = null;

document.addEventListener("DOMContentLoaded", () => {

  const scanLine   = document.getElementById("scanLine");
  const labelBadge = document.getElementById("labelBadge");
  const summaryBox = document.getElementById("summary");
  const scoreEl    = document.getElementById("scoreValue");
  const confEl     = document.getElementById("confidenceValue");
  const proSection = document.getElementById("proSection");

  function startScanUI() {
    if (scanLine) scanLine.classList.add("active");

    labelBadge.textContent  = "Analizando contenido...";
    labelBadge.style.background = "#333";
    labelBadge.style.color      = "#aaa";

    summaryBox.classList.add("hidden");

    scoreEl.textContent = "--";
    confEl.textContent  = "--";

    proSection.classList.add("locked");

    ["pro-emocionalidad","pro-manipulacion","pro-evidencia","pro-coherencia"]
      .forEach(id => document.getElementById(id).textContent = "🔒");

    const btn = document.getElementById("upgradeBtn");
    btn.textContent = "Ver qué hay detrás de este contenido";
    btn.style.display = "block";
    btn.style.opacity = "1";

    currentProData = null;
    currentMeta = null;
  }

  function stopScanUI() {
    if (scanLine) scanLine.classList.remove("active");
  }

  function showError(msg) {
    stopScanUI();

    labelBadge.textContent = "Error";
    labelBadge.style.background = "#471b1b";
    labelBadge.style.color = "#f87171";

    summaryBox.textContent = msg;
    summaryBox.classList.remove("hidden");
  }

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
              "x-extension-id": EXT_ID
            },
            body: JSON.stringify({
              text,
              url: extracted.url || tab.url
            })
          });

          if (!res.ok) return showError("Error servidor.");

          const data = await res.json();
          renderResult(data);

        } catch {
          showError("Error conexión.");
        }
      });

    } catch {
      showError("Error inesperado.");
    }
  }

  function renderResult(data) {
    const analysis = data?.analysis || data;
    if (!analysis) return showError("Sin datos.");

    const level = (analysis.level || "medio").toLowerCase();

    if (level === "bajo") {
      labelBadge.textContent = "🟢 Bajo riesgo";
      labelBadge.style.background = "rgba(34,197,94,0.2)";
      labelBadge.style.color = "#4ade80";
    } else if (level === "medio") {
      labelBadge.textContent = "🟡 Riesgo moderado";
      labelBadge.style.background = "rgba(250,204,21,0.2)";
      labelBadge.style.color = "#facc15";
    } else {
      labelBadge.textContent = "🔴 Alto riesgo";
      labelBadge.style.background = "rgba(239,68,68,0.2)";
      labelBadge.style.color = "#f87171";
    }

    const score = Math.round((analysis.structural_index || 0) * 100);
    const conf  = Math.round((analysis.confidence || 0) * 100);

    scoreEl.textContent = score;
    confEl.textContent  = conf;

    summaryBox.textContent = analysis.summary || "Análisis completado.";
    summaryBox.classList.remove("hidden");

    currentMeta = {
      score,
      level,
      confidence: conf
    };

    if (analysis.pro && analysis.pro._scores) {
      currentProData = analysis.pro._scores;
    } else {
      currentProData = {
        emotions: 0.7,
        polarization: 0.4,
        scientific_claims: 0.2,
        contradictions: 0.1
      };
    }

    stopScanUI();
  }

  // =====================================
  // CLICK HANDLER
  // =====================================
  document.addEventListener("click", (e) => {

    // 👉 BOTÓN PRO (FUNNEL)
    if (e.target.id === "upgradeBtn") {

      if (!currentMeta) return;

      // 👉 redirección a landing analysis
      const url = `${PRO_URL}?score=${currentMeta.score}&level=${currentMeta.level}&conf=${currentMeta.confidence}`;

      chrome.tabs.create({ url });

      // 👉 efecto visual leve (no desbloqueo real)
      const format = v => Math.round(v * 100) + "%";

      document.getElementById("pro-emocionalidad").textContent = format(currentProData.emotions);
      document.getElementById("pro-manipulacion").textContent = format(currentProData.polarization);
      document.getElementById("pro-evidencia").textContent = format(currentProData.scientific_claims);
      document.getElementById("pro-coherencia").textContent = format(currentProData.contradictions);

      proSection.classList.remove("locked");

      e.target.style.display = "none";
    }

    // 👉 RE-ANALIZAR
    if (e.target.id === "analyzeBtn") {
      runAnalysis();
    }
  });

  runAnalysis();
});