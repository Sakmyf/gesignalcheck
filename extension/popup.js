const API_URL = "https://gesignalcheck-production-8e78.up.railway.app/v3/verify";

document.addEventListener("DOMContentLoaded", () => {

  const analyzeBtn = document.getElementById("analyzeBtn");
  const scanLine   = document.getElementById("scanLine");
  const labelBadge = document.getElementById("labelBadge");
  const summaryBox = document.getElementById("summary");
  const scoreEl    = document.getElementById("scoreValue");
  const confEl     = document.getElementById("confidenceValue");

  const upgradeBtn = document.getElementById("upgradeBtn");
  const proSection = document.getElementById("proSection");
  const proWarning = document.getElementById("proWarning");

  function startScanUI() {
    if (scanLine) scanLine.classList.add("active");

    labelBadge.textContent = "Analizando contenido...";
    labelBadge.style.background = "#333";
    labelBadge.style.color = "#aaa";

    summaryBox.classList.add("hidden");
    scoreEl.textContent = "--";
    confEl.textContent = "--";
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

      if (!tab?.id || tab.url.startsWith("chrome://")) {
        labelBadge.textContent = "Página no compatible";
        stopScanUI();
        return;
      }

      try {
        await chrome.scripting.executeScript({
          target: { tabId: tab.id },
          files: ["content_script.js"]
        });
      } catch {}

      await new Promise(r => setTimeout(r, 150));

      chrome.tabs.sendMessage(tab.id, { action: "extractText" }, async (extracted) => {

        if (!extracted) {
          labelBadge.textContent = "Error leyendo página";
          stopScanUI();
          return;
        }

        const text = extracted.text || "";
        if (text.length < 30) {
          labelBadge.textContent = "Texto insuficiente";
          stopScanUI();
          return;
        }

        try {

          const res = await fetch(API_URL, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "x-extension-id": chrome.runtime.id
            },
            body: JSON.stringify({
              text,
              url: extracted.url || tab.url
            })
          });

          const data = await res.json();

          const wait = Math.max(0, MIN_TIME - (Date.now() - startTime));

          setTimeout(() => {
            renderResult(data);
            stopScanUI();
          }, wait);

        } catch {
          labelBadge.textContent = "Error de conexión";
          stopScanUI();
        }

      });

    } catch {
      labelBadge.textContent = "Error inesperado";
      stopScanUI();
    }
  }

  function renderResult(data) {

    const analysis = data?.analysis || data;
    if (!analysis) return;

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

    const score = analysis.structural_index ?? 0;
    scoreEl.textContent = score <= 1 ? Math.round(score * 100) : Math.round(score);

    const conf = analysis.confidence ?? 0;
    confEl.textContent = conf <= 1 ? Math.round(conf * 100) : Math.round(conf);

    summaryBox.textContent =
      analysis.insight ||
      "El contenido no presenta señales relevantes de manipulación o riesgo.";

    summaryBox.classList.remove("hidden");

    const plan = data?.meta?.plan || "free";

    // 🔐 CONTROL PRO (FIX REAL)
    if (plan === "free") {

      proSection.classList.add("locked");

      if (proWarning) proWarning.style.display = "block";
      if (upgradeBtn) upgradeBtn.style.display = "block";

    } else {

      proSection.classList.remove("locked");

      if (proWarning) proWarning.style.display = "none";
      if (upgradeBtn) upgradeBtn.style.display = "none";

    }
  }

  if (upgradeBtn) {
    upgradeBtn.addEventListener("click", () => {
      chrome.tabs.create({
        url: "https://gesignalcheck.com/analysis"
      });
    });
  }

  runAnalysis();

  if (analyzeBtn) {
    analyzeBtn.addEventListener("click", runAnalysis);
  }

});