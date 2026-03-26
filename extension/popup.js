const API_URL = "https://gesignalcheck-production-8e78.up.railway.app/v3/verify";
const EXT_ID  = "dpgnanocamaeieplhgnapgcannjcpghn";

document.addEventListener("DOMContentLoaded", () => {

  const analyzeBtn = document.getElementById("analyzeBtn");
  const scanLine   = document.getElementById("scanLine");
  const labelBadge = document.getElementById("labelBadge");
  const summaryBox = document.getElementById("summary");
  const scoreEl    = document.getElementById("scoreValue");
  const confEl     = document.getElementById("confidenceValue");

  function startScanUI() {
    if (scanLine) scanLine.classList.add("active");
    labelBadge.textContent  = "Analizando contenido...";
    labelBadge.style.background = "#333";
    labelBadge.style.color      = "#aaa";
    summaryBox.classList.add("hidden");
    if (scoreEl) scoreEl.textContent = "--";
    if (confEl)  confEl.textContent  = "--";
  }

  function stopScanUI() {
    if (scanLine) scanLine.classList.remove("active");
  }

  async function runAnalysis() {

    const MIN_TIME  = 2000;
    const startTime = Date.now();

    startScanUI();

    try {

      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

      if (!tab?.id || tab.url.startsWith("chrome://") || tab.url.startsWith("chrome-extension://")) {
        labelBadge.textContent = "Página no compatible";
        stopScanUI();
        return;
      }

      // Asegurar content script inyectado
      try {
        await chrome.scripting.executeScript({
          target: { tabId: tab.id },
          files: ["content_script.js"]
        });
      } catch (_) {}

      await new Promise(r => setTimeout(r, 150));

      chrome.tabs.sendMessage(tab.id, { action: "extractText" }, async (extracted) => {

        if (chrome.runtime.lastError || !extracted) {
          labelBadge.textContent = "Error leyendo página";
          stopScanUI();
          return;
        }

        const textToSend = extracted.text || "";

        if (textToSend.length < 30) {
          labelBadge.textContent = "Texto insuficiente";
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
              text: textToSend,
              url:  extracted.url || tab.url
            })
          });

          if (!res.ok) {
            labelBadge.textContent = "Error del servidor (" + res.status + ")";
            stopScanUI();
            return;
          }

          const data = await res.json();

          const wait = Math.max(0, MIN_TIME - (Date.now() - startTime));
          setTimeout(() => {
            renderResult(data);
            stopScanUI();
          }, wait);

        } catch (e) {
          console.error("❌ fetch error:", e);
          labelBadge.textContent = "Error de conexión";
          stopScanUI();
        }

      });

    } catch (err) {
      console.error("❌ Error general:", err);
      labelBadge.textContent = "Error inesperado";
      stopScanUI();
    }
  }

  function renderResult(data) {

    console.log("🔥 RENDER DATA:", JSON.stringify(data, null, 2));

    const analysis = data?.analysis || data;

    if (!analysis) {
      labelBadge.textContent = "Sin datos";
      return;
    }

    // =============================================
    // LEVEL → badge
    // FIX: leer analysis.level (no analysis.status)
    // =============================================
    const level = (analysis.level || "medio").toLowerCase();

    if (level === "bajo") {
      labelBadge.textContent      = "🟢 Bajo riesgo";
      labelBadge.style.background = "rgba(34,197,94,0.2)";
      labelBadge.style.color      = "#4ade80";
    } else if (level === "medio") {
      labelBadge.textContent      = "🟡 Riesgo moderado";
      labelBadge.style.background = "rgba(250,204,21,0.2)";
      labelBadge.style.color      = "#facc15";
    } else {
      labelBadge.textContent      = "🔴 Alto riesgo";
      labelBadge.style.background = "rgba(239,68,68,0.2)";
      labelBadge.style.color      = "#f87171";
    }

    // =============================================
    // SCORE
    // FIX: leer structural_index (no score)
    // =============================================
    const rawScore = analysis.structural_index;

    if (scoreEl && rawScore !== undefined) {
      // El engine devuelve 0.0–1.0, mostrar como 0–100
      const display = rawScore <= 1.0
        ? Math.round(rawScore * 100)
        : Math.round(rawScore);
      scoreEl.textContent = display;
    }

    // =============================================
    // CONFIDENCE
    // =============================================
    const conf = analysis.confidence;
    if (confEl && conf !== undefined) {
      const display = conf <= 1.0
        ? Math.round(conf * 100)
        : Math.round(conf);
      confEl.textContent = display;
    }

    // =============================================
    // SUMMARY / INSIGHT
    // =============================================
    summaryBox.textContent =
      analysis.insight  ||
      analysis.summary  ||
      analysis.message  ||
      "Análisis completado.";

    summaryBox.classList.remove("hidden");
  }

  // Auto-run + botón manual
  runAnalysis();
  analyzeBtn.addEventListener("click", runAnalysis);

});