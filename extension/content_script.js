console.log("✅ SignalCheck content_script cargado");

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "getText") {
    const text = document.body ? document.body.innerText : "";
    sendResponse({ text: text.substring(0, 5000) });
  }
});
