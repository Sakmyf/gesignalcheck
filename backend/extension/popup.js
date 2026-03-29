// ==========================================
// SIGNALCHECK POPUP.JS - MODERN UI & PRO FIX
// ==========================================

console.log("🔥 POPUP JS CARGADO");

const API_URL = "https://gesignalcheck-production-8e78.up.railway.app/v3/verify";
const EXT_ID  = "dpgnanocamaeieplhgnapgcannjcpghn";

// Variable global para guardar los datos PRO temporalmente
let currentProData = null;

document.addEventListener("DOMContentLoaded", () => {

  const analyzeBtn = document.getElementById("analyzeBtn");
  const scanLine   = document.getElementById("scanLine");
  const labelBadge = document.getElementById("labelBadge");
  const summaryBox = document.getElementById("summary");
  const scoreEl    = document.getElementById("scoreValue");
  const confEl     = document.getElementById("confidenceValue");
  
  const upgradeBtn = document.getElementById("upgradeBtn");
  const proSection = document.getElementById("proSection");

  function startScanUI() {
    if (scanLine) scanLine.classList.add("active");
    labelBadge.textContent  = "Analizando contenido...";
    labelBadge.style.background = "#333";
    labelBadge.style.color      = "#aaa";
    
    summaryBox.classList.add("hidden");
    summaryBox.textContent = "";
    
    if (scoreEl) scoreEl.textContent = "--";
    if (confEl)  confEl.textContent  = "--";
    
    proSection.classList.add("locked");
    document.getElementById("pro-emocionalidad").textContent = "🔒";
    document.getElementById("pro-manipulacion").textContent = "🔒";
    document.getElementById("pro-evidencia").textContent = "🔒";
    document.getElementById("pro-coherencia").textContent = "🔒";
    if(upgradeBtn) {
        upgradeBtn.textContent = "Desbloquear análisis completo";
        upgradeBtn.style.display = "block";
        upgradeBtn.style.opacity = "1";
    }
    currentProData = null;
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
    const MIN_TIME  = 1500;
    const startTime = Date.now();
    startScanUI();

    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (!tab?.id || tab.url.startsWith("chrome://") || tab.url.startsWith("chrome-extension://")) {
        showError("Página no compatible para análisis.");
        return;
      }

      try {
        await chrome.scripting.executeScript({ target: { tabId: tab.id }, files: ["content_script.js"] });
      } catch (e) {}

      await new Promise(r => setTimeout(r, 150));

      chrome.tabs.sendMessage(tab.id, { action: "extractText" }, async (extracted) => {
        if (chrome.runtime.lastError || !extracted) {
          showError("Error leyendo la página. Intenta recargar (F5).");
          return;
        }
        const textToSend = extracted.text || "";
        if (textToSend.length < 30) {
          showError("Texto insuficiente.");
          return;
        }

        try {
          const res = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json", "x-extension-id": EXT_ID },
            body: JSON.stringify({ text: textToSend, url: extracted.url || tab.url })
          });

          if (!res.ok) {
            showError("Error del servidor (" + res.status + ").");
            return;
          }
          const data = await res.json();
          const wait = Math.max(0, MIN_TIME - (Date.now() - startTime));
          setTimeout(() => { renderResult(data); stopScanUI(); }, wait);

        } catch (e) {
          showError("Error de conexión.");
        }
      });
    } catch (err) {
      showError("Error inesperado.");
    }
  }

  function renderResult(data) {
    const analysis = data?.analysis || data;
    if (!analysis) return showError("Sin datos.");

    const level = (analysis.level || "medio").toLowerCase();
    if (level === "bajo") {
      labelBadge.textContent = "🟢 Bajo riesgo"; labelBadge.style.background = "rgba(34,197,94,0.2)"; labelBadge.style.color = "#4ade80";
    } else if (level === "medio") {
      labelBadge.textContent = "🟡 Riesgo moderado"; labelBadge.style.background = "rgba(250,204,21,0.2)"; labelBadge.style.color = "#facc15";
    } else {
      labelBadge.textContent = "🔴 Alto riesgo"; labelBadge.style.background = "rgba(239,68,68,0.2)"; labelBadge.style.color = "#f87171";
    }

    if (scoreEl && analysis.structural_index !== undefined) {
      scoreEl.textContent = analysis.structural_index <= 1.0 ? Math.round(analysis.structural_index * 100) : Math.round(analysis.structural_index);
    }
    if (confEl && analysis.confidence !== undefined) {
      confEl.textContent = analysis.confidence <= 1.0 ? Math.round(analysis.confidence * 100) : Math.round(analysis.confidence);
    }

    summaryBox.textContent = analysis.insight || analysis.summary || "Completado.";
    summaryBox.classList.remove("hidden");

    if (analysis.pro && analysis.pro._scores) {
       currentProData = analysis.pro._scores;
    }
  }

  // =============================================
  // LÓGICA DEL BOTÓN PRO (LA QUE FALTABA)
  // =============================================
  if(upgradeBtn) {
      upgradeBtn.addEventListener("click", () => {
        if (!currentProData) {
            upgradeBtn.textContent = "Analizando... Espera por favor.";
            return;
        }
        
        upgradeBtn.textContent = "Desbloqueando...";
        upgradeBtn.style.opacity = "0.7";

        setTimeout(() => {
            const formatScore = (val) => `${Math.round((val || 0) * 100)}%`;
            document.getElementById("pro-emocionalidad").textContent = formatScore(currentProData.emotions);
            document.getElementById("pro-manipulacion").textContent = formatScore(currentProData.polarization);
            document.getElementById("pro-evidencia").textContent = formatScore(currentProData.scientific_claims);
            document.getElementById("pro-coherencia").textContent = formatScore(currentProData.contradictions);

            proSection.classList.remove("locked");
            upgradeBtn.style.display = "none"; 
        }, 500); 
      });
  }

  runAnalysis();
  if(analyzeBtn) analyzeBtn.addEventListener("click", runAnalysis);
});