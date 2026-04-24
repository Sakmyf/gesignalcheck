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
      "[role='main']", // Fundamental para Facebook y Twitter
      "main",
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
    // 🔥 FIX 1: Jamás clonar el document.body entero en sitios masivos
    if (container === document.body) {
      return null; 
    }

    const cloned = container.cloneNode(true);

    const selectorsToRemove = [
      "script", "style", "noscript", "svg", "img", "video", "canvas", "iframe",
      "header", "footer", "nav", "aside", "form", "button",
      ".advertisement", ".ads", ".banner", ".popup"
    ];

    const elements = cloned.querySelectorAll(selectorsToRemove.join(","));
    elements.forEach(el => el.remove());

    return cloned;
  }

  // ------------------------------------------------------
  // NUEVO: DETECTAR ENTORNO COMERCIAL (FUNNELS / E-COMMERCE)
  // ------------------------------------------------------
  function detectEcommerceContext() {
    const ecomSelectors = [
      'button[name="add-to-cart"]',
      '.add-to-cart',
      'a[href*="checkout"]',
      '.cart-icon',
      '[data-testid="checkout-button"]',
      'a[href*="pay.hotmart.com"]', // Pasarelas conocidas
      '.price-tag'
    ];
    
    // 1. Buscar clases o IDs típicos de comercio
    const hasCommerceElements = ecomSelectors.some(selector => document.querySelector(selector) !== null);
    
    // 2. Buscar intenciones de compra en botones
    const buttons = Array.from(document.querySelectorAll('button, a'));
    const hasBuyText = buttons.some(btn => {
       const text = (btn.textContent || "").toLowerCase();
       return text.includes('comprar ahora') || 
              text.includes('añadir al carrito') || 
              text.includes('inscribirme') ||
              text.includes('comprar');
    });

    return hasCommerceElements || hasBuyText;
  }

  // ------------------------------------------------------
  // EXTRAER TEXTO LIMPIO
  // ------------------------------------------------------
  function extractCleanText() {
    if (!document.body) return "";

    try {
      const container = detectMainContainer();
      const cleaned = cleanDOM(container);

      let text = "";

      if (cleaned) {
        // 🔥 FIX 2: textContent no calcula estilos, no crashea en nodos desconectados
        text = normalizeText(cleaned.textContent || "");
      }

      // 🔒 Fallback seguro: Si no hay texto o se usó document.body
      if (!text || text.length < 200) {
        text = normalizeText(document.body.innerText || "");
      }

      return text.substring(0, 20000);

    } catch (err) {
      console.warn("⚠ fallback extracción:", err);
      return normalizeText(document.body.innerText || "").substring(0, 20000);
    }
  }

  // ------------------------------------------------------
  // LISTENER EXTENSION
  // ------------------------------------------------------
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (!request || (request.action !== "extractText" && request.type !== "GET_PAGE_CONTENT")) {
      return;
    }

    try {
      const cleanText = extractCleanText();
      const isEcommerce = detectEcommerceContext(); // ¡Ejecutamos el radar!

      sendResponse({
        ok: true, 
        text: cleanText,
        url: window.location.href,
        title: document.title || "",
        is_ecommerce: isEcommerce // Se lo pasamos a popup.js
      });

    } catch (error) {
      console.error("❌ Error extrayendo texto:", error);
      sendResponse({
        ok: false,
        text: "",
        url: window.location.href,
        title: document.title || "",
        error: true,
        is_ecommerce: false
      });
    }

    return true; 
  });
}