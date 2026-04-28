import json
import random
import os

INPUT_FILE = r"E:\Machine Learning\raw_reviews.json"
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
    "LOSER": [
        "VERDICT: LOSER\n\nSCORE: {score}/10\n\nRED FLAGS:\n{flags}\n\nMARKET TRUTH:\n{truth}\n\nRECOMMENDATION:\nAvoid. {reason}",
    ],
    "RISKY": [
        "VERDICT: RISKY\n\nSCORE: {score}/10\n\nRED FLAGS:\n{flags}\n\nMARKET TRUTH:\n{truth}\n\nRECOMMENDATION:\nTest with small budget. {reason}",
    ],
    "WINNER": [
        "VERDICT: WINNER\n\nSCORE: {score}/10\n\nRED FLAGS:\n{flags}\n\nMARKET TRUTH:\n{truth}\n\nRECOMMENDATION:\nInvest. {reason}",
    ],
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
]

POSITIVE_FLAGS = [
    "- No significant quality issues reported",
    "- Consistent positive feedback across buyer segments",
    "- Product matches listing description accurately",
]

NEGATIVE_TRUTHS = [
    "Customers consistently report receiving a product that underperforms compared to the listing. The marketing language hides fundamental quality issues that lead to high return rates.",
    "The product fails to deliver on its core promise. Multiple buyers report the same defects, indicating a systemic manufacturing problem rather than isolated incidents.",
    "Real-world performance is significantly below what the listing suggests. The gap between marketing claims and actual experience is a major refund risk.",
]

POSITIVE_TRUTHS = [
    "Customers report that the product delivers on its promises. Satisfaction is consistent across different buyer types, indicating a reliable product with genuine market demand.",
    "The product meets or exceeds buyer expectations. Positive reviews are specific and credible, suggesting authentic satisfaction rather than incentivized reviews.",
]

RISKY_TRUTHS = [
    "Mixed results — some buyers are happy, others report issues. The inconsistency suggests quality control problems that could be addressed with a better supplier.",
    "The product has real appeal but execution is inconsistent. With careful supplier selection and quality checks, this could be a winner.",
]

NEGATIVE_REASONS = [
    "Too many red flags point to a high refund rate. The risk outweighs the potential margin.",
    "The pattern of complaints is too consistent to be ignored. This product will hurt your store's reputation.",
    "Quality issues are fundamental, not cosmetic. A different supplier won't fix this.",
]

POSITIVE_REASONS = [
    "Strong demand signal with low complaint volume. This product has the fundamentals to scale.",
    "Buyer satisfaction is genuine and consistent. High reorder potential makes this a long-term play.",
    "The market is proven and the product delivers. Start with a test order and scale fast.",
]

RISKY_REASONS = [
    "Order a sample batch first. If quality checks pass, this could be profitable.",
    "The upside is real but so is the risk. Negotiate quality standards with your supplier before scaling.",
]


def make_verdict(rating):
    if rating == 1:
        return "LOSER", random.randint(2, 4)
    else:
        return "WINNER", random.randint(7, 9)


def make_flags(verdict):
    if verdict == "LOSER":
        return "\n".join(random.sample(NEGATIVE_FLAGS, k=random.randint(3, 5)))
    elif verdict == "WINNER":
        return "\n".join(random.sample(POSITIVE_FLAGS, k=2))
    else:
        return "\n".join(random.sample(NEGATIVE_FLAGS[:5], k=2))


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


def build_qa(review_entry):
    review = review_entry["review"]
    rating = review_entry["rating"]

    verdict, score = make_verdict(rating)
    flags = make_flags(verdict)
    truth = make_truth(verdict)
    reason = make_reason(verdict)

    question = f"Analyze this product based on the following customer review:\n\n\"{review}\"\n\nIs this worth investing in for dropshipping?"

    answer = random.choice(VERDICT_TEMPLATES[verdict]).format(
        score=score,
        flags=flags,
        truth=truth,
        reason=reason,
    )

    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
            {"role": "assistant", "content": answer},
        ]
    }


def main():
    print("Loading reviews...")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        reviews = json.load(f)

    print(f"Loaded {len(reviews)} reviews")

    total = 0
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for entry in reviews:
            try:
                qa = build_qa(entry)
                f.write(json.dumps(qa, ensure_ascii=False) + "\n")
                total += 1
            except Exception as e:
                print(f"  Warning: {e}")
                continue

    print(f"Done! Generated {total} Q&A entries")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
