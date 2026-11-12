import math
import random
from datetime import date, datetime
import pandas as pd
from PIL import Image, ImageDraw
import streamlit as st

st.set_page_config(page_title="ShopImpact — Conscious Shopping Dashboard", page_icon="🌱", layout="wide")

def render_html(html_str: str):
    clean = "\n".join(line.strip() for line in html_str.splitlines() if line.strip())
    st.markdown(clean, unsafe_allow_html=True)

CATEGORIES = {
    "Fast Fashion Apparel": {"multiplier": 0.42, "rating": "High Carbon", "icon": "👗", "fact": "Synthetic polyester spinning and chemical dyes drive emissions."},
    "Footwear & Leather": {"multiplier": 0.65, "rating": "Very High", "icon": "👞", "fact": "Cattle methane and energy-intensive chrome tanning create heavy footprints."},
    "Consumer Electronics": {"multiplier": 0.55, "rating": "High Carbon", "icon": "📱", "fact": "Semiconductor cleanrooms & rare earth mining drive ~80% of lifecycle CO₂."},
    "Refurbished Tech": {"multiplier": 0.11, "rating": "Low Carbon", "icon": "♻️", "fact": "Avoids raw mining; only covers diagnostics and clean parcel shipping."},
    "Second-Hand / Thrift": {"multiplier": 0.05, "rating": "Minimal Impact", "icon": "🧥", "fact": "Pure circular economy; manufacturing emissions are 100% amortized."},
    "Packaged Groceries": {"multiplier": 0.38, "rating": "Medium-High", "icon": "🛒", "fact": "Multi-layer non-recyclable plastic packaging and industrial processing."},
    "Local / Organic Food": {"multiplier": 0.08, "rating": "Low Carbon", "icon": "🥗", "fact": "Zero air-freight logistics and organic regenerative soil practices."},
    "Home & Plastics": {"multiplier": 0.46, "rating": "High Carbon", "icon": "📦", "fact": "Virgin petroleum feedstocks and high-heat injection molding."},
    "Zero-Waste Reusables": {"multiplier": 0.07, "rating": "Minimal Impact", "icon": "🌿", "fact": "Durable steel and bamboo replace thousands of single-use disposables."},
}

ETHICAL_ALTERNATIVES = {
    "Fast Fashion Apparel": [
        {"brand": "Patagonia", "perk": "100% organic cotton, Fair Trade sewing & free repairs", "saving": "65%"},
        {"brand": "Depop / Thrift", "perk": "Extends existing garment life; 0 new factory emissions", "saving": "92%"},
    ],
    "Footwear & Leather": [
        {"brand": "Allbirds / Veja", "perk": "Sugarcane SweetFoam & wild Amazonian rubber", "saving": "52%"},
        {"brand": "Will's Vegan Store", "perk": "Bio-based agricultural waste; plastic-free packing", "saving": "70%"},
    ],
    "Consumer Electronics": [
        {"brand": "Back Market Refurbished", "perk": "Certified renew tech avoids toxic raw mining", "saving": "82%"},
        {"brand": "Fairphone Modular", "perk": "Modular build with 5-year guaranteed spare parts", "saving": "60%"},
    ],
    "Refurbished Tech": [
        {"brand": "Certified Renewed Hub", "perk": "Optimal circular loop! Extends hardware life by 3+ years", "saving": "Optimal"},
    ],
    "Second-Hand / Thrift": [
        {"brand": "Local Community Thrift", "perk": "Top-tier circular reuse; zero new factory footprint", "saving": "Optimal"},
    ],
    "Packaged Groceries": [
        {"brand": "Local Farmers Market", "perk": "Seasonal crops, zero air-miles & plastic-free baskets", "saving": "58%"},
        {"brand": "Bulk Food Co-op", "perk": "Bring-your-own container pantry essentials", "saving": "45%"},
    ],
    "Local / Organic Food": [
        {"brand": "Community CSA Farm", "perk": "Regenerative soil farming preserving local groundwater", "saving": "Optimal"},
    ],
    "Home & Plastics": [
        {"brand": "Zero-Waste Refill Station", "perk": "Refill bulk cleaners in reusable glass jars", "saving": "75%"},
        {"brand": "Bamboo & Steel Essentials", "perk": "Fast-growing renewable bamboo; fully biodegradable", "saving": "68%"},
    ],
    "Zero-Waste Reusables": [
        {"brand": "Circular Home Refill", "perk": "Gold standard zero-waste; keeps oceans clean", "saving": "Optimal"},
    ],
}

