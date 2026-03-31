// ==========================================
// SIGNALCHECK POPUP.JS - FUNNEL + PRO REAL
// ==========================================

console.log("🔥 POPUP JS CARGADO");

// 👉 BACKEND
const API_URL = "https://gesignalcheck-production-8e78.up.railway.app/v3/verify";

// 👉 LANDING
const PRO_URL = "https://gesignalcheck.com/analysis";

let currentProData = null;
let currentMeta = null;

document.addEventListener("DOMContentLoaded", async () => {

  const scanLine   = document.getElementById("scanLine");
  const labelBadge = document.getElementById("labelBadge");
  const summaryBox = document.getElementById("summary");
  const scoreEl    = document.getElementById("scoreValue");
  const confEl     = document.getElementById("confidenceValue");
  const proSection = document.getElementById("proSection");

  const tokenInput = document.getElementById("proTokenInput");
  const activateBtn = document.getElementById("activateProBtn");

  let storedToken = "";

  // 🔐 LEER TOKEN GUARDADO
  const stored = await chrome.storage.local.get("pro_token");
  storedToken = stored.pro_token || "";

  // =========================
  // 🔓 ACTIVAR PRO
  // =========================
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
              "x-extension-id": chrome.runtime.id,
              "x-pro-token": storedToken || ""
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

    const plan = data?.meta?.plan || "free";

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

    currentMeta = { score, level, confidence: conf };

    // =========================
    // 🔐 PRO REAL
    // =========================
    if (plan === "pro") {

      proSection.classList.remove("locked");

      document.getElementById("upgradeBtn").style.display = "none";

      // ejemplo visual real
      ["pro-emocionalidad","pro-manipulacion","pro-evidencia","pro-coherencia"]
        .forEach(id => document.getElementById(id).textContent = "✔");

    } else {

      proSection.classList.add("locked");
      document.getElementById("upgradeBtn").style.display = "block";
    }

    stopScanUI();
  }

  // =========================
  // FUNNEL (BOTÓN PRO)
  // =========================
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