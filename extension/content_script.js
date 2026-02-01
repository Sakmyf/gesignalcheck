function getPageText() {
  const root = document.querySelector("article, main") || document.body;
  let text = root ? root.innerText : (document.body?.innerText || "");
  if (text.length > 15000) text = text.slice(0, 15000);
  const title = document.title || "";
  return { text, title };
}

chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg?.type === "GET_TEXT") {
    try { sendResponse(getPageText()); } catch { sendResponse({ text: "", title: document.title || "" }); }
    return true;
  }
});