ECO_MASCOTS = {
    "Shelly the Sea Turtle 🐢": "Patience, wisdom & clean, plastic-free oceans",
    "Pip the Forest Fox 🦊": "Agile thrifting, clever reuse & finding vintage gems",
    "Barnaby the Eco Owl 🦉": "Science, footprint analytics & carbon budget discipline",
    "Bumble the Pollinator 🐝": "Local organic farmers, seasonal harvest & biodiversity",
    "Bao the Bamboo Panda 🐼": "Zero-waste reusables, gentle living & compostable goods",
}

ECO_TIPS = [
    "Buying a single cotton shirt second-hand saves ~2,700 liters of drinking water.",
    "Keeping your smartphone for 4 years instead of 2 cuts its manufacturing emissions by 50%.",
    "Package-free shampoo bars prevent roughly 3 plastic bottles from landfills each year.",
    "Refurbished laptops save up to 190 kg of CO₂ and 1,200 kg of raw mined minerals.",
    "Shopping at a local farmers market eliminates long-haul cold-chain logistics emissions.",
]

def render_animated_turtle_svg(mood="happy", width=180, height=180):
    is_worried = (mood == "worried")
    is_happy = (mood == "happy")
    shiver_class = "shiver" if is_worried else "bob"
    
    svg = f"""
    <svg width="{width}" height="{height}" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
    <style>
    @keyframes turtle-bob {{ 0%, 100% {{ transform: translateY(0px); }} 50% {{ transform: translateY(-7px); }} }}
    @keyframes flipper-wave-l {{ 0%, 100% {{ transform: rotate(0deg); }} 50% {{ transform: rotate(20deg); }} }}
    @keyframes flipper-wave-r {{ 0%, 100% {{ transform: rotate(0deg); }} 50% {{ transform: rotate(-20deg); }} }}
    @keyframes sprout-sway {{ 0%, 100% {{ transform: rotate(-7deg); }} 50% {{ transform: rotate(7deg); }} }}
    @keyframes eye-blink {{ 0%, 90%, 100% {{ transform: scaleY(1); }} 95% {{ transform: scaleY(0.1); }} }}
    @keyframes sweat-drip {{ 0% {{ opacity: 0; transform: translateY(-4px); }} 40% {{ opacity: 1; transform: translateY(0px); }} 80% {{ opacity: 0; transform: translateY(7px); }} 100% {{ opacity: 0; transform: translateY(7px); }} }}
    @keyframes turtle-shiver {{ 0%, 100% {{ transform: translate(0, 0); }} 25% {{ transform: translate(-2px, 1.5px); }} 75% {{ transform: translate(2px, -1.5px); }} }}
    .bob {{ animation: turtle-bob 2.2s ease-in-out infinite; transform-origin: center; }}
    .shiver {{ animation: turtle-shiver 0.25s infinite; }}
    .wave-l {{ animation: flipper-wave-l 1.5s ease-in-out infinite; transform-origin: 50px 85px; }}
    .wave-r {{ animation: flipper-wave-r 1.5s ease-in-out infinite; transform-origin: 150px 85px; }}
    .sprout {{ animation: sprout-sway 2s ease-in-out infinite; transform-origin: 100px 30px; }}
    .blink {{ animation: eye-blink 3.8s infinite; transform-origin: 100px 50px; }}
    .sweat {{ animation: sweat-drip 1.3s infinite; }}
    </style>
    <g class="{shiver_class}">
    <ellipse cx="60" cy="155" rx="15" ry="22" fill="#40916c" stroke="#1b4332" stroke-width="2.5" transform="rotate(-25 60 155)"/>
    <ellipse cx="140" cy="155" rx="15" ry="22" fill="#40916c" stroke="#1b4332" stroke-width="2.5" transform="rotate(25 140 155)"/>
    <polygon points="95,160 105,160 100,180" fill="#40916c" stroke="#1b4332" stroke-width="2"/>
    <g class="wave-l">
    <ellipse cx="48" cy="88" rx="17" ry="28" fill="#52b788" stroke="#1b4332" stroke-width="2.5" transform="rotate(-35 48 88)"/>
    </g>
    <g class="wave-r">
    <ellipse cx="152" cy="88" rx="17" ry="28" fill="#52b788" stroke="#1b4332" stroke-width="2.5" transform="rotate(35 152 88)"/>
    </g>
    <ellipse cx="100" cy="120" rx="54" ry="48" fill="#2d6a4f" stroke="#1b4332" stroke-width="3"/>
    <ellipse cx="100" cy="120" rx="42" ry="36" fill="#40916c" stroke="#1b4332" stroke-width="2"/>
    <ellipse cx="100" cy="120" rx="26" ry="22" fill="#74c69d" stroke="#2d6a4f" stroke-width="2"/>
    <ellipse cx="100" cy="55" rx="28" ry="26" fill="#74c69d" stroke="#1b4332" stroke-width="2.5"/>
    """

    if is_happy:
        svg += """
        <g class="sprout">
        <line x1="100" y1="30" x2="100" y2="14" stroke="#1b4332" stroke-width="2.5"/>
        <ellipse cx="94" cy="12" rx="7" ry="4.5" fill="#52b788" stroke="#1b4332" stroke-width="1.5" transform="rotate(-30 94 12)"/>
        <ellipse cx="106" cy="12" rx="7" ry="4.5" fill="#52b788" stroke="#1b4332" stroke-width="1.5" transform="rotate(30 106 12)"/>
        </g>
        <g class="blink">
        <circle cx="89" cy="49" r="5" fill="#1b4332"/>
        <circle cx="87" cy="47" r="1.8" fill="#ffffff"/>
        <circle cx="111" cy="49" r="5" fill="#1b4332"/>
        <circle cx="109" cy="47" r="1.8" fill="#ffffff"/>
        </g>
        <ellipse cx="81" cy="61" rx="5.5" ry="3.5" fill="#fb7185" opacity="0.6"/>
        <ellipse cx="119" cy="61" rx="5.5" ry="3.5" fill="#fb7185" opacity="0.6"/>
        <path d="M 88 61 Q 100 73 112 61" fill="none" stroke="#1b4332" stroke-width="3" stroke-linecap="round"/>
        """
    elif is_worried:
        svg += """
        <circle cx="89" cy="52" r="5.5" fill="#1b4332"/>
        <circle cx="111" cy="52" r="5.5" fill="#1b4332"/>
        <path d="M 89 67 Q 100 58 111 67" fill="none" stroke="#1b4332" stroke-width="2.8" stroke-linecap="round"/>
        <g class="sweat">
        <path d="M 124 38 Q 128 47 124 51 Q 120 47 124 38" fill="#38bdf8" stroke="#0284c7" stroke-width="1.2"/>
        </g>
        """
    else:
        svg += """
        <g class="sprout">
        <line x1="100" y1="30" x2="100" y2="16" stroke="#1b4332" stroke-width="2"/>
        <ellipse cx="94" cy="14" rx="6" ry="4" fill="#52b788" stroke="#1b4332" stroke-width="1.5" transform="rotate(-30 94 14)"/>
        <ellipse cx="106" cy="14" rx="6" ry="4" fill="#52b788" stroke="#1b4332" stroke-width="1.5" transform="rotate(30 106 14)"/>
        </g>
        <path d="M 84 50 Q 89 44 94 50" fill="none" stroke="#1b4332" stroke-width="2.5" stroke-linecap="round"/>
        <path d="M 106 50 Q 111 44 116 50" fill="none" stroke="#1b4332" stroke-width="2.5" stroke-linecap="round"/>
        <path d="M 91 63 Q 100 69 109 63" fill="none" stroke="#1b4332" stroke-width="2.2" stroke-linecap="round"/>
        """

    svg += "</g></svg>"
    return svg

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
    tree_months = round((carbon_kg / 21.0) * 12, 1)
    return f"🚗 ~{miles:,} petrol miles • 📱 ~{charges:,} phone charges • 🌲 {tree_months} tree-months"

