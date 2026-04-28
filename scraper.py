import requests
from bs4 import BeautifulSoup
import random
import time

HEADERS_LIST = [
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://www.google.com/",
        "DNT": "1",
    },
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://www.google.com/",
        "DNT": "1",
    },
]


def get_headers():
    return random.choice(HEADERS_LIST)


def detect_site(url: str) -> str:
    url = url.lower()
    if "amazon." in url:
        return "amazon"
    if "temu.com" in url:
        return "temu"
    if "aliexpress.com" in url:
        return "aliexpress"
    if "alibaba.com" in url:
        return "alibaba"
    if "ebay.com" in url:
        return "ebay"
    if "walmart.com" in url:
        return "walmart"
    return "unknown"


def fetch(url: str) -> BeautifulSoup:
    session = requests.Session()
    time.sleep(random.uniform(1.5, 3.0))
    response = session.get(url, headers=get_headers(), timeout=15)
    if response.status_code != 200:
        raise Exception(f"HTTP {response.status_code}")
    return BeautifulSoup(response.text, "html.parser")


def scrape_amazon(url: str) -> dict:
    soup = fetch(url)

    title = ""
    t = soup.find("span", {"id": "productTitle"})
    if t:
        title = t.get_text(strip=True)

    price = ""
    p = soup.find("span", {"class": "a-price-whole"})
    if p:
        fraction = soup.find("span", {"class": "a-price-fraction"})
        price = "$" + p.get_text(strip=True) + (fraction.get_text(strip=True) if fraction else "")

    rating = ""
    r = soup.find("span", {"class": "a-icon-alt"})
    if r:
        rating = r.get_text(strip=True)

    review_count = ""
    rc = soup.find("span", {"id": "acrCustomerReviewText"})
    if rc:
        review_count = rc.get_text(strip=True)

    features = []
    feature_div = soup.find("div", {"id": "feature-bullets"})
    if feature_div:
        for li in feature_div.find_all("li"):
            text = li.get_text(strip=True)
            if text and "Make sure this fits" not in text:
                features.append(text)

    reviews = {"1_star": [], "3_star": [], "5_star": []}
    for review in soup.find_all("div", {"data-hook": "review"}):
        star_span = review.find("i", {"data-hook": "review-star-rating"}) or \
                    review.find("i", {"data-hook": "cmps-review-star-rating"})
        body = review.find("span", {"data-hook": "review-body"})
        if not star_span or not body:
            continue
        star_text = star_span.get_text(strip=True)
        body_text = body.get_text(strip=True)
        if "1.0" in star_text or "1 out" in star_text:
            reviews["1_star"].append(body_text[:300])
        elif "3.0" in star_text or "3 out" in star_text:
            reviews["3_star"].append(body_text[:300])
        elif "5.0" in star_text or "5 out" in star_text:
            reviews["5_star"].append(body_text[:300])

    return {"title": title, "price": price, "rating": rating,
            "review_count": review_count, "features": features, "reviews": reviews}


def scrape_aliexpress(url: str) -> dict:
    soup = fetch(url)

    title = ""
    for sel in [{"class": "product-title-text"}, {"class": "title--wrap--Ms0tQKA"}]:
        t = soup.find("h1", sel) or soup.find("span", sel)
        if t:
            title = t.get_text(strip=True)
            break

    price = ""
    for sel in [{"class": "product-price-value"}, {"class": "price--currentPriceText--"}]:
        p = soup.find("span", sel)
        if p:
            price = p.get_text(strip=True)
            break

    rating = ""
    r = soup.find("span", {"class": "overview-rating-average"})
    if r:
        rating = r.get_text(strip=True) + "/5"

    review_count = ""
    rc = soup.find("span", {"class": "product-reviewer-reviews"})
    if rc:
        review_count = rc.get_text(strip=True)

    features = []
    spec_div = soup.find("div", {"class": "product-props"})
    if spec_div:
        for item in spec_div.find_all("li"):
            text = item.get_text(strip=True)
            if text:
                features.append(text)

    reviews = {"1_star": [], "3_star": [], "5_star": []}
    for review in soup.find_all("div", {"class": "feedback-item"}):
        stars = review.find("span", {"class": "star-view"})
        body = review.find("p", {"class": "buyer-feedback"})
        if not body:
            continue
        body_text = body.get_text(strip=True)
        star_count = len(review.find_all("span", {"class": "star-on"})) if stars else 0
        if star_count == 1:
            reviews["1_star"].append(body_text[:300])
        elif star_count == 3:
            reviews["3_star"].append(body_text[:300])
        elif star_count == 5:
            reviews["5_star"].append(body_text[:300])

    return {"title": title, "price": price, "rating": rating,
            "review_count": review_count, "features": features, "reviews": reviews}


