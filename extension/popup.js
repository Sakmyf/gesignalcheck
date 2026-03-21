const API_URL = "https://gesignalcheck-production-8e78.up.railway.app/v3/verify";
const EXT_ID = "dpgnanocamaeieplhgnapgcannjcpghn";

document.addEventListener("DOMContentLoaded", () => {

  const analyzeBtn = document.getElementById("analyzeBtn");
  const scanLine   = document.getElementById("scanLine");
  const labelBadge = document.getElementById("labelBadge");
  const summaryBox = document.getElementById("summary");

  function startScanUI() {
    scanLine.classList.add("active");
    labelBadge.textContent = "Analizando contenido...";
    labelBadge.className = "signal-label";
    summaryBox.classList.add("hidden");
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

  function renderResult(data) {

    const analysis = data.analysis || data;
    const level = (analysis.level || "low").toLowerCase();

    labelBadge.textContent =
      level === "low" ? "Bajo riesgo" :
      level === "high" ? "Alto riesgo" :
      "Requiere atención";

    labelBadge.className = `signal-label badge-${level === "low" ? "low" : "high"}`;

    summaryBox.textContent =
      analysis.insight ||
      analysis.summary ||
      "Análisis completado.";

    summaryBox.classList.remove("hidden");
  }

  // auto-run
  runAnalysis();

  // botón manual
  analyzeBtn.addEventListener("click", runAnalysis);

});