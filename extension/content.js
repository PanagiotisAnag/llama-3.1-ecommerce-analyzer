function detectSite() {
  const host = window.location.hostname;
  if (host.includes("amazon.")) return "amazon";
  if (host.includes("temu.")) return "temu";
  if (host.includes("aliexpress.")) return "aliexpress";
  if (host.includes("alibaba.")) return "alibaba";
  if (host.includes("ebay.")) return "ebay";
  if (host.includes("walmart.")) return "walmart";
  return "unknown";
}

function scrapeAmazon() {
  const title = document.querySelector("#productTitle")?.innerText?.trim() || "";
  const price = document.querySelector(".a-price-whole")?.innerText?.trim() || "";
  const rating = document.querySelector(".a-icon-alt")?.innerText?.trim() || "";
  const reviewCount = document.querySelector("#acrCustomerReviewText")?.innerText?.trim() || "";

  const features = [];
  document.querySelectorAll("#feature-bullets li span").forEach(el => {
    const text = el.innerText.trim();
    if (text && !text.includes("Make sure this fits")) features.push(text);
  });

  const reviews = { "1_star": [], "3_star": [], "5_star": [] };
  document.querySelectorAll("[data-hook='review']").forEach(el => {
    const starEl = el.querySelector("[data-hook='review-star-rating']") ||
                   el.querySelector("[data-hook='cmps-review-star-rating']");
    const bodyEl = el.querySelector("[data-hook='review-body']");
    if (!starEl || !bodyEl) return;
    const stars = starEl.innerText.trim();
    const body = bodyEl.innerText.trim().substring(0, 300);
    if (stars.startsWith("1")) reviews["1_star"].push(body);
    else if (stars.startsWith("3")) reviews["3_star"].push(body);
    else if (stars.startsWith("5")) reviews["5_star"].push(body);
  });

  return { title, price: price ? `$${price}` : "", rating, reviewCount, features, reviews };
}

function scrapeAliExpress() {
  const title = document.querySelector(".product-title-text")?.innerText?.trim() ||
                document.querySelector("h1")?.innerText?.trim() || "";
  const price = document.querySelector(".product-price-value")?.innerText?.trim() || "";
  const rating = document.querySelector(".overview-rating-average")?.innerText?.trim() || "";
  const reviewCount = document.querySelector(".product-reviewer-reviews")?.innerText?.trim() || "";

  const features = [];
  document.querySelectorAll(".product-props li").forEach(el => {
    const text = el.innerText.trim();
    if (text) features.push(text);
  });

  const reviews = { "1_star": [], "3_star": [], "5_star": [] };
  document.querySelectorAll(".feedback-item").forEach(el => {
    const stars = el.querySelectorAll(".star-on").length;
    const body = el.querySelector(".buyer-feedback")?.innerText?.trim().substring(0, 300) || "";
    if (!body) return;
    if (stars === 1) reviews["1_star"].push(body);
    else if (stars === 3) reviews["3_star"].push(body);
    else if (stars === 5) reviews["5_star"].push(body);
  });

  return { title, price, rating, reviewCount, features, reviews };
}

function scrapeTemu() {
  const title = document.querySelector("h1")?.innerText?.trim() ||
                document.querySelector(".goods-title")?.innerText?.trim() || "";
  const price = document.querySelector(".price-text")?.innerText?.trim() ||
                document.querySelector("[class*='price']")?.innerText?.trim() || "";
  const rating = document.querySelector("[class*='rating-value']")?.innerText?.trim() || "";
  const reviewCount = document.querySelector("[class*='review-count']")?.innerText?.trim() || "";

  const features = [];
  document.querySelectorAll("[class*='goods-detail'] li, [class*='spec'] li").forEach(el => {
    const text = el.innerText.trim();
    if (text) features.push(text);
  });

  const reviews = { "1_star": [], "3_star": [], "5_star": [] };
  document.querySelectorAll("[class*='review-item'], [class*='comment-item']").forEach(el => {
    const stars = el.querySelectorAll("[class*='star-fill'], [class*='star-on']").length;
    const body = el.querySelector("[class*='review-content'], [class*='comment-text']")
                   ?.innerText?.trim().substring(0, 300) || "";
    if (!body) return;
    if (stars === 1) reviews["1_star"].push(body);
    else if (stars === 3) reviews["3_star"].push(body);
    else if (stars === 5) reviews["5_star"].push(body);
  });

  return { title, price, rating, reviewCount, features, reviews };
}

function scrapeEbay() {
  const title = document.querySelector(".x-item-title__mainTitle")?.innerText?.trim() || "";
  const price = document.querySelector(".x-price-primary")?.innerText?.trim() || "";
  const rating = document.querySelector(".reviews-star-rating")?.getAttribute("title") || "";
  const reviewCount = document.querySelector(".reviews-count")?.innerText?.trim() || "";

  const features = [];
  document.querySelectorAll(".ux-layout-section--features dl").forEach(el => {
    const text = el.innerText.trim().replace(/\n/g, ": ");
    if (text) features.push(text);
  });

  const reviews = { "1_star": [], "3_star": [], "5_star": [] };

  return { title, price, rating, reviewCount, features, reviews };
}

function scrapeWalmart() {
  const title = document.querySelector("h1[itemprop='name']")?.innerText?.trim() || "";
  const price = document.querySelector("[itemprop='price']")?.getAttribute("content") || "";
  const rating = document.querySelector(".average-rating")?.innerText?.trim() || "";
  const reviewCount = document.querySelector(".review-count")?.innerText?.trim() || "";

  const features = [];
  document.querySelectorAll(".about-desc li").forEach(el => {
    const text = el.innerText.trim();
    if (text) features.push(text);
  });

  const reviews = { "1_star": [], "3_star": [], "5_star": [] };

  return { title, price: price ? `$${price}` : "", rating, reviewCount, features, reviews };
}

function formatProductData(data, site) {
  const lines = [];
  lines.push(`Product: ${data.title}`);
  lines.push(`Price: ${data.price}`);
  lines.push(`Rating: ${data.rating} (${data.reviewCount})`);
  lines.push(`Source: ${site}`);
  lines.push("");

  if (data.features.length > 0) {
    lines.push("Product Features:");
    data.features.slice(0, 8).forEach(f => lines.push(`- ${f}`));
    lines.push("");
  }

  if (data.reviews["1_star"].length > 0) {
    lines.push("1-Star Reviews:");
    data.reviews["1_star"].slice(0, 5).forEach(r => lines.push(`- "${r}"`));
    lines.push("");
  }

  if (data.reviews["3_star"].length > 0) {
    lines.push("3-Star Reviews:");
    data.reviews["3_star"].slice(0, 5).forEach(r => lines.push(`- "${r}"`));
    lines.push("");
  }

  if (data.reviews["5_star"].length > 0) {
    lines.push("5-Star Reviews:");
    data.reviews["5_star"].slice(0, 3).forEach(r => lines.push(`- "${r}"`));
  }

  return lines.join("\n");
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action !== "scrape") return;

  const site = detectSite();
  let data;

  try {
    if (site === "amazon") data = scrapeAmazon();
    else if (site === "aliexpress") data = scrapeAliExpress();
    else if (site === "temu") data = scrapeTemu();
    else if (site === "ebay") data = scrapeEbay();
    else if (site === "walmart") data = scrapeWalmart();
    else {
      sendResponse({ error: "Unsupported site" });
      return;
    }

    if (!data.title) {
      sendResponse({ error: "Could not extract product title. Make sure you are on a product page." });
      return;
    }

    sendResponse({
      success: true,
      site,
      product_data: formatProductData(data, site),
      title: data.title,
    });
  } catch (e) {
    sendResponse({ error: e.message });
  }
});
