"""
ShopImpact — Conscious Shopping Dashboard
=========================================
Course: IDAI 102 (Python Programming) — Summative Assessment (SA)
Candidate: Parth Pravinbhai Gajera (ID: 1000544)
CRS: Artificial Intelligence

Engineering Doctrine: Senior Developer Pragmatism (Ponytail Method)
- Single self-contained module (app.py)
- Modular business logic separated from presentation
- Headless pure-Python Turtle graphics engine
- Real-time emissions calculator and monthly dashboard
"""

import math
import random
from datetime import date, datetime
import pandas as pd
from PIL import Image, ImageDraw
import streamlit as st

# ==============================================================================
# 1. PAGE CONFIGURATION & ACCESSIBLE STYLING
# ==============================================================================
st.set_page_config(
    page_title="ShopImpact — Conscious Shopping Dashboard",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar: Accessible Dark Mode Toggle (Brief Stage 1 Optional Feature P065)
dark_mode = st.sidebar.toggle("🌙 High-Contrast Dark Mode", value=False)

if dark_mode:
    theme_css = """
    <style>
    :root {
        --bg-main: #0f1711;
        --bg-card: #18231c;
        --border-color: #2b3d30;
        --text-primary: #ecfdf5;
        --text-secondary: #a7f3d0;
        --accent-green: #34d399;
        --accent-gold: #fbbf24;
    }
    .stApp {
        background-color: var(--bg-main);
        color: var(--text-primary);
    }
    .kpi-card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 14px;
        padding: 1.1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    .alt-card {
        background: #142a1e;
        border: 1px solid #059669;
        border-radius: 12px;
        padding: 0.9rem;
    }
    .badge-card {
        background: var(--bg-card);
        border: 1.5px solid var(--border-color);
        border-radius: 12px;
        padding: 0.8rem 1rem;
        margin-bottom: 0.6rem;
    }
    .badge-unlocked {
        border-color: #10b981;
        background: #064e3b;
    }
    .tip-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 0.9rem;
    }
    </style>
    """
else:
    theme_css = """
    <style>
    :root {
        --bg-main: #fcfbf7;
        --bg-card: #ffffff;
        --border-color: #e2e8f0;
        --text-primary: #1b382b;
        --text-secondary: #475569;
        --accent-green: #2d6a4f;
        --accent-gold: #d97706;
    }
    .stApp {
        background-color: var(--bg-main);
        color: var(--text-primary);
    }
    .kpi-card {
        background: var(--bg-card);
        border: 1px solid #d1e7dd;
        border-radius: 14px;
        padding: 1.1rem;
        box-shadow: 0 3px 10px rgba(45, 106, 79, 0.05);
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
        margin-bottom: 0.6rem;
    }
    .badge-unlocked {
        border-color: #52b788;
        background: #f7fee7;
    }
    .tip-card {
        background: #f0f9ff;
        border: 1px solid #bae6fd;
        border-radius: 12px;
        padding: 0.9rem;
    }
    </style>
    """

st.markdown(theme_css, unsafe_allow_html=True)

# ==============================================================================
# 2. KNOWLEDGE BASE: CATEGORIES, MULTIPLIERS & GREEN ALTERNATIVES
# ==============================================================================
# Curated emission intensity multipliers (kg CO2e per dollar spent)
# Based on lifecycle assessments (raw material extraction to consumer end-of-life)
CATEGORIES = {
    "Fast Fashion Apparel": {"multiplier": 0.42, "rating": "High", "icon": "👗"},
    "Footwear & Leather": {"multiplier": 0.65, "rating": "Very High", "icon": "👞"},
    "Consumer Electronics": {"multiplier": 0.55, "rating": "High", "icon": "📱"},
    "Refurbished Electronics": {"multiplier": 0.11, "rating": "Low", "icon": "♻️"},
    "Second-Hand / Thrift": {"multiplier": 0.05, "rating": "Minimal", "icon": "🧥"},
    "Groceries (Packaged / Meat)": {"multiplier": 0.38, "rating": "Medium-High", "icon": "🛒"},
    "Groceries (Local / Organic)": {"multiplier": 0.08, "rating": "Low", "icon": "🥗"},
    "Home & Plastic Wares": {"multiplier": 0.46, "rating": "High", "icon": "📦"},
    "Zero-Waste Reusables": {"multiplier": 0.07, "rating": "Minimal", "icon": "🌿"},
}

ETHICAL_ALTERNATIVES = {
    "Fast Fashion Apparel": [
        {"brand": "Patagonia", "perk": "100% GOTS Organic Cotton; Ironclad Repair Guarantee", "saving": "65%"},
        {"brand": "Depop / Vinted", "perk": "Pre-loved fashion; zero new textile manufacturing emissions", "saving": "92%"},
    ],
    "Footwear & Leather": [
        {"brand": "Allbirds / Veja", "perk": "Sugarcane SweetFoam & wild Amazonian natural rubber", "saving": "52%"},
        {"brand": "Will's Vegan Store", "perk": "Bio-based cereal crops; eliminates toxic chrome tanning", "saving": "70%"},
    ],
    "Consumer Electronics": [
        {"brand": "Back Market", "perk": "Certified refurbished tech; avoids heavy mineral mining", "saving": "82%"},
        {"brand": "Fairphone", "perk": "Fully modular, repairable smartphone with 5-year spare parts", "saving": "60%"},
    ],
    "Refurbished Electronics": [
        {"brand": "Direct Manufacturer Refurbished", "perk": "Outstanding choice! Circular electronics loop active", "saving": "Optimal"},
    ],
    "Second-Hand / Thrift": [
        {"brand": "Local Community Charity Shops", "perk": "Top-tier circular economy; zero new packaging or shipping", "saving": "Optimal"},
    ],
    "Groceries (Packaged / Meat)": [
        {"brand": "Local Farmer's Market", "perk": "Zero air-miles, seasonal crops, plastic-free baskets", "saving": "58%"},
        {"brand": "Bulk Food Co-op", "perk": "Bring-your-own-container package-free whole grains", "saving": "45%"},
    ],
    "Groceries (Local / Organic)": [
        {"brand": "Community CSA Farm Box", "perk": "Soil-regenerative farming without chemical nitrates", "saving": "Optimal"},
    ],
    "Home & Plastic Wares": [
        {"brand": "Zero-Waste Refill Stations", "perk": "Bulk refills in existing bottles; eliminates single-use plastics", "saving": "75%"},
        {"brand": "Bamboo & Stainless Steel Essentials", "perk": "Rapidly renewable raw materials; biodegrades cleanly", "saving": "68%"},
    ],
    "Zero-Waste Reusables": [
        {"brand": "Circular Home Refill", "perk": "Gold standard sustainability! Keeps oceans plastic-free", "saving": "Optimal"},
    ],
}

ECO_TIPS = [
    "Buying a single cotton shirt second-hand saves approximately 2,700 liters of fresh water.",
    "Keeping your smartphone for 4 years instead of 2 cuts its lifecycle carbon footprint by nearly 50%.",
    "Opting for package-free soap bars eliminates roughly 1.5 kg of household plastic waste annually.",
    "Refurbished laptops save up to 190 kg of CO2 equivalent emissions and 1,200 kg of mined raw minerals.",
    "Shopping at a local farmers market eliminates long-haul cold-chain transport emissions.",
    "Bamboo reaches full harvest maturity in just 3-5 years, requiring zero chemical fertilizers.",
]

SUSTAINABLE_QUOTES = [
    "“The greatest threat to our planet is the belief that someone else will save it.” — Robert Swan",
    "“We do not inherit the Earth from our ancestors; we borrow it from our children.” — Native Proverb",
    "“Small acts, when multiplied by millions of people, can transform the world.” — Howard Zinn",
    "“There is no such thing as ‘away’. When we throw anything away it must go somewhere.” — Annie Leonard",
    "“Refuse what you do not need; reduce what you do need; reuse what you consume.” — Bea Johnson",
]

# ==============================================================================
# 3. HEADLESS VECTOR TURTLE GRAPHICS ENGINE
# ==============================================================================
# Why: Streamlit Cloud runs on headless Linux containers without graphical Tkinter displays.
# This engine translates turtle geometry primitives onto a PIL RGBA canvas for web safety.
class HeadlessTurtle:
    """Pure-Python vector turtle engine safe for headless web environments."""
    def __init__(self, width=300, height=300):
        self.width = width
        self.height = height
        self.image = Image.new("RGBA", (width, height), (255, 255, 255, 0))
        self.draw = ImageDraw.Draw(self.image)
        self.x = width / 2
        self.y = height / 2
        self.heading = 90  # 90 = facing upward
        self.pen_down = True
        self.pen_color = (45, 106, 79, 255)
        self.pen_width = 3

    def forward(self, distance):
        rad = math.radians(self.heading)
        nx = self.x + distance * math.cos(rad)
        ny = self.y - distance * math.sin(rad)
        if self.pen_down:
            self.draw.line([(self.x, self.y), (nx, ny)], fill=self.pen_color, width=self.pen_width)
        self.x = nx
        self.y = ny

    def left(self, angle):
        self.heading = (self.heading + angle) % 360

    def right(self, angle):
        self.heading = (self.heading - angle) % 360

    def penup(self):
        self.pen_down = False

    def pendown(self):
        self.pen_down = True

    def goto(self, x, y):
        if self.pen_down:
            self.draw.line([(self.x, self.y), (x, y)], fill=self.pen_color, width=self.pen_width)
        self.x = x
        self.y = y

    def circle_arc(self, radius, extent, steps=18):
        """Draws a smooth curve arc using incremental heading turns."""
        step_len = (2 * math.pi * radius * (abs(extent) / 360.0)) / steps
        step_angle = extent / steps
        for _ in range(steps):
            self.forward(step_len)
            self.left(step_angle)


def draw_turtle_art(art_type="leaf"):
    """Draws procedural vector artwork using Turtle geometry primitives (P060)."""
    t = HeadlessTurtle(300, 300)

    if art_type == "leaf":
        # Procedural Eco Leaf
        t.penup(); t.goto(150, 260); t.heading = 90
        t.pen_color = (64, 145, 108, 255); t.pen_width = 4; t.pendown()
        t.forward(45)  # Stem

        # Left lobe curve
        t.pen_color = (45, 106, 79, 255); t.pen_width = 3
        t.circle_arc(100, 58, steps=20)
        t.left(122)
        t.circle_arc(100, 58, steps=20)

        # Center spine
        t.penup(); t.goto(150, 215); t.heading = 90
        t.pen_color = (82, 183, 136, 255); t.pen_width = 2; t.pendown()
        t.forward(95)

        # Branching veins
        for y, angle in [(185, 45), (185, 135), (155, 45), (155, 135), (125, 45), (125, 135)]:
            t.penup(); t.goto(150, y); t.heading = angle; t.pendown(); t.forward(20)

        # Turtle tip avatar
        t.penup(); t.goto(150, 65)
        t.draw.ellipse([(144, 59), (156, 71)], fill=(116, 198, 157, 255), outline=(27, 67, 50, 255))

    elif art_type == "footprint":
        # Procedural Carbon Footprint
        t.pen_color = (45, 106, 79, 255); t.pen_width = 3
        t.penup(); t.goto(150, 240); t.heading = 90; t.pendown()
        t.circle_arc(70, 40, steps=12)
        t.circle_arc(25, -50, steps=10)
        t.circle_arc(60, 70, steps=16)
        t.circle_arc(40, 90, steps=14)
        t.circle_arc(90, 45, steps=14)
        t.circle_arc(35, 80, steps=14)
        t.goto(150, 240)
        # Toes
        toes = [(126, 88, 9), (142, 77, 11), (160, 80, 10), (176, 88, 8), (190, 100, 7)]
        for tx, ty, r in toes:
            t.draw.ellipse([(tx-r, ty-r), (tx+r, ty+r)], fill=(82, 183, 136, 220), outline=(45, 106, 79, 255), width=2)

    else:
        # Procedural Eco Award Badge
        t.pen_color = (217, 119, 6, 255); t.pen_width = 3
        t.penup(); t.goto(150, 130); t.heading = 0
        t.draw.ellipse([(90, 70), (210, 190)], fill=(254, 243, 199, 230), outline=(217, 119, 6, 255), width=3)
        t.draw.ellipse([(105, 85), (195, 175)], fill=(236, 253, 245, 230), outline=(5, 150, 105, 255), width=2)
        # Ribbons
        t.penup(); t.goto(130, 185); t.heading = 250; t.pendown(); t.pen_color = (5, 150, 105, 255)
        t.forward(65); t.left(120); t.forward(25); t.left(120); t.forward(60)
        t.penup(); t.goto(170, 185); t.heading = 290; t.pendown()
        t.forward(65); t.right(120); t.forward(25); t.right(120); t.forward(60)

    return t.image


# ==============================================================================
# 4. DATA ENGINE: CALCULATIONS, BADGES & SEED INITIALIZATION
# ==============================================================================
def init_session_state():
    """Seeds 12 diverse realistic transactions covering cheap/expensive & eco/non-eco."""
    if "purchases" not in st.session_state:
        st.session_state.purchases = [
            {"id": 1, "item": "Organic Hemp Jacket", "category": "Fast Fashion Apparel", "brand": "Patagonia", "price": 120.0, "carbon_kg": 35.28, "date": "2026-10-02", "is_ethical": True},
            {"id": 2, "item": "Graphic Polyester T-Shirt", "category": "Fast Fashion Apparel", "brand": "Shein", "price": 18.0, "carbon_kg": 7.56, "date": "2026-10-05", "is_ethical": False},
            {"id": 3, "item": "Refurbished iPad Mini", "category": "Refurbished Electronics", "brand": "Back Market", "price": 280.0, "carbon_kg": 21.56, "date": "2026-10-10", "is_ethical": True},
            {"id": 4, "item": "Leather Oxford Shoes", "category": "Footwear & Leather", "brand": "Zara", "price": 110.0, "carbon_kg": 71.50, "date": "2026-10-14", "is_ethical": False},
            {"id": 5, "item": "Thrifted Denim Jacket", "category": "Second-Hand / Thrift", "brand": "Local Thrift", "price": 25.0, "carbon_kg": 0.88, "date": "2026-10-18", "is_ethical": True},
            {"id": 6, "item": "Weekly Farm Fresh Veggies", "category": "Groceries (Local / Organic)", "brand": "Green Valley CSA", "price": 42.0, "carbon_kg": 2.35, "date": "2026-10-22", "is_ethical": True},
            {"id": 7, "item": "Single-Use Plastic Food Bins", "category": "Home & Plastic Wares", "brand": "Generic Mart", "price": 16.0, "carbon_kg": 7.36, "date": "2026-10-25", "is_ethical": False},
            {"id": 8, "item": "Bamboo Kitchen Cutlery Set", "category": "Zero-Waste Reusables", "brand": "EcoLiving", "price": 22.0, "carbon_kg": 1.08, "date": "2026-10-28", "is_ethical": True},
            {"id": 9, "item": "Winter Down Coat", "category": "Fast Fashion Apparel", "brand": "H&M", "price": 85.0, "carbon_kg": 35.70, "date": "2026-11-01", "is_ethical": False},
            {"id": 10, "item": "Noise Cancelling Headphones", "category": "Consumer Electronics", "brand": "Sony", "price": 190.0, "carbon_kg": 104.50, "date": "2026-11-03", "is_ethical": False},
            {"id": 11, "item": "Modular Phone Replacement Battery", "category": "Refurbished Electronics", "brand": "Fairphone", "price": 38.0, "carbon_kg": 2.93, "date": "2026-11-05", "is_ethical": True},
            {"id": 12, "item": "Organic Fair-Trade Coffee", "category": "Groceries (Local / Organic)", "brand": "Equator Organics", "price": 24.0, "carbon_kg": 1.34, "date": "2026-11-06", "is_ethical": True},
        ]

init_session_state()


def calculate_carbon(price: float, category: str, is_ethical: bool) -> float:
    """Calculates estimated CO2 emissions: price * multiplier, with 30% discount for green choices."""
    base_mult = CATEGORIES.get(category, {"multiplier": 0.35})["multiplier"]
    base_carbon = price * base_mult
    # Why: Reward verified circular or ethical brands with a 30% footprint discount
    final_carbon = base_carbon * 0.70 if is_ethical else base_carbon
    return round(final_carbon, 2)


def evaluate_badges(purchases):
    """Evaluates user transaction records to unlock milestone badges (P058)."""
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
            "progress": f"{min(total_items, 1)}/1 item",
        },
        {
            "id": "low_impact",
            "name": "Low Impact Shopper",
            "desc": "Maintained carbon intensity below 0.25 kg CO2/$.",
            "icon": "🥉",
            "unlocked": total_items >= 3 and avg_intensity <= 0.25,
            "progress": f"{avg_intensity:.2f} kg/$ (Goal: ≤0.25)",
        },
        {
            "id": "ethical_pioneer",
            "name": "Conscious Pioneer",
            "desc": "Chose 5 or more verified green alternatives or thrifted items.",
            "icon": "🥈",
            "unlocked": ethical_count >= 5,
            "progress": f"{ethical_count}/5 green choices",
        },
        {
            "id": "eco_saver",
            "name": "Eco Saver of the Month",
            "desc": "Kept cumulative carbon footprint under 220 kg with ≥8 items.",
            "icon": "🥇",
            "unlocked": total_items >= 8 and total_co2 <= 220.0,
            "progress": f"{total_co2:.1f} kg CO2 (Limit: ≤220)",
        },
        {
            "id": "zero_waste",
            "name": "Zero-Waste Champion",
            "desc": "Logged 2 or more zero-waste reusable or bulk purchases.",
            "icon": "🏆",
            "unlocked": sum(1 for p in purchases if "Zero-Waste" in p["category"] or "Thrift" in p["category"]) >= 2,
            "progress": f"{sum(1 for p in purchases if 'Zero-Waste' in p['category'] or 'Thrift' in p['category'])}/2 circular items",
        },
    ]
    return badges, total_spend, total_co2, avg_intensity, ethical_count