def scrape_ebay(url: str) -> dict:
    soup = fetch(url)

    title = ""
    t = soup.find("h1", {"class": "x-item-title__mainTitle"})
    if t:
        title = t.get_text(strip=True)

    price = ""
    p = soup.find("div", {"class": "x-price-primary"})
    if p:
        price = p.get_text(strip=True)

    rating = ""
    r = soup.find("span", {"class": "reviews-star-rating"})
    if r:
        rating = r.get("title", "")

    review_count = ""
    rc = soup.find("span", {"class": "reviews-count"})
    if rc:
        review_count = rc.get_text(strip=True)

    features = []
    spec_table = soup.find("div", {"class": "ux-layout-section--features"})
    if spec_table:
        for row in spec_table.find_all("dl"):
            text = row.get_text(strip=True, separator=": ")
            if text:
                features.append(text)

    reviews = {"1_star": [], "3_star": [], "5_star": []}
    for review in soup.find_all("div", {"class": "ebay-review-section"}):
        body = review.find("p")
        stars_elem = review.find("div", {"class": "ebay-star-rating"})
        if not body:
            continue
        body_text = body.get_text(strip=True)
        star_count = len(review.find_all("svg", {"class": "icon icon--star-filled"})) if stars_elem else 0
        if star_count == 1:
            reviews["1_star"].append(body_text[:300])
        elif star_count == 3:
            reviews["3_star"].append(body_text[:300])
        elif star_count == 5:
            reviews["5_star"].append(body_text[:300])

    return {"title": title, "price": price, "rating": rating,
            "review_count": review_count, "features": features, "reviews": reviews}


def scrape_walmart(url: str) -> dict:
    soup = fetch(url)

    title = ""
    t = soup.find("h1", {"itemprop": "name"}) or soup.find("h1", {"class": "prod-ProductTitle"})
    if t:
        title = t.get_text(strip=True)

    price = ""
    p = soup.find("span", {"itemprop": "price"}) or soup.find("span", {"class": "price-characteristic"})
    if p:
        price = "$" + p.get("content", p.get_text(strip=True))

    rating = ""
    r = soup.find("span", {"class": "average-rating"})
    if r:
        rating = r.get_text(strip=True) + "/5"

    review_count = ""
    rc = soup.find("span", {"class": "review-count"})
    if rc:
        review_count = rc.get_text(strip=True)

    features = []
    spec_div = soup.find("div", {"class": "about-desc"})
    if spec_div:
        for li in spec_div.find_all("li"):
            text = li.get_text(strip=True)
            if text:
                features.append(text)

    reviews = {"1_star": [], "3_star": [], "5_star": []}
    for review in soup.find_all("div", {"class": "Grid ReviewList-content"}):
        body = review.find("span", {"class": "review-text"})
        rating_elem = review.find("span", {"class": "visuallyhidden"})
        if not body:
            continue
        body_text = body.get_text(strip=True)
        rating_text = rating_elem.get_text(strip=True) if rating_elem else ""
        if "1 out" in rating_text or "1 star" in rating_text:
            reviews["1_star"].append(body_text[:300])
        elif "3 out" in rating_text or "3 star" in rating_text:
            reviews["3_star"].append(body_text[:300])
        elif "5 out" in rating_text or "5 star" in rating_text:
            reviews["5_star"].append(body_text[:300])

    return {"title": title, "price": price, "rating": rating,
            "review_count": review_count, "features": features, "reviews": reviews}


def scrape(url: str) -> dict:
    site = detect_site(url)
    if site == "amazon":
        return scrape_amazon(url)
    elif site == "aliexpress":
        return scrape_aliexpress(url)
    elif site == "ebay":
        return scrape_ebay(url)
    elif site == "walmart":
        return scrape_walmart(url)
    elif site in ("temu", "alibaba"):
        raise Exception(f"{site.capitalize()} blocks automated scraping. Please paste the product data manually.")
    else:
        raise Exception("Unrecognized site. Supported: Amazon, AliExpress, eBay, Walmart.")


def format_for_analysis(data: dict) -> str:
    lines = []
    lines.append(f"Product: {data['title']}")
    lines.append(f"Price: {data['price']}")
    lines.append(f"Rating: {data['rating']} ({data['review_count']})")
    lines.append("")

    if data["features"]:
        lines.append("Product Features:")
        for f in data["features"][:8]:
            lines.append(f"- {f}")
        lines.append("")

    r = data["reviews"]
    if r["1_star"]:
        lines.append("1-Star Reviews (Most Critical):")
        for rev in r["1_star"][:5]:
            lines.append(f'- "{rev}"')
        lines.append("")

    if r["3_star"]:
        lines.append("3-Star Reviews (Mixed):")
        for rev in r["3_star"][:5]:
            lines.append(f'- "{rev}"')
        lines.append("")

    if r["5_star"]:
        lines.append("5-Star Reviews (Positive):")
        for rev in r["5_star"][:3]:
            lines.append(f'- "{rev}"')

    return "\n".join(lines)


MANUAL_TEMPLATE = """
Copy the following info from the product page and paste it below:

  Product: [product name]
  Price: [price]
  Rating: [e.g. 4.2/5, 3847 reviews]

  Features:
  - [feature 1]
  - [feature 2]

  1-Star Reviews:
  - "[review text]"
  - "[review text]"

  3-Star Reviews:
  - "[review text]"
  - "[review text]"

  5-Star Reviews:
  - "[review text]"

Type END on a new line when done.
"""


def manual_paste() -> str:
    print(MANUAL_TEMPLATE)
    lines = []
    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        lines.append(line)
    return "\n".join(lines).strip()
