const API_URL = "http://127.0.0.1:5000";

const btn = document.getElementById("analyze-btn");
const status = document.getElementById("status");
const productTitle = document.getElementById("product-title");
const verdictBox = document.getElementById("verdict-box");
const verdictLabel = document.getElementById("verdict-label");
const scoreLabel = document.getElementById("score-label");
const fullAnalysis = document.getElementById("full-analysis");
const adcopyBox = document.getElementById("adcopy-box");
const adcopyContent = document.getElementById("adcopy-content");
const copyBtn = document.getElementById("copy-btn");
const errorBox = document.getElementById("error-box");
const siteLabel = document.getElementById("site-label");
const serverWarning = document.getElementById("server-warning");

function showError(msg) {
  errorBox.textContent = msg;
  errorBox.style.display = "block";
  verdictBox.style.display = "none";
  adcopyBox.style.display = "none";
  status.textContent = "";
  btn.disabled = false;
}

function setStatus(msg) {
  status.textContent = msg;
}

async function checkServer() {
  try {
    const res = await fetch(`${API_URL}/health`, { signal: AbortSignal.timeout(2000) });
    return res.ok;
  } catch {
    return false;
  }
}

async function fetchAdCopy(productData) {
  try {
    const res = await fetch(`${API_URL}/adcopy`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ product_data: productData }),
      signal: AbortSignal.timeout(120000),
    });

    if (!res.ok) return null;
    const data = await res.json();
    return data.ad_copy || null;
  } catch {
    return null;
  }
}

copyBtn.addEventListener("click", () => {
  const text = adcopyContent.textContent;
  if (!text) return;
  navigator.clipboard.writeText(text).then(() => {
    copyBtn.textContent = "Copied!";
    setTimeout(() => { copyBtn.textContent = "Copy Ad Copy"; }, 2000);
  });
});

async function main() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  const url = tab.url || "";
  let site = "unknown";
  try {
    const host = new URL(url).hostname;
    if (host.includes("amazon.")) site = "Amazon";
    else if (host.includes("temu.")) site = "Temu";
    else if (host.includes("aliexpress.")) site = "AliExpress";
    else if (host.includes("alibaba.")) site = "Alibaba";
    else if (host.includes("ebay.")) site = "eBay";
    else if (host.includes("walmart.")) site = "Walmart";
  } catch {}
  siteLabel.textContent = site !== "unknown" ? site : "Unsupported site";

  const serverOk = await checkServer();
  if (!serverOk) {
    serverWarning.style.display = "block";
    btn.disabled = true;
    return;
  }
}

btn.addEventListener("click", async () => {
  errorBox.style.display = "none";
  verdictBox.style.display = "none";
  adcopyBox.style.display = "none";
  productTitle.style.display = "none";
  btn.disabled = true;
  setStatus("Extracting product data...");

  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  chrome.tabs.sendMessage(tab.id, { action: "scrape" }, async (response) => {
    if (chrome.runtime.lastError || !response) {
      showError("Could not connect to page. Refresh the page and try again.");
      return;
    }

    if (response.error) {
      showError(response.error);
      return;
    }

    productTitle.textContent = response.title;
    productTitle.style.display = "block";
    setStatus("Analyzing with AI (this takes ~30 seconds)...");

    try {
      const res = await fetch(`${API_URL}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ product_data: response.product_data }),
        signal: AbortSignal.timeout(120000),
      });

      if (!res.ok) {
        const err = await res.json();
        showError(err.error || "Server error.");
        return;
      }

      const data = await res.json();

      verdictBox.className = "verdict-box " + data.verdict.toLowerCase();
      verdictLabel.textContent = data.verdict;
      scoreLabel.textContent = `Score: ${data.score}`;
      fullAnalysis.textContent = data.full_analysis;
      verdictBox.style.display = "block";

      if (data.verdict === "WINNER") {
        setStatus("Generating ad copy...");
        const adCopy = await fetchAdCopy(response.product_data);
        if (adCopy) {
          adcopyContent.textContent = adCopy;
          adcopyBox.style.display = "block";
        }
      }

      setStatus("");
      btn.disabled = false;

    } catch (e) {
      if (e.name === "TimeoutError") {
        showError("Analysis timed out. The model is still loading — try again in 30 seconds.");
      } else {
        showError("Could not reach API server. Make sure python api_server.py is running.");
      }
    }
  });
});

main();
