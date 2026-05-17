import json
import os
import random

INPUT_FILE  = r"E:\Machine Learning\raw_products_with_reviews.json"
OUTPUT_FILE = r"E:\Machine Learning\ecommerce_marketing_qa.jsonl"

SYSTEM_PROMPT = (
    "You are an expert e-commerce marketing AI specializing in creating high-converting "
    "ad copy for Meta Ads, TikTok, Google, and all major social media platforms. "
    "You help businesses find winning products, craft powerful hooks, headlines, primary text, "
    "and full ad campaigns. You explain marketing concepts clearly and help users understand "
    "strategy, ad angles, and copywriting principles."
)

# ---------------------------------------------------------------------------
# TEMPLATE LIBRARY
# ---------------------------------------------------------------------------

HOOK_TEMPLATES = [
    "Write 5 scroll-stopping hooks for {title} priced at {price}.",
    "Give me 5 TikTok-style hooks for {title} in the {category} category.",
    "Create 5 powerful opening lines for a {category} ad featuring {title}.",
    "What are 5 curiosity-driven hooks I can use to sell {title}?",
    "Write 5 pain-point hooks for {title} targeting buyers who need {category} products.",
]

HOOK_RESPONSE_TEMPLATES = [
    (
        "Here are 5 high-converting hooks for {title}:\n\n"
        "1. \"{hook1}\"\n"
        "2. \"{hook2}\"\n"
        "3. \"{hook3}\"\n"
        "4. \"{hook4}\"\n"
        "5. \"{hook5}\"\n\n"
        "These hooks work by triggering curiosity, addressing pain points directly, "
        "and creating a pattern interrupt that stops the scroll. "
        "Always A/B test at least 3 hooks simultaneously to find your lowest-CPM winner."
    )
]

HEADLINE_TEMPLATES = [
    "Write 5 compelling headlines for {title} in the {category} niche.",
    "Give me 5 Facebook ad headlines for {title} priced at {price}.",
    "Create 5 Google-style headlines for {title}.",
    "What are the best headlines to use for {title}?",
]

HEADLINE_RESPONSE_TEMPLATES = [
    (
        "Here are 5 high-converting headlines for {title}:\n\n"
        "1. \"{h1}\"\n"
        "2. \"{h2}\"\n"
        "3. \"{h3}\"\n"
        "4. \"{h4}\"\n"
        "5. \"{h5}\"\n\n"
        "Strong headlines combine a clear benefit, credibility signal, or urgency. "
        "Test all 5 as separate ad sets to find your winner. "
        "For {category} products, benefit-led and social-proof headlines typically outperform clever wordplay."
    )
]

PRIMARY_TEXT_TEMPLATES = [
    "Write Facebook primary text for {title} priced at {price}.",
    "Create Instagram ad primary text for {title} in the {category} category.",
    "Write a PAS-format primary text for {title}.",
    "Give me primary text for a Meta ad promoting {title}.",
]

PRIMARY_TEXT_RESPONSE_TEMPLATES = [
    (
        "Here is high-converting primary text for {title}:\n\n"
        "---\n"
        "{primary_text}\n"
        "---\n\n"
        "This structure follows: Problem → Agitation → Solution → Proof → Offer → CTA. "
        "It's the most reliable framework for Facebook primary text and works across cold and warm audiences. "
        "Pair with a strong visual creative showing the product in use for best results."
    )
]

FULL_AD_TEMPLATES = [
    "Write a complete Facebook ad (hook + headline + primary text + CTA) for {title}.",
    "Create a full TikTok ad script for {title} in the {category} category.",
    "Write a complete Instagram Reels ad for {title} priced at {price}.",
    "Give me a ready-to-publish Meta ad for {title}.",
]

FULL_AD_RESPONSE_TEMPLATES = [
    (
        "Here is a complete, ready-to-publish ad for {title}:\n\n"
        "---\n"
        "🪝 HOOK:\n\"{hook}\"\n\n"
        "📌 HEADLINE:\n\"{headline}\"\n\n"
        "📝 PRIMARY TEXT:\n{primary_text}\n\n"
        "🎯 CTA: {cta}\n"
        "---\n\n"
        "Strategy notes: Run this as a cold audience ad targeting {category} interests. "
        "Use a product demonstration video or before/after image creative. "
        "Always A/B test the hook line against 2 alternatives to find your lowest-CPM winner."
    )
]

ANGLE_TEMPLATES = [
    "What are the best ad angles for {title} in the {category} category?",
    "Give me 5 unique marketing angles to sell {title}.",
    "How should I position {title} in my ads to maximize conversions?",
    "What angle would you use to sell {title} priced at {price}?",
]

ANGLE_RESPONSE_TEMPLATES = [
    (
        "Here are the top ad angles for {title}:\n\n"
        "1. PAIN ANGLE\n"
        "Lead with the problem your customer is experiencing and position {title} as the immediate fix. "
        "Best for cold audiences who are problem-aware.\n\n"
        "2. TRANSFORMATION ANGLE\n"
        "Show the before/after — what life looks like without vs. with {title}. "
        "Specific, believable results create aspirational desire.\n\n"
        "3. SOCIAL PROOF ANGLE\n"
        "Lead with how many people already love this product. "
        "Herd behavior is a deeply wired human instinct — use it.\n\n"
        "4. VALUE/SAVINGS ANGLE\n"
        "At {price}, show what the customer is saving vs. alternatives. "
        "ROI framing makes the purchase feel financially smart, not impulsive.\n\n"
        "5. IDENTITY ANGLE\n"
        "Speak to who your buyer believes they are. "
        "People buy products that reinforce their self-image in the {category} space.\n\n"
        "Pro tip: Test all 5 angles with separate creatives. The winner is rarely the one you predict."
    )
]


# ---------------------------------------------------------------------------
# CONTENT GENERATORS
# ---------------------------------------------------------------------------

def make_hooks(title, category, price, features=""):
    t = title.lower()
    c = category.lower().replace("_", " ")
    feat = features.split("|")[0].strip() if features else ""
    hooks = [
        f"I didn't believe this {t} would actually work. I was wrong.",
        f"This is the {c} product everyone is talking about right now.",
        f"POV: You finally found the {t} that actually delivers.",
        f"Stop wasting money on {c} products that don't work.",
        f"Why is everyone in {c} obsessing over this {t}?",
    ]
    if feat:
        hooks.append(f"The secret behind this {t}? {feat}.")
    return hooks


def make_headlines(title, category, price, avg_rating=None):
    c = category.replace("_", " ")
    rating_str = f"{avg_rating}★ rated" if avg_rating else "top-rated"
    return [
        f"The {title} Everyone In {c} Is Switching To",
        f"Get {title} — {price} With Free Shipping Today" if price else f"Get {title} — Free Shipping Today",
        f"Discover Why Thousands Love This {rating_str} {title}",
        f"The Best {c} Upgrade You Haven't Tried Yet",
        f"{title} — Trusted, Proven, Loved By Thousands",
    ]


def make_primary_text(title, category, price, features="", description=""):
    c = category.lower().replace("_", " ")
    price_str = f"🔥 Limited time: {price} + Free Shipping today only.\n\n" if price else "🔥 Free Shipping today only.\n\n"

    # Build feature bullets from real features if available
    if features:
        feat_list = [f.strip() for f in features.split("|") if f.strip()][:4]
        bullets = "\n".join(f"✅ {f}" for f in feat_list)
    else:
        bullets = (
            f"✅ Premium quality at an unbeatable price\n"
            f"✅ Loved by thousands of verified customers\n"
            f"✅ Fast shipping — arrives in days\n"
            f"✅ 30-day money-back guarantee — zero risk"
        )

    desc_line = f"{description[:150]}\n\n" if description else ""

    return (
        f"Are you still settling for average {c} products?\n\n"
        f"{desc_line}"
        f"{title} is designed for people who are done compromising.\n\n"
        f"{bullets}\n\n"
        f"{price_str}"
        f"Your best {c} experience starts here. 👇\n"
        f"[Shop Now]"
    )


def make_cta(category):
    ctas = [
        "Shop Now",
        "Get Yours Today",
        "Claim Your Discount",
        "Order Now — Free Shipping",
        "Try It Risk-Free",
    ]
    return random.choice(ctas)


# ---------------------------------------------------------------------------
# Q&A BUILDERS
# ---------------------------------------------------------------------------

def _get_fields(product):
    title    = product.get("title", "this product")
    category = product.get("category", "e-commerce").replace("_", " ")
    price    = str(product.get("price", "")) or "a great price"
    features = product.get("features", "") or ""
    desc     = product.get("description", "") or ""
    avg      = product.get("average_rating")
    return title, category, price, features, desc, avg


def build_hook_qa(product):
    title, category, price, features, desc, avg = _get_fields(product)
    question = random.choice(HOOK_TEMPLATES).format(title=title, category=category, price=price)
    hooks = make_hooks(title, category, price, features)
    answer = random.choice(HOOK_RESPONSE_TEMPLATES).format(
        title=title,
        hook1=hooks[0], hook2=hooks[1], hook3=hooks[2],
        hook4=hooks[3], hook5=hooks[4],
    )
    return _qa(question, answer)


def build_headline_qa(product):
    title, category, price, features, desc, avg = _get_fields(product)
    question = random.choice(HEADLINE_TEMPLATES).format(title=title, category=category, price=price)
    headlines = make_headlines(title, category, price, avg)
    answer = random.choice(HEADLINE_RESPONSE_TEMPLATES).format(
        title=title, category=category,
        h1=headlines[0], h2=headlines[1], h3=headlines[2],
        h4=headlines[3], h5=headlines[4],
    )
    return _qa(question, answer)


def build_primary_text_qa(product):
    title, category, price, features, desc, avg = _get_fields(product)
    question = random.choice(PRIMARY_TEXT_TEMPLATES).format(title=title, category=category, price=price)
    pt = make_primary_text(title, category, price, features, desc)
    answer = random.choice(PRIMARY_TEXT_RESPONSE_TEMPLATES).format(title=title, primary_text=pt)
    return _qa(question, answer)


def build_full_ad_qa(product):
    title, category, price, features, desc, avg = _get_fields(product)
    question = random.choice(FULL_AD_TEMPLATES).format(title=title, category=category, price=price)
    hooks     = make_hooks(title, category, price, features)
    headlines = make_headlines(title, category, price, avg)
    pt        = make_primary_text(title, category, price, features, desc)
    cta       = make_cta(category)
    answer = random.choice(FULL_AD_RESPONSE_TEMPLATES).format(
        title=title, category=category,
        hook=hooks[0], headline=headlines[0],
        primary_text=pt, cta=cta,
    )
    return _qa(question, answer)


def build_angle_qa(product):
    title, category, price, features, desc, avg = _get_fields(product)
    question = random.choice(ANGLE_TEMPLATES).format(title=title, category=category, price=price)
    answer = random.choice(ANGLE_RESPONSE_TEMPLATES).format(title=title, category=category, price=price)
    return _qa(question, answer)


def _qa(question, answer):
    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
            {"role": "assistant", "content": answer},
        ]
    }


QA_BUILDERS = [
    build_hook_qa,
    build_headline_qa,
    build_primary_text_qa,
    build_full_ad_qa,
    build_angle_qa,
]

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def load_products():
    if not os.path.exists(INPUT_FILE):
        print(f"ERROR: {INPUT_FILE} not found. Run temu_scraper.py first.")
        return []
    with open(INPUT_FILE, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def load_existing_qa_count():
    if not os.path.exists(OUTPUT_FILE):
        return 0
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        return sum(1 for line in f if line.strip())


def generate_qa_for_product(product):
    """Generate 3-5 Q&A entries for a single product."""
    num = random.randint(3, 5)
    builders = random.sample(QA_BUILDERS, min(num, len(QA_BUILDERS)))
    results = []
    for builder in builders:
        try:
            results.append(builder(product))
        except Exception as e:
            print(f"  Warning: builder failed for '{product.get('title', '?')}': {e}")
    return results


def main():
    print("=" * 60)
    print("Q&A GENERATOR - Starting")
    print("=" * 60)

    products = load_products()
    if not products:
        return

    print(f"Loaded {len(products)} products from {INPUT_FILE}")

    existing_count = load_existing_qa_count()
    print(f"Existing Q&A entries in {OUTPUT_FILE}: {existing_count}")

    total_generated = 0

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for i, product in enumerate(products):
            title = product.get("title", "unknown")
            qa_list = generate_qa_for_product(product)

            for qa in qa_list:
                f.write(json.dumps(qa, ensure_ascii=False) + "\n")
                total_generated += 1

            if (i + 1) % 50 == 0:
                print(f"  Processed {i+1}/{len(products)} products | Generated {total_generated} Q&A entries so far...")

    final_count = existing_count + total_generated

    print("\n" + "=" * 60)
    print(f"GENERATION COMPLETE")
    print(f"New Q&A generated: {total_generated}")
    print(f"Total Q&A in {OUTPUT_FILE}: {final_count}")
    print("=" * 60)


if __name__ == "__main__":
    main()
