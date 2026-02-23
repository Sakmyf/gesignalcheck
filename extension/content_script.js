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

    // 1️⃣ Priorizar <main> si existe (SPA modernas)
    let container = document.querySelector("main");

    // 2️⃣ Si no existe main, usar body
    if (!container) {
      container = document.body;
    }

    // 3️⃣ Clonar el contenedor principal
    const cloned = container.cloneNode(true);

    // 4️⃣ Remover elementos irrelevantes
    const elementsToRemove = cloned.querySelectorAll(
      "script, style, noscript, svg, img, video, canvas, iframe, header, footer"
    );

    elementsToRemove.forEach(el => el.remove());

    let text = cloned.innerText || "";

    // 5️⃣ Normalizar espacios
    text = text.replace(/\s+/g, " ").trim();

    // 6️⃣ Protección contra textos vacíos
    if (text.length < 200) {
      // Fallback total
      text = (document.body.innerText || "")
        .replace(/\s+/g, " ")
        .trim();
    }

    return text.substring(0, 20000);

  } catch (err) {

    console.warn("⚠ Fallback extracción directa:", err);

    return (document.body.innerText || "")
      .replace(/\s+/g, " ")
      .trim()
      .substring(0, 20000);
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
