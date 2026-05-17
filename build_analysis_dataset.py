import json
import random

INPUT_FILE  = r"E:\Machine Learning\raw_products_with_reviews.json"
OUTPUT_FILE = r"E:\Machine Learning\product_analysis_qa.jsonl"

SYSTEM_PROMPT = """You are a cynical e-commerce product auditor. Your job is to analyze product specs and customer reviews to determine if a product is worth investing in for dropshipping or white label.

Rules:
- Ignore 5-star reviews that sound like marketing copy
- Focus on 1-star and 3-star reviews — they reveal real problems
- Look for patterns: quality issues, shipping problems, misleading descriptions, high return rates
- Be brutally honest. No sugarcoating.
- Always output your verdict in this exact format:

VERDICT: [WINNER / LOSER / RISKY]

SCORE: [X/10]

RED FLAGS:
- [list real problems found in reviews]

MARKET TRUTH:
[What customers actually experience vs what the listing promises]

RECOMMENDATION:
[Invest / Avoid / Test with small budget — and why]"""

VERDICT_TEMPLATES = {
    "LOSER":  "VERDICT: LOSER\n\nSCORE: {score}/10\n\nRED FLAGS:\n{flags}\n\nMARKET TRUTH:\n{truth}\n\nRECOMMENDATION:\nAvoid. {reason}",
    "RISKY":  "VERDICT: RISKY\n\nSCORE: {score}/10\n\nRED FLAGS:\n{flags}\n\nMARKET TRUTH:\n{truth}\n\nRECOMMENDATION:\nTest with small budget. {reason}",
    "WINNER": "VERDICT: WINNER\n\nSCORE: {score}/10\n\nRED FLAGS:\n{flags}\n\nMARKET TRUTH:\n{truth}\n\nRECOMMENDATION:\nInvest. {reason}",
}

NEGATIVE_FLAGS = [
    "- Quality control issues reported by multiple buyers",
    "- Product stops working within weeks of purchase",
    "- Description misleading — does not match actual product",
    "- High return rate likely due to unmet expectations",
    "- Cheap materials that break easily",
    "- Customer service unresponsive to complaints",
    "- Shipping damage reported frequently",
    "- Battery/motor fails prematurely",
    "- Size/fit significantly off from listing",
    "- Strong chemical smell upon unboxing",
    "- Product arrived damaged or incomplete",
    "- Seller refuses refunds despite defects",
]

POSITIVE_FLAGS = [
    "- No significant quality issues reported",
    "- Consistent positive feedback across buyer segments",
    "- Product matches listing description accurately",
    "- High reorder rate suggesting genuine satisfaction",
    "- Durable build quality confirmed by long-term buyers",
]

RISKY_FLAGS = [
    "- Mixed quality reports — some units fine, others defective",
    "- Inconsistent sizing across batches",
    "- A few complaints about packaging but product intact",
    "- Minor cosmetic issues reported but functionality intact",
]

NEGATIVE_TRUTHS = [
    "Customers consistently report receiving a product that underperforms compared to the listing. The marketing language hides fundamental quality issues that lead to high return rates.",
    "The product fails to deliver on its core promise. Multiple buyers report the same defects, indicating a systemic manufacturing problem rather than isolated incidents.",
    "Real-world performance is significantly below what the listing suggests. The gap between marketing claims and actual experience is a major refund risk.",
    "The listing overpromises and underdelivers. Negative reviews follow a clear pattern pointing to a supplier-level quality problem.",
]

POSITIVE_TRUTHS = [
    "Customers report that the product delivers on its promises. Satisfaction is consistent across different buyer types, indicating a reliable product with genuine market demand.",
    "The product meets or exceeds buyer expectations. Positive reviews are specific and credible, suggesting authentic satisfaction rather than incentivized reviews.",
    "Strong alignment between listing claims and real-world performance. Buyers repeatedly highlight the same benefits, confirming the product's core value proposition.",
]

RISKY_TRUTHS = [
    "Mixed results — some buyers are happy, others report issues. The inconsistency suggests quality control problems that could be addressed with a better supplier.",
    "The product has real appeal but execution is inconsistent. With careful supplier selection and quality checks, this could be a winner.",
    "Demand is clearly there but fulfillment quality is unpredictable. The product works well when made correctly — the challenge is consistency.",
]

NEGATIVE_REASONS = [
    "Too many red flags point to a high refund rate. The risk outweighs the potential margin.",
    "The pattern of complaints is too consistent to be ignored. This product will hurt your store's reputation.",
    "Quality issues are fundamental, not cosmetic. A different supplier won't fix this.",
    "Return rates will eat your margins. The product cannot survive at scale.",
]