# ==============================================================================
# 5. SIDEBAR: TARGETS, SETTINGS & WISDOM
# ==============================================================================
st.sidebar.title("🌿 ShopImpact Control")

# Monthly Carbon Budget Goal (Slider Interactive Control)
carbon_budget = st.sidebar.slider(
    "🎯 Monthly Carbon Target (kg CO₂e)",
    min_value=50,
    max_value=400,
    value=180,
    step=10,
    help="Set your personal carbon allowance to keep your monthly impact sustainable.",
)

# Active Month Selection Filter
if st.session_state.purchases:
    available_months = sorted(list({p["date"][:7] for p in st.session_state.purchases}), reverse=True)
else:
    available_months = [date.today().strftime("%Y-%m")]

month_filter = st.sidebar.selectbox("📅 Filter by Month", options=["All Months"] + available_months)

st.sidebar.markdown("---")

# Motivational Quote Card (Brief Optional Feature P066)
st.sidebar.markdown(f"*{random.choice(SUSTAINABLE_QUOTES)}*")

st.sidebar.markdown("---")

# Demo State Management
if st.sidebar.button("🔄 Reload Demo Transaction Data", help="Restores the benchmark 12 test purchases"):
    st.session_state.purchases = []
    init_session_state()
    st.rerun()

if st.sidebar.button("🗑️ Clear All Transactions"):
    st.session_state.purchases = []
    st.rerun()


