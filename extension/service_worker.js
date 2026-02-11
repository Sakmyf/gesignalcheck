// service_worker.js

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {

  if (request.action === "analyze") {

    fetch("https://gesignalcheck-production-91c9.up.railway.app/v1/verify", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        url: request.url,
        text: request.text,
        page_type: "unknown"
      })
    })
    .then(response => response.json())
    .then(data => sendResponse(data))
    .catch(() => sendResponse({ error: "API connection failed" }));

    return true;
  }

});
