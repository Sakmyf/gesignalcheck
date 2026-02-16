// ======================================================
// SIGNALCHECK CONTENT SCRIPT – STABLE VERSION
// ======================================================

// 🔒 Evitar doble inyección
if (!window.__SignalCheckInjected__) {

  window.__SignalCheckInjected__ = true;

  console.log("🚀 SIGNALCHECK CONTENT SCRIPT ACTIVO");

  // ------------------------------------------------------
  // EXTRAER TEXTO LIMPIO
  // ------------------------------------------------------
  function extractCleanText() {

    if (!document.body) return "";

    try {

      // Clonar body para no tocar DOM real
      const clonedBody = document.body.cloneNode(true);

      // Remover elementos no relevantes
      const elementsToRemove = clonedBody.querySelectorAll(
        "script, style, noscript, svg, img, video, canvas, iframe"
      );

      elementsToRemove.forEach(el => el.remove());

      let text = clonedBody.innerText || "";

      // Normalizar espacios
      text = text.replace(/\s+/g, " ").trim();

      // Límite defensivo
      return text.substring(0, 15000);

    } catch (err) {

      console.warn("⚠ Fallback extracción directa:", err);

      return (document.body.innerText || "")
        .replace(/\s+/g, " ")
        .trim()
        .substring(0, 15000);
    }
  }

  // ------------------------------------------------------
  // LISTENER ÚNICO
  // ------------------------------------------------------
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {

    if (!request || request.action !== "extractText") {
      return;
    }

    try {

      const cleanText = extractCleanText();

      sendResponse({
        text: cleanText,
        url: window.location.href,
        title: document.title || ""
      });

    } catch (error) {

      console.error("❌ Error extrayendo texto:", error);

      sendResponse({
        text: "",
        url: window.location.href,
        title: document.title || "",
        error: true
      });
    }

    return true; // MV3 safe
  });

}