# ==============================================================================
# 6. HEADER & ACADEMIC DOSSIER
# ==============================================================================
col_title, col_dossier = st.columns([2.6, 1.4])

with col_title:
    st.title("🌱 ShopImpact — Conscious Shopping Dashboard")
    st.markdown(
        "**Transforming everyday consumer choices into measurable environmental impact.** "
        "Track planned purchases, estimate carbon footprints with curated lifecycle multipliers, and discover greener brand swaps."
    )

with col_dossier:
    st.markdown(
        """
        <div style="background: rgba(45, 106, 79, 0.08); border: 1px solid rgba(45, 106, 79, 0.25); border-radius: 12px; padding: 0.85rem 1rem; font-size: 0.83rem;">
            <strong>Parth Pravinbhai Gajera</strong> &bull; Registration: <code>1000544</code><br>
            <span style="color: #4b5563;">CRS: Artificial Intelligence | Course: Python Programming</span><br>
            <span style="color: #047857; font-weight: 600;">Status: Verified Single-File Architecture (app.py)</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()

# ==============================================================================
# 7. FILTERED METRICS & MONTHLY KPI CARDS
# ==============================================================================
all_purchases = st.session_state.purchases

if month_filter == "All Months":
    filtered_purchases = all_purchases
    period_label = "All Time"
else:
    filtered_purchases = [p for p in all_purchases if p["date"].startswith(month_filter)]
    period_label = month_filter

badges, total_spend, total_co2, avg_intensity, ethical_count = evaluate_badges(filtered_purchases)

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
bench_co2 = total_spend * 0.45  # Conventional unoptimized spending benchmark
co2_saved = max(0.0, round(bench_co2 - total_co2, 1))
trees_needed = round(total_co2 / 21.0, 1)  # 1 mature tree absorbs ~21kg CO2/year

with kpi1:
    st.metric(
        label=f"Total Spend ({period_label})",
        value=f"${total_spend:,.2f}",
        delta=f"{len(filtered_purchases)} Items Logged"
    )
with kpi2:
    st.metric(
        label=f"Estimated Footprint",
        value=f"{total_co2:.1f} kg CO₂e",
        delta=f"{avg_intensity:.2f} kg/$ intensity",
        delta_color="inverse"
    )
with kpi3:
    st.metric(
        label="Carbon Saved vs Standard",
        value=f"{co2_saved:.1f} kg CO₂",
        delta="Via Green Choices"
    )
with kpi4:
    st.metric(
        label="Trees Needed to Offset",
        value=f"{trees_needed} Trees",
        delta="21 kg/tree/yr absorption"
    )

# Carbon Budget Progress Indicator
budget_pct = min(100, int((total_co2 / carbon_budget) * 100)) if carbon_budget > 0 else 0
if budget_pct < 75:
    st.progress(budget_pct / 100, text=f"Carbon Allowance: {total_co2:.1f} / {carbon_budget} kg ({budget_pct}% used — Healthy Status 🌿)")
elif budget_pct < 100:
    st.progress(budget_pct / 100, text=f"Carbon Allowance: {total_co2:.1f} / {carbon_budget} kg ({budget_pct}% used — Approaching Ceiling ⚠️)")
else:
    st.progress(1.0, text=f"Carbon Allowance: {total_co2:.1f} / {carbon_budget} kg ({budget_pct}% used — Budget Exceeded! Consider Green Swaps 🚨)")

st.markdown("<br>", unsafe_allow_html=True)

# ==============================================================================
# 8. MAIN WORKSPACE: SPLIT SCREEN (INPUTS & ANALYTICS vs. TURTLE & BADGES)
# ==============================================================================
col_main, col_side = st.columns([1.8, 1.2], gap="large")

with col_main:
    # --------------------------------------------------------------------------
    # A. LOG PURCHASE FORM (Compulsory Features P055 & P056)
    # --------------------------------------------------------------------------
    st.subheader("🛒 Log a Planned Purchase")
    with st.form("purchase_form", clear_on_submit=True):
        f_left, f_right = st.columns(2)
        with f_left:
            item_name = st.text_input("Item Description", placeholder="e.g. Vintage Linen Shirt, Fairphone Battery")
            category_choice = st.selectbox(
                "Product Category",
                options=list(CATEGORIES.keys()),
                help="Each category maps to a researched lifecycle emission multiplier."
            )
            brand_name = st.text_input("Brand / Merchant", placeholder="e.g. Patagonia, Depop, Zara, Apple")

        with f_right:
            price_val = st.number_input("Purchase Price ($)", min_value=1.0, max_value=5000.0, value=50.0, step=5.0)
            purchase_date = st.date_input("Purchase Date", value=date.today())
            is_ethical_flag = st.checkbox(
                "🌱 Verified Ethical / Thrifted / Circular Brand",
                help="Applies an automatic 30% carbon discount for sustainable brand practices."
            )

        # Real-time preview calculation before logging (P056)
        preview_carbon = calculate_carbon(price_val, category_choice, is_ethical_flag)
        cat_rate = CATEGORIES[category_choice]["multiplier"]
        st.info(f"⚡ **Instant Carbon Preview:** `{preview_carbon} kg CO₂e` (Rate: `{cat_rate} kg/$` | Benchmark: `{CATEGORIES[category_choice]['rating']}`)")

        submit_btn = st.form_submit_button("➕ Record Purchase in Dashboard", width="stretch")
        if submit_btn:
            if not item_name.strip():
                st.error("Please enter a valid item description.")
            else:
                new_entry = {
                    "id": len(st.session_state.purchases) + 1,
                    "item": item_name.strip(),
                    "category": category_choice,
                    "brand": brand_name.strip() if brand_name.strip() else "Unspecified",
                    "price": float(price_val),
                    "carbon_kg": float(preview_carbon),
                    "date": str(purchase_date),
                    "is_ethical": is_ethical_flag,
                }
                st.session_state.purchases.append(new_entry)
                if is_ethical_flag:
                    st.balloons()
                    st.session_state["recent_green"] = True
                else:
                    st.session_state["recent_green"] = False
                st.success(f"Successfully recorded '{item_name}' (+{preview_carbon} kg CO₂e)!")
                st.rerun()

    # --------------------------------------------------------------------------
    # B. GREENER ALTERNATIVES RECOMMENDER (Compulsory Feature P059)
    # --------------------------------------------------------------------------
    st.subheader(f"🔄 Suggested Greener Swaps for {category_choice}")
    alts = ETHICAL_ALTERNATIVES.get(category_choice, [])
    alt_cols = st.columns(len(alts))
    for idx, alt in enumerate(alts):
        with alt_cols[idx]:
            st.markdown(
                f"""
                <div class="alt-card">
                    <strong style="color: #065f46; font-size: 1rem;">{alt['brand']}</strong><br>
                    <span style="font-size: 0.85rem; color: #374151;">{alt['perk']}</span><br>
                    <span style="display: inline-block; margin-top: 0.4rem; font-size: 0.78rem; font-weight: 700; color: #166534; background: #dcfce7; padding: 0.2rem 0.55rem; border-radius: 6px;">
                        Carbon Reduction: {alt['saving']}
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            # 1-Click quick adopt button
            if st.button(f"Adopt {alt['brand'].split('/')[0].strip()}! 🌿", key=f"adopt_{idx}"):
                adopt_entry = {
                    "id": len(st.session_state.purchases) + 1,
                    "item": f"Green Swap: {category_choice}",
                    "category": category_choice,
                    "brand": alt['brand'].split('/')[0].strip(),
                    "price": 35.0,
                    "carbon_kg": calculate_carbon(35.0, category_choice, True),
                    "date": str(date.today()),
                    "is_ethical": True,
                }
                st.session_state.purchases.append(adopt_entry)
                st.session_state["recent_green"] = True
                st.balloons()
                st.success(f"Adopted {alt['brand']}! Logged in your dashboard.")
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # C. MONTHLY DASHBOARD & DATA LEDGER (Compulsory Feature P057)
    # --------------------------------------------------------------------------
    st.subheader(f"📊 Monthly Carbon Ledger ({period_label})")
    if filtered_purchases:
        df = pd.DataFrame(filtered_purchases)
        df["month"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m")

        # Category Breakdown Bar Chart
        st.markdown("**Emissions by Product Category (kg CO₂e)**")
        cat_grouped = df.groupby("category")["carbon_kg"].sum().sort_values(ascending=False)
        st.bar_chart(cat_grouped, color="#2d6a4f")

        # Detailed Interactive Table
        display_df = df[["date", "item", "category", "brand", "price", "carbon_kg", "is_ethical"]].copy()
        display_df.columns = ["Date", "Item Description", "Category", "Brand", "Price ($)", "CO₂ (kg)", "Ethical?"]
        st.dataframe(display_df, width="stretch", hide_index=True)

        # CSV Download Option
        csv_data = display_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Ledger to CSV",
            data=csv_data,
            file_name=f"shopimpact_ledger_{period_label.lower().replace(' ', '_')}.csv",
            mime="text/csv",
        )
    else:
        st.info("No purchases recorded for this period. Use the form above to log your first conscious shopping item!")

with col_side:
    # --------------------------------------------------------------------------
    # D. TURTLE ECO-VISUALIZER (Compulsory Feature P060)
    # --------------------------------------------------------------------------
    st.subheader("🎨 Turtle Eco-Visualizer")
    st.caption("Rendered live using a headless vector Turtle engine (pure Python).")

    # Select Turtle Vector Artwork type (Brief P060: footprint, badge, or leaf)
    selected_art = st.radio(
        "Choose Turtle Vector Artwork:",
        options=["leaf", "footprint", "badge"],
        format_func=lambda x: {"leaf": "🌿 Procedural Eco Leaf", "footprint": "👣 Low Carbon Footprint", "badge": "⭐ Sustainability Rosette"}[x],
        horizontal=True
    )

    turtle_image = draw_turtle_art(selected_art)
    st.image(
        turtle_image,
        caption=f"Vector Drawing: {selected_art.capitalize()} (Drawn using Headless Turtle primitives)",
        width="stretch"
    )

    if st.session_state.get("recent_green", False):
        st.success("🎉 Turtle Celebration Active! You chose an eco-friendly green swap!")

    st.markdown("---")

    # --------------------------------------------------------------------------
    # E. FUN BADGES & MILESTONES (Compulsory Feature P058)
    # --------------------------------------------------------------------------
    st.subheader("🏆 Badges & Achievement Hall")
    for b in badges:
        is_unlocked = b["unlocked"]
        badge_style = "badge-unlocked" if is_unlocked else ""
        status_label = "✅ UNLOCKED" if is_unlocked else "🔒 IN PROGRESS"
        status_color = "#15803d" if is_unlocked else "#9ca3af"

        st.markdown(
            f"""
            <div class="badge-card {badge_style}">
                <div style="display: flex; align-items: center; gap: 0.85rem;">
                    <div style="font-size: 2rem;">{b['icon']}</div>
                    <div style="flex: 1;">
                        <strong style="color: var(--text-primary); font-size: 0.95rem;">{b['name']}</strong><br>
                        <span style="font-size: 0.8rem; color: #64748b;">{b['desc']}</span><br>
                        <span style="font-size: 0.76rem; font-weight: 700; color: {status_color};">
                            {status_label} &bull; {b['progress']}
                        </span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # --------------------------------------------------------------------------
    # F. ROTATING DAILY ECO TIP (Brief Optional Feature P064)
    # --------------------------------------------------------------------------
    st.subheader("💡 Eco Tip of the Day")
    st.markdown(
        f"""
        <div class="tip-card">
            <strong style="color: #0284c7;">Did you know?</strong><br>
            <span style="font-size: 0.88rem; color: #334155;">{random.choice(ECO_TIPS)}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==============================================================================
# 9. FOOTER & ACADEMIC ATTRIBUTION
# ==============================================================================
st.divider()
st.markdown(
    """
    <div style="text-align: center; color: #64748b; font-size: 0.82rem; padding: 1rem 0;">
        <strong>ShopImpact Conscious Shopping Dashboard</strong> &bull; Summative Assessment (60 Marks)<br>
        Candidate: <strong>Parth Pravinbhai Gajera</strong> (ID: <code>1000544</code>) &bull; CRS: Artificial Intelligence &bull; Python Programming (IDAI 102)<br>
        Built with Streamlit, Pandas, and PIL Vector Turtle Graphics.
    </div>
    """,
    unsafe_allow_html=True,
)
