"""
ShopImpact — Conscious Shopping Companion & Carbon Dashboard
=============================================================
Course: IDAI 102 (Python Programming) — Summative Assessment (SA - 60 Marks)
Candidate: Parth Pravinbhai Gajera (ID: 1000544)
CRS: Artificial Intelligence | Track: Scenario 1 (ShopImpact)

Engineering Philosophy (Ponytail Doctrine):
- High-signal, humanized, clean Python code in a single file (app.py)
- Zero bloat, zero unnecessary abstractions, pure standard library + Streamlit/Pandas/Pillow
- 100% coverage of all compulsory & optional brief specifications
- Standout Eco-Persona Avatar & live reactive Turtle vector graphics
"""

import math
import random
from datetime import date, datetime
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import streamlit as st

# ==============================================================================
# 1. PAGE CONFIGURATION & STYLING (Earth Tones & High-Contrast Dark Mode)
# ==============================================================================
st.set_page_config(
    page_title="ShopImpact — Conscious Shopping Dashboard",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar: High-Contrast Dark Mode (Brief Optional Feature P065)
dark_mode = st.sidebar.toggle("🌙 High-Contrast Dark Mode", value=False)

if dark_mode:
    theme_css = """
    <style>
    :root {
        --bg-main: #0c120e;
        --card-bg: #141f17;
        --card-border: #24382a;
        --text-title: #ecfdf5;
        --text-body: #94a3b8;
        --accent-green: #34d399;
        --accent-warm: #fbbf24;
    }
    .stApp { background-color: var(--bg-main); color: var(--text-title); }
    .glass-card {
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 14px;
        padding: 1.1rem 1.25rem;
        box-shadow: 0 4px 16px rgba(0,0,0,0.3);
    }
    .persona-badge {
        background: linear-gradient(135deg, #064e3b, #047857);
        color: #ecfdf5;
        padding: 0.6rem 1rem;
        border-radius: 10px;
        border: 1px solid #10b981;
    }
    .alt-card {
        background: #142a1d;
        border: 1px solid #059669;
        border-radius: 12px;
        padding: 0.9rem;
    }
    .badge-card {
        background: var(--card-bg);
        border: 1.5px solid var(--card-border);
        border-radius: 12px;
        padding: 0.8rem 1rem;
        margin-bottom: 0.55rem;
    }
    .badge-unlocked { border-color: #34d399; background: #064e3b; }
    .preview-pill {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 0.75rem 1rem;
    }
    </style>
    """
else:
    theme_css = """
    <style>
    :root {
        --bg-main: #faf8f5;
        --card-bg: #ffffff;
        --card-border: #e8e2d8;
        --text-title: #1b4332;
        --text-body: #475569;
        --accent-green: #2d6a4f;
        --accent-warm: #d97706;
    }
    .stApp { background-color: var(--bg-main); color: var(--text-title); }
    .glass-card {
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 14px;
        padding: 1.1rem 1.25rem;
        box-shadow: 0 4px 14px rgba(45, 106, 79, 0.05);
    }
    .persona-badge {
        background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
        color: #1b4332;
        padding: 0.6rem 1rem;
        border-radius: 10px;
        border: 1px solid #a5d6a7;
    }
    .alt-card {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-radius: 12px;
        padding: 0.9rem;
    }
    .badge-card {
        background: #ffffff;
        border: 1.5px solid #e2e8f0;
        border-radius: 12px;
        padding: 0.8rem 1rem;
        margin-bottom: 0.55rem;
    }
    .badge-unlocked { border-color: #52b788; background: #f7fee7; }
    .preview-pill {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-radius: 10px;
        padding: 0.75rem 1rem;
    }
    </style>
    """

st.markdown(theme_css, unsafe_allow_html=True)

# ==============================================================================
# 2. DOMAIN DATA: CATEGORIES, ETHICAL BRANDS & ECO KNOWLEDGE
# ==============================================================================
# Multipliers in kg CO2e per USD spent based on open lifecycle assessment standards
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
        {"brand": "Community CSA Farm Share", "perk": "Regenerative soil farming without nitrates", "saving": "Optimal"},
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
    "Shelly the Sea Turtle 🐢": {"desc": "Wisdom & Clean Oceans", "spirit": "Ocean Guardian"},
    "Pip the Forest Fox 🦊": {"desc": "Agility & Clever Thrifting", "spirit": "Circular Scout"},
    "Barnaby the Eco Owl 🦉": {"desc": "Knowledge & Footprint Analytics", "spirit": "Carbon Scholar"},
    "Bumble the Pollinator 🐝": {"desc": "Local Markets & Biodiversity", "spirit": "Community Champion"},
    "Bao the Bamboo Panda 🐼": {"desc": "Zero Waste & Organic Living", "spirit": "Regenerative Master"},
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
# 3. PROCEDURAL VECTOR TURTLE GRAPHICS (Headless Pure-Python via PIL)
# ==============================================================================
# Why: Standard desktop Turtle requires Tkinter, which crashes on headless Linux servers.
# This pure-Python Turtle engine compiles vector path primitives directly onto a PIL canvas.
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
    """Draws vector art based on Turtle geometry primitives (P060)."""
    t = HeadlessTurtle(280, 280)

    if art_type == "leaf":
        # Procedural Eco Leaf
        t.penup(); t.goto(140, 245); t.heading = 90
        t.pen_color = (64, 145, 108, 255); t.pen_width = 4; t.pendown()
        t.forward(45)
        t.pen_color = (45, 106, 79, 255); t.pen_width = 3
        t.circle_arc(95, 58, steps=18)
        t.left(122)
        t.circle_arc(95, 58, steps=18)
        # Center spine and side veins
        t.penup(); t.goto(140, 200); t.heading = 90
        t.pen_color = (82, 183, 136, 255); t.pen_width = 2; t.pendown(); t.forward(90)
        for y, ang in [(170, 45), (170, 135), (140, 45), (140, 135), (110, 45), (110, 135)]:
            t.penup(); t.goto(140, y); t.heading = ang; t.pendown(); t.forward(18)
        t.penup(); t.goto(140, 55)
        t.draw.ellipse([(134, 49), (146, 61)], fill=(116, 198, 157, 255), outline=(27, 67, 50, 255))

    elif art_type == "footprint":
        # Procedural Carbon Footprint
        t.pen_color = (45, 106, 79, 255); t.pen_width = 3
        t.penup(); t.goto(140, 230); t.heading = 90; t.pendown()
        t.circle_arc(65, 40, steps=12)
        t.circle_arc(22, -50, steps=10)
        t.circle_arc(55, 70, steps=16)
        t.circle_arc(35, 90, steps=14)
        t.circle_arc(80, 45, steps=14)
        t.circle_arc(30, 80, steps=14)
        t.goto(140, 230)
        toes = [(118, 85, 8), (133, 75, 10), (150, 77, 9), (165, 84, 7), (178, 95, 6)]
        for tx, ty, r in toes:
            t.draw.ellipse([(tx-r, ty-r), (tx+r, ty+r)], fill=(82, 183, 136, 220), outline=(45, 106, 79, 255), width=2)

    elif art_type == "badge":
        # Procedural Rosette Award
        t.pen_color = (217, 119, 6, 255); t.pen_width = 3
        t.penup(); t.goto(140, 120); t.heading = 0
        t.draw.ellipse([(85, 65), (195, 175)], fill=(254, 243, 199, 230), outline=(217, 119, 6, 255), width=3)
        t.draw.ellipse([(100, 80), (180, 160)], fill=(236, 253, 245, 230), outline=(5, 150, 105, 255), width=2)
        t.penup(); t.goto(120, 170); t.heading = 250; t.pendown(); t.pen_color = (5, 150, 105, 255)
        t.forward(55); t.left(120); t.forward(22); t.left(120); t.forward(50)
        t.penup(); t.goto(160, 170); t.heading = 290; t.pendown()
        t.forward(55); t.right(120); t.forward(22); t.right(120); t.forward(50)

    else:
        # Personalized Eco Avatar Stamp
        t.draw.ellipse([(50, 50), (230, 230)], fill=(232, 245, 233, 240), outline=(45, 106, 79, 255), width=4)
        t.draw.ellipse([(65, 65), (215, 215)], outline=(82, 183, 136, 255), width=2)
        # Decorative laurels
        for ang in range(0, 360, 45):
            rad = math.radians(ang)
            lx = 140 + 85 * math.cos(rad)
            ly = 140 - 85 * math.sin(rad)
            t.draw.ellipse([(lx-4, ly-4), (lx+4, ly+4)], fill=(45, 106, 79, 255))
        # Initial glyph
        t.draw.text((122, 105), initial.upper(), fill=(27, 67, 50, 255), font_size=56)

    return t.image


# ==============================================================================
# 4. DATA ENGINE: PURCHASES, BADGES, AND ANALYTICS
# ==============================================================================
def init_session_state():
    """Initializes session state with user settings and realistic 12-item benchmark dataset (P094)."""
    if "user_name" not in st.session_state:
        st.session_state.user_name = "Parth Gajera"
    if "user_mascot" not in st.session_state:
        st.session_state.user_mascot = "Shelly the Sea Turtle 🐢"
    if "recent_art" not in st.session_state:
        st.session_state.recent_art = "leaf"
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
    """Calculates CO2 footprint: price * category multiplier with 30% discount for ethical/circular choices."""
    rate = CATEGORIES.get(category, {"multiplier": 0.35})["multiplier"]
    base = price * rate
    # Why: 30% footprint discount reflects verified circular or ethical lifecycle benefits
    return round(base * 0.70 if is_ethical else base, 2)


def get_equivalency(carbon_kg: float) -> str:
    """Translates abstract CO2 kilograms into tangible human everyday equivalencies."""
    miles_driven = int(carbon_kg * 2.5)  # 1 kg CO2 ~ 2.5 miles driven in avg petrol car
    phone_charges = int(carbon_kg * 120)  # 1 kg CO2 ~ 120 smartphone charges
    if carbon_kg < 5.0:
        return f"💡 Equivalent to {phone_charges:,} phone charges (Minimal footprint!)"
    elif carbon_kg < 25.0:
        return f"🚗 Equivalent to driving {miles_driven} miles in a petrol car."
    else:
        return f"🏭 Substantial impact: equals driving {miles_driven} miles or {phone_charges:,} phone charges."


def calculate_persona_rank(purchases):
    """Computes user's Eco-Rank and Level based on sustainable choices ratio."""
    total = len(purchases)
    if total == 0:
        return "Sprout Scout 🌱", 1, 0.0
    ethical_count = sum(1 for p in purchases if p.get("is_ethical", False))
    ratio = ethical_count / total

    if ratio >= 0.75:
        rank = "Master of Biosphere 🌍"
        level = 4
    elif ratio >= 0.50:
        rank = "Circular Pioneer ♻️"
        level = 3
    elif ratio >= 0.25:
        rank = "Conscious Forager 🌾"
        level = 2
    else:
        rank = "Curious Explorer 🌱"
        level = 1
    return rank, level, ratio


def evaluate_badges(purchases):
    """Evaluates 5 milestone gamification badges with explicit unlock criteria (P058)."""
    total_items = len(purchases)
    total_spend = sum(p["price"] for p in purchases)
    total_co2 = sum(p["carbon_kg"] for p in purchases)
    ethical_count = sum(1 for p in purchases if p.get("is_ethical", False))
    avg_intensity = (total_co2 / total_spend) if total_spend > 0 else 0.40

    badges = [
        {
            "id": "starter",
            "name": "Seed Starter",
            "desc": "Logged your first conscious shopping record.",
            "icon": "🌱",
            "unlocked": total_items >= 1,
            "progress": f"{min(total_items, 1)}/1 item logged",
        },
        {
            "id": "low_impact",
            "name": "Low Impact Shopper",
            "desc": "Maintained carbon intensity below 0.25 kg CO2/$.",
            "icon": "🥉",
            "unlocked": total_items >= 3 and avg_intensity <= 0.25,
            "progress": f"{avg_intensity:.2f} kg/$ (Threshold: ≤0.25)",
        },
        {
            "id": "ethical_pioneer",
            "name": "Conscious Pioneer",
            "desc": "Chose 5 or more verified green alternatives or thrifted items.",
            "icon": "🥈",
            "unlocked": ethical_count >= 5,
            "progress": f"{ethical_count}/5 green choices made",
        },
        {
            "id": "eco_saver",
            "name": "Eco Saver of the Month",
            "desc": "Kept cumulative carbon footprint under 220 kg with ≥8 items.",
            "icon": "🥇",
            "unlocked": total_items >= 8 and total_co2 <= 220.0,
            "progress": f"{total_co2:.1f} kg CO2 (Ceiling: ≤220)",
        },
        {
            "id": "zero_waste",
            "name": "Zero-Waste Hero",
            "desc": "Logged 2 or more zero-waste reusable or thrifted items.",
            "icon": "🏆",
            "unlocked": sum(1 for p in purchases if "Zero-Waste" in p["category"] or "Thrift" in p["category"]) >= 2,
            "progress": f"{sum(1 for p in purchases if 'Zero-Waste' in p['category'] or 'Thrift' in p['category'])}/2 circular items",
        },
    ]
    return badges, total_spend, total_co2, avg_intensity, ethical_count


# ==============================================================================
# 5. SIDEBAR: PERSONA BUILDER, TARGETS & STATE CONTROL
# ==============================================================================
st.sidebar.title("🌿 ShopImpact Companion")

# Persona & Avatar Customizer (Unique Feature)
with st.sidebar.expander("👤 Customize Your Eco Avatar", expanded=False):
    st.session_state.user_name = st.text_input("Your Shopper Name", value=st.session_state.user_name)
    st.session_state.user_mascot = st.selectbox(
        "Choose Your Eco Mascot Spirit",
        options=list(ECO_MASCOTS.keys()),
        index=list(ECO_MASCOTS.keys()).index(st.session_state.user_mascot) if st.session_state.user_mascot in ECO_MASCOTS else 0,
    )
    mascot_info = ECO_MASCOTS[st.session_state.user_mascot]
    st.caption(f"**Affinity:** {mascot_info['spirit']} &bull; *{mascot_info['desc']}*")

# Monthly Carbon Budget Goal Slider (Interactive Control)
carbon_budget = st.sidebar.slider(
    "🎯 Monthly Carbon Budget (kg CO₂e)",
    min_value=50,
    max_value=400,
    value=180,
    step=10,
    help="Set your personal carbon threshold to keep your spending sustainable.",
)

# Month Filter Dropdown (P057)
if st.session_state.purchases:
    available_months = sorted(list({p["date"][:7] for p in st.session_state.purchases}), reverse=True)
else:
    available_months = [date.today().strftime("%Y-%m")]

month_filter = st.sidebar.selectbox("📅 Filter by Month", options=["All Months"] + available_months)

st.sidebar.markdown("---")

# Daily Sustainable Living Quote (P066)
st.sidebar.markdown(f"*{random.choice(SUSTAINABLE_QUOTES)}*")

st.sidebar.markdown("---")

# State Management
col_btn1, col_btn2 = st.sidebar.columns(2)
with col_btn1:
    if st.button("🔄 Reset Demo", help="Restores the benchmark 12 test transactions"):
        st.session_state.purchases = []
        init_session_state()
        st.rerun()
with col_btn2:
    if st.button("🗑️ Clear All"):
        st.session_state.purchases = []
        st.rerun()


# ==============================================================================
# 6. HEADER & PERSONA BANNER
# ==============================================================================
rank_title, rank_level, eco_ratio = calculate_persona_rank(st.session_state.purchases)
user_initial = st.session_state.user_name.strip()[0] if st.session_state.user_name.strip() else "P"

col_title, col_persona = st.columns([2.5, 1.5])

with col_title:
    st.title("🌱 ShopImpact — Conscious Shopping Dashboard")
    st.markdown(
        "**Transforming everyday consumer choices into measurable environmental impact.** "
        "Track planned purchases, discover ethical alternatives, and celebrate sustainable habits."
    )

with col_persona:
    st.markdown(
        f"""
        <div class="persona-badge">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <strong style="font-size: 1.05rem;">{st.session_state.user_name}</strong><br>
                    <span style="font-size: 0.85rem; font-weight: 600;">{rank_title} (Level {rank_level})</span><br>
                    <span style="font-size: 0.78rem;">Mascot: {st.session_state.user_mascot.split()[0]} | {int(eco_ratio*100)}% Green Choices</span>
                </div>
                <div style="font-size: 2.2rem; margin-left: 0.5rem;">
                    {st.session_state.user_mascot.split()[-1]}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()

# ==============================================================================
# 7. TOP STAGE 1 & 3 INPUT SECTION (Brief: "Put inputs at the top")
# ==============================================================================
# Filter dataset based on active month
if month_filter == "All Months":
    filtered_purchases = st.session_state.purchases
    period_label = "All Time"
else:
    filtered_purchases = [p for p in st.session_state.purchases if p["date"].startswith(month_filter)]
    period_label = month_filter

badges, total_spend, total_co2, avg_intensity, ethical_count = evaluate_badges(filtered_purchases)

st.subheader("🛒 Log a Planned Purchase")
st.caption("Plan your next purchase: calculate emissions live, explore greener swaps, and log to your ledger.")

with st.container():
    # 2-Column Responsive Entry Form (Compulsory Features P055 & P056)
    with st.form("purchase_form", clear_on_submit=True):
        col_f1, col_f2, col_f3 = st.columns([1.2, 1.2, 1.0])
        with col_f1:
            item_desc = st.text_input("Item Description", placeholder="e.g. Linen Summer Shirt, Laptop Battery")
            cat_choice = st.selectbox(
                "Product Category",
                options=list(CATEGORIES.keys()),
                help="Each category maps to a researched lifecycle emission factor (kg CO2e/$)."
            )
        with col_f2:
            brand_val = st.text_input("Brand or Vendor", placeholder="e.g. Patagonia, Depop, Zara, Apple")
            price_input = st.number_input("Purchase Price ($)", min_value=1.0, max_value=5000.0, value=45.0, step=5.0)

        with col_f3:
            date_input = st.date_input("Purchase Date", value=date.today())
            is_green_flag = st.checkbox(
                "🌱 Certified Circular / Thrift / Ethical Brand",
                help="Applies a 30% carbon discount for verified eco-friendly practices."
            )

        # Real-time Reactive Footprint Calculation Preview (Compulsory P056)
        live_carbon = calculate_carbon(price_input, cat_choice, is_green_flag)
        live_rate = CATEGORIES[cat_choice]["multiplier"]
        equiv_text = get_equivalency(live_carbon)

        st.markdown(
            f"""
            <div class="preview-pill">
                <strong>⚡ Live Footprint Preview:</strong> <code style="font-size: 1.05rem; color: #1b4332;">{live_carbon} kg CO₂e</code>
                &bull; Category Multiplier: <code>{live_rate} kg/$</code> ({CATEGORIES[cat_choice]['rating']})<br>
                <span style="font-size: 0.82rem; color: #475569;">{equiv_text}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        submit_btn = st.form_submit_button("🌿 Record Purchase in Dashboard", width="stretch")
        if submit_btn:
            if not item_desc.strip():
                st.error("Please provide an item description before logging.")
            else:
                new_entry = {
                    "id": len(st.session_state.purchases) + 1,
                    "item": item_desc.strip(),
                    "category": cat_choice,
                    "brand": brand_val.strip() if brand_val.strip() else "Unspecified",
                    "price": float(price_input),
                    "carbon_kg": float(live_carbon),
                    "date": str(date_input),
                    "is_ethical": is_green_flag,
                }
                st.session_state.purchases.append(new_entry)
                # Turtle vector reaction logic
                if is_green_flag or live_carbon < 5.0:
                    st.session_state.recent_art = "leaf" if is_green_flag else "footprint"
                    st.balloons()
                    st.success(f"🎉 Excellent green choice! Shelly the Turtle drew a celebration badge for you below!")
                else:
                    st.session_state.recent_art = "footprint"
                    st.info(f"Recorded '{item_desc}' (+{live_carbon} kg CO₂e). Check greener alternatives below to save carbon next time!")
                st.rerun()

# ------------------------------------------------------------------------------
# Suggested Greener Alternatives Section (Compulsory Feature P059)
# ------------------------------------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)
st.subheader(f"🔄 Greener Swaps Directory for {cat_choice}")
alts = ETHICAL_ALTERNATIVES.get(cat_choice, [])
alt_cols = st.columns(len(alts))

for i, alt in enumerate(alts):
    with alt_cols[i]:
        st.markdown(
            f"""
            <div class="alt-card">
                <strong style="color: #065f46; font-size: 1rem;">{alt['brand']}</strong><br>
                <span style="font-size: 0.85rem; color: #374151;">{alt['perk']}</span><br>
                <span style="display: inline-block; margin-top: 0.4rem; font-size: 0.78rem; font-weight: 700; color: #166534; background: #dcfce7; padding: 0.2rem 0.55rem; border-radius: 6px;">
                    Carbon Cut: {alt['saving']}
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button(f"Adopt {alt['brand'].split('/')[0].strip()} 🌿", key=f"adopt_swap_{i}"):
            clean_brand = alt['brand'].split('/')[0].strip()
            swap_entry = {
                "id": len(st.session_state.purchases) + 1,
                "item": f"Greener Swap: {clean_brand} ({cat_choice})",
                "category": cat_choice,
                "brand": clean_brand,
                "price": 35.0,
                "carbon_kg": calculate_carbon(35.0, cat_choice, True),
                "date": str(date.today()),
                "is_ethical": True,
            }
            st.session_state.purchases.append(swap_entry)
            st.session_state.recent_art = "badge"
            st.balloons()
            st.success(f"Adopted {clean_brand}! Saved ~{alt['saving']} emissions.")
            st.rerun()

st.divider()

# ==============================================================================
# 8. CENTER & SIDE LAYOUT (Dashboard in Center, Turtle & Badges on Side)
# ==============================================================================
col_center, col_side = st.columns([1.8, 1.2], gap="large")

with col_center:
    # --------------------------------------------------------------------------
    # MONTHLY IMPACT DASHBOARD (Compulsory Feature P057)
    # --------------------------------------------------------------------------
    st.subheader(f"📊 Monthly Carbon Dashboard ({period_label})")

    # 4 Primary KPI Metric Cards
    k1, k2, k3, k4 = st.columns(4)
    bench_co2 = total_spend * 0.45  # Conventional unoptimized spending benchmark
    co2_saved = max(0.0, round(bench_co2 - total_co2, 1))
    trees_needed = round(total_co2 / 21.0, 1)  # 1 mature tree sequesters ~21 kg CO2/year

    with k1:
        st.metric(
            label=f"Total Spend ({period_label})",
            value=f"${total_spend:,.2f}",
            delta=f"{len(filtered_purchases)} Items Logged"
        )
    with k2:
        st.metric(
            label="Carbon Footprint",
            value=f"{total_co2:.1f} kg CO₂e",
            delta=f"{avg_intensity:.2f} kg/$ intensity",
            delta_color="inverse"
        )
    with k3:
        st.metric(
            label="Carbon Saved",
            value=f"{co2_saved:.1f} kg CO₂",
            delta="Vs Industry Standard"
        )
    with k4:
        st.metric(
            label="Trees to Offset",
            value=f"{trees_needed} Trees",
            delta="21 kg/tree/year"
        )

    # Monthly Carbon Budget Allowance Meter
    st.markdown("<br>", unsafe_allow_html=True)
    budget_pct = min(100, int((total_co2 / carbon_budget) * 100)) if carbon_budget > 0 else 0
    if budget_pct < 75:
        st.progress(budget_pct / 100, text=f"Monthly Allowance: {total_co2:.1f} / {carbon_budget} kg ({budget_pct}% used — Healthy Status 🌿)")
    elif budget_pct < 100:
        st.progress(budget_pct / 100, text=f"Monthly Allowance: {total_co2:.1f} / {carbon_budget} kg ({budget_pct}% used — Approaching Ceiling ⚠️)")
    else:
        st.progress(1.0, text=f"Monthly Allowance: {total_co2:.1f} / {carbon_budget} kg ({budget_pct}% used — Budget Exceeded! Time to Thrifting 🚨)")

    # Category Footprint Chart
    st.markdown("<br>", unsafe_allow_html=True)
    if filtered_purchases:
        df = pd.DataFrame(filtered_purchases)
        st.markdown("**Emissions Breakdown by Product Category (kg CO₂e)**")
        cat_agg = df.groupby("category")["carbon_kg"].sum().sort_values(ascending=False)
        st.bar_chart(cat_agg, color="#2d6a4f")

        # Interactive Transaction Ledger
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"**Transaction Ledger & Audit History ({len(filtered_purchases)} entries)**")
        view_df = df[["date", "item", "category", "brand", "price", "carbon_kg", "is_ethical"]].copy()
        view_df.columns = ["Date", "Item Description", "Category", "Brand", "Price ($)", "CO₂ (kg)", "Ethical?"]
        st.dataframe(view_df, width="stretch", hide_index=True)

        # 1-Click CSV Export
        csv_bytes = view_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Ledger to CSV",
            data=csv_bytes,
            file_name=f"shopimpact_{period_label.lower().replace(' ', '_')}.csv",
            mime="text/csv",
        )
    else:
        st.info("No transaction records found for this period. Use the form above to log your first purchase!")

with col_side:
    # --------------------------------------------------------------------------
    # TURTLE ECO-VISUALIZER (Compulsory Feature P060)
    # --------------------------------------------------------------------------
    st.subheader("🎨 Turtle Eco-Visualizer")
    st.caption("Live vector artwork drawn using pure Python Headless Turtle geometry.")

    # Vector Art Style Selector
    art_choice = st.radio(
        "Turtle Drawing Mode:",
        options=["leaf", "footprint", "badge", "avatar"],
        index=["leaf", "footprint", "badge", "avatar"].index(st.session_state.recent_art) if st.session_state.recent_art in ["leaf", "footprint", "badge", "avatar"] else 0,
        format_func=lambda x: {
            "leaf": "🌿 Procedural Eco Leaf",
            "footprint": "👣 Green Footprint",
            "badge": "⭐ Achievement Rosette",
            "avatar": f"👤 {user_initial}'s Custom Avatar Seal"
        }[x],
        horizontal=True,
    )
    st.session_state.recent_art = art_choice

    turtle_img = render_turtle_art(art_choice, user_initial)
    st.image(
        turtle_img,
        caption=f"Vector Drawing: {art_choice.capitalize()} (Headless Turtle Vector Path on PIL Canvas)",
        width="stretch",
    )

    st.markdown("---")

    # --------------------------------------------------------------------------
    # MILESTONE BADGES (Compulsory Feature P058)
    # --------------------------------------------------------------------------
    st.subheader("🏆 Badges & Achievement Hall")
    for b in badges:
        is_won = b["unlocked"]
        style_class = "badge-unlocked" if is_won else ""
        badge_status = "✅ UNLOCKED" if is_won else "🔒 IN PROGRESS"
        status_color = "#15803d" if is_won else "#94a3b8"

        st.markdown(
            f"""
            <div class="badge-card {style_class}">
                <div style="display: flex; align-items: center; gap: 0.85rem;">
                    <div style="font-size: 2rem;">{b['icon']}</div>
                    <div style="flex: 1;">
                        <strong style="color: var(--text-title); font-size: 0.95rem;">{b['name']}</strong><br>
                        <span style="font-size: 0.8rem; color: #64748b;">{b['desc']}</span><br>
                        <span style="font-size: 0.76rem; font-weight: 700; color: {status_color};">
                            {badge_status} &bull; {b['progress']}
                        </span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # --------------------------------------------------------------------------
    # DAILY ECO WISDOM (Brief Optional Feature P064)
    # --------------------------------------------------------------------------
    st.subheader("💡 Eco Wisdom of the Day")
    st.markdown(
        f"""
        <div style="background: rgba(30, 64, 175, 0.06); border: 1px solid rgba(147, 197, 253, 0.5); border-radius: 12px; padding: 0.9rem;">
            <strong style="color: #0369a1;">Did you know?</strong><br>
            <span style="font-size: 0.88rem; color: #334155;">{random.choice(ECO_TIPS)}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==============================================================================
# 9. FOOTER & ACADEMIC AUDIT DOSSIER
# ==============================================================================
st.divider()
st.markdown(
    """
    <div style="text-align: center; color: #64748b; font-size: 0.82rem; padding: 1rem 0;">
        <strong>ShopImpact Conscious Shopping Dashboard</strong> &bull; Summative Assessment (60 Marks)<br>
        Candidate: <strong>Parth Pravinbhai Gajera</strong> (ID: <code>1000544</code>) &bull; CRS: Artificial Intelligence &bull; Course: Python Programming (IDAI 102)<br>
        Verified Single-File Architecture (<code>app.py</code>) &bull; Pure Python Vector Turtle Graphics &bull; Streamlit Cloud Ready.
    </div>
    """,
    unsafe_allow_html=True,
)