POSITIVE_REASONS = [
    "Strong demand signal with low complaint volume. This product has the fundamentals to scale.",
    "Buyer satisfaction is genuine and consistent. High reorder potential makes this a long-term play.",
    "The market is proven and the product delivers. Start with a test order and scale fast.",
    "Low return risk combined with strong repeat purchase signals. This is a reliable catalog staple.",
]

RISKY_REASONS = [
    "Order a sample batch first. If quality checks pass, this could be profitable.",
    "The upside is real but so is the risk. Negotiate quality standards with your supplier before scaling.",
    "Run a small test campaign to validate conversion before committing to large inventory.",
]


def make_verdict(product):
    avg = product.get("average_rating") or 0
    reviews = product.get("reviews", [])
    neg_count = sum(1 for r in reviews if r["rating"] <= 2)
    pos_count = sum(1 for r in reviews if r["rating"] >= 4)

    if avg >= 4.2 and neg_count == 0:
        return "WINNER", random.randint(7, 9)
    elif avg <= 3.0 or neg_count >= 2:
        return "LOSER", random.randint(2, 4)
    else:
        return "RISKY", random.randint(4, 6)


def make_flags(verdict):
    if verdict == "LOSER":
        return "\n".join(random.sample(NEGATIVE_FLAGS, k=random.randint(3, 5)))
    elif verdict == "WINNER":
        return "\n".join(random.sample(POSITIVE_FLAGS, k=random.randint(2, 3)))
    else:
        return "\n".join(random.sample(RISKY_FLAGS, k=2) + random.sample(NEGATIVE_FLAGS[:4], k=1))


def make_truth(verdict):
    if verdict == "LOSER":
        return random.choice(NEGATIVE_TRUTHS)
    elif verdict == "WINNER":
        return random.choice(POSITIVE_TRUTHS)
    else:
        return random.choice(RISKY_TRUTHS)


def make_reason(verdict):
    if verdict == "LOSER":
        return random.choice(NEGATIVE_REASONS)
    elif verdict == "WINNER":
        return random.choice(POSITIVE_REASONS)
    else:
        return random.choice(RISKY_REASONS)


def format_product_input(product):
    parts = []

    title = product.get("title", "").strip()
    if title:
        parts.append(f"PRODUCT: {title}")

    category = product.get("category", "").replace("_", " ")
    if category:
        parts.append(f"CATEGORY: {category}")

    price = product.get("price")
    if price:
        parts.append(f"PRICE: {price}")

    avg = product.get("average_rating")
    rating_num = product.get("rating_number") or 0
    if avg:
        parts.append(f"AVERAGE RATING: {avg}/5 ({rating_num:,} reviews)")

    store = product.get("store", "").strip()
    if store:
        parts.append(f"STORE: {store}")

    description = product.get("description", "").strip()
    if description:
        parts.append(f"\nDESCRIPTION:\n{description}")

    features = product.get("features", "").strip()
    if features:
        parts.append(f"\nFEATURES:\n{features}")

    reviews = product.get("reviews", [])
    if reviews:
        parts.append("\nCUSTOMER REVIEWS:")
        for r in reviews:
            stars = "★" * r["rating"] + "☆" * (5 - r["rating"])
            parts.append(f"[{stars}] {r['text']}")

    return "\n".join(parts)


def build_qa(product):
    verdict, score = make_verdict(product)
    flags  = make_flags(verdict)
    truth  = make_truth(verdict)
    reason = make_reason(verdict)

    product_input = format_product_input(product)
    question = f"Analyze this product listing and its customer reviews. Is it worth investing in for dropshipping?\n\n{product_input}"

    answer = VERDICT_TEMPLATES[verdict].format(
        score=score,
        flags=flags,
        truth=truth,
        reason=reason,
    )

    return {
        "messages": [
            {"role": "system",    "content": SYSTEM_PROMPT},
            {"role": "user",      "content": question},
            {"role": "assistant", "content": answer},
        ]
    }


def main():
    print("Loading products...")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        products = json.load(f)
    print(f"Loaded {len(products):,} products")

    total = 0
    verdicts = {"WINNER": 0, "LOSER": 0, "RISKY": 0}

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for product in products:
            try:
                qa = build_qa(product)
                f.write(json.dumps(qa, ensure_ascii=False) + "\n")
                verdict = qa["messages"][2]["content"].split("\n")[0].replace("VERDICT: ", "")
                verdicts[verdict] = verdicts.get(verdict, 0) + 1
                total += 1
            except Exception as e:
                print(f"  Warning: {e}")
                continue

    print(f"\nDone! Generated {total:,} Q&A entries")
    print(f"  WINNER: {verdicts['WINNER']:,}")
    print(f"  RISKY:  {verdicts['RISKY']:,}")
    print(f"  LOSER:  {verdicts['LOSER']:,}")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
