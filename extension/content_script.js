// ======================================================
// SIGNALCHECK CONTENT SCRIPT – PRO STABLE VERSION (FIXED)
// ======================================================

// 🔒 Evitar doble inyección
if (!window.__SignalCheckInjected__) {

  window.__SignalCheckInjected__ = true;

  console.log("🚀 SIGNALCHECK CONTENT SCRIPT ACTIVO");

  // ------------------------------------------------------
  // UTILIDAD: LIMPIAR TEXTO
  // ------------------------------------------------------

  function normalizeText(text) {

    if (!text) return "";

    return text
      .replace(/\s+/g, " ")
      .replace(/\n+/g, " ")
      .replace(/\t+/g, " ")
      .trim();
  }

  // ------------------------------------------------------
  // DETECTAR CONTENEDOR PRINCIPAL
  // ------------------------------------------------------

  function detectMainContainer() {

    const selectors = [
      "article",
      "main",
      "[role='main']",
      ".content",
      "#content",
      ".post",
      ".article"
    ];

    for (const selector of selectors) {

      const el = document.querySelector(selector);

      if (el && el.innerText && el.innerText.length > 200) {
        return el;
      }

    }

    return document.body;

  }

  // ------------------------------------------------------
  // LIMPIAR ELEMENTOS IRRELEVANTES
  // ------------------------------------------------------

  function cleanDOM(container) {

    const cloned = container.cloneNode(true);

    const selectorsToRemove = [
      "script",
      "style",
      "noscript",
      "svg",
      "img",
      "video",
      "canvas",
      "iframe",
      "header",
      "footer",
      "nav",
      "aside",
      "form",
      "button",
      ".advertisement",
      ".ads",
      ".banner",
      ".popup"
    ];

    const elements = cloned.querySelectorAll(selectorsToRemove.join(","));

    elements.forEach(el => el.remove());

    return cloned;

  }

  // ------------------------------------------------------
  // EXTRAER TEXTO LIMPIO
  // ------------------------------------------------------

  function extractCleanText() {

    if (!document.body) return "";

    try {

      const container = detectMainContainer();

      const cleaned = cleanDOM(container);

      let text = cleaned.innerText || "";

      text = normalizeText(text);

      // 🔒 fallback si contenido es muy corto
      if (text.length < 200) {

        text = normalizeText(document.body.innerText || "");

      }

      // limitar tamaño para backend
      return text.substring(0, 20000);

    } catch (err) {

      console.warn("⚠ fallback extracción:", err);

      return normalizeText(document.body.innerText || "").substring(0, 20000);

    }

  }

  // ------------------------------------------------------
  // LISTENER EXTENSION (FIX CLAVE)
  // ------------------------------------------------------

  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {

    // 🔥 FIX: aceptar ambos formatos (popup viejo y nuevo)
    if (!request || (request.action !== "extractText" && request.type !== "GET_PAGE_CONTENT")) {
      return;
    }

    try {

      const cleanText = extractCleanText();

      sendResponse({
        ok: true, // 🔥 IMPORTANTE para popup
        text: cleanText,
        url: window.location.href,
        title: document.title || ""
      });

    } catch (error) {

      console.error("❌ Error extrayendo texto:", error);

      sendResponse({
        ok: false,
        text: "",
        url: window.location.href,
        title: document.title || "",
        error: true
      });

    }

    return true; // 🔥 CRÍTICO para async en Chrome

  });

}