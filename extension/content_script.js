// content_script.js — Chenuke v15.32
// Extrae texto útil de páginas, landings, formularios y artículos.
// NO modifica el DOM ni inyecta UI propia.
//
// v15.28: se dejan de extraer atributos técnicos del DOM (name, id, value,
// placeholder) y elementos de formulario ("email", "pass", "lgnjs").
// v15.29: se filtra CÓDIGO CRUDO. textContent de <section>/<li> incluía
// scripts inline embebidos (ej: 'var ba147url="...botmaker...init.js"'),
// que entraban al análisis como "narrativa" y ensuciaban el informe de
// sitios oficiales. Ahora: se saltan nodos dentro de script/style/etc.,
// se prefiere innerText, y pushUnique descarta fragmentos con firma de
// JS/CSS/markup.
// v15.32: EXTRACCIÓN ACOTADA AL ARTÍCULO. Antes se barría TODA la página
// (querySelectorAll sobre todo el body): en un portal de noticias eso
// arrastraba la sidebar ("Más leídas", "Te puede interesar"), el menú y el
// footer — títulos de OTRAS notas (dólar, bitcoin, trading) que no son la
// nota abierta. Una nota de turismo de ~5.400 chars se mandaba como ~12.700,
// y el ruido comercial de esas otras notas disparaba commercial_risk => la
// nota daba "alto" falsamente. Ahora: si la página tiene un contenedor de
// artículo real, se extrae SOLO de ahí; si no (landing, mensaje suelto,
// estafa sin estructura), se cae al barrido completo de siempre para no
// perder cobertura. Además se excluyen zonas de ruido (nav/aside/footer y
// bloques "relacionadas/más leídas") en cualquier caso.

'use strict';

(function () {
  if (window.__chenuke_injected) return;
  window.__chenuke_injected = true;

  const MAX_CHARS = 30000;
  const MIN_USEFUL_LEN = 150;

  const MAIN_SELECTORS = [
    'article', 'main', 'section', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'li', 'td', 'th', 'blockquote', 'figcaption'
  ].join(',');

  // Solo elementos con texto visible para el usuario. NO se incluyen
  // input/textarea/select/option: sus atributos técnicos (name, id, value)
  // son markup de la interfaz, no discurso, y contaminan el análisis.
  const ACTION_SELECTORS = [
    'button', '[role="button"]', 'a', 'label'
  ].join(',');

  const META_SELECTORS = [
    'meta[name="description"]',
    'meta[property="og:title"]',
    'meta[property="og:description"]',
    'meta[name="twitter:title"]',
    'meta[name="twitter:description"]'
  ].join(',');

  // Nodos cuyo texto NUNCA es discurso: código, estilos, plantillas.
  // textContent los incluiría (a diferencia de innerText), metiendo JS
  // crudo como "var ba147url=..." en el análisis. Se descartan a nivel
  // de elemento y de ancestro.
  const NOISE_TAGS = new Set(['SCRIPT', 'STYLE', 'NOSCRIPT', 'TEMPLATE', 'CODE', 'PRE']);

  // v15.32 — Contenedor del ARTÍCULO. Se prueba en orden; el primero que
  // exista y tenga texto sustancial gana. Cubre la mayoría de CMS/diarios.
  const ARTICLE_SELECTORS = [
    '[itemprop="articleBody"]',
    '[class*="article-content"]',   // iprofesional: "board board-article-content"
    '[class*="article-body"]',
    '[class*="article__body"]',
    '[class*="articleBody"]',
    '[class*="entry-content"]',
    '[class*="post-content"]',
    '[class*="nota-cuerpo"]',
    '[class*="cuerpo-nota"]',
    '[class*="nota-contenido"]',
    '[class*="story-body"]',
    '[class*="news-body"]',
    'article',
    'main article',
    'main'
  ];

  // v15.32 — Zonas de RUIDO estructural: nunca son el cuerpo de la nota.
  // Se excluyen tanto en modo artículo como en modo barrido completo.
  const NOISE_CONTAINERS = 'nav, aside, header, footer, form';
  // Bloques de "relacionadas / más leídas / seguinos" por texto de encabezado.
  const NOISE_TEXT_HINTS = [
    'te puede interesar', 'más leídas', 'mas leidas', 'más leído', 'mas leido',
    'lo más visto', 'lo mas visto', 'seguinos', 'seguí leyendo', 'segui leyendo',
    'notas relacionadas', 'también te puede', 'tambien te puede', 'newsletter',
    'suscribite', 'suscríbete', 'suscribete'
  ];

  // ¿El elemento está dentro de una zona de ruido estructural?
  function inNoiseContainer(el) {
    return !!(el.closest && el.closest(NOISE_CONTAINERS));
  }

  // Busca el contenedor del artículo. Devuelve el elemento o null.
  // Exige un mínimo de texto para no quedarse con un <article> decorativo
  // vacío (algunos temas usan <article> para las tarjetas de la sidebar).
  function findArticleRoot() {
    for (const sel of ARTICLE_SELECTORS) {
      let el;
      try { el = document.querySelector(sel); } catch (_) { continue; }
      if (!el) continue;
      const len = (el.innerText || el.textContent || '').trim().length;
      if (len >= 400) return el;
    }
    return null;
  }

  function inNoiseNode(el) {
    let n = el;
    while (n && n !== document.body) {
      if (NOISE_TAGS.has(n.tagName)) return true;
      n = n.parentElement;
    }
    return false;
  }

  // Heurística anti-código: fragmentos con firma de JS/CSS/markup no son
  // texto que el usuario lee. Evita que un <script> sin envolver o un
  // bloque de config se cuele como "narrativa".
  function looksLikeCode(text) {
    if (!text) return false;
    if (/\b(?:var|let|const|function)\s+[\w$]+\s*=/.test(text)) return true;
    if (/https?:\/\/\S+\.(?:js|css)(?:["';)\s]|$)/.test(text)) return true;
    if (/[{};]\s*$/.test(text) && /[:=(]/.test(text)) return true;
    if (/<\/?[a-z][\w-]*[^>]*>/i.test(text)) return true;
    return false;
  }

  function cleanText(value) {
    return String(value || '')
      .replace(/\s+/g, ' ')
      .replace(/\u00a0/g, ' ')
      .trim();
  }

  function pushUnique(parts, seen, value, minLen = 2) {
    const text = cleanText(value);
    if (!text || text.length < minLen) return;
    if (looksLikeCode(text)) return;   // no dejar pasar JS/CSS/markup crudo
    const key = text.toLowerCase();
    if (seen.has(key)) return;
    seen.add(key);
    parts.push(text);
  }

  function extractMetaText(parts, seen) {
    pushUnique(parts, seen, document.title || '', 3);
    document.querySelectorAll(META_SELECTORS).forEach((el) => {
      pushUnique(parts, seen, el.getAttribute('content'), 3);
    });
  }

  function extractMainText(parts, seen) {
    // v15.32 — Si hay un artículo real, se recorre SOLO dentro de él. Así el
    // texto es la nota y nada más (sin sidebar, "más leídas", menú ni footer).
    // Si no hay artículo (landing, mensaje, estafa sin estructura), root es
    // document y se mantiene el barrido completo de siempre.
    const articleRoot = findArticleRoot();
    const root = articleRoot || document;

    root.querySelectorAll(MAIN_SELECTORS).forEach((el) => {
      if (inNoiseNode(el)) return;              // dentro de <script>/<style>/etc.
      if (inNoiseContainer(el)) return;         // dentro de nav/aside/footer/form
      const text = el.innerText || el.textContent || '';
      if (!text) return;
      // Descartar bloques de "relacionadas / más leídas / seguinos" por texto.
      const low = text.toLowerCase();
      if (NOISE_TEXT_HINTS.some((h) => low.startsWith(h))) return;
      // innerText respeta lo renderizado (ignora scripts); textContent NO,
      // por eso solo se cae a textContent si innerText viene realmente vacío
      // Y el resultado no parece código (lo filtra pushUnique igual).
      pushUnique(parts, seen, text, 20);
    });
  }

  function extractActionAndFormText(parts, seen) {
    document.querySelectorAll(ACTION_SELECTORS).forEach((el) => {
      // Solo lo que el usuario efectivamente lee en pantalla (o escucha vía
      // lector de pantalla). Se excluyen a propósito:
      //   - el.name / el.id  → nombres técnicos del DOM ("email", "pass",
      //     "lgnjs"). No son discurso: inflan el largo del texto, disparan
      //     falsos positivos y mandan estructura de formularios de sesión
      //     al backend y a la IA. Fueron la causa de que un análisis de
      //     Facebook incluyera campos de login.
      //   - el.getAttribute('value') → idem para botones.
      pushUnique(parts, seen, el.innerText || el.textContent || '', 2);
      pushUnique(parts, seen, el.getAttribute('aria-label'), 2);
      pushUnique(parts, seen, el.getAttribute('title'), 2);
      pushUnique(parts, seen, el.getAttribute('alt'), 2);
    });
  }

  function extractText() {
    try {
      const parts = [];
      const seen = new Set();
      extractMetaText(parts, seen);
      extractMainText(parts, seen);
      extractActionAndFormText(parts, seen);

      let text = parts.join('\n').replace(/\n{3,}/g, '\n\n').trim();
      if (text.length < MIN_USEFUL_LEN && document.body) {
        text = cleanText(document.body.innerText || document.body.textContent || '');
      }
      return text.slice(0, MAX_CHARS);
    } catch (e) {
      try {
        return cleanText(document.body.innerText || document.body.textContent || '').slice(0, MAX_CHARS);
      } catch (_) {
        return '';
      }
    }
  }

  function detectEcommerce(text, url) {
    const t = (text || '').toLowerCase();
    const u = (url || '').toLowerCase();

    const urlSignals = ['shop', 'store', 'tienda', 'compra', 'cart', 'checkout', 'product', 'oferta', 'catalogo', 'catálogo'];
    const textSignals = ['comprar', 'carrito', 'precio', 'descuento', 'envío', 'checkout', 'agregar al carrito', 'buy now', 'add to cart'];
    const financialSignals = ['trading', 'forex', 'acciones', 'invertir', 'invierta', 'inversión', 'ganar dinero', 'dinero extra', 'segundo ingreso', 'ingresos ilimitados', 'solicitar información', 'registrate ahora', 'regístrate ahora', 'aprende y gana', 'aprendé y ganá'];

    return (
      urlSignals.some((w) => u.includes(w)) ||
      textSignals.some((w) => t.includes(w)) ||
      financialSignals.some((w) => t.includes(w) || u.includes(w))
    );
  }

  chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
    if (msg && msg.type === 'ping') {
      sendResponse({ injected: true });
      return true;
    }
    if (msg && msg.action === 'extractText') {
      try {
        const text = extractText();
        const url = window.location.href;
        const title = document.title || '';
        const is_ecommerce = detectEcommerce(text, url);

        if (!text || text.trim().length < 30) {
          sendResponse({ ok: false, error: 'Texto insuficiente en la página' });
        } else {
          sendResponse({ ok: true, text, url, title, is_ecommerce });
        }
      } catch (e) {
        sendResponse({ ok: false, error: String(e) });
      }
      return true;
    }
  });
})();