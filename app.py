import math
import random
from datetime import date, datetime
import pandas as pd
from PIL import Image, ImageDraw
import streamlit as st

st.set_page_config(page_title="ShopImpact — Conscious Shopping Dashboard", page_icon="🌱", layout="wide")

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
    "Shelly the Sea Turtle 🐢": "Wisdom & plastic-free clean oceans",
    "Pip the Forest Fox 🦊": "Agile thrifting & clever second-hand hunting",
    "Barnaby the Eco Owl 🦉": "Analytics, science & carbon tracking",
    "Bumble the Pollinator 🐝": "Local organic farms & biodiversity",
    "Bao the Bamboo Panda 🐼": "Zero-waste reusables & gentle living",
}

ECO_TIPS = [
    "Buying a single cotton shirt second-hand saves ~2,700 liters of water (3 years of drinking water).",
    "Keeping your phone for 4 years instead of 2 cuts manufacturing emissions by 50%.",
    "Package-free shampoo bars prevent roughly 3 plastic bottles from landfills each year.",
    "Refurbished laptops save up to 190 kg of CO2 and 1,200 kg of raw mined minerals.",
    "Shopping at a farmers market eliminates long-haul cold-chain logistics emissions.",
]

SUSTAINABLE_QUOTES = [
    "“The greatest threat to our planet is the belief that someone else will save it.” — Robert Swan",
    "“We do not inherit the Earth from our ancestors; we borrow it from our children.” — Native Proverb",
    "“Small acts, when multiplied by millions of people, can transform the world.” — Howard Zinn",
]

class HeadlessTurtle:
    def __init__(self, w=260, h=260):
        self.w, self.h = w, h
        self.img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        self.draw = ImageDraw.Draw(self.img)
        self.x, self.y = w / 2, h / 2
        self.heading = 90
        self.down = True
        self.color = (45, 106, 79, 255)
        self.width = 3

    def forward(self, d):
        rad = math.radians(self.heading)
        nx = self.x + d * math.cos(rad)
        ny = self.y - d * math.sin(rad)
        if self.down:
            self.draw.line([(self.x, self.y), (nx, ny)], fill=self.color, width=self.width)
        self.x, self.y = nx, ny

    def left(self, a): self.heading = (self.heading + a) % 360
    def right(self, a): self.heading = (self.heading - a) % 360
    def penup(self): self.down = False
    def pendown(self): self.down = True
    def goto(self, x, y):
        if self.down:
            self.draw.line([(self.x, self.y), (x, y)], fill=self.color, width=self.width)
        self.x, self.y = x, y

    def arc(self, r, ext, steps=14):
        step_len = (2 * math.pi * r * (abs(ext) / 360.0)) / steps
        for _ in range(steps):
            self.forward(step_len)
            self.left(ext / steps)

def draw_turtle_mascot(mood="happy"):
    t = HeadlessTurtle(260, 260)
    d = t.draw
    d.ellipse([(45, 65), (85, 115)], fill=(74, 150, 110), outline=(30, 75, 50), width=2)
    d.ellipse([(175, 65), (215, 115)], fill=(74, 150, 110), outline=(30, 75, 50), width=2)
    d.ellipse([(55, 160), (95, 205)], fill=(74, 150, 110), outline=(30, 75, 50), width=2)
    d.ellipse([(165, 160), (205, 205)], fill=(74, 150, 110), outline=(30, 75, 50), width=2)
    d.polygon([(125, 215), (135, 235), (135, 215)], fill=(74, 150, 110), outline=(30, 75, 50))
    d.ellipse([(65, 80), (195, 210)], fill=(45, 106, 79), outline=(27, 67, 50), width=3)
    d.ellipse([(85, 100), (175, 190)], fill=(82, 183, 136), outline=(27, 67, 50), width=2)
    d.ellipse([(105, 120), (155, 170)], fill=(116, 198, 157), outline=(45, 106, 79), width=2)
    d.ellipse([(100, 35), (160, 95)], fill=(116, 198, 157), outline=(30, 75, 50), width=3)

    if mood == "happy":
        d.ellipse([(114, 50), (128, 64)], fill=(20, 40, 30))
        d.ellipse([(117, 52), (121, 56)], fill=(255, 255, 255))
        d.ellipse([(132, 50), (146, 64)], fill=(20, 40, 30))
        d.ellipse([(135, 52), (139, 56)], fill=(255, 255, 255))
        d.ellipse([(108, 65), (118, 73)], fill=(251, 113, 133, 180))
        d.ellipse([(142, 65), (152, 73)], fill=(251, 113, 133, 180))
        d.arc([(118, 62), (142, 82)], start=10, end=170, fill=(20, 40, 30), width=3)
        d.line([(130, 35), (130, 18)], fill=(45, 106, 79), width=3)
        d.ellipse([(116, 10), (130, 22)], fill=(116, 198, 157), outline=(45, 106, 79), width=2)
        d.ellipse([(130, 10), (144, 22)], fill=(116, 198, 157), outline=(45, 106, 79), width=2)
    elif mood == "worried":
        d.ellipse([(114, 52), (128, 66)], fill=(20, 40, 30))
        d.ellipse([(132, 52), (146, 66)], fill=(20, 40, 30))
        d.arc([(120, 74), (140, 84)], start=190, end=350, fill=(20, 40, 30), width=3)
        d.ellipse([(148, 38), (158, 52)], fill=(56, 189, 248), outline=(2, 132, 199), width=1)
    else:
        d.ellipse([(115, 52), (127, 64)], fill=(20, 40, 30))
        d.ellipse([(117, 54), (121, 58)], fill=(255, 255, 255))
        d.ellipse([(133, 52), (145, 64)], fill=(20, 40, 30))
        d.ellipse([(135, 54), (139, 58)], fill=(255, 255, 255))
        d.arc([(122, 66), (138, 78)], start=20, end=160, fill=(20, 40, 30), width=2)
        d.line([(130, 35), (130, 22)], fill=(45, 106, 79), width=2)
        d.ellipse([(124, 15), (136, 25)], fill=(116, 198, 157), outline=(45, 106, 79), width=1)
    return t.img

def draw_vector_art(art_type="leaf", initial="P"):
    t = HeadlessTurtle(260, 260)
    if art_type == "leaf":
        t.penup(); t.goto(130, 235); t.heading = 90; t.color = (64, 145, 108, 255); t.pendown(); t.forward(40)
        t.color = (45, 106, 79, 255); t.arc(95, 58); t.left(122); t.arc(95, 58)
        t.penup(); t.goto(130, 195); t.heading = 90; t.color = (82, 183, 136, 255); t.width = 2; t.pendown(); t.forward(90)
        for y, ang in [(165, 45), (165, 135), (135, 45), (135, 135), (105, 45), (105, 135)]:
            t.penup(); t.goto(130, y); t.heading = ang; t.pendown(); t.forward(18)
    elif art_type == "footprint":
        t.penup(); t.goto(130, 225); t.heading = 90; t.color = (45, 106, 79, 255); t.pendown()
        t.arc(60, 40); t.arc(22, -50); t.arc(50, 70); t.arc(32, 90); t.arc(75, 45); t.arc(28, 80); t.goto(130, 225)
        for tx, ty, r in [(110, 80, 7), (124, 70, 9), (138, 72, 8), (152, 78, 6), (164, 88, 5)]:
            t.draw.ellipse([(tx-r, ty-r), (tx+r, ty+r)], fill=(82, 183, 136, 220), outline=(45, 106, 79, 255), width=2)
    elif art_type == "badge":
        t.draw.ellipse([(75, 55), (185, 165)], fill=(254, 243, 199, 240), outline=(217, 119, 6, 255), width=3)
        t.draw.ellipse([(90, 70), (170, 150)], fill=(236, 253, 245, 240), outline=(5, 150, 105, 255), width=2)
        t.penup(); t.goto(110, 160); t.heading = 250; t.pendown(); t.color = (5, 150, 105, 255)
        t.forward(50); t.left(120); t.forward(20); t.left(120); t.forward(45)
        t.penup(); t.goto(150, 160); t.heading = 290; t.pendown()
        t.forward(50); t.right(120); t.forward(20); t.right(120); t.forward(45)
    else:
        t.draw.ellipse([(45, 45), (215, 215)], fill=(232, 245, 233, 240), outline=(45, 106, 79, 255), width=4)
        t.draw.ellipse([(60, 60), (200, 200)], outline=(82, 183, 136, 255), width=2)
        for ang in range(0, 360, 45):
            rad = math.radians(ang)
            lx = 130 + 80 * math.cos(rad)
            ly = 130 - 80 * math.sin(rad)
            t.draw.ellipse([(lx-4, ly-4), (lx+4, ly+4)], fill=(45, 106, 79, 255))
        glyph = initial.upper() if initial else "P"
        t.draw.text((115, 105), glyph, fill=(27, 67, 50, 255), font_size=56)
    return t.img

def calculate_carbon(price, category, is_ethical):
    rate = CATEGORIES.get(category, {"multiplier": 0.35})["multiplier"]
    base = price * rate
    return round(base * 0.70 if is_ethical else base, 2)

def get_equivalency(carbon_kg):
    miles = int(carbon_kg * 2.4)
    charges = int(carbon_kg * 121)
    return f"🚗 ~{miles:,} petrol miles • 📱 ~{charges:,} phone charges"

def evaluate_badges(purchases, overrides=None):
    if overrides is None: overrides = {}
    total_items = len(purchases)
    total_spend = sum(p["price"] for p in purchases)
    total_co2 = sum(p["carbon_kg"] for p in purchases)
    ethical_count = sum(1 for p in purchases if p.get("is_ethical", False))
    avg_intensity = (total_co2 / total_spend) if total_spend > 0 else 0.40
    co2_saved = max(0.0, round(total_spend * 0.45 - total_co2, 1))
    zero_waste_count = sum(1 for p in purchases if "Zero-Waste" in p["category"] or "Thrift" in p["category"])

    badges = [
        {"id": "starter", "name": "Seed Starter", "icon": "🌱", "desc": "Log your 1st conscious purchase", "unlocked": overrides.get("starter", total_items >= 1), "progress": f"{min(total_items, 1)}/1 item"},
        {"id": "low_impact", "name": "Low Impact Shopper", "icon": "🍃", "desc": "Maintain carbon intensity ≤ 0.25 kg/$", "unlocked": overrides.get("low_impact", total_items >= 3 and avg_intensity <= 0.25), "progress": f"{avg_intensity:.2f} kg/$ (Goal ≤ 0.25)"},
        {"id": "ethical_pioneer", "name": "Conscious Pioneer", "icon": "♻️", "desc": "Choose 5+ verified circular or thrift items", "unlocked": overrides.get("ethical_pioneer", ethical_count >= 5), "progress": f"{ethical_count}/5 green choices"},
        {"id": "eco_saver", "name": "Eco Saver of Month", "icon": "🌟", "desc": "Save 15+ kg CO₂ vs industry standard", "unlocked": overrides.get("eco_saver", co2_saved >= 15.0), "progress": f"{co2_saved:.1f}/15.0 kg saved"},
        {"id": "zero_waste", "name": "Zero-Waste Hero", "icon": "🏆", "desc": "Log 2+ zero-waste or thrift items", "unlocked": overrides.get("zero_waste", zero_waste_count >= 2), "progress": f"{zero_waste_count}/2 items"},
        {"id": "biosphere_master", "name": "Biosphere Master", "icon": "👑", "desc": "Unlock 4+ badges and stay within budget", "unlocked": overrides.get("biosphere_master", False), "progress": ""},
    ]
    if "biosphere_master" not in overrides:
        badges[5]["unlocked"] = sum(1 for b in badges[:5] if b["unlocked"]) >= 4 and total_co2 <= st.session_state.carbon_budget
        badges[5]["progress"] = f"{sum(1 for b in badges[:5] if b['unlocked'])}/4 badges"
    else:
        badges[5]["progress"] = "Demo override"
    return badges, total_spend, total_co2, avg_intensity, co2_saved, ethical_count

if "onboarded" not in st.session_state: st.session_state.onboarded = False
if "user_name" not in st.session_state: st.session_state.user_name = "Parth Gajera"
if "user_mascot" not in st.session_state: st.session_state.user_mascot = "Shelly the Sea Turtle 🐢"
if "carbon_budget" not in st.session_state: st.session_state.carbon_budget = 150
if "recent_art" not in st.session_state: st.session_state.recent_art = "leaf"
if "mascot_mood" not in st.session_state: st.session_state.mascot_mood = "happy"
if "mascot_message" not in st.session_state: st.session_state.mascot_message = "Hi! I am Shelly, your conscious shopping guide!"
if "badge_overrides" not in st.session_state: st.session_state.badge_overrides = {}
if "nav_view" not in st.session_state: st.session_state.nav_view = "📊 Dashboard"
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

# ------------------------------------------------------------------------------
# SCREEN 1: WELCOME & ONBOARDING (Clean, Visual, Not a sub-page)
# ------------------------------------------------------------------------------
if not st.session_state.onboarded:
    st.markdown("<h1 style='text-align: center; color: #1b4332; margin-bottom: 0;'>🌱 Meet ShopImpact</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #475569; font-size: 1.15rem; margin-bottom: 2rem;'>Your playful, conscious shopping companion.</p>", unsafe_allow_html=True)

    c1, c2 = st.columns([1.1, 0.9], gap="large")
    with c1:
        st.subheader("Personalize Your Eco Journey")
        u_name = st.text_input("What is your name?", value=st.session_state.user_name)
        m_choice = st.selectbox("Choose your spirit guide:", options=list(ECO_MASCOTS.keys()))
        b_choice = st.slider("Monthly Carbon Target (kg CO₂e):", min_value=50, max_value=300, value=st.session_state.carbon_budget, step=10)

        st.caption(f"✨ **{m_choice.split()[0]}**: {ECO_MASCOTS[m_choice]}")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 Enter ShopImpact Dashboard →", type="primary", use_container_width=True):
            st.session_state.user_name = u_name.strip() if u_name.strip() else "Shopper"
            st.session_state.user_mascot = m_choice
            st.session_state.carbon_budget = b_choice
            st.session_state.onboarded = True
            st.rerun()

    with c2:
        img_mascot = draw_turtle_mascot("happy")
        st.image(img_mascot, width=240, caption="Shelly the Sea Turtle is excited to guide you!")
        st.markdown(
            """
            <div style="background: #ecfdf5; border: 1.5px solid #a7f3d0; border-radius: 12px; padding: 1rem; color: #065f46;">
                <strong>What you'll do inside:</strong>
                <ul style="margin: 0.5rem 0 0 1.2rem; padding: 0;">
                    <li>⚡ See real-time CO₂ as you type purchases</li>
                    <li>🔄 Discover greener alternative brand swaps</li>
                    <li>🏆 Watch badges turn from gray to radiant color</li>
                    <li>🎨 See Shelly react to every choice you make!</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ------------------------------------------------------------------------------
# SCREEN 2: MAIN APPLICATION (DASHBOARD, BADGES, TURTLE STUDIO)
# ------------------------------------------------------------------------------
else:
    # Sidebar
    st.sidebar.markdown(f"### 👤 {st.session_state.user_name}")
    st.sidebar.caption(f"{st.session_state.user_mascot} • Goal: {st.session_state.carbon_budget} kg")
    if st.sidebar.button("⚙️ Edit Profile / Goals", use_container_width=True):
        st.session_state.onboarded = False
        st.rerun()

    st.sidebar.markdown("---")
    st.session_state.nav_view = st.sidebar.radio("Go to:", ["📊 Dashboard", "🏆 Wall of Badges", "🎨 Turtle Studio"])

    dark_theme = st.sidebar.toggle("🌙 Dark Mode", value=False)
    st.sidebar.markdown("---")
    st.sidebar.caption(f"💡 *{random.choice(ECO_TIPS)}*")

    c_rst1, c_rst2 = st.sidebar.columns(2)
    with c_rst1:
        if st.button("🔄 Reset Demo", use_container_width=True):
            st.session_state.purchases = []
            st.session_state.badge_overrides = {}
            st.rerun()
    with c_rst2:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.purchases = []
            st.rerun()

    # Dynamic CSS styling
    card_bg = "#17221b" if dark_theme else "#ffffff"
    text_c = "#f0fdf4" if dark_theme else "#1b4332"
    sub_c = "#94a3b8" if dark_theme else "#475569"
    border_c = "#2a3d31" if dark_theme else "#e2d9cc"
    pill_bg = "#1b2d23" if dark_theme else "#ecfdf5"
    pill_b = "#34d399" if dark_theme else "#6ee7b7"

    st.markdown(
        f"""
        <style>
        .kpi-box {{ background: {card_bg}; border: 1.5px solid {border_c}; border-radius: 12px; padding: 1rem; color: {text_c}; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}
        .kpi-box h4 {{ margin: 0; font-size: 0.8rem; text-transform: uppercase; color: {sub_c}; }}
        .kpi-box .val {{ font-size: 1.7rem; font-weight: 800; color: {text_c}; margin: 0.2rem 0; }}
        .preview-box {{ background: {pill_bg}; border: 1.5px solid {pill_b}; border-radius: 10px; padding: 0.8rem 1rem; color: {text_c}; margin: 0.5rem 0; }}
        .badge-on {{ background: linear-gradient(135deg, #1b4332, #2d6a4f); border: 2px solid #52b788; border-radius: 14px; padding: 1rem; color: #ffffff; margin-bottom: 0.8rem; }}
        .badge-off {{ background: #f1f5f9; border: 2px dashed #94a3b8; border-radius: 14px; padding: 1rem; color: #64748b; filter: grayscale(100%); opacity: 0.6; margin-bottom: 0.8rem; }}
        .swap-card {{ background: {card_bg}; border: 1.5px solid {border_c}; border-radius: 10px; padding: 0.85rem; color: {text_c}; margin-bottom: 0.5rem; }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------------------------
    # VIEW: 📊 DASHBOARD
    # --------------------------------------------------------------------------
    if st.session_state.nav_view == "📊 Dashboard":
        # Interactive Mascot Reaction Bar
        col_m1, col_m2 = st.columns([0.8, 3.2])
        with col_m1:
            st.image(draw_turtle_mascot(st.session_state.mascot_mood), width=150)
        with col_m2:
            st.markdown(
                f"""
                <div style="background: {pill_bg}; border: 1.5px solid {pill_b}; border-radius: 14px; padding: 1rem 1.4rem; color: {text_c}; margin-top: 0.5rem;">
                    <div style="font-size: 1.15rem; font-weight: 800; color: {text_c};">{st.session_state.user_mascot.split()[0]}'s Live Reaction:</div>
                    <div style="font-size: 0.95rem; margin-top: 0.2rem;">"{st.session_state.mascot_message}"</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # Log a Purchase Form (Input at top as required)
        st.subheader("🛒 Log a Planned Purchase")
        with st.form("quick_log_form", clear_on_submit=True):
            f1, f2, f3 = st.columns([1.2, 1.2, 1.0])
            with f1:
                item_name = st.text_input("Item Description", placeholder="e.g. Vintage Denim Jacket, USB Cable")
                cat_choice = st.selectbox("Product Category", options=list(CATEGORIES.keys()))
            with f2:
                brand_val = st.text_input("Brand or Vendor", placeholder="e.g. Patagonia, Zara, Back Market")
                price_val = st.number_input("Price ($)", min_value=1.0, max_value=5000.0, value=45.0, step=5.0)
            with f3:
                date_val = st.date_input("Date", value=date.today())
                is_eth = st.checkbox("🌱 Certified Circular / Thrift / Ethical", help="Applies a 30% carbon discount for green practices.")

            live_co2 = calculate_carbon(price_val, cat_choice, is_eth)
            equiv_msg = get_equivalency(live_co2)
            st.markdown(
                f"""
                <div class="preview-box">
                    <strong>⚡ Live Preview:</strong> <code>{live_co2} kg CO₂e</code> ({CATEGORIES[cat_choice]['rating']}) • {equiv_msg}
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.form_submit_button("🌿 Record Purchase in Dashboard", use_container_width=True):
                if not item_name.strip():
                    st.error("Please enter an item name.")
                else:
                    new_rec = {
                        "id": len(st.session_state.purchases) + 1,
                        "item": item_name.strip(),
                        "category": cat_choice,
                        "brand": brand_val.strip() if brand_val.strip() else "Unspecified",
                        "price": float(price_val),
                        "carbon_kg": float(live_co2),
                        "date": str(date_val),
                        "is_ethical": is_eth,
                    }
                    st.session_state.purchases.append(new_rec)
                    if is_eth or live_co2 < 4.0:
                        st.session_state.mascot_mood = "happy"
                        st.session_state.mascot_message = f"Woohoo! Loving your choice of '{item_name}'! Shelly is smiling bright!"
                        st.balloons()
                    else:
                        st.session_state.mascot_mood = "worried"
                        st.session_state.mascot_message = f"That added {live_co2} kg CO₂e. Check the greener swaps below for next time!"
                    st.rerun()

        # Greener Swaps
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader(f"🔄 Greener Swaps for {cat_choice}")
        swaps = ETHICAL_ALTERNATIVES.get(cat_choice, [])
        sw_cols = st.columns(len(swaps))
        for idx, sw in enumerate(swaps):
            with sw_cols[idx]:
                st.markdown(
                    f"""
                    <div class="swap-card">
                        <strong>{sw['brand']}</strong><br>
                        <span style="font-size: 0.85rem; color: {sub_c};">{sw['perk']}</span><br>
                        <span style="color: #10b981; font-weight: 700; font-size: 0.8rem;">Cut: {sw['saving']}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                b_name = sw['brand'].split('/')[0].strip()
                if st.button(f"Adopt {b_name} 🌿", key=f"adopt_btn_{idx}"):
                    st.session_state.purchases.append({
                        "id": len(st.session_state.purchases) + 1,
                        "item": f"Greener Swap: {b_name}",
                        "category": cat_choice,
                        "brand": b_name,
                        "price": 30.0,
                        "carbon_kg": calculate_carbon(30.0, cat_choice, True),
                        "date": str(date.today()),
                        "is_ethical": True,
                    })
                    st.session_state.mascot_mood = "happy"
                    st.session_state.mascot_message = f"Awesome swap to {b_name}! That's how we heal the planet!"
                    st.balloons()
                    st.rerun()

        st.markdown("---")

        # Monthly Metrics & Ledger
        months = sorted(list({p["date"][:7] for p in st.session_state.purchases}), reverse=True) if st.session_state.purchases else [date.today().strftime("%Y-%m")]
        sel_month = st.radio("Filter Month:", ["All Time"] + months, horizontal=True)

        if sel_month == "All Time":
            view_data = st.session_state.purchases
            period_str = "All Time"
        else:
            view_data = [p for p in st.session_state.purchases if p["date"].startswith(sel_month)]
            period_str = sel_month

        badges, spend_tot, co2_tot, avg_int, saved_tot, eth_cnt = evaluate_badges(view_data, st.session_state.badge_overrides)
        trees_tot = round(co2_tot / 21.0, 1)

        m1, m2, m3, m4 = st.columns(4)
        m1.markdown(f"<div class='kpi-box'><h4>Total Spend</h4><div class='val'>${spend_tot:,.2f}</div><span>{len(view_data)} items</span></div>", unsafe_allow_html=True)
        m2.markdown(f"<div class='kpi-box'><h4>Carbon Footprint</h4><div class='val'>{co2_tot:.1f} kg</div><span>{avg_int:.2f} kg/$</span></div>", unsafe_allow_html=True)
        m3.markdown(f"<div class='kpi-box'><h4>Carbon Saved</h4><div class='val'>{saved_tot:.1f} kg</div><span>Vs baseline</span></div>", unsafe_allow_html=True)
        m4.markdown(f"<div class='kpi-box'><h4>Trees to Offset</h4><div class='val'>{trees_tot} Trees</div><span>21 kg/tree/yr</span></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        b_lim = st.session_state.carbon_budget
        pct = min(100, int((co2_tot / b_lim) * 100)) if b_lim > 0 else 0
        st.progress(pct / 100, text=f"Monthly Budget: {co2_tot:.1f} / {b_lim} kg CO₂e ({pct}% used)")

        col_g1, col_g2 = st.columns([1.1, 1.3], gap="large")
        with col_g1:
            st.markdown(f"**Emissions by Category ({period_str})**")
            if view_data:
                df = pd.DataFrame(view_data)
                st.bar_chart(df.groupby("category")["carbon_kg"].sum().sort_values(ascending=False), color="#2d6a4f")
            else:
                st.caption("No data for this timeframe.")

        with col_g2:
            st.markdown(f"**Ledger ({len(view_data)} entries)**")
            if view_data:
                df = pd.DataFrame(view_data)[["date", "item", "category", "price", "carbon_kg", "is_ethical"]]
                df.columns = ["Date", "Item", "Category", "Price ($)", "CO₂ (kg)", "Ethical?"]
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.download_button("📥 Export CSV", df.to_csv(index=False).encode("utf-8"), f"shopimpact_{period_str}.csv", "text/csv")
            else:
                st.caption("No items recorded yet.")

    # --------------------------------------------------------------------------
    # VIEW: 🏆 WALL OF BADGES (Unlocked = Colorful, Locked = Black/White)
    # --------------------------------------------------------------------------
    elif st.session_state.nav_view == "🏆 Wall of Badges":
        st.title("🏆 Wall of Badges & Eco Fame")
        st.caption("Achievements glow in full radiant color once unlocked. Locked badges stay in black & white until earned!")

        badges, _, _, _, _, _ = evaluate_badges(st.session_state.purchases, st.session_state.badge_overrides)
        unlocked_num = sum(1 for b in badges if b["unlocked"])

        st.metric("Badges Unlocked", f"{unlocked_num} of {len(badges)}", f"{int((unlocked_num/len(badges))*100)}% Complete")

        with st.expander("🎯 Test & Allot Badges (Demo Sandbox)", expanded=False):
            st.write("Toggle badges on/off to watch them transition between **Black & White** and **Vibrant Color** live:")
            sb_cols = st.columns(3)
            for i, b in enumerate(badges):
                with sb_cols[i % 3]:
                    st.session_state.badge_overrides[b["id"]] = st.checkbox(f"Allot {b['name']}", value=b["unlocked"], key=f"sb_{b['id']}")

        st.markdown("<br>", unsafe_allow_html=True)
        b_c1, b_c2 = st.columns(2, gap="large")
        badges, _, _, _, _, _ = evaluate_badges(st.session_state.purchases, st.session_state.badge_overrides)

        for i, b in enumerate(badges):
            target = b_c1 if i % 2 == 0 else b_c2
            with target:
                if b["unlocked"]:
                    st.markdown(
                        f"""
                        <div class="badge-on">
                            <div style="display: flex; gap: 1rem; align-items: center;">
                                <div style="font-size: 3rem;">{b['icon']}</div>
                                <div>
                                    <h3 style="margin: 0; color: #ffffff;">{b['name']}</h3>
                                    <p style="margin: 0.2rem 0; font-size: 0.9rem; color: #d1fae5;">{b['desc']}</p>
                                    <span style="background: #34d399; color: #064e3b; font-weight: 800; font-size: 0.75rem; padding: 0.2rem 0.6rem; border-radius: 99px;">
                                        ✨ UNLOCKED ({b['progress']})
                                    </span>
                                </div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f"""
                        <div class="badge-off">
                            <div style="display: flex; gap: 1rem; align-items: center;">
                                <div style="font-size: 3rem;">🔒</div>
                                <div>
                                    <h3 style="margin: 0; color: #475569;">{b['name']}</h3>
                                    <p style="margin: 0.2rem 0; font-size: 0.9rem; color: #64748b;">{b['desc']}</p>
                                    <span style="background: #94a3b8; color: #ffffff; font-weight: 700; font-size: 0.75rem; padding: 0.2rem 0.6rem; border-radius: 99px;">
                                        🔒 LOCKED ({b['progress']})
                                    </span>
                                </div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    # --------------------------------------------------------------------------
    # VIEW: 🎨 TURTLE STUDIO
    # --------------------------------------------------------------------------
    elif st.session_state.nav_view == "🎨 Turtle Studio":
        st.title("🎨 Turtle Vector Studio")
        st.caption("Pure Python headless vector Turtle graphics drawn natively onto PIL canvases.")

        a_col1, a_col2 = st.columns([1.0, 1.2], gap="large")
        with a_col1:
            u_init = st.session_state.user_name.strip()[0] if st.session_state.user_name.strip() else "P"
            opts = ["mascot_happy", "mascot_worried", "mascot_mindful", "leaf", "footprint", "badge", "seal"]
            labels = {
                "mascot_happy": "🐢 Shelly Mascot (Happy / Celebrating)",
                "mascot_worried": "💧 Shelly Mascot (Worried / High Carbon)",
                "mascot_mindful": "🌱 Shelly Mascot (Calm / Mindful)",
                "leaf": "🌿 Procedural Eco Leaf",
                "footprint": "👣 Low Carbon Footprint",
                "badge": "⭐ Achievement Rosette",
                "seal": f"🛡️ {u_init}'s Personal Avatar Seal",
            }
            pick = st.radio("Choose artwork to draw:", opts, format_func=lambda x: labels[x])

        with a_col2:
            if pick.startswith("mascot_"):
                mood = pick.replace("mascot_", "")
                out_img = draw_turtle_mascot(mood)
            else:
                out_img = draw_vector_art(pick, u_init)

            st.image(out_img, width=280, caption=f"Vector Turtle Path: {labels[pick]}")
            import io
            buf = io.BytesIO()
            out_img.save(buf, format="PNG")
            st.download_button("💾 Download Artwork (PNG)", buf.getvalue(), f"turtle_{pick}.png", "image/png")

st.divider()
st.markdown(
    """
    <div style="text-align: center; color: #64748b; font-size: 0.8rem; padding: 0.8rem 0;">
        <strong>ShopImpact Conscious Shopping Dashboard</strong> • Summative Assessment (60 Marks)<br>
        Candidate: <strong>Parth Pravinbhai Gajera</strong> (ID: <code>1000544</code>) • CRS: Artificial Intelligence • IDAI 102
    </div>
    """,
    unsafe_allow_html=True,
)
