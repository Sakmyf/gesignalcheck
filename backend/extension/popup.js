// ==========================================
// SIGNALCHECK POPUP.JS - MODERN UI & PRO FIX
// ==========================================

console.log("🔥 POPUP JS CARGADO");

const API_URL = "https://gesignalcheck-production-8e78.up.railway.app/v3/verify";
const EXT_ID  = "dpgnanocamaeieplhgnapgcannjcpghn";

// Variable global para guardar los datos PRO temporalmente
let currentProData = null;

document.addEventListener("DOMContentLoaded", () => {

  // ================================
  // ELEMENTOS DEL DOM
  // ================================
  const analyzeBtn = document.getElementById("analyzeBtn");
  const scanLine   = document.getElementById("scanLine");
  const labelBadge = document.getElementById("labelBadge");
  const summaryBox = document.getElementById("summary");
  const scoreEl    = document.getElementById("scoreValue");
  const confEl     = document.getElementById("confidenceValue");
  
  // Elementos PRO
  const upgradeBtn = document.getElementById("upgradeBtn");
  const proSection = document.getElementById("proSection");

  // ================================
  // HELPERS UI
  // ================================
  function startScanUI() {
    if (scanLine) scanLine.classList.add("active");
    labelBadge.textContent  = "Analizando contenido...";
    labelBadge.style.background = "#333";
    labelBadge.style.color      = "#aaa";
    
    summaryBox.classList.add("hidden");
    summaryBox.textContent = "";
    
    if (scoreEl) scoreEl.textContent = "--";
    if (confEl)  confEl.textContent  = "--";
    
    // Resetear el bloque PRO a estado bloqueado
    proSection.classList.add("locked");
    document.getElementById("pro-emocionalidad").textContent = "🔒";
    document.getElementById("pro-manipulacion").textContent = "🔒";
    document.getElementById("pro-evidencia").textContent = "🔒";
    document.getElementById("pro-coherencia").textContent = "🔒";
    upgradeBtn.textContent = "Desbloquear análisis completo";
    upgradeBtn.style.display = "block";
    upgradeBtn.style.opacity = "1";
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

  // ================================
  // MAIN FLOW
  // ================================
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

      // Inyectar script por si acaso
      try {
        await chrome.scripting.executeScript({
          target: { tabId: tab.id },
          files: ["content_script.js"]
        });
      } catch (e) {
        console.log("Script ya inyectado o no permitido.");
      }

      await new Promise(r => setTimeout(r, 150));

      // Extraer texto
      chrome.tabs.sendMessage(tab.id, { action: "extractText" }, async (extracted) => {
        if (chrome.runtime.lastError || !extracted) {
          showError("Error leyendo la página. Intenta recargar (F5).");
          return;
        }

        const textToSend = extracted.text || "";

        if (textToSend.length < 30) {
          showError("El texto de esta página es insuficiente para un análisis confiable.");
          return;
        }

        // Llamada al Backend
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
            showError("Error del servidor (" + res.status + ").");
            return;
          }

          const data = await res.json();

          // Esperar un mínimo de tiempo para que la animación se vea bien
          const wait = Math.max(0, MIN_TIME - (Date.now() - startTime));
          setTimeout(() => {
            renderResult(data);
            stopScanUI();
          }, wait);

        } catch (e) {
          console.error("❌ fetch error:", e);
          showError("No se pudo conectar con el servidor SignalCheck.");
        }
      });

    } catch (err) {
      console.error("❌ Error general:", err);
      showError("Ocurrió un error inesperado.");
    }
  }

  // ================================
  // RENDER RESULTADOS
  // ================================
  function renderResult(data) {
    const analysis = data?.analysis || data;

    if (!analysis) {
      showError("Sin datos en la respuesta.");
      return;
    }

    // Nivel Visual
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

    // Score Numérico (0-100)
    const rawScore = analysis.structural_index;
    if (scoreEl && rawScore !== undefined) {
      const display = rawScore <= 1.0 ? Math.round(rawScore * 100) : Math.round(rawScore);
      scoreEl.textContent = display;
    }

    // Confianza
    const conf = analysis.confidence;
    if (confEl && conf !== undefined) {
      const display = conf <= 1.0 ? Math.round(conf * 100) : Math.round(conf);
      confEl.textContent = display;
    }

    // Mensaje / Resumen
    summaryBox.textContent = analysis.insight || analysis.summary || analysis.message || "Análisis completado.";
    summaryBox.classList.remove("hidden");

    // Guardar los datos PRO (Vienen del backend)
    if (analysis.pro && analysis.pro._scores) {
       currentProData = analysis.pro._scores;
    }
  }

  // =============================================
  // LÓGICA DE DESBLOQUEO DEL BOTÓN PRO
  // =============================================
  upgradeBtn.addEventListener("click", () => {
    if (!currentProData) {
        upgradeBtn.textContent = "Analiza una página primero";
        return;
    }

    // Efecto visual de carga
    upgradeBtn.textContent = "Desbloqueando...";
    upgradeBtn.style.opacity = "0.7";
    upgradeBtn.style.cursor = "wait";

    setTimeout(() => {
        // Formatear los números (de 0.0-1.0 a porcentaje)
        const formatScore = (val) => `${Math.round((val || 0) * 100)}%`;

        // Inyectar los datos reales reemplazando los candados
        document.getElementById("pro-emocionalidad").textContent = formatScore(currentProData.emotions);
        document.getElementById("pro-manipulacion").textContent = formatScore(currentProData.polarization);
        document.getElementById("pro-evidencia").textContent = formatScore(currentProData.scientific_claims);
        document.getElementById("pro-coherencia").textContent = formatScore(currentProData.contradictions);

        // Cambiar estilos para mostrar que está desbloqueado
        proSection.classList.remove("locked");
        upgradeBtn.style.display = "none"; // Ocultamos el botón
    }, 800); // 800ms de demora para sim