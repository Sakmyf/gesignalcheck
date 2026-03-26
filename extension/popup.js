const API_URL = "https://gesignalcheck-production-8e78.up.railway.app/v3/verify";

// 🔥 FIX CRÍTICO: definir EXT_ID
const EXT_ID = "dpgnanocamaeieplhgnapgcannjcpghn";

document.addEventListener("DOMContentLoaded", () => {

  const analyzeBtn = document.getElementById("analyzeBtn");
  const scanLine   = document.getElementById("scanLine");
  const labelBadge = document.getElementById("labelBadge");
  const summaryBox = document.getElementById("summary");

  const scoreEl = document.getElementById("scoreValue");
  const confEl  = document.getElementById("confidenceValue");

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

        if (chrome.runtime.lastError || !extracted || !extracted.ok) {
          console.error("❌ Error content script:", chrome.runtime.lastError);
          labelBadge.textContent = "Error leyendo página";
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

          console.log("📡 Response status:", res.status);

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
          console.error("❌ Error fetch:", e);
          labelBadge.textContent = "Error de conexión";
          stopScanUI();
        }

      });

    } catch (err) {
      console.error("❌ Error general:", err);
      labelBadge.textContent = "Error de pestaña";
      stopScanUI();
    }
  }

  function renderResult(data) {

    const analysis = data.analysis || data;

    const level      = (analysis.level || "yellow").toLowerCase();
    const score      = analysis.score;
    const confidence = analysis.confidence;

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

    if (scoreEl && score !== undefined) {
      scoreEl.textContent = Math.round(score);
    }

    if (confEl && confidence !== undefined) {
      confEl.textContent = Math.round(confidence);
    }

    summaryBox.textContent =
      analysis.insight ||
      analysis.summary ||
      "Análisis completado.";

    summaryBox.classList.remove("hidden");
  }

  runAnalysis();
  analyzeBtn.addEventListener("click", runAnalysis);

});