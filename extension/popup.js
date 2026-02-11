document.addEventListener("DOMContentLoaded", () => {

  const analyzeBtn = document.getElementById("analyzeBtn");

  analyzeBtn.addEventListener("click", async () => {

    try {

      const [tab] = await chrome.tabs.query({
        active: true,
        currentWindow: true
      });

      if (!tab) return;

      const response = await fetch(
        "https://gesignalcheck-production-91c9.up.railway.app/v1/verify",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            url: tab.url,
            text: "",
            page_type: "unknown"
          })
        }
      );

      const data = await response.json();

      updateUI(data);

    } catch (error) {
      showError("Error al analizar la página");
      console.error(error);
    }

  });

});

function updateUI(data) {

  if (!data) return;

  const scoreEl = document.getElementById("scoreValue");
  if (scoreEl) scoreEl.textContent = data.score;

  updateConfidence(data.score);
  updateLabel(data.label);
  updateSignals(data.evidence);

}

function updateConfidence(score) {

  const bar = document.getElementById("confidenceBar");
  if (!bar) return;

  bar.style.width = (score * 100) + "%";

  if (score >= 0.75) {
    bar.style.background = "linear-gradient(90deg, #4caf50, #2e7d32)";
  } else if (score >= 0.45) {
    bar.style.background = "linear-gradient(90deg, #ffb74d, #f57c00)";
  } else {
    bar.style.background = "linear-gradient(90deg, #ef5350, #b71c1c)";
  }
}

function updateLabel(label) {

  const el = document.getElementById("labelBadge");
  if (!el) return;

  let text = "";
  let bg = "";
  let color = "";

  if (label === "high_confidence") {
    text = "Alta confiabilidad";
    bg = "#e8f5e9";
    color = "#2e7d32";
  } 
  else if (label === "en_debate") {
    text = "En debate";
    bg = "#fff3e0";
    color = "#ef6c00";
  } 
  else {
    text = "Riesgo alto";
    bg = "#ffebee";
    color = "#c62828";
  }

  el.textContent = text;
  el.style.background = bg;
  el.style.color = color;
}

function updateSignals(evidence) {

  const list = document.getElementById("signalsList");
  if (!list) return;

  list.innerHTML = "";

  if (!evidence || evidence.length === 0) {
    list.innerHTML = "<li>No se detectaron señales relevantes</li>";
    return;
  }

  evidence.forEach(signal => {
    const li = document.createElement("li");
    li.textContent = signal;
    list.appendChild(li);
  });
}

function showError(message) {
  const errorEl = document.getElementById("error");
  if (!errorEl) return;

  errorEl.textContent = message;
  errorEl.style.display = "block";
}
