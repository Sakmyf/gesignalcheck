const API_URL = "https://gesignalcheck-production-8e78.up.railway.app/v3/verify";
const EXT_ID = "dpgnanocamaeieplhgnapgcannjcpghn";

document.addEventListener("DOMContentLoaded", () => {

  const analyzeBtn = document.getElementById("analyzeBtn");
  const scanLine   = document.getElementById("scanLine");
  const labelBadge = document.getElementById("labelBadge");
  const summaryBox = document.getElementById("summary");

  const scoreEl = document.getElementById("scoreValue");
  const confEl  = document.getElementById("confidenceValue");

  // =========================
  // UI STATES
  // =========================

  function startScanUI() {
    scanLine.classList.add("active");
    labelBadge.textContent = "Analizando contenido...";
    labelBadge.className = "signal-label";
    summaryBox.classList.add("hidden");

    if (scoreEl) scoreEl.textContent = "--";
    if (confEl) confEl.textContent = "--";
  }

  function stopScanUI() {
    scanLine.classList.remove("active");
  }

  // =========================
  // MAIN ANALYSIS
  // =========================

  async function runAnalysis() {

    const MIN_TIME = 3000;
    const startTime = Date.now();

    startScanUI();

    try {

      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

      if (!tab?.id || tab.url.startsWith("chrome://")) {
        throw new Error("Incompatible");
      }

      chrome.tabs.sendMessage(tab.id, { action: "extractText" }, async (extracted) => {

        if (chrome.runtime.lastError || !extracted) {
          labelBadge.textContent = "Error: recargar página";
          stopScanUI();
          return;
        }

        try {

          const res = await fetch(API_URL, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "x-extension-id": EXT_ID
            },
            body: JSON.stringify({
              text: extracted.text,
              url: extracted.url
            })
          });

          if (res.status === 401) {
            labelBadge.textContent = "Extensión no autorizada";
            stopScanUI();
            return;
          }

          if (res.status === 429) {
            labelBadge.textContent = "Límite alcanzado";
            stopScanUI();
            return;
          }

          if (!res.ok) throw new Error("Servidor");

          const data = await res.json();

          const wait = Math.max(0, MIN_TIME - (Date.now() - startTime));

          setTimeout(() => {
            renderResult(data);
            stopScanUI();
          }, wait);

        } catch (e) {
          labelBadge.textContent = "Error de conexión";
          stopScanUI();
        }

      });

    } catch (err) {
      labelBadge.textContent = "Error de pestaña";
      stopScanUI();
    }
  }

  // =========================
  // RENDER RESULT (PRO READY)
  // =========================

  function renderResult(data) {

    const analysis = data.analysis || data;

    const level      = (analysis.level || "yellow").toLowerCase();
    const score      = analysis.structural_index;
    const confidence = analysis.confidence;

    // =========================
    // BADGE
    // =========================

    if (level === "green") {
      labelBadge.textContent = "🟢 Bajo riesgo";
      labelBadge.style.background = "#1e7f4f";
    }
    else if (level === "yellow") {
      labelBadge.textContent = "🟡 Riesgo moderado";
      labelBadge.style.background = "#b38b00";
    }
    else {
      labelBadge.textContent = "🔴 Alto riesgo";
      labelBadge.style.background = "#a12d2d";
    }

    // =========================
    // SCORE
    // =========================

    if (scoreEl && score !== undefined) {
      scoreEl.textContent = Math.round(score);
    }

    // =========================
    // CONFIDENCE
    // =========================

    if (confEl && confidence !== undefined) {
      confEl.textContent = Math.round(confidence * 100);
    }

    // =========================
    // INSIGHT
    // =========================

    summaryBox.textContent =
      analysis.insight ||
      analysis.summary ||
      "Análisis completado.";

    summaryBox.classList.remove("hidden");
  }

  // =========================
  // INIT
  // =========================

  runAnalysis();
  analyzeBtn.addEventListener("click", runAnalysis);

});