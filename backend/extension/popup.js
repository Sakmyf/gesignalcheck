console.log("🔥 POPUP JS CARGADO");

const API_URL = "https://gesignalcheck-production-8e78.up.railway.app/v3/verify";

document.addEventListener("DOMContentLoaded", () => {

  // ================================
  // ELEMENTOS
  // ================================

  const analyzeBtn     = document.getElementById("analyzeBtn");
  const labelBadge     = document.getElementById("labelBadge");
  const loader         = document.getElementById("loader");
  const summaryBox     = document.getElementById("summary");
  const contextNote    = document.getElementById("contextNote");
  const signalsList    = document.getElementById("signalsList");
  const scoreContainer = document.getElementById("scoreContainer");
  const scoreValue     = document.getElementById("scoreValue");
  const errorBox       = document.getElementById("error");

  resetUI();

  setTimeout(() => analyzeBtn?.click(), 300);

  analyzeBtn.addEventListener("click", runAnalysis);

  // ================================
  // MAIN
  // ================================

  async function runAnalysis() {

    resetUI();
    setLoading(true);

    try {

      console.log("🚀 INICIANDO ANALISIS");

      const tab = await getActiveTab();

      console.log("📄 TAB ACTIVA:", tab);

      // 🔥 FIX CLAVE → ASEGURAR CONTENT SCRIPT
      await ensureContentScript(tab.id);

      // pequeña espera para asegurar carga
      await new Promise(r => setTimeout(r, 200));

      const extracted = await getPageText(tab);

      console.log("📄 TEXTO EXTRAIDO:", extracted);

      if (!extracted?.text || extracted.text.length < 30) {
        throw new Error("Texto insuficiente para analizar");
      }

      const data = await callBackend(extracted);

      console.log("✅ RESPUESTA BACKEND:", data);

      renderResult(data);

    } catch (err) {

      console.error("❌ ERROR:", err);
      showError(err.message || "Error inesperado");

    } finally {

      setLoading(false);

    }
  }

  // ================================
  // 🔥 INYECCIÓN SEGURA
  // ================================

  async function ensureContentScript(tabId) {

    try {

      await chrome.scripting.executeScript({
        target: { tabId },
        files: ["content_script.js"]
      });

      console.log("✅ Content script asegurado");

    } catch (e) {

      console.log("⚠️ Ya estaba inyectado o no necesario:", e);

    }

  }

  // ================================
  // HELPERS UI
  // ================================

  function resetUI() {

    errorBox.style.display = "none";
    errorBox.textContent = "";

    labelBadge.textContent = "Analizando...";
    labelBadge.className = "signal-label";

    loader.classList.remove("done");

    summaryBox.classList.add("hidden");
    summaryBox.textContent = "";

    contextNote.classList.add("hidden");
    contextNote.textContent = "";

    signalsList.classList.add("hidden");
    signalsList.innerHTML = "";

    scoreContainer.classList.add("hidden");
  }

  function setLoading(on) {
    loader.classList.toggle("done", !on);
  }

  function showError(msg) {

    loader.classList.add("done");

    errorBox.textContent = msg;
    errorBox.style.display = "block";

    labelBadge.textContent = "Error";
  }

  // ================================
  // VISUAL LEVEL
  // ================================

  function setLevelVisual(level) {

    labelBadge.className = "signal-label";

    switch ((level || "").toLowerCase()) {

      case "low":
      case "bajo":
        labelBadge.textContent = "Bajo riesgo";
        labelBadge.classList.add("badge-low");
        break;

      case "high":
      case "alto":
        labelBadge.textContent = "Alto riesgo";
        labelBadge.classList.add("badge-high");
        break;

      default:
        labelBadge.textContent = "Riesgo medio";
        labelBadge.classList.add("badge-medium");
    }
  }

  // ================================
  // TAB ACTIVA
  // ================================

  async function getActiveTab() {

    const [tab] = await chrome.tabs.query({
      active: true,
      currentWindow: true
    });

    if (!tab?.url) throw new Error("No se pudo obtener la pestaña");

    const blocked = [
      "chrome://",
      "chrome-extension://",
      "edge://",
      "about:",
      "file://"
    ];

    if (blocked.some(p => tab.url.startsWith(p))) {
      throw new Error("Página no compatible");
    }

    return tab;
  }

  // ================================
  // CONTENT SCRIPT
  // ================================

  async function getPageText(tab) {

    return new Promise((resolve, reject) => {

      console.log("📤 Enviando mensaje al content script...");

      chrome.tabs.sendMessage(tab.id, { action: "extractText" }, response => {

        if (chrome.runtime.lastError) {

          console.error("❌ runtime.lastError:", chrome.runtime.lastError.message);

          reject(new Error("No se pudo conectar con la página"));
          return;
        }

        if (!response) {
          reject(new Error("Sin respuesta del content script"));
          return;
        }

        console.log("📥 RESPUESTA CONTENT SCRIPT:", response);

        resolve(response);
      });

    });
  }

  // ================================
  // BACKEND
  // ================================

  async function callBackend(extracted) {

    console.log("🚀 ENVIANDO REQUEST:", extracted);

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 12000);

    try {

      const response = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-extension-id": chrome.runtime.id
        },
        body: JSON.stringify({
          url: extracted.url,
          text: extracted.text,
          title: extracted.title || ""
        }),
        signal: controller.signal
      });

      console.log("📡 STATUS:", response.status);

      clearTimeout(timeout);

      if (!response.ok) {
        throw new Error("Error del servidor: " + response.status);
      }

      const data = await response.json();

      console.log("📦 RESPONSE JSON:", data);

      return data;

    } catch (err) {

      if (err.name === "AbortError") {
        throw new Error("Servidor no respondió (timeout)");
      }

      throw err;
    }
  }

  // ================================
  // RENDER
  // ================================

  function renderResult(data) {

    console.log("🔥 RENDER:", data);

    const analysis = data.analysis || data;

    if (!analysis) {
      showError("No hay análisis en respuesta");
      return;
    }

    const level =
      analysis.level ||
      analysis.risk_level ||
      "medio";

    const summary =
      analysis.summary ||
      analysis.message ||
      "Análisis estructural básico completado";

    const indicators =
      analysis.indicators ||
      analysis.signals ||
      [];

    setLevelVisual(level);

    summaryBox.textContent = summary;
    summaryBox.classList.remove("hidden");

    signalsList.innerHTML = "";

    if (indicators.length === 0) {

      const li = document.createElement("li");
      li.textContent = "Análisis superficial sin señales fuertes";
      signalsList.appendChild(li);

    } else {

      indicators.slice(0, 3).forEach(s => {

        const li = document.createElement("li");
        li.textContent = s.title || s;
        signalsList.appendChild(li);

      });

    }

    const teaser = document.createElement("li");
    teaser.className = "teaser";
    teaser.textContent = "+ análisis avanzado disponible en PRO";
    signalsList.appendChild(teaser);

    signalsList.classList.remove("hidden");
  }

});