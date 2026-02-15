document.addEventListener("DOMContentLoaded", () => {

  const analyzeBtn = document.getElementById("analyzeBtn");
  const scoreValue = document.getElementById("scoreValue");
  const confidenceBar = document.getElementById("confidenceBar");
  const signalsList = document.getElementById("signalsList");
  const labelBadge = document.getElementById("labelBadge");
  const errorDiv = document.getElementById("error");

  const API_URL = "https://ge-signal-check-production.up.railway.app/v3/verify";

  analyzeBtn.addEventListener("click", async () => {

    resetUI();

    try {

      // 1️⃣ Obtener pestaña activa
      const tabs = await chrome.tabs.query({ active: true, currentWindow: true });

      if (!tabs || tabs.length === 0) {
        showError("No se encontró pestaña activa.");
        return;
      }

      const tab = tabs[0];

      if (!tab.id) {
        showError("ID de pestaña inválido.");
        return;
      }

      // 2️⃣ Extraer texto desde content_script
      const response = await chrome.tabs.sendMessage(tab.id, { action: "extractText" });

      if (!response || !response.text || response.text.length < 50) {
        showError("No se pudo extraer texto significativo.");
        return;
      }

      // 3️⃣ Obtener ID real de la extensión (seguridad)
      const extensionId = chrome.runtime.id;

      if (!extensionId) {
        showError("No se pudo obtener ID de extensión.");
        return;
      }

      // 4️⃣ Llamada al backend
      const apiResponse = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-extension-id": extensionId
        },
        body: JSON.stringify({
          url: response.url,
          text: response.text
        })
      });

      if (!apiResponse.ok) {
        const errorText = await apiResponse.text();
        console.error("HTTP ERROR:", apiResponse.status, errorText);
        showError("Error del servidor (" + apiResponse.status + ")");
        return;
      }

      const data = await apiResponse.json();
      updateUI(data);

    } catch (error) {
      console.error("Error general:", error);
      showError("Error en la comunicación con el servidor.");
    }

  });

  // ----------------------------------------
  // UI FUNCTIONS
  // ----------------------------------------

  function resetUI() {
    errorDiv.style.display = "none";
    labelBadge.textContent = "Analizando...";
    labelBadge.className = "signal-label";
    scoreValue.textContent = "0.00";
    confidenceBar.style.width = "0%";
    confidenceBar.className = "confidence-bar";
    signalsList.innerHTML = "<li>Procesando...</li>";
  }

  function updateUI(data) {

    if (!data || typeof data.risk_index !== "number") {
      showError("Respuesta inválida del servidor.");
      return;
    }

    const risk = Math.max(0, Math.min(1, data.risk_index));

    scoreValue.textContent = risk.toFixed(2);
    confidenceBar.style.width = (risk * 100) + "%";

    signalsList.innerHTML = "";

    const signals = data?.details?.rhetorical_signals || [];

    if (signals.length > 0) {
      signals.forEach(signal => {
        const li = document.createElement("li");
        li.textContent = signal;
        signalsList.appendChild(li);
      });
    } else {
      signalsList.innerHTML = "<li>No se detectaron señales relevantes</li>";
    }

    if (risk < 0.35) {
      labelBadge.textContent = "Riesgo Bajo";
      labelBadge.classList.add("risk-low");
      confidenceBar.classList.add("bar-low");
    } else if (risk < 0.65) {
      labelBadge.textContent = "Riesgo Medio";
      labelBadge.classList.add("risk-medium");
      confidenceBar.classList.add("bar-medium");
    } else {
      labelBadge.textContent = "Riesgo Alto";
      labelBadge.classList.add("risk-high");
      confidenceBar.classList.add("bar-high");
    }
  }

  function showError(message) {
    errorDiv.textContent = message;
    errorDiv.style.display = "block";
    labelBadge.textContent = "Error";
    labelBadge.className = "signal-label";
  }

});
