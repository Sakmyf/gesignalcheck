function extractCleanText() {
  if (!document.body) return "";

  const clonedBody = document.body.cloneNode(true);
  const elementsToRemove = clonedBody.querySelectorAll("script, style, noscript");
  elementsToRemove.forEach(el => el.remove());

  const text = clonedBody.innerText || "";
  return text.replace(/\s+/g, " ").trim();
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {

  if (request.action === "extractText") {

    const cleanText = extractCleanText();

    sendResponse({
      text: cleanText.substring(0, 12000),
      url: window.location.href,
      title: document.title || ""
    });
  }

  return true;
});
