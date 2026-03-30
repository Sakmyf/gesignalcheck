const API_URL = "https://gesignalcheck-production-8e78.up.railway.app/v3/verify";

document.addEventListener("DOMContentLoaded", () => {

  const analyzeBtn = document.getElementById("analyzeBtn");
  const scanLine   = document.getElementById("scanLine");
  const labelBadge = document.getElementById("labelBadge");
  const summaryBox = document.getElementById("summary");
  const scoreEl    = document.getElementById("scoreValue");
  const confEl     = document.getElementById("confidenceValue");

  // 🔥 BOTÓN PRO (ROBUSTO)
  const unlockBtn =
    document.getElementById("upgradeBtn") ||
    document.getElementById("unlockBtn")  ||
    document.querySelector("button.upgrade-btn");

  const proSection = document.querySelector(".pro-section");

  function startScanUI() {
    if (scanLine) scanLine.classList.add("active");

    if (labelBadge) {
      labelBadge.textContent  = "Analizando contenido...";
      labelBadge.style.background = "#333";
      labelBadge.style.color      = "#aaa";
    }

    if (summaryBox) summaryBox.classList.add("hidden");
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
        if (labelBadge) labelBadge.textContent = "Página no compatible";
        stopScanUI();
        return;
      }

      try {
        await chrome.scripting.executeScript({
          target: { tabId: tab.id },
          files: ["content_script.js"]
        });
      } catch (_) {}

      await new Promise(r => setTimeout(r, 150));

      chrome.tabs.sendMessage(tab.id, { action: "extractText" }, async (extracted) => {

        if (chrome.runtime.lastError || !extracted) {
          if (labelBadge) labelBadge.textContent = "Error leyendo página";
          stopScanUI();
          return;
        }

        const textToSend = extracted.text || "";

        if (textToSend.length < 30) {
          if (labelBadge) labelBadge.textContent = "Texto insuficiente";
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
              text: textToSend,
              url:  extracted.url || tab.url
            })
          });

          if (!res.ok) {
            if (labelBadge) labelBadge.textContent = "Error del servidor (" + res.status + ")";
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
          if (labelBadge) labelBadge.textContent = "Error de conexión";
          stopScanUI();
        }

      });

    } catch (err) {
      console.error("❌ Error general:", err);
      if (labelBadge) labelBadge.textContent = "Error inesperado";
      stopScanUI();
    }
  }

  function renderResult(data) {

    console.log("🔥 RENDER DATA:", JSON.stringify(data, null, 2));

    const analysis = data?.analysis || data;

    if (!analysis) {
      if (labelBadge) labelBadge.textContent = "Sin datos";
      return;
    }

    const level = (analysis.level || "medio").toLowerCase();

    if (labelBadge) {
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
    }

    const rawScore = analysis.structural_index;

    if (scoreEl && rawScore !== undefined) {
      const display = rawScore <= 1.0
        ? Math.round(rawScore * 100)
        : Math.round(rawScore);
      scoreEl.textContent = display;
    }

    const conf = analysis.confidence;

    if (confEl && conf !== undefined) {
      const display = conf <= 1.0
        ? Math.round(conf * 100)
        : Math.round(conf);
      confEl.textContent = display;
    }

    if (summaryBox) {
      summaryBox.textContent =
        analysis.insight  ||
        analysis.summary  ||
        analysis.message  ||
        "Análisis completado.";

      summaryBox.classList.remove("hidden");
    }

    // ============================
    // 🔐 CONTROL PRO (NUEVO)
    // ============================
    const plan = data?.meta?.plan || "free";

    if (plan === "free") {

      if (proSection) proSection.classList.add("locked");
      if (unlockBtn) unlockBtn.style.display = "block";

    } else {

      if (proSection) proSection.classList.remove("locked");
      if (unlockBtn) unlockBtn.style.display = "none";

    }
  }

  // ============================
  // 🚀 BOTÓN PRO
  // ============================
  if (unlockBtn) {

    unlockBtn.addEventListener("click", () => {

      console.log("🚀 Click PRO detectado");

      chrome.tabs.create({
        url: "https://gesignalcheck.com/analysis"
      });

    });

  } else {
    console.warn("⚠️ Botón PRO no encontrado (revisar HTML)");
  }

  // AUTO-RUN + BOTÓN
  runAnalysis();

  if (analyzeBtn) {
    analyzeBtn.addEventListener("click", runAnalysis);
  }

});