def evaluate_badges(purchases, overrides=None):
    if overrides is None: overrides = {}
    total_items = len(purchases)
    total_spend = sum(p["price"] for p in purchases)
    total_co2 = sum(p["carbon_kg"] for p in purchases)
    ethical_count = sum(1 for p in purchases if p.get("is_ethical", False))
    avg_intensity = (total_co2 / total_spend) if total_spend > 0 else 0.0
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
        badges[5]["unlocked"] = sum(1 for b in badges[:5] if b["unlocked"]) >= 4 and total_co2 <= st.session_state.carbon_budget and total_items > 0
        badges[5]["progress"] = f"{sum(1 for b in badges[:5] if b['unlocked'])}/4 badges"
    else:
        badges[5]["progress"] = "Demo override"
    return badges, total_spend, total_co2, avg_intensity, co2_saved, ethical_count

# Session state initialization - Starts completely CLEAN with zero seed data
if "onboarded" not in st.session_state: st.session_state.onboarded = False
if "user_name" not in st.session_state: st.session_state.user_name = "Parth Gajera"
if "user_mascot" not in st.session_state: st.session_state.user_mascot = "Shelly the Sea Turtle 🐢"
if "carbon_budget" not in st.session_state: st.session_state.carbon_budget = 150
if "recent_art" not in st.session_state: st.session_state.recent_art = "leaf"
if "mascot_mood" not in st.session_state: st.session_state.mascot_mood = "happy"
if "mascot_message" not in st.session_state: st.session_state.mascot_message = "Welcome! I am Shelly, your conscious shopping guide!"
if "badge_overrides" not in st.session_state: st.session_state.badge_overrides = {}
if "nav_view" not in st.session_state: st.session_state.nav_view = "📊 Dashboard"
if "last_logged" not in st.session_state: st.session_state.last_logged = None
if "purchases" not in st.session_state: st.session_state.purchases = []

# ------------------------------------------------------------------------------
# SCREEN 1: WELCOME & ONBOARDING (Clean, Visual, Standalone First-Run)
# ------------------------------------------------------------------------------
if not st.session_state.onboarded:
    render_html("<h1 style='text-align: center; color: #1b4332; margin-top: 1rem; margin-bottom: 0;'>🌱 Meet ShopImpact</h1><p style='text-align: center; color: #64748b; font-size: 1.15rem; margin-bottom: 2.2rem;'>Your playful, conscious shopping companion.</p>")

    c1, c2 = st.columns([1.1, 0.9], gap="large")
    with c1:
        st.subheader("Set Your Goals & Avatar")
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
        render_html(render_animated_turtle_svg("happy", 220, 220))
        render_html("""
        <div style="background: #f0fdf4; border: 1.5px solid #a7f3d0; border-radius: 14px; padding: 1.1rem; color: #166534; margin-top: 0.8rem;">
            <strong>What you'll experience inside:</strong>
            <ul style="margin: 0.5rem 0 0 1.2rem; padding: 0; line-height: 1.6;">
                <li>⚡ <strong>Live Carbon Preview:</strong> calculate footprint as you type</li>
                <li>🔄 <strong>Dynamic Swaps:</strong> get greener brand recommendations right after logging</li>
                <li>🏆 <strong>Wall of Badges:</strong> watch gray badges turn into glowing colors</li>
                <li>🐢 <strong>Live Mascot:</strong> Shelly smiles, bobs, and waves at your choices!</li>
            </ul>
        </div>
        """)

# ------------------------------------------------------------------------------
# SCREEN 2: MAIN DASHBOARD & TABS
# ------------------------------------------------------------------------------
else:
    # Sidebar
    st.sidebar.markdown(f"### 👤 {st.session_state.user_name}")
    st.sidebar.caption(f"{st.session_state.user_mascot} • Goal: {st.session_state.carbon_budget} kg")
    if st.sidebar.button("⚙️ Edit Profile / Goals", use_container_width=True):
        st.session_state.onboarded = False
        st.rerun()

    st.sidebar.markdown("---")
    st.session_state.nav_view = st.sidebar.radio("Navigation:", ["📊 Dashboard", "🏆 Wall of Badges", "🎨 Turtle Studio"])

    dark_theme = st.sidebar.toggle("🌙 High-Contrast Dark Mode", value=False)
    st.sidebar.markdown("---")
    st.sidebar.caption(f"💡 *{random.choice(ECO_TIPS)}*")

    c_rst1, c_rst2 = st.sidebar.columns(2)
    with c_rst1:
        if st.button("📥 Load Demo", help="Populates 12 test transactions for demo evaluation", use_container_width=True):
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
            st.session_state.last_logged = st.session_state.purchases[-1]
            st.rerun()
    with c_rst2:
        if st.button("🗑️ Clear All", use_container_width=True):
            st.session_state.purchases = []
            st.session_state.last_logged = None
            st.session_state.badge_overrides = {}
            st.rerun()

    # High-Contrast Complete Theme Engine
    if dark_theme:
        render_html("""
        <style>
        .stApp { background-color: #0c120e !important; color: #f8fafc !important; }
        h1, h2, h3, h4, h5, p, span, label { color: #f8fafc !important; }
        .preview-box { background: #13271c !important; border: 1.5px solid #34d399 !important; border-radius: 12px; padding: 0.9rem 1.2rem; color: #f8fafc !important; }
        .swap-card { background: #152219 !important; border: 1.5px solid #2d3e32 !important; border-radius: 12px; padding: 1rem; color: #f8fafc !important; margin-bottom: 0.5rem; }
        .badge-on { background: linear-gradient(135deg, #064e3b, #047857) !important; border: 2px solid #34d399 !important; border-radius: 14px; padding: 1rem; color: #ffffff !important; margin-bottom: 0.8rem; }
        .badge-off { background: #1e293b !important; border: 2px dashed #475569 !important; border-radius: 14px; padding: 1rem; color: #94a3b8 !important; filter: grayscale(100%); opacity: 0.6; margin-bottom: 0.8rem; }
        .reaction-bubble { border-radius: 14px; padding: 1rem 1.3rem; margin-top: 0.6rem; border: 1.5px solid #34d399; background: #162a1e; color: #f8fafc; }
        </style>
        """)
    else:
        render_html("""
        <style>
        .stApp { background-color: #fafaf9 !important; color: #0f172a !important; }
        h1, h2, h3, h4, h5, p, span, label { color: #0f172a !important; }
        .preview-box { background: #f0fdf4 !important; border: 1.5px solid #86efac !important; border-radius: 12px; padding: 0.9rem 1.2rem; color: #14532d !important; }
        .swap-card { background: #ffffff !important; border: 1.5px solid #e2e8f0 !important; border-radius: 12px; padding: 1rem; color: #0f172a !important; box-shadow: 0 2px 8px rgba(0,0,0,0.04); margin-bottom: 0.5rem; }
        .badge-on { background: linear-gradient(135deg, #1b4332, #2d6a4f) !important; border: 2px solid #52b788 !important; border-radius: 14px; padding: 1rem; color: #ffffff !important; box-shadow: 0 4px 14px rgba(45,106,79,0.18); margin-bottom: 0.8rem; }
        .badge-off { background: #f1f5f9 !important; border: 2px dashed #cbd5e1 !important; border-radius: 14px; padding: 1rem; color: #64748b !important; filter: grayscale(100%); opacity: 0.6; margin-bottom: 0.8rem; }
        .reaction-bubble { border-radius: 14px; padding: 1rem 1.3rem; margin-top: 0.6rem; border: 1.5px solid #86efac; background: #f0fdf4; color: #14532d; }
        </style>
        """)

    # --------------------------------------------------------------------------
    # VIEW: 📊 DASHBOARD
    # --------------------------------------------------------------------------
    if st.session_state.nav_view == "📊 Dashboard":
        col_m1, col_m2 = st.columns([0.65, 3.35])
        with col_m1:
            render_html(render_animated_turtle_svg(st.session_state.mascot_mood, 140, 140))
        with col_m2:
            render_html(f"""
            <div class="reaction-bubble">
                <div style="font-size: 1.1rem; font-weight: 800;">{st.session_state.user_mascot.split()[0]}'s Live Reaction:</div>
                <div style="font-size: 0.95rem; margin-top: 0.2rem;">"{st.session_state.mascot_message}"</div>
            </div>
            """)

        st.markdown("<br>", unsafe_allow_html=True)

        # Log a Purchase Form
        st.subheader("🛒 Log a Planned Purchase")
        with st.form("quick_log_form", clear_on_submit=True):
            f1, f2, f3 = st.columns([1.2, 1.2, 1.0])
            with f1:
                item_name = st.text_input("Item Description", placeholder="e.g. Vintage Denim Jacket, USB Charger")
                cat_choice = st.selectbox("Product Category", options=list(CATEGORIES.keys()))
            with f2:
                brand_val = st.text_input("Brand or Vendor", placeholder="e.g. Patagonia, Zara, Back Market")
                price_val = st.number_input("Price ($)", min_value=1.0, max_value=5000.0, value=45.0, step=5.0)
            with f3:
                date_val = st.date_input("Date", value=date.today())
                is_eth = st.checkbox("🌱 Certified Circular / Thrift / Ethical", help="Applies a 30% footprint discount for verified reuse or certified clean logistics.")

            live_co2 = calculate_carbon(price_val, cat_choice, is_eth)
            equiv_msg = get_equivalency(live_co2)
            c_info = CATEGORIES[cat_choice]
            discount_note = "30% Eco Discount applied" if is_eth else "Standard lifecycle factor"
            
            render_html(f"""
            <div class="preview-box">
                <strong>⚡ Live Lifecycle Calculation:</strong> <code>${price_val:.2f} × {c_info['multiplier']} kg/$ = {live_co2} kg CO₂e</code> ({discount_note})<br>
                <span style="font-size: 0.86rem;">📊 Impact Context: {equiv_msg} • <em>{c_info['fact']}</em></span>
            </div>
            """)

            if st.form_submit_button("🌿 Record Purchase in Dashboard", use_container_width=True):
                if not item_name.strip():
                    st.error("Please enter an item name before recording.")
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
                    st.session_state.last_logged = new_rec
                    if is_eth or live_co2 < 4.0:
                        st.session_state.mascot_mood = "happy"
                        st.session_state.mascot_message = f"Woohoo! Loving your green choice of '{item_name}'! Shelly is waving happily!"
                        st.balloons()
                    else:
                        st.session_state.mascot_mood = "worried"
                        st.session_state.mascot_message = f"Careful! '{item_name}' added {live_co2} kg CO₂e. Check the greener swaps below for your next purchase!"
                    st.rerun()

        # Contextual Greener Swaps: Appears reactively right after a purchase is logged
        if st.session_state.last_logged:
            last = st.session_state.last_logged
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader(f"🌱 Greener Alternatives for '{last['item']}' ({last['category']})")
            
            sc1, sc2 = st.columns([1.1, 2.0], gap="medium")
            with sc1:
                render_html(render_animated_turtle_svg("happy", 130, 130))
                st.caption(f"💡 **Shelly's Tip**: You logged **{last['carbon_kg']} kg CO₂e**. Adopting a verified circular swap can reduce emissions by up to 92%!")
            
            with sc2:
                swaps = ETHICAL_ALTERNATIVES.get(last["category"], [])
                sw_cols = st.columns(len(swaps))
                for idx, sw in enumerate(swaps):
                    with sw_cols[idx]:
                        render_html(f"""
                        <div class="swap-card">
                            <strong>{sw['brand']}</strong><br>
                            <span style="font-size: 0.85rem;">{sw['perk']}</span><br>
                            <span style="color: #10b981; font-weight: 700; font-size: 0.82rem;">⚡ Carbon Cut: {sw['saving']}</span>
                        </div>
                        """)
                        b_name = sw['brand'].split('/')[0].strip()
                        if st.button(f"Adopt {b_name} 🌿", key=f"adopt_swap_{idx}"):
                            st.session_state.purchases.append({
                                "id": len(st.session_state.purchases) + 1,
                                "item": f"Greener Swap: {b_name} ({last['category']})",
                                "category": last['category'],
                                "brand": b_name,
                                "price": 35.0,
                                "carbon_kg": calculate_carbon(35.0, last['category'], True),
                                "date": str(date.today()),
                                "is_ethical": True,
                            })
                            st.session_state.mascot_mood = "happy"
                            st.session_state.mascot_message = f"Brilliant choice! You adopted {b_name} and protected the planet!"
                            st.balloons()
                            st.rerun()

        st.markdown("---")

        # Period Filter: Supports All Time, Filter by Year, and Filter by Month
        if st.session_state.purchases:
            all_years = sorted(list({p["date"][:4] for p in st.session_state.purchases}), reverse=True)
            all_months = sorted(list({p["date"][:7] for p in st.session_state.purchases}), reverse=True)
            filter_choices = ["All Time"] + [f"Year {y}" for y in all_years] + all_months
        else:
            filter_choices = ["All Time"]

        st.markdown("##### 📅 Dashboard Timeline Filter:")
        period_choice = st.radio("Period", filter_choices, horizontal=True, label_visibility="collapsed")

        if period_choice == "All Time":
            filtered_data = st.session_state.purchases
            period_label = "All Time (Cumulative)"
        elif period_choice.startswith("Year "):
            sel_yr = period_choice.replace("Year ", "")
            filtered_data = [p for p in st.session_state.purchases if p["date"].startswith(sel_yr)]
            period_label = f"Year {sel_yr}"
        else:
            filtered_data = [p for p in st.session_state.purchases if p["date"].startswith(period_choice)]
            period_label = period_choice

        badges, spend_tot, co2_tot, avg_int, saved_tot, eth_cnt = evaluate_badges(filtered_data, st.session_state.badge_overrides)
        trees_tot = round(co2_tot / 21.0, 1)

        # 4 Primary KPI Cards using clean native Streamlit metrics
        st.markdown("<br>", unsafe_allow_html=True)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Spend", f"${spend_tot:,.2f}", f"{len(filtered_data)} items recorded")
        m2.metric("Carbon Footprint", f"{co2_tot:.1f} kg", f"{avg_int:.2f} kg/$ intensity", delta_color="inverse")
        m3.metric("Carbon Avoided", f"{saved_tot:.1f} kg", "Vs standard 0.45 kg/$")
        m4.metric("Trees to Offset", f"{trees_tot} Trees", "21 kg CO₂/tree/year", delta_color="inverse")

        st.markdown("<br>", unsafe_allow_html=True)
        b_lim = st.session_state.carbon_budget
        pct = min(100, int((co2_tot / b_lim) * 100)) if b_lim > 0 else 0
        st.progress(pct / 100, text=f"Carbon Allowance Budget: {co2_tot:.1f} / {b_lim} kg CO₂e ({pct}% used — {period_label})")

        # Category Chart & Ledger Table
        col_g1, col_g2 = st.columns([1.1, 1.3], gap="large")
        with col_g1:
            st.markdown(f"**Emissions by Category ({period_label})**")
            if filtered_data:
                df = pd.DataFrame(filtered_data)
                st.bar_chart(df.groupby("category")["carbon_kg"].sum().sort_values(ascending=False), color="#2d6a4f")
            else:
                st.info("No purchases recorded yet for this period. Plan and log your first purchase above!")

        with col_g2:
            st.markdown(f"**Transaction Ledger ({len(filtered_data)} records)**")
            if filtered_data:
                df_view = pd.DataFrame(filtered_data)[["date", "item", "category", "price", "carbon_kg", "is_ethical"]]
                df_view.columns = ["Date", "Item", "Category", "Price ($)", "CO₂ (kg)", "Ethical?"]
                st.dataframe(df_view, use_container_width=True, hide_index=True)
                st.download_button("📥 Export CSV", df_view.to_csv(index=False).encode("utf-8"), f"shopimpact_{period_label.lower().replace(' ', '_')}.csv", "text/csv")
            else:
                st.caption("No records available to export. Your recorded purchases will appear here.")

    # --------------------------------------------------------------------------
    # VIEW: 🏆 WALL OF BADGES
    # --------------------------------------------------------------------------
    elif st.session_state.nav_view == "🏆 Wall of Badges":
        st.title("🏆 Wall of Badges & Eco Fame")
        st.caption("Unlocked achievements glow in full vibrant color. Locked badges stay in black & white until earned!")

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
                    render_html(f"""
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
                    """)
                else:
                    render_html(f"""
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
                    """)

    # --------------------------------------------------------------------------
    # VIEW: 🎨 TURTLE STUDIO
    # --------------------------------------------------------------------------
    elif st.session_state.nav_view == "🎨 Turtle Studio":
        st.title("🎨 Turtle Vector Studio")
        st.caption("Live animated SVG mascot and pure Python vector Turtle graphics drawn natively onto PIL canvases.")

        a_col1, a_col2 = st.columns([1.0, 1.2], gap="large")
        with a_col1:
            u_init = st.session_state.user_name.strip()[0] if st.session_state.user_name.strip() else "P"
            opts = ["mascot_happy", "mascot_worried", "mascot_mindful", "leaf", "footprint", "badge", "seal"]
            labels = {
                "mascot_happy": "🐢 Shelly Animated (Happy & Celebrating)",
                "mascot_worried": "💧 Shelly Animated (Worried & Sweating)",
                "mascot_mindful": "🌱 Shelly Animated (Calm & Mindful)",
                "leaf": "🌿 Procedural Eco Leaf",
                "footprint": "👣 Low Carbon Footprint",
                "badge": "⭐ Achievement Rosette",
                "seal": f"🛡️ {u_init}'s Personal Avatar Seal",
            }
            pick = st.radio("Choose artwork:", opts, format_func=lambda x: labels[x])

        with a_col2:
            if pick.startswith("mascot_"):
                mood = pick.replace("mascot_", "")
                render_html(render_animated_turtle_svg(mood, 220, 220))
                st.caption(f"Live 60 FPS Animated Vector SVG: {labels[pick]}")
            else:
                out_img = draw_vector_art(pick, u_init)
                st.image(out_img, width=260, caption=f"Headless Turtle Canvas: {labels[pick]}")
                import io
                buf = io.BytesIO()
                out_img.save(buf, format="PNG")
                st.download_button("💾 Download Artwork (PNG)", buf.getvalue(), f"turtle_{pick}.png", "image/png")

st.divider()
render_html("""
<div style="text-align: center; color: #64748b; font-size: 0.8rem; padding: 0.8rem 0;">
    <strong>ShopImpact Conscious Shopping Dashboard</strong> • Summative Assessment (60 Marks)<br>
    Candidate: <strong>Parth Pravinbhai Gajera</strong> (ID: <code>1000544</code>) • CRS: Artificial Intelligence • IDAI 102
</div>
""")
