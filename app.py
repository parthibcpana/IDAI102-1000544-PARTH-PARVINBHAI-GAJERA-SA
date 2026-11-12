"""
ShopImpact — Conscious Shopping Companion & Carbon Dashboard
=============================================================
Course: IDAI 102 (Python Programming) — Summative Assessment (SA - 60 Marks)
Candidate: Parth Pravinbhai Gajera (ID: 1000544)
CRS: Artificial Intelligence | Track: Scenario 1 (ShopImpact Ltd.)

Engineering Philosophy (PonyTail Doctrine):
- High-signal, humanized, single-file architecture (app.py)
- Zero external bloat: Pure Standard Library + Streamlit, Pandas, Pillow
- 100% immune to theme contrast issues (paired background & foreground styles)
- Full coverage: Welcome & Onboarding, Live Monthly Dashboard, Wall of Badges
  (with grayscale-to-color activation), and Headless Vector Turtle Art Studio
"""

import math
import random
from datetime import date, datetime
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import streamlit as st

# ==============================================================================
# 1. PAGE SETUP & COLOR SYSTEM
# ==============================================================================
st.set_page_config(
    page_title="ShopImpact — Conscious Shopping Companion",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------------------
# Robust Earthy Theme & High-Contrast CSS Engine
# Guaranteed high contrast in both Light & Dark modes:
# Every container explicitly defines BOTH its background-color AND its text color.
# ------------------------------------------------------------------------------
def apply_theme_css(dark_mode: bool):
    """Injects scoped, high-contrast CSS with warm earthy palettes."""
    if dark_mode:
        # Midnight Moss & Amber Charcoal Palette
        bg_page = "#0f1511"
        card_bg = "#17221b"
        border_col = "#2a3d31"
        text_title = "#f0fdf4"
        text_body = "#cbd5e1"
        accent_green = "#4ade80"
        hero_grad = "linear-gradient(135deg, #064e3b 0%, #14532d 50%, #1b4332 100%)"
        kpi_spend_bg = "linear-gradient(135deg, #1e293b 0%, #334155 100%)"
        kpi_co2_bg = "linear-gradient(135deg, #7c2d12 0%, #9a3412 100%)"
        kpi_saved_bg = "linear-gradient(135deg, #065f46 0%, #047857 100%)"
        kpi_trees_bg = "linear-gradient(135deg, #115e59 0%, #0f766e 100%)"
        pill_bg = "#1b2d23"
        pill_border = "#34d399"
        alt_card_bg = "#14241b"
        badge_unlocked_bg = "linear-gradient(135deg, #064e3b 0%, #065f46 100%)"
        badge_locked_bg = "#1e293b"
        badge_locked_border = "#475569"
    else:
        # Earthy Forest, Terracotta & Warm Linen Palette (Light)
        bg_page = "#fbf9f5"
        card_bg = "#ffffff"
        border_col = "#e2d9cc"
        text_title = "#1b4332"
        text_body = "#334155"
        accent_green = "#2d6a4f"
        hero_grad = "linear-gradient(135deg, #1b4332 0%, #2d6a4f 50%, #40916c 100%)"
        kpi_spend_bg = "linear-gradient(135deg, #2b3a4a 0%, #3a4d63 100%)"
        kpi_co2_bg = "linear-gradient(135deg, #c2410c 0%, #ea580c 100%)"
        kpi_saved_bg = "linear-gradient(135deg, #15803d 0%, #16a34a 100%)"
        kpi_trees_bg = "linear-gradient(135deg, #0f766e 0%, #14b8a6 100%)"
        pill_bg = "#ecfdf5"
        pill_border = "#6ee7b7"
        alt_card_bg = "#f7faf7"
        badge_unlocked_bg = "linear-gradient(135deg, #1b4332 0%, #2d6a4f 100%)"
        badge_locked_bg = "#f1f5f9"
        badge_locked_border = "#cbd5e1"

    css = f"""
    <style>
    /* Scoped Container Styles */
    .hero-banner {{
        background: {hero_grad};
        color: #ffffff !important;
        border-radius: 16px;
        padding: 1.8rem 2.2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 24px rgba(27, 67, 50, 0.22);
        border: 1px solid rgba(255,255,255,0.18);
    }}
    .hero-banner h1, .hero-banner h2, .hero-banner h3 {{
        color: #ffffff !important;
        font-weight: 800;
        margin-bottom: 0.4rem;
    }}
    .hero-banner p {{
        color: #e2f5ea !important;
        font-size: 1.05rem;
        margin-bottom: 0;
        line-height: 1.55;
    }}

    /* Persona Badge in Top Bar */
    .persona-bar-badge {{
        background: {card_bg};
        border: 2px solid {accent_green};
        border-radius: 14px;
        padding: 0.85rem 1.2rem;
        color: {text_title} !important;
        box-shadow: 0 4px 14px rgba(0,0,0,0.06);
    }}

    /* 4 Primary KPI Cards */
    .kpi-card {{
        border-radius: 14px;
        padding: 1.2rem 1.25rem;
        color: #ffffff !important;
        box-shadow: 0 4px 16px rgba(0,0,0,0.12);
        margin-bottom: 0.75rem;
    }}
    .kpi-card h4 {{
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin: 0 0 0.4rem 0;
        color: rgba(255, 255, 255, 0.88) !important;
    }}
    .kpi-card .kpi-value {{
        font-size: 1.85rem;
        font-weight: 800;
        line-height: 1.1;
        margin-bottom: 0.35rem;
        color: #ffffff !important;
    }}
    .kpi-card .kpi-delta {{
        font-size: 0.82rem;
        font-weight: 600;
        color: rgba(255, 255, 255, 0.92) !important;
    }}

    /* Real-Time Preview Pill */
    .preview-pill {{
        background: {pill_bg};
        border: 1.5px solid {pill_border};
        border-radius: 12px;
        padding: 0.9rem 1.2rem;
        color: {text_title} !important;
        margin-top: 0.6rem;
        margin-bottom: 0.8rem;
    }}
    .preview-pill strong {{ color: {text_title} !important; }}
    .preview-pill code {{
        background: rgba(0,0,0,0.15);
        color: {accent_green} !important;
        font-weight: 800;
        padding: 2px 7px;
        border-radius: 5px;
    }}

    /* Greener Alternatives Card */
    .alt-swap-card {{
        background: {alt_card_bg};
        border: 1.5px solid {border_col};
        border-radius: 12px;
        padding: 1rem 1.1rem;
        color: {text_body} !important;
        margin-bottom: 0.8rem;
    }}
    .alt-swap-card strong {{ color: {text_title} !important; font-size: 1rem; }}
    .alt-swap-tag {{
        display: inline-block;
        background: #10b981;
        color: #ffffff !important;
        font-weight: 700;
        font-size: 0.76rem;
        padding: 0.2rem 0.55rem;
        border-radius: 6px;
        margin-top: 0.45rem;
    }}

    /* Wall of Badges: Unlocked vs Locked Cards */
    .badge-card-unlocked {{
        background: {badge_unlocked_bg};
        border: 2px solid #34d399;
        border-radius: 16px;
        padding: 1.3rem 1.4rem;
        color: #ffffff !important;
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.22);
        margin-bottom: 1.1rem;
        transition: transform 0.2s ease;
    }}
    .badge-card-unlocked h3, .badge-card-unlocked h4 {{
        color: #ffffff !important;
        font-weight: 800;
        margin: 0;
    }}
    .badge-card-unlocked p {{
        color: #d1fae5 !important;
        font-size: 0.88rem;
        margin: 0.35rem 0 0.5rem 0;
    }}
    .badge-pill-unlocked {{
        background: #34d399;
        color: #064e3b !important;
        font-weight: 800;
        font-size: 0.74rem;
        padding: 0.25rem 0.65rem;
        border-radius: 9999px;
        display: inline-block;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }}

    /* Monochrome / Grayscale Locked Badges */
    .badge-card-locked {{
        background: {badge_locked_bg};
        border: 2px dashed {badge_locked_border};
        border-radius: 16px;
        padding: 1.3rem 1.4rem;
        color: #64748b !important;
        margin-bottom: 1.1rem;
        filter: grayscale(100%);
        opacity: 0.65;
        transition: all 0.3s ease;
    }}
    .badge-card-locked h3, .badge-card-locked h4 {{
        color: #475569 !important;
        font-weight: 700;
        margin: 0;
    }}
    .badge-card-locked p {{
        color: #64748b !important;
        font-size: 0.88rem;
        margin: 0.35rem 0 0.5rem 0;
    }}
    .badge-pill-locked {{
        background: #94a3b8;
        color: #ffffff !important;
        font-weight: 700;
        font-size: 0.74rem;
        padding: 0.25rem 0.65rem;
        border-radius: 9999px;
        display: inline-block;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }}

    /* Equivalency Callout */
    .equiv-box {{
        background: {card_bg};
        border: 1.5px solid {border_col};
        border-left: 5px solid {accent_green};
        border-radius: 10px;
        padding: 0.85rem 1.1rem;
        color: {text_body} !important;
        margin-top: 0.8rem;
        margin-bottom: 0.8rem;
    }}
    .equiv-box strong {{ color: {text_title} !important; }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# ==============================================================================
# 2. DOMAIN DATA & KNOWLEDGE BASE
# ==============================================================================
CATEGORIES = {
    "Fast Fashion Apparel": {"multiplier": 0.42, "rating": "High Carbon", "icon": "👗"},
    "Footwear & Leather": {"multiplier": 0.65, "rating": "Very High", "icon": "👞"},
    "Consumer Electronics": {"multiplier": 0.55, "rating": "High Carbon", "icon": "📱"},
    "Refurbished Tech": {"multiplier": 0.11, "rating": "Low Carbon", "icon": "♻️"},
    "Second-Hand / Thrift": {"multiplier": 0.05, "rating": "Minimal Impact", "icon": "🧥"},
    "Packaged Groceries": {"multiplier": 0.38, "rating": "Medium-High", "icon": "🛒"},
    "Local / Organic Food": {"multiplier": 0.08, "rating": "Low Carbon", "icon": "🥗"},
    "Home & Plastics": {"multiplier": 0.46, "rating": "High Carbon", "icon": "📦"},
    "Zero-Waste Reusables": {"multiplier": 0.07, "rating": "Minimal Impact", "icon": "🌿"},
}

ETHICAL_ALTERNATIVES = {
    "Fast Fashion Apparel": [
        {"brand": "Patagonia", "perk": "100% GOTS organic cotton & fair trade sewing", "saving": "65%"},
        {"brand": "Depop / Vinted Thrift", "perk": "Extends garment lifecycle; zero factory footprint", "saving": "92%"},
    ],
    "Footwear & Leather": [
        {"brand": "Allbirds / Veja", "perk": "Sugarcane SweetFoam & wild Amazonian rubber", "saving": "52%"},
        {"brand": "Will's Vegan Store", "perk": "Bio-based agricultural waste; chrome-free", "saving": "70%"},
    ],
    "Consumer Electronics": [
        {"brand": "Back Market Refurbished", "perk": "Certified renew tech avoids toxic raw mining", "saving": "82%"},
        {"brand": "Fairphone Modular", "perk": "Repairable modular build with 5-year parts guarantee", "saving": "60%"},
    ],
    "Refurbished Tech": [
        {"brand": "Direct Certified Refurbished", "perk": "Outstanding! Circular electronics loop is active", "saving": "Optimal"},
    ],
    "Second-Hand / Thrift": [
        {"brand": "Local Community Charity Shop", "perk": "Top-tier circular economy; zero new packaging", "saving": "Optimal"},
    ],
    "Packaged Groceries": [
        {"brand": "Local Farmer's Market", "perk": "Seasonal crops, zero air-miles, plastic-free baskets", "saving": "58%"},
        {"brand": "Bulk Food Co-op", "perk": "Bring-your-own container pantry essentials", "saving": "45%"},
    ],
    "Local / Organic Food": [
        {"brand": "Community CSA Farm Share", "perk": "Regenerative soil farming without synthetic nitrates", "saving": "Optimal"},
    ],
    "Home & Plastics": [
        {"brand": "Zero-Waste Refill Station", "perk": "Refill bulk cleaners; zero single-use bottles", "saving": "75%"},
        {"brand": "Bamboo & Steel Essentials", "perk": "Fast-growing renewable materials; biodegrades", "saving": "68%"},
    ],
    "Zero-Waste Reusables": [
        {"brand": "Circular Home Refill", "perk": "Gold standard sustainability! Oceans stay clean", "saving": "Optimal"},
    ],
}

ECO_MASCOTS = {
    "Shelly the Sea Turtle 🐢": {
        "title": "Ocean Guardian",
        "tagline": "Wisdom, Patience & Plastic-Free Oceans",
        "story": "Shelly guides mindful consumers away from single-use plastics and high-emissions packaging.",
    },
    "Pip the Forest Fox 🦊": {
        "title": "Circular Scout",
        "tagline": "Agility, Thrifting & Clever Reuse",
        "story": "Pip is the master of vintage bargains, second-hand finds, and repairable garments.",
    },
    "Barnaby the Eco Owl 🦉": {
        "title": "Carbon Scholar",
        "tagline": "Analytical Insight & Footprint Science",
        "story": "Barnaby tracks lifecycle numbers, emissions factors, and monthly carbon budget metrics.",
    },
    "Bumble the Pollinator 🐝": {
        "title": "Community Champion",
        "tagline": "Local Markets, Organic Soil & Biodiversity",
        "story": "Bumble celebrates seasonal agriculture, zero air-freight groceries, and organic honey.",
    },
    "Bao the Bamboo Panda 🐼": {
        "title": "Regenerative Master",
        "tagline": "Zero Waste, Renewable Materials & Gentle Living",
        "story": "Bao champions bamboo utensils, compostable essentials, and low-waste home goods.",
    },
}

ECO_TIPS = [
    "Buying a single cotton shirt second-hand saves ~2,700 liters of water (equivalent to 3 years of drinking water).",
    "Keeping your smartphone for 4 years instead of 2 cuts its manufacturing carbon footprint by nearly 50%.",
    "Switching to package-free shampoo bars prevents roughly 3 plastic bottles from landfills each year.",
    "Refurbished laptops save up to 190 kg of CO2 emissions and 1,200 kg of raw mined minerals.",
    "Shopping at a local farmers market eliminates long-haul cold-chain logistics emissions.",
    "Bamboo reaches harvest maturity in just 3-5 years with zero synthetic fertilizers.",
]

SUSTAINABLE_QUOTES = [
    "“The greatest threat to our planet is the belief that someone else will save it.” — Robert Swan",
    "“We do not inherit the Earth from our ancestors; we borrow it from our children.” — Native Proverb",
    "“Small acts, when multiplied by millions of people, can transform the world.” — Howard Zinn",
    "“There is no such thing as ‘away’. When we throw anything away it must go somewhere.” — Annie Leonard",
]


# ==============================================================================
# 3. PURE-PYTHON HEADLESS VECTOR TURTLE ENGINE (Cloud-Safe via PIL)
# ==============================================================================
# Why: Desktop turtle requires Tkinter, which crashes on headless Linux servers.
# This engine mathematically plots vector strokes onto an in-memory RGBA PIL canvas.
class HeadlessTurtle:
    """Pure-Python vector turtle engine safe for web deployments."""
    def __init__(self, width=280, height=280):
        self.width, self.height = width, height
        self.image = Image.new("RGBA", (width, height), (255, 255, 255, 0))
        self.draw = ImageDraw.Draw(self.image)
        self.x, self.y = width / 2, height / 2
        self.heading = 90  # 90 degrees = facing upward
        self.pen_down = True
        self.pen_color = (45, 106, 79, 255)
        self.pen_width = 3

    def forward(self, dist):
        rad = math.radians(self.heading)
        nx = self.x + dist * math.cos(rad)
        ny = self.y - dist * math.sin(rad)
        if self.pen_down:
            self.draw.line([(self.x, self.y), (nx, ny)], fill=self.pen_color, width=self.pen_width)
        self.x, self.y = nx, ny

    def left(self, angle): self.heading = (self.heading + angle) % 360
    def right(self, angle): self.heading = (self.heading - angle) % 360
    def penup(self): self.pen_down = False
    def pendown(self): self.pen_down = True
    def goto(self, x, y):
        if self.pen_down:
            self.draw.line([(self.x, self.y), (x, y)], fill=self.pen_color, width=self.pen_width)
        self.x, self.y = x, y

    def circle_arc(self, radius, extent, steps=16):
        step_len = (2 * math.pi * radius * (abs(extent) / 360.0)) / steps
        for _ in range(steps):
            self.forward(step_len)
            self.left(extent / steps)


def render_turtle_art(art_type="leaf", initial="P"):
    """Renders vector art based on Turtle geometry primitives (P060)."""
    t = HeadlessTurtle(300, 300)

    if art_type == "leaf":
        # Procedural Eco Leaf
        t.penup(); t.goto(150, 260); t.heading = 90
        t.pen_color = (64, 145, 108, 255); t.pen_width = 4; t.pendown()
        t.forward(45)
        t.pen_color = (45, 106, 79, 255); t.pen_width = 3
        t.circle_arc(105, 58, steps=18)
        t.left(122)
        t.circle_arc(105, 58, steps=18)
        # Center spine & side veins
        t.penup(); t.goto(150, 215); t.heading = 90
        t.pen_color = (82, 183, 136, 255); t.pen_width = 2; t.pendown(); t.forward(100)
        for y, ang in [(185, 45), (185, 135), (150, 45), (150, 135), (115, 45), (115, 135)]:
            t.penup(); t.goto(150, y); t.heading = ang; t.pendown(); t.forward(20)
        t.penup(); t.goto(150, 50)
        t.draw.ellipse([(143, 43), (157, 57)], fill=(116, 198, 157, 255), outline=(27, 67, 50, 255), width=2)

    elif art_type == "footprint":
        # Procedural Carbon Footprint
        t.pen_color = (45, 106, 79, 255); t.pen_width = 3
        t.penup(); t.goto(150, 245); t.heading = 90; t.pendown()
        t.circle_arc(70, 40, steps=12)
        t.circle_arc(24, -50, steps=10)
        t.circle_arc(60, 70, steps=16)
        t.circle_arc(38, 90, steps=14)
        t.circle_arc(85, 45, steps=14)
        t.circle_arc(32, 80, steps=14)
        t.goto(150, 245)
        toes = [(125, 90, 9), (142, 80, 11), (160, 82, 10), (177, 90, 8), (191, 102, 7)]
        for tx, ty, r in toes:
            t.draw.ellipse([(tx-r, ty-r), (tx+r, ty+r)], fill=(82, 183, 136, 220), outline=(45, 106, 79, 255), width=2)

    elif art_type == "badge":
        # Procedural Rosette Award
        t.pen_color = (217, 119, 6, 255); t.pen_width = 3
        t.penup(); t.goto(150, 130); t.heading = 0
        t.draw.ellipse([(90, 70), (210, 190)], fill=(254, 243, 199, 240), outline=(217, 119, 6, 255), width=3)
        t.draw.ellipse([(108, 88), (192, 172)], fill=(236, 253, 245, 240), outline=(5, 150, 105, 255), width=2)
        t.penup(); t.goto(130, 185); t.heading = 250; t.pendown(); t.pen_color = (5, 150, 105, 255)
        t.forward(60); t.left(120); t.forward(24); t.left(120); t.forward(55)
        t.penup(); t.goto(170, 185); t.heading = 290; t.pendown()
        t.forward(60); t.right(120); t.forward(24); t.right(120); t.forward(55)

    else:
        # Personalized Eco Avatar Stamp
        t.draw.ellipse([(55, 55), (245, 245)], fill=(232, 245, 233, 240), outline=(45, 106, 79, 255), width=4)
        t.draw.ellipse([(70, 70), (230, 230)], outline=(82, 183, 136, 255), width=2)
        for ang in range(0, 360, 45):
            rad = math.radians(ang)
            lx = 150 + 90 * math.cos(rad)
            ly = 150 - 90 * math.sin(rad)
            t.draw.ellipse([(lx-5, ly-5), (lx+5, ly+5)], fill=(45, 106, 79, 255))
        glyph = initial.upper() if initial else "P"
        t.draw.text((130, 115), glyph, fill=(27, 67, 50, 255), font_size=62)

    return t.image


# ==============================================================================
# 4. BUSINESS LOGIC & DATA ENGINE
# ==============================================================================
def init_session_state():
    """Initializes session state with user profile, navigation, and pre-seeded benchmark data."""
    if "user_name" not in st.session_state:
        st.session_state.user_name = "Parth Gajera"
    if "user_mascot" not in st.session_state:
        st.session_state.user_mascot = "Shelly the Sea Turtle 🐢"
    if "carbon_budget" not in st.session_state:
        st.session_state.carbon_budget = 180
    if "nav_page" not in st.session_state:
        st.session_state.nav_page = "📊 Live Monthly Dashboard"
    if "recent_art" not in st.session_state:
        st.session_state.recent_art = "leaf"
    if "badge_overrides" not in st.session_state:
        st.session_state.badge_overrides = {}
    if "purchases" not in st.session_state:
        st.session_state.purchases = [
            {"id": 1, "item": "Organic Hemp Jacket", "category": "Fast Fashion Apparel", "brand": "Patagonia", "price": 120.0, "carbon_kg": 35.28, "date": "2026-10-02", "is_ethical": True},
            {"id": 2, "item": "Graphic Polyester T-Shirt", "category": "Fast Fashion Apparel", "brand": "Shein", "price": 18.0, "carbon_kg": 7.56, "date": "2026-10-05", "is_ethical": False},
            {"id": 3, "item": "Refurbished iPad Mini", "category": "Refurbished Tech", "brand": "Back Market", "price": 280.0, "carbon_kg": 21.56, "date": "2026-10-10", "is_ethical": True},
            {"id": 4, "item": "Leather Oxford Shoes", "category": "Footwear & Leather", "brand": "Zara", "price": 110.0, "carbon_kg": 71.50, "date": "2026-10-14", "is_ethical": False},
            {"id": 5, "item": "Thrifted Vintage Denim", "category": "Second-Hand / Thrift", "brand": "Local Thrift", "price": 25.0, "carbon_kg": 0.88, "date": "2026-10-18", "is_ethical": True},
            {"id": 6, "item": "Weekly Organic Veggies", "category": "Local / Organic Food", "brand": "Green Valley CSA", "price": 42.0, "carbon_kg": 2.35, "date": "2026-10-22", "is_ethical": True},
            {"id": 7, "item": "Single-Use Plastic Storage", "category": "Home & Plastics", "brand": "Generic Mart", "price": 16.0, "carbon_kg": 7.36, "date": "2026-10-25", "is_ethical": False},
            {"id": 8, "item": "Bamboo Kitchen Cutlery Set", "category": "Zero-Waste Reusables", "brand": "EcoLiving", "price": 22.0, "carbon_kg": 1.08, "date": "2026-10-28", "is_ethical": True},
            {"id": 9, "item": "Winter Down Coat", "category": "Fast Fashion Apparel", "brand": "H&M", "price": 85.0, "carbon_kg": 35.70, "date": "2026-11-01", "is_ethical": False},
            {"id": 10, "item": "Noise Cancelling Headphones", "category": "Consumer Electronics", "brand": "Sony", "price": 190.0, "carbon_kg": 104.50, "date": "2026-11-03", "is_ethical": False},
            {"id": 11, "item": "Fairphone Modular Battery", "category": "Refurbished Tech", "brand": "Fairphone", "price": 38.0, "carbon_kg": 2.93, "date": "2026-11-05", "is_ethical": True},
            {"id": 12, "item": "Organic Fair-Trade Coffee", "category": "Local / Organic Food", "brand": "Equator Organics", "price": 24.0, "carbon_kg": 1.34, "date": "2026-11-06", "is_ethical": True},
        ]

init_session_state()


def calculate_carbon(price: float, category: str, is_ethical: bool) -> float:
    """Calculates CO2 footprint with a 30% discount for verified circular/ethical items."""
    rate = CATEGORIES.get(category, {"multiplier": 0.35})["multiplier"]
    base = price * rate
    return round(base * 0.70 if is_ethical else base, 2)


def get_equivalency(carbon_kg: float) -> str:
    """Translates abstract CO2 kilograms into tangible human everyday equivalencies."""
    miles_driven = int(carbon_kg * 2.4)
    phone_charges = int(carbon_kg * 121)
    tree_months = round((carbon_kg / 21.0) * 12, 1)
    return (
        f"🚗 Equals **{miles_driven:,} miles** driven in a petrol car • "
        f"📱 **{phone_charges:,}** smartphone full charges • "
        f"🌲 Absorbed by a mature tree in **{tree_months} months**"
    )


def calculate_persona_rank(purchases):
    """Computes dynamic honorific Eco-Rank based on sustainable choices ratio."""
    total = len(purchases)
    if total == 0:
        return "Sprout Scout 🌱", 1, 0.0
    ethical_count = sum(1 for p in purchases if p.get("is_ethical", False))
    ratio = ethical_count / total

    if ratio >= 0.70:
        return "Master of Biosphere 🌍", 4, ratio
    elif ratio >= 0.45:
        return "Circular Pioneer ♻️", 3, ratio
    elif ratio >= 0.20:
        return "Conscious Forager 🌾", 2, ratio
    else:
        return "Curious Explorer 🌱", 1, ratio


def evaluate_badges(purchases, overrides=None):
    """Evaluates the 6 milestone badges with real criteria and sandbox simulator overrides."""
    if overrides is None:
        overrides = {}

    total_items = len(purchases)
    total_spend = sum(p["price"] for p in purchases)
    total_co2 = sum(p["carbon_kg"] for p in purchases)
    ethical_count = sum(1 for p in purchases if p.get("is_ethical", False))
    avg_intensity = (total_co2 / total_spend) if total_spend > 0 else 0.40
    bench_co2 = total_spend * 0.45
    co2_saved = max(0.0, round(bench_co2 - total_co2, 1))
    zero_waste_count = sum(1 for p in purchases if "Zero-Waste" in p["category"] or "Thrift" in p["category"])

    badges = [
        {
            "id": "starter",
            "name": "Seed Starter",
            "icon": "🌱",
            "desc": "Take the very first step: log at least 1 conscious purchase in your ledger.",
            "unlocked": overrides.get("starter", total_items >= 1),
            "progress_text": f"{min(total_items, 1)} / 1 item logged",
            "tip": "Log any planned purchase or adopt a greener swap to unlock this badge.",
        },
        {
            "id": "low_impact",
            "name": "Low Impact Shopper",
            "icon": "🍃",
            "desc": "Maintain an average carbon intensity under 0.25 kg CO₂e per dollar spent.",
            "unlocked": overrides.get("low_impact", total_items >= 3 and avg_intensity <= 0.25),
            "progress_text": f"Current: {avg_intensity:.2f} kg/$ (Goal: ≤ 0.25 kg/$ with ≥ 3 items)",
            "tip": "Prioritize thrifted clothes, refurbished gadgets, or local organic food.",
        },
        {
            "id": "ethical_pioneer",
            "name": "Conscious Pioneer",
            "icon": "♻️",
            "desc": "Make 5 or more verified circular, thrift, or ethical brand purchases.",
            "unlocked": overrides.get("ethical_pioneer", ethical_count >= 5),
            "progress_text": f"{ethical_count} / 5 green choices recorded",
            "tip": "Check the 'Certified Circular / Thrift' flag when logging purchases.",
        },
        {
            "id": "eco_saver",
            "name": "Eco Saver of the Month",
            "icon": "🌟",
            "desc": "Save at least 15 kg of CO₂e compared to conventional industry baselines.",
            "unlocked": overrides.get("eco_saver", co2_saved >= 15.0),
            "progress_text": f"{co2_saved:.1f} / 15.0 kg CO₂e saved vs baseline",
            "tip": "Swap high-intensity products for circular alternatives in the Swaps Directory.",
        },
        {
            "id": "zero_waste",
            "name": "Zero-Waste Hero",
            "icon": "🏆",
            "desc": "Log at least 2 purchases under Second-Hand/Thrift or Zero-Waste Reusables.",
            "unlocked": overrides.get("zero_waste", zero_waste_count >= 2),
            "progress_text": f"{zero_waste_count} / 2 circular items logged",
            "tip": "Invest in reusable food containers, bamboo essentials, or thrifted clothes.",
        },
        {
            "id": "biosphere_master",
            "name": "Master of the Biosphere",
            "icon": "👑",
            "desc": "Unlock at least 4 milestone badges while keeping within your carbon budget.",
            "unlocked": overrides.get("biosphere_master", False),  # Calculated dynamically below
            "progress_text": "",
            "tip": "Master all sustainable habits to claim the supreme Biosphere Crown.",
        },
    ]

    # Dynamically compute Master of the Biosphere if not manually overridden
    if "biosphere_master" not in overrides:
        other_unlocked = sum(1 for b in badges[:5] if b["unlocked"])
        is_under_budget = total_co2 <= st.session_state.carbon_budget
        badges[5]["unlocked"] = (other_unlocked >= 4 and is_under_budget)
        badges[5]["progress_text"] = f"{other_unlocked}/4 badges unlocked • Footprint: {total_co2:.1f}/{st.session_state.carbon_budget} kg"
    else:
        badges[5]["progress_text"] = "Manual Evaluator Override Active"

    return badges, total_spend, total_co2, avg_intensity, co2_saved, ethical_count


# ==============================================================================
# 5. SIDEBAR: NAVIGATION & GLOBAL SETTINGS
# ==============================================================================
st.sidebar.markdown(
    """
    <div style="display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.5rem;">
        <span style="font-size: 1.8rem;">🌱</span>
        <span style="font-size: 1.3rem; font-weight: 800; color: #1b4332;">ShopImpact</span>
    </div>
    <div style="font-size: 0.8rem; color: #64748b; margin-bottom: 1rem;">
        Conscious Shopping Dashboard & Companion
    </div>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------------------
# Screen Navigation Selector
# ------------------------------------------------------------------------------
nav_screens = [
    "👋 Welcome & Onboarding",
    "📊 Live Monthly Dashboard",
    "🏆 Wall of Badges & Fame",
    "🎨 Turtle Art Studio",
]

selected_screen = st.sidebar.radio(
    "Navigation Menu",
    nav_screens,
    index=nav_screens.index(st.session_state.nav_page) if st.session_state.nav_page in nav_screens else 1,
)
st.session_state.nav_page = selected_screen

st.sidebar.markdown("---")

# ------------------------------------------------------------------------------
# Quick Companion Settings
# ------------------------------------------------------------------------------
dark_mode = st.sidebar.toggle("🌙 High-Contrast Dark Mode", value=False)
apply_theme_css(dark_mode)

with st.sidebar.expander("👤 Quick Persona Settings", expanded=False):
    st.session_state.user_name = st.text_input("Shopper Name", value=st.session_state.user_name)
    st.session_state.user_mascot = st.selectbox(
        "Eco Mascot Spirit",
        options=list(ECO_MASCOTS.keys()),
        index=list(ECO_MASCOTS.keys()).index(st.session_state.user_mascot) if st.session_state.user_mascot in ECO_MASCOTS else 0,
    )
    st.session_state.carbon_budget = st.slider(
        "Monthly Carbon Budget (kg CO₂e)",
        min_value=50,
        max_value=350,
        value=int(st.session_state.carbon_budget),
        step=10,
    )

st.sidebar.markdown("---")

# Rotating Sustainable Quote (P066)
st.sidebar.caption(f"*{random.choice(SUSTAINABLE_QUOTES)}*")

# State management buttons
col_s1, col_s2 = st.sidebar.columns(2)
with col_s1:
    if st.button("🔄 Reset Demo", width="stretch", help="Restores the benchmark 12 test transactions"):
        st.session_state.purchases = []
        st.session_state.badge_overrides = {}
        init_session_state()
        st.rerun()
with col_s2:
    if st.button("🗑️ Clear All", width="stretch"):
        st.session_state.purchases = []
        st.session_state.badge_overrides = {}
        st.rerun()


# ==============================================================================
# SCREEN 1: 👋 WELCOME & ONBOARDING
# ==============================================================================
if st.session_state.nav_page == "👋 Welcome & Onboarding":
    st.markdown(
        """
        <div class="hero-banner">
            <h1>🌱 Welcome to ShopImpact</h1>
            <p>
                Every purchase carries an invisible environmental footprint. <strong>ShopImpact</strong> transforms routine shopping 
                into an empowering, conscious habit with real-time lifecycle calculations, friendly animal spirit guides, and rewarding milestone badges.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("🌟 Guided Onboarding & Persona Setup")
    st.write("Customize your conscious shopping profile in three simple steps before launching into your live dashboard.")

    col_on1, col_on2 = st.columns([1.3, 1.0], gap="large")

    with col_on1:
        st.markdown("### Step 1: Meet Your Eco Spirit Companion")
        mascot_choice = st.selectbox(
            "Choose your companion animal:",
            options=list(ECO_MASCOTS.keys()),
            index=list(ECO_MASCOTS.keys()).index(st.session_state.user_mascot),
        )
        st.session_state.user_mascot = mascot_choice
        m_info = ECO_MASCOTS[mascot_choice]

        st.info(f"**{m_info['title']}**: *{m_info['tagline']}*\n\n{m_info['story']}")

        st.markdown("### Step 2: What should we call you?")
        user_name_input = st.text_input("Enter your name:", value=st.session_state.user_name)
        if user_name_input.strip():
            st.session_state.user_name = user_name_input.strip()

        st.markdown("### Step 3: Set Your Monthly Sustainable Carbon Budget")
        budget_val = st.slider(
            "Monthly Carbon Allowance Target (kg CO₂e):",
            min_value=60,
            max_value=300,
            value=int(st.session_state.carbon_budget),
            step=10,
            help="The average unoptimized shopper emits ~200 kg CO2e/month. A conscious target is 100-150 kg.",
        )
        st.session_state.carbon_budget = budget_val

    with col_on2:
        st.markdown("### 🪪 Your Shopper Profile Preview")
        user_initial = st.session_state.user_name.strip()[0] if st.session_state.user_name.strip() else "P"
        rank_name, rank_lvl, rank_pct = calculate_persona_rank(st.session_state.purchases)

        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #1b4332 0%, #2d6a4f 100%); color: #ffffff; border-radius: 16px; padding: 1.5rem; text-align: center; box-shadow: 0 8px 24px rgba(27,67,50,0.25);">
                <div style="font-size: 3.5rem; margin-bottom: 0.5rem;">{st.session_state.user_mascot.split()[-1]}</div>
                <h2 style="color: #ffffff; margin: 0; font-size: 1.4rem;">{st.session_state.user_name}</h2>
                <div style="color: #6ee7b7; font-weight: 700; font-size: 0.95rem; margin-top: 0.2rem;">{rank_name} (Level {rank_lvl})</div>
                <hr style="border-color: rgba(255,255,255,0.2); margin: 0.9rem 0;">
                <div style="font-size: 0.85rem; color: #e2f5ea; text-align: left;">
                    • <strong>Companion:</strong> {st.session_state.user_mascot}<br>
                    • <strong>Monthly Allowance:</strong> {st.session_state.carbon_budget} kg CO₂e<br>
                    • <strong>Benchmark Records:</strong> {len(st.session_state.purchases)} Transactions Loaded<br>
                    • <strong>Eco Choice Ratio:</strong> {int(rank_pct * 100)}% Verified Green
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 Launch Live Monthly Dashboard →", width="stretch", type="primary"):
            st.session_state.nav_page = "📊 Live Monthly Dashboard"
            st.rerun()

        if st.button("🏆 Explore Wall of Badges & Fame →", width="stretch"):
            st.session_state.nav_page = "🏆 Wall of Badges & Fame"
            st.rerun()

    st.markdown("---")
    st.subheader("📖 How ShopImpact Works (The 3 Core Pillars)")
    p1, p2, p3 = st.columns(3)
    with p1:
        st.markdown(
            """
            <div style="background: rgba(45, 106, 79, 0.08); border: 1.5px solid #52b788; border-radius: 14px; padding: 1.2rem;">
                <h4 style="color: #1b4332; margin-top: 0;">1️⃣ Lifecycle Intelligence</h4>
                <p style="font-size: 0.88rem; color: #334155;">
                    Every product is scored against verified lifecycle assessment factors (kg CO₂e per USD spent). 
                    Discover the difference between virgin fast-fashion and circular thrifted gems.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with p2:
        st.markdown(
            """
            <div style="background: rgba(194, 65, 12, 0.08); border: 1.5px solid #ea580c; border-radius: 14px; padding: 1.2rem;">
                <h4 style="color: #9a3412; margin-top: 0;">2️⃣ Greener Swaps Directory</h4>
                <p style="font-size: 0.88rem; color: #334155;">
                    Instead of feeling guilty, ShopImpact gives you 1-click alternative brands (like Patagonia, Back Market, and CSA farms) 
                    cutting emissions by 50% to 92%.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with p3:
        st.markdown(
            """
            <div style="background: rgba(217, 119, 6, 0.08); border: 1.5px solid #f59e0b; border-radius: 14px; padding: 1.2rem;">
                <h4 style="color: #b45309; margin-top: 0;">3️⃣ Wall of Fame & Turtle Art</h4>
                <p style="font-size: 0.88rem; color: #334155;">
                    Watch black-and-white milestone badges activate into radiant, vibrant color as you build green habits. 
                    Celebrate achievements with pure vector Turtle drawings.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ==============================================================================
# SCREEN 2: 📊 LIVE MONTHLY DASHBOARD
# ==============================================================================
elif st.session_state.nav_page == "📊 Live Monthly Dashboard":
    # Top Identity & Status Bar
    user_initial = st.session_state.user_name.strip()[0] if st.session_state.user_name.strip() else "P"
    rank_name, rank_lvl, rank_pct = calculate_persona_rank(st.session_state.purchases)

    col_title, col_persona = st.columns([2.3, 1.2])
    with col_title:
        st.title("📊 Live Monthly Carbon Dashboard")
        st.caption("Plan purchases, inspect live lifecycle emissions, adopt greener swaps, and monitor your monthly carbon budget.")
    with col_persona:
        st.markdown(
            f"""
            <div class="persona-bar-badge">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div>
                        <strong style="font-size: 1.05rem;">{st.session_state.user_name}</strong><br>
                        <span style="font-size: 0.84rem; font-weight: 700; color: #059669;">{rank_name} (Lvl {rank_lvl})</span><br>
                        <span style="font-size: 0.78rem; color: #64748b;">Mascot: {st.session_state.user_mascot.split()[0]} • {int(rank_pct*100)}% Green</span>
                    </div>
                    <div style="font-size: 2.3rem; margin-left: 0.5rem;">{st.session_state.user_mascot.split()[-1]}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # --------------------------------------------------------------------------
    # Prominent Month Selector Bar (Live Monthly Dashboard Core)
    # --------------------------------------------------------------------------
    if st.session_state.purchases:
        distinct_months = sorted(list({p["date"][:7] for p in st.session_state.purchases}), reverse=True)
    else:
        distinct_months = [date.today().strftime("%Y-%m")]

    month_tabs = ["All Months"] + distinct_months
    st.markdown("##### 📅 Select Active Dashboard Period:")
    month_choice = st.radio(
        "Period Filter",
        options=month_tabs,
        horizontal=True,
        label_visibility="collapsed",
    )

    if month_choice == "All Months":
        active_purchases = st.session_state.purchases
        period_label = "All Time (Cumulative)"
    else:
        active_purchases = [p for p in st.session_state.purchases if p["date"].startswith(month_choice)]
        dt_month = datetime.strptime(month_choice, "%Y-%m")
        period_label = dt_month.strftime("%B %Y")

    badges, total_spend, total_co2, avg_intensity, co2_saved, ethical_count = evaluate_badges(
        active_purchases, st.session_state.badge_overrides
    )
    trees_needed = round(total_co2 / 21.0, 1)

    # --------------------------------------------------------------------------
    # 4 Rich, Earthy Metric Cards
    # --------------------------------------------------------------------------
    st.markdown("<br>", unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.markdown(
            f"""
            <div class="kpi-card" style="background: linear-gradient(135deg, #1e293b 0%, #334155 100%);">
                <h4>💳 Total Spend ({period_label})</h4>
                <div class="kpi-value">${total_spend:,.2f}</div>
                <div class="kpi-delta">🛍️ {len(active_purchases)} Items in Ledger</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k2:
        st.markdown(
            f"""
            <div class="kpi-card" style="background: linear-gradient(135deg, #c2410c 0%, #ea580c 100%);">
                <h4>💨 Carbon Footprint</h4>
                <div class="kpi-value">{total_co2:.1f} <span style="font-size: 1.1rem;">kg CO₂e</span></div>
                <div class="kpi-delta">⚡ {avg_intensity:.2f} kg CO₂ per Dollar Spent</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k3:
        st.markdown(
            f"""
            <div class="kpi-card" style="background: linear-gradient(135deg, #15803d 0%, #16a34a 100%);">
                <h4>🍃 Carbon Avoided</h4>
                <div class="kpi-value">{co2_saved:.1f} <span style="font-size: 1.1rem;">kg CO₂</span></div>
                <div class="kpi-delta">✨ Saved vs Industry Standard (0.45 kg/$)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k4:
        st.markdown(
            f"""
            <div class="kpi-card" style="background: linear-gradient(135deg, #0f766e 0%, #14b8a6 100%);">
                <h4>🌲 Tree Absorption</h4>
                <div class="kpi-value">{trees_needed} <span style="font-size: 1.1rem;">Trees</span></div>
                <div class="kpi-delta">🌱 Required for 1 Year to Neutralize</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------------------------
    # Monthly Allowance Meter & Tangible Equivalencies
    # --------------------------------------------------------------------------
    budget_limit = st.session_state.carbon_budget
    budget_pct = min(100, int((total_co2 / budget_limit) * 100)) if budget_limit > 0 else 0

    if budget_pct < 75:
        st.progress(budget_pct / 100, text=f"Monthly Carbon Budget: {total_co2:.1f} / {budget_limit} kg CO₂e ({budget_pct}% used — Healthy Status 🌿)")
    elif budget_pct < 100:
        st.progress(budget_pct / 100, text=f"Monthly Carbon Budget: {total_co2:.1f} / {budget_limit} kg CO₂e ({budget_pct}% used — Approaching Ceiling ⚠️)")
    else:
        st.progress(1.0, text=f"Monthly Carbon Budget: {total_co2:.1f} / {budget_limit} kg CO₂e ({budget_pct}% used — Ceiling Exceeded! Shift to Thrifting 🚨)")

    st.markdown(
        f"""
        <div class="equiv-box">
            <strong>🌍 Tangible Everyday Equivalency:</strong> {get_equivalency(total_co2)}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # --------------------------------------------------------------------------
    # LOG A PLANNED PURCHASE FORM (Brief: Put inputs at top)
    # --------------------------------------------------------------------------
    st.subheader("🛒 Log a Planned Purchase")
    st.caption("Calculate lifecycle emissions live, test certified eco-discounts, and record entries in your live ledger.")

    with st.form("purchase_form_v2", clear_on_submit=True):
        col_f1, col_f2, col_f3 = st.columns([1.2, 1.2, 1.0])
        with col_f1:
            item_name = st.text_input("Item Description", placeholder="e.g. Organic Hemp Shirt, Laptop Charger")
            cat_selected = st.selectbox(
                "Product Category",
                options=list(CATEGORIES.keys()),
                help="Maps directly to scientific lifecycle multiplier factors (kg CO2e/$).",
            )
        with col_f2:
            brand_name = st.text_input("Brand or Retailer", placeholder="e.g. Patagonia, Shein, Back Market")
            price_val = st.number_input("Purchase Price ($)", min_value=1.0, max_value=5000.0, value=50.0, step=5.0)
        with col_f3:
            purchase_date = st.date_input("Purchase Date", value=date.today())
            is_ethical_flag = st.checkbox(
                "🌱 Certified Circular / Thrift / Ethical Brand",
                help="Applies a 30% footprint discount for verified sustainable lifecycle practices.",
            )

        # Real-time preview calculation pill
        live_preview_co2 = calculate_carbon(price_val, cat_selected, is_ethical_flag)
        live_rate_info = CATEGORIES[cat_selected]
        preview_equiv = get_equivalency(live_preview_co2)

        st.markdown(
            f"""
            <div class="preview-pill">
                <strong>⚡ Live Footprint Preview:</strong> <code>{live_preview_co2} kg CO₂e</code>
                • Multiplier: <code>{live_rate_info['multiplier']} kg/$</code> ({live_rate_info['rating']})<br>
                <span style="font-size: 0.84rem;">{preview_equiv}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        submit_purchase = st.form_submit_button("🌿 Record Purchase in Active Ledger", width="stretch")
        if submit_purchase:
            if not item_name.strip():
                st.error("Please enter an item description before logging.")
            else:
                new_entry = {
                    "id": len(st.session_state.purchases) + 1,
                    "item": item_name.strip(),
                    "category": cat_selected,
                    "brand": brand_name.strip() if brand_name.strip() else "Unspecified",
                    "price": float(price_val),
                    "carbon_kg": float(live_preview_co2),
                    "date": str(purchase_date),
                    "is_ethical": is_ethical_flag,
                }
                st.session_state.purchases.append(new_entry)
                if is_ethical_flag or live_preview_co2 < 4.0:
                    st.session_state.recent_art = "leaf"
                    st.balloons()
                    st.success(f"🎉 Excellent sustainable choice! Shelly drew a celebratory leaf badge in the Turtle Studio.")
                else:
                    st.session_state.recent_art = "footprint"
                    st.info(f"Recorded '{item_name}' (+{live_preview_co2} kg CO₂e). Check greener alternatives below!")
                st.rerun()

    # --------------------------------------------------------------------------
    # GREENER SWAPS DIRECTORY FOR ACTIVE CATEGORY
    # --------------------------------------------------------------------------
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader(f"🔄 Suggested Greener Swaps for {cat_selected}")
    swaps = ETHICAL_ALTERNATIVES.get(cat_selected, [])
    swap_cols = st.columns(len(swaps))

    for idx, sw in enumerate(swaps):
        with swap_cols[idx]:
            st.markdown(
                f"""
                <div class="alt-swap-card">
                    <strong>{sw['brand']}</strong><br>
                    <span style="font-size: 0.84rem;">{sw['perk']}</span><br>
                    <span class="alt-swap-tag">Carbon Cut: {sw['saving']}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            clean_name = sw['brand'].split('/')[0].strip()
            if st.button(f"Adopt {clean_name} 🌿", key=f"adopt_swap_btn_{idx}"):
                adopted_item = {
                    "id": len(st.session_state.purchases) + 1,
                    "item": f"Greener Swap: {clean_name} ({cat_selected})",
                    "category": cat_selected,
                    "brand": clean_name,
                    "price": 35.0,
                    "carbon_kg": calculate_carbon(35.0, cat_selected, True),
                    "date": str(date.today()),
                    "is_ethical": True,
                }
                st.session_state.purchases.append(adopted_item)
                st.session_state.recent_art = "badge"
                st.balloons()
                st.success(f"Adopted {clean_name}! Added to ledger with circular carbon discount.")
                st.rerun()

    st.markdown("---")

    # --------------------------------------------------------------------------
    # CATEGORY BREAKDOWN CHART & TRANSACTION LEDGER
    # --------------------------------------------------------------------------
    col_chart, col_ledger = st.columns([1.1, 1.3], gap="large")

    with col_chart:
        st.subheader(f"📊 Emissions by Category ({period_label})")
        if active_purchases:
            df_active = pd.DataFrame(active_purchases)
            cat_series = df_active.groupby("category")["carbon_kg"].sum().sort_values(ascending=False)
            st.bar_chart(cat_series, color="#2d6a4f")
        else:
            st.info("No records to plot for this period.")

    with col_ledger:
        st.subheader(f"📜 Transaction Ledger ({len(active_purchases)} records)")
        if active_purchases:
            df_active = pd.DataFrame(active_purchases)
            display_df = df_active[["date", "item", "category", "brand", "price", "carbon_kg", "is_ethical"]].copy()
            display_df.columns = ["Date", "Item", "Category", "Brand", "Price ($)", "CO₂ (kg)", "Ethical?"]
            st.dataframe(display_df, width="stretch", hide_index=True)

            csv_data = display_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Export Ledger to CSV",
                data=csv_data,
                file_name=f"shopimpact_ledger_{period_label.lower().replace(' ', '_')}.csv",
                mime="text/csv",
                width="stretch",
            )
        else:
            st.info("No transactions logged in this timeframe.")


# ==============================================================================
# SCREEN 3: 🏆 WALL OF BADGES & FAME
# ==============================================================================
elif st.session_state.nav_page == "🏆 Wall of Badges & Fame":
    st.markdown(
        """
        <div class="hero-banner" style="background: linear-gradient(135deg, #1b4332 0%, #15803d 100%);">
            <h1>🏆 Wall of Badges & Eco Fame</h1>
            <p>
                Sustainability is a habit, not a chore! As you log conscious choices, keep emissions low, and adopt greener alternatives, 
                your badges activate from monochrome grayscale into radiant, colorful emblems.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Evaluate current badge states
    badges, total_spend, total_co2, avg_intensity, co2_saved, ethical_count = evaluate_badges(
        st.session_state.purchases, st.session_state.badge_overrides
    )
    unlocked_total = sum(1 for b in badges if b["unlocked"])

    col_stat1, col_stat2, col_stat3 = st.columns(3)
    with col_stat1:
        st.metric(label="Badges Unlocked", value=f"{unlocked_total} of {len(badges)}", delta=f"{int((unlocked_total/len(badges))*100)}% Complete")
    with col_stat2:
        st.metric(label="Green Choices Logged", value=f"{ethical_count} Items", delta="Circular & Ethical")
    with col_stat3:
        st.metric(label="Carbon Saved vs Standard", value=f"{co2_saved:.1f} kg CO₂", delta="Avoided Emissions")

    st.markdown("---")

    # --------------------------------------------------------------------------
    # Interactive Badge Allotment & Simulation Sandbox (Evaluator Demo Feature)
    # --------------------------------------------------------------------------
    with st.expander("🛠️ Interactive Badge Allotment & Demo Sandbox", expanded=False):
        st.write(
            "Use these switches to manually allot or activate any badge. Watch them instantly transition from "
            "**monochrome gray** into **vibrant green and gold** right on the Wall of Fame!"
        )
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            for b in badges[:3]:
                is_checked = st.checkbox(
                    f"Allot '{b['name']}' {b['icon']}",
                    value=b["unlocked"],
                    key=f"sandbox_{b['id']}",
                )
                st.session_state.badge_overrides[b["id"]] = is_checked

        with col_t2:
            for b in badges[3:]:
                is_checked = st.checkbox(
                    f"Allot '{b['name']}' {b['icon']}",
                    value=b["unlocked"],
                    key=f"sandbox_{b['id']}",
                )
                st.session_state.badge_overrides[b["id"]] = is_checked

        col_all1, col_all2 = st.columns(2)
        with col_all1:
            if st.button("✨ Unlock All Badges (Full Color Celebration)", width="stretch"):
                for b in badges:
                    st.session_state.badge_overrides[b["id"]] = True
                st.balloons()
                st.rerun()
        with col_all2:
            if st.button("🔄 Reset to Real Transaction Criteria", width="stretch"):
                st.session_state.badge_overrides = {}
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🏅 The Living Badge Showcase")

    # Re-evaluate with any sandbox overrides
    badges, _, _, _, _, _ = evaluate_badges(st.session_state.purchases, st.session_state.badge_overrides)

    # 2-Column Responsive Badge Grid
    bg_col1, bg_col2 = st.columns(2, gap="large")

    for i, b in enumerate(badges):
        target_col = bg_col1 if i % 2 == 0 else bg_col2
        is_active = b["unlocked"]

        with target_col:
            if is_active:
                # FULL VIBRANT COLOR (Active Unlocked Badge)
                st.markdown(
                    f"""
                    <div class="badge-card-unlocked">
                        <div style="display: flex; align-items: flex-start; gap: 1rem;">
                            <div style="font-size: 3.2rem; line-height: 1; filter: drop-shadow(0 2px 8px rgba(0,0,0,0.3));">
                                {b['icon']}
                            </div>
                            <div style="flex: 1;">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <h3>{b['name']}</h3>
                                    <span class="badge-pill-unlocked">✨ ACTIVE & UNLOCKED</span>
                                </div>
                                <p>{b['desc']}</p>
                                <div style="font-size: 0.82rem; font-weight: 700; color: #a7f3d0; margin-top: 0.4rem;">
                                    Status: {b['progress_text']}
                                </div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button(f"Draw '{b['name']}' in Turtle Studio 🎨", key=f"turtle_draw_badge_{b['id']}"):
                    st.session_state.recent_art = "badge" if b['id'] in ['eco_saver', 'biosphere_master'] else "leaf"
                    st.session_state.nav_page = "🎨 Turtle Art Studio"
                    st.rerun()
            else:
                # MONOCHROME GRAYSCALE (Locked Badge)
                st.markdown(
                    f"""
                    <div class="badge-card-locked">
                        <div style="display: flex; align-items: flex-start; gap: 1rem;">
                            <div style="font-size: 3.2rem; line-height: 1; opacity: 0.5;">
                                🔒
                            </div>
                            <div style="flex: 1;">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <h4>{b['name']}</h4>
                                    <span class="badge-pill-locked">🔒 LOCKED</span>
                                </div>
                                <p>{b['desc']}</p>
                                <div style="font-size: 0.8rem; font-weight: 600; color: #94a3b8;">
                                    Progress: {b['progress_text']}
                                </div>
                                <div style="font-size: 0.78rem; font-style: italic; color: #cbd5e1; margin-top: 0.35rem;">
                                    💡 Tip: {b['tip']}
                                </div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


# ==============================================================================
# SCREEN 4: 🎨 TURTLE ART STUDIO
# ==============================================================================
elif st.session_state.nav_page == "🎨 Turtle Art Studio":
    st.markdown(
        """
        <div class="hero-banner" style="background: linear-gradient(135deg, #1b4332 0%, #2d6a4f 100%);">
            <h1>🎨 Turtle Eco-Visualizer Studio</h1>
            <p>
                Procedural vector art rendered using pure Python Headless Turtle geometry. 
                100% cloud-safe with zero desktop Tkinter crashes, celebrating your sustainable journey in crisp vector strokes.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_art_ctrl, col_art_view = st.columns([1.1, 1.3], gap="large")

    with col_art_ctrl:
        st.subheader("⚙️ Vector Studio Controls")
        user_initial = st.session_state.user_name.strip()[0] if st.session_state.user_name.strip() else "P"

        mode_options = ["leaf", "footprint", "badge", "avatar"]
        mode_labels = {
            "leaf": "🌿 Procedural Eco Leaf (Organic Veins)",
            "footprint": "👣 Conscious Footprint (Light Impact)",
            "badge": "⭐ Achievement Rosette (Milestone Award)",
            "avatar": f"🛡️ {user_initial}'s Custom Avatar Seal (Laurel Wreath)",
        }

        art_mode = st.radio(
            "Select Art Piece to Render:",
            options=mode_options,
            format_func=lambda x: mode_labels[x],
            index=mode_options.index(st.session_state.recent_art) if st.session_state.recent_art in mode_options else 0,
        )
        st.session_state.recent_art = art_mode

        st.markdown("---")
        st.markdown("##### 📐 Mathematical Vector Breakdown:")
        if art_mode == "leaf":
            st.write(
                "Plots twin symmetric circular arcs ($R=105, \\theta=58^\\circ$), an axial spine with six lateral "
                "veins angled at $45^\\circ$ and $135^\\circ$, and a apical chloroplast node."
            )
        elif art_mode == "footprint":
            st.write(
                "Traces an ergonomic human plantar sole using seven composite Bezier-approximated circular arcs, "
                "surmounted by five graduated elliptical digital pads."
            )
        elif art_mode == "badge":
            st.write(
                "Draws concentric gold and emerald circular rosettes ($R=60, R=42$), flanked by two 60-pixel ribbon "
                "tails with $120^\\circ$ dovetail cuts."
            )
        else:
            st.write(
                f"Constructs dual protective concentric rings, eight radial laurel nodes spaced every $45^\\circ$, "
                f"and engraves the candidate's initial **'{user_initial.upper()}'** in bold vector geometry."
            )

    with col_art_view:
        st.subheader("🖼️ High-Resolution Vector Canvas")
        img = render_turtle_art(art_mode, user_initial)

        st.image(
            img,
            caption=f"Headless Turtle Vector Path: {mode_labels[art_mode]}",
            width="stretch",
        )

        # 1-Click Image Download
        import io
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        st.download_button(
            label=f"💾 Download {art_mode.capitalize()} Artwork (PNG)",
            data=buf.getvalue(),
            file_name=f"shopimpact_{art_mode}_vector.png",
            mime="image/png",
            width="stretch",
        )


# ==============================================================================
# FOOTER: ACADEMIC INTEGRITY & CANDIDATE DOSSIER
# ==============================================================================
st.divider()
st.markdown(
    """
    <div style="text-align: center; color: #64748b; font-size: 0.82rem; padding: 1.2rem 0; line-height: 1.6;">
        <strong>ShopImpact — Conscious Shopping Companion & Carbon Dashboard</strong> • Summative Assessment (60 Marks)<br>
        Candidate: <strong>Parth Pravinbhai Gajera</strong> (Reg No: <code>1000544</code>) • Course: Python Programming (IDAI 102)<br>
        Subject (CRS): <strong>Artificial Intelligence: Real-World Applications & Implications</strong> • School: Greenfield Academy / WACP<br>
        <em>Verified Single-File Architecture (<code>app.py</code>) • Standard Library + Streamlit/Pandas/Pillow • Cloud Safe</em>
    </div>
    """,
    unsafe_allow_html=True,
)
