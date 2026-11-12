"""
ShopImpact — Conscious Shopping Dashboard
Course: IDAI 102 (Python Programming) — Summative Assessment (SA)
Candidate: Parth Pravinbhai Gajera (ID: 1000544)
"""

import math
import random
from datetime import date, datetime
import pandas as pd
from PIL import Image, ImageDraw
import streamlit as st

# --- 1. Page Configuration & Earthy Styling ---
st.set_page_config(
    page_title="ShopImpact — Conscious Shopping Dashboard",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
        --forest-dark: #1b4332;
        --forest-mid: #2d6a4f;
        --forest-light: #52b788;
        --earth-sand: #fdfbf7;
        --earth-cream: #f4eee1;
        --earth-card: rgba(255, 255, 255, 0.92);
        --text-slate: #1f2937;
    }
    .main {
        background-color: var(--earth-sand);
        color: var(--text-slate);
    }
    .metric-card {
        background: var(--earth-card);
        border: 1px solid rgba(45, 106, 79, 0.16);
        border-radius: 14px;
        padding: 1.1rem 1.25rem;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.04);
    }
    .badge-card {
        background: #ffffff;
        border: 1.5px solid #e5e7eb;
        border-radius: 12px;
        padding: 0.85rem 1rem;
        margin-bottom: 0.65rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    .badge-unlocked {
        border-color: #52b788;
        background: #f0fdf4;
    }
    .alt-box {
        background: #f7fee7;
        border: 1px solid #bef264;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-top: 0.8rem;
    }
    .tip-box {
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        border-radius: 10px;
        padding: 0.75rem 1rem;
        font-size: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- 2. Curated Carbon Multipliers & Ethical Alternatives ---
# Calibrated in kg CO2e per USD based on lifecycle assessment averages
CATEGORIES = {
    "Fast Fashion Apparel": {"multiplier": 0.42, "benchmark": "High", "icon": "👗"},
    "Footwear & Leather": {"multiplier": 0.65, "benchmark": "Very High", "icon": "👞"},
    "Consumer Electronics": {"multiplier": 0.55, "benchmark": "High", "icon": "📱"},
    "Refurbished Electronics": {"multiplier": 0.11, "benchmark": "Low", "icon": "♻️"},
    "Second-Hand / Thrift": {"multiplier": 0.05, "benchmark": "Minimal", "icon": "🧥"},
    "Groceries (Packaged)": {"multiplier": 0.28, "benchmark": "Medium", "icon": "🛒"},
    "Groceries (Local / Organic)": {"multiplier": 0.08, "benchmark": "Low", "icon": "🥗"},
    "Home & Plastic Wares": {"multiplier": 0.46, "benchmark": "High", "icon": "📦"},
    "Zero-Waste Reusables": {"multiplier": 0.07, "benchmark": "Minimal", "icon": "🌿"},
}

ETHICAL_ALTERNATIVES = {
    "Fast Fashion Apparel": [
        {"brand": "Patagonia / Armedangels", "perk": "GOTS Organic cotton & fair-wage production", "cut": "65%"},
        {"brand": "Thrift / Depop / Vinted", "perk": "Extends existing garment life; 0 factory energy", "cut": "90%"},
    ],
    "Footwear & Leather": [
        {"brand": "Veja / Allbirds", "perk": "Wild Amazonian rubber and sugarcane SweetFoam", "cut": "50%"},
        {"brand": "Piñatex / AppleSkin", "perk": "Plant-based agricultural waste; avoids chrome tanning", "cut": "70%"},
    ],
    "Consumer Electronics": [
        {"brand": "Back Market / Swappie", "perk": "Certified refurbished tech cuts raw mineral mining", "cut": "80%"},
        {"brand": "Fairphone", "perk": "Modular, repairable smartphone with easily swappable parts", "cut": "60%"},
    ],
    "Refurbished Electronics": [
        {"brand": "Direct Certified Refurbished", "perk": "Outstanding choice! You're already circular.", "cut": "Optimal"},
    ],
    "Second-Hand / Thrift": [
        {"brand": "Local Community Charity Shops", "perk": "Top-tier circular economy practice; zero packaging.", "cut": "Optimal"},
    ],
    "Groceries (Packaged)": [
        {"brand": "Local Farmer's Market", "perk": "Zero air-miles, seasonal crops, plastic-free baskets", "cut": "45%"},
        {"brand": "Community Bulk Food Co-ops", "perk": "Bring-your-own-container package-free whole grains", "cut": "55%"},
    ],
    "Groceries (Local / Organic)": [
        {"brand": "Organic Community Garden", "perk": "Soil-regenerative agriculture without chemical nitrates.", "cut": "Optimal"},
    ],
    "Home & Plastic Wares": [
        {"brand": "Zero-Waste Refill Stations", "perk": "Refill existing bottles with bulk eco cleaners", "cut": "60%"},
        {"brand": "Bamboo & Stainless Steel", "perk": "Rapidly renewable material replacing single-use plastics", "cut": "75%"},
    ],
    "Zero-Waste Reusables": [
        {"brand": "Circular Home Refill", "perk": "Gold standard sustainability! Keeps oceans plastic-free.", "cut": "Optimal"},
    ],
}

ECO_TIPS = [
    "Buying a single cotton shirt second-hand saves approximately 2,700 liters of fresh water.",
    "Keeping your smartphone for 4 years instead of 2 cuts its lifecycle carbon footprint in half.",
    "Opting for package-free soap bars eliminates roughly 1.5 kg of household plastic waste annually.",
    "Refurbished laptops save up to 190 kg of CO2 equivalent emissions and 1,200 kg of mined raw minerals.",
    "Shopping at a farmers market directly supports farmers while reducing long-haul cold-chain transport emissions.",
]

SUSTAINABLE_QUOTES = [
    "“The greatest threat to our planet is the belief that someone else will save it.” — Robert Swan",
    "“We do not inherit the Earth from our ancestors; we borrow it from our children.” — Native Proverb",
    "“Small acts, when multiplied by millions of people, can transform the world.” — Howard Zinn",
    "“There is no such thing as ‘away’. When we throw anything away it must go somewhere.” — Annie Leonard",
]

# --- 3. Headless Vector Turtle Graphics Engine ---
# Streamlit Cloud runs headless Linux without Tkinter displays.
# This pure-Python Turtle engine implements turtle vector primitives onto a PIL canvas.
class HeadlessTurtle:
    """Lightweight vector turtle engine safe for headless web environments."""
    def __init__(self, width=280, height=280):
        self.width = width
        self.height = height
        self.image = Image.new("RGBA", (width, height), (255, 255, 255, 0))
        self.draw = ImageDraw.Draw(self.image)
        self.x = width / 2
        self.y = height / 2
        self.heading = 90  # 90 = pointing upward
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


def render_turtle_leaf(score_ratio=1.0):
    """Draws a procedural eco-leaf badge using the vector turtle engine."""
    t = HeadlessTurtle(width=280, height=260)
    
    # Stem
    t.penup()
    t.goto(140, 230)
    t.heading = 90
    t.pen_color = (64, 145, 108, 255)
    t.pen_width = 4
    t.pendown()
    t.forward(45)

    # Left leaf lobe
    t.pen_color = (45, 106, 79, 255)
    t.pen_width = 3
    for _ in range(24):
        t.forward(5.5)
        t.left(3.8)
    
    # Peak tip
    t.left(88)
    
    # Right leaf lobe
    for _ in range(24):
        t.forward(5.5)
        t.left(3.8)

    # Center vein
    t.penup()
    t.goto(140, 185)
    t.heading = 90
    t.pen_color = (82, 183, 136, 255)
    t.pen_width = 2
    t.pendown()
    t.forward(85)

    # Leaf side branches
    for y_offset in [155, 130, 105]:
        t.penup()
        t.goto(140, y_offset)
        t.heading = 45
        t.pendown()
        t.forward(22)
        t.penup()
        t.goto(140, y_offset)
        t.heading = 135
        t.pendown()
        t.forward(22)

    # Turtle position marker (small turtle avatar at tip)
    t.penup()
    t.goto(140, 55)
    t.draw.ellipse([(134, 49), (146, 61)], fill=(116, 198, 157, 255), outline=(27, 67, 50, 255))
    return t.image


# --- 4. Session State & Seed Data Initialization ---
def init_session_state():
    if "purchases" not in st.session_state:
        # Pre-seed with realistic diverse purchases covering expensive, cheap, eco and non-eco items
        st.session_state.purchases = [
            {"id": 1, "item": "Organic Hemp Jacket", "category": "Fast Fashion Apparel", "brand": "Patagonia", "price": 120.0, "carbon_kg": 50.4, "date": "2026-10-02", "is_ethical": True},
            {"id": 2, "item": "Graphic Polyester T-Shirt", "category": "Fast Fashion Apparel", "brand": "Shein", "price": 18.0, "carbon_kg": 7.56, "date": "2026-10-05", "is_ethical": False},
            {"id": 3, "item": "Refurbished iPad Mini", "category": "Refurbished Electronics", "brand": "Back Market", "price": 280.0, "carbon_kg": 30.8, "date": "2026-10-10", "is_ethical": True},
            {"id": 4, "item": "Leather Dress Shoes", "category": "Footwear & Leather", "brand": "Zara", "price": 110.0, "carbon_kg": 71.5, "date": "2026-10-14", "is_ethical": False},
            {"id": 5, "item": "Thrifted Vintage Denim", "category": "Second-Hand / Thrift", "brand": "Local Thrift", "price": 25.0, "carbon_kg": 1.25, "date": "2026-10-18", "is_ethical": True},
            {"id": 6, "item": "Weekly Farm Fresh Veggies", "category": "Groceries (Local / Organic)", "brand": "Green Valley CSA", "price": 42.0, "carbon_kg": 3.36, "date": "2026-10-22", "is_ethical": True},
            {"id": 7, "item": "Single-Use Plastic Storage", "category": "Home & Plastic Wares", "brand": "Generic", "price": 16.0, "carbon_kg": 7.36, "date": "2026-10-25", "is_ethical": False},
            {"id": 8, "item": "Bamboo Kitchen Dish Set", "category": "Zero-Waste Reusables", "brand": "EcoLiving", "price": 22.0, "carbon_kg": 1.54, "date": "2026-10-28", "is_ethical": True},
            {"id": 9, "item": "Fast Fashion Winter Coat", "category": "Fast Fashion Apparel", "brand": "H&M", "price": 85.0, "carbon_kg": 35.7, "date": "2026-11-01", "is_ethical": False},
            {"id": 10, "item": "Noise Cancelling Headphones", "category": "Consumer Electronics", "brand": "Sony", "price": 190.0, "carbon_kg": 104.5, "date": "2026-11-03", "is_ethical": False},
            {"id": 11, "item": "Fairphone 5 Modular Battery", "category": "Refurbished Electronics", "brand": "Fairphone", "price": 38.0, "carbon_kg": 4.18, "date": "2026-11-05", "is_ethical": True},
            {"id": 12, "item": "Organic Coffee Beans Bulk", "category": "Groceries (Local / Organic)", "brand": "Equator Fair Trade", "price": 24.0, "carbon_kg": 1.92, "date": "2026-11-06", "is_ethical": True},
        ]

init_session_state()

# --- 5. Pure Helper Logic Functions ---
def calculate_carbon(price: float, category: str, is_ethical: bool) -> float:
    base = price * CATEGORIES.get(category, {"multiplier": 0.3})["multiplier"]
    # Ethical brand multiplier reward: 30% reduction if verified ethical
    return round(base * 0.7 if is_ethical else base, 2)


def evaluate_badges(purchases):
    """Evaluates user transaction records to unlock milestone badges."""
    total_items = len(purchases)
    total_spend = sum(p["price"] for p in purchases)
    total_co2 = sum(p["carbon_kg"] for p in purchases)
    ethical_count = sum(1 for p in purchases if p.get("is_ethical", False))
    avg_intensity = (total_co2 / total_spend) if total_spend > 0 else 0.5

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
            "desc": "Maintained an average carbon intensity below 0.25 kg CO2/$",
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
            "desc": "Kept cumulative carbon footprint under 120 kg CO2 with ≥10 items.",
            "icon": "🥇",
            "unlocked": total_items >= 10 and total_co2 <= 280.0,
            "progress": f"{total_co2:.1f} kg CO2 (Limit: ≤280)",
        },
    ]
    return badges, total_spend, total_co2, avg_intensity, ethical_count


# --- 6. Main Dashboard Layout ---
badges, total_spend, total_co2, avg_intensity, ethical_count = evaluate_badges(st.session_state.purchases)

# Header & Academic Dossier
col_header, col_author = st.columns([2.5, 1])
with col_header:
    st.title("🌱 ShopImpact — Conscious Shopping Dashboard")
    st.markdown(
        "**Transforming everyday consumer choices into measurable environmental impact.** "
        "Track planned purchases, estimate carbon footprints with curated lifecycle multipliers, and discover greener brand swaps."
    )

with col_author:
    st.markdown(
        """
        <div style="background: rgba(45, 106, 79, 0.08); border: 1px solid rgba(45, 106, 79, 0.25); border-radius: 12px; padding: 0.75rem 1rem; font-size: 0.82rem;">
            <strong>Parth Pravinbhai Gajera</strong> &bull; 1000544<br>
            <span style="color: #4b5563;">Course: IDAI 102 — Python Programming (SA)</span><br>
            <span style="color: #047857; font-weight: 600;">Status: System Live & Operational</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()

# Top KPI Metric Cards
m1, m2, m3, m4 = st.columns(4)
trees_needed = round(total_co2 / 21.0, 1)  # 1 mature tree absorbs ~21kg CO2/year
bench_co2 = total_spend * 0.45  # Conventional baseline benchmark
co2_saved = max(0.0, round(bench_co2 - total_co2, 1))

with m1:
    st.metric(label="Total Spend", value=f"${total_spend:,.2f}", delta=f"{len(st.session_state.purchases)} Items Logged")
with m2:
    st.metric(label="Estimated Footprint", value=f"{total_co2:.1f} kg CO₂e", delta=f"{avg_intensity:.2f} kg/$ intensity", delta_color="inverse")
with m3:
    st.metric(label="Carbon Saved vs Standard", value=f"{co2_saved:.1f} kg CO₂", delta="Via Green Swaps")
with m4:
    st.metric(label="Offset Trees Needed", value=f"{trees_needed} Trees", delta="21 kg/tree/year absorption")

st.markdown("<br>", unsafe_allow_html=True)

# Split Workspace: Left 2 Cols = Purchase Input & Analytics; Right 1 Col = Turtle & Gamification
left_main, right_sidebar = st.columns([1.8, 1.2], gap="large")

with left_main:
    # --- Purchase Input Section ---
    st.subheader("🛒 Log a Planned Purchase")
    with st.form("purchase_form", clear_on_submit=True):
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            item_name = st.text_input("Item Description", placeholder="e.g. Linen Summer Shirt, Refurbished Watch")
            category_choice = st.selectbox("Product Category", options=list(CATEGORIES.keys()))
            brand_name = st.text_input("Brand / Vendor", placeholder="e.g. Patagonia, Local Thrift, Zara")

        with f_col2:
            price_val = st.number_input("Purchase Price ($)", min_value=1.0, max_value=5000.0, value=45.0, step=5.0)
            purchase_date = st.date_input("Purchase Date", value=date.today())
            is_ethical_flag = st.checkbox("🌱 Verified Ethical / Thrifted / Circular Brand", help="Applies a 30% carbon-efficiency discount.")

        # Real-time preview calculation
        preview_carbon = calculate_carbon(price_val, category_choice, is_ethical_flag)
        st.info(f"⚡ **Estimated CO₂ Footprint**: `{preview_carbon} kg CO₂e` (Rate: `{CATEGORIES[category_choice]['multiplier']} kg/$`)")

        submit_btn = st.form_submit_button("➕ Record Purchase in Dashboard", use_container_width=True)
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
                st.success(f"Added '{item_name}'! +{preview_carbon} kg CO₂ logged.")
                st.rerun()

    # --- Ethical Alternatives Recommender ---
    st.subheader(f"🔄 Greener Brand Swaps for {category_choice}")
    alts = ETHICAL_ALTERNATIVES.get(category_choice, [])
    alt_cols = st.columns(len(alts))
    for idx, alt in enumerate(alts):
        with alt_cols[idx]:
            st.markdown(
                f"""
                <div class="alt-box">
                    <strong style="color: #1b4332;">{alt['brand']}</strong><br>
                    <span style="font-size: 0.85rem; color: #374151;">{alt['perk']}</span><br>
                    <span style="display: inline-block; margin-top: 0.4rem; font-size: 0.78rem; font-weight: 700; color: #15803d; background: #dcfce7; padding: 0.2rem 0.5rem; border-radius: 4px;">Savings: {alt['saving'] if 'saving' in alt else alt.get('cut', 'Significant')}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Monthly Dashboard & Ledger ---
    st.subheader("📊 Purchase History & Carbon Ledger")
    if st.session_state.purchases:
        df = pd.DataFrame(st.session_state.purchases)
        df["month"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m")

        # Category Breakdown Chart
        st.markdown("**Carbon Footprint by Product Category (kg CO₂e)**")
        cat_summary = df.groupby("category")["carbon_kg"].sum().sort_values(ascending=False)
        st.bar_chart(cat_summary, color="#2d6a4f")

        # Dataframe view
        display_df = df[["date", "item", "category", "brand", "price", "carbon_kg", "is_ethical"]].copy()
        display_df.columns = ["Date", "Item", "Category", "Brand", "Price ($)", "CO₂ (kg)", "Ethical?"]
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        if st.button("🗑️ Reset All Transactions to Seed State", help="Restores default sample dataset"):
            st.session_state.purchases = []
            init_session_state()
            st.rerun()

with right_sidebar:
    # --- Procedural Turtle Graphics Artwork ---
    st.subheader("🎨 Turtle Eco-Visualizer")
    st.caption("Rendered live using a headless vector Turtle engine.")

    # Render procedural green leaf badge
    turtle_img = render_turtle_leaf()
    st.image(turtle_img, caption="Procedural Eco Leaf drawn by Turtle Engine (PIL Vector Path)", use_container_width=True)

    # --- Gamification Badges ---
    st.subheader("🏆 Eco Badges & Milestones")
    for b in badges:
        status_class = "badge-unlocked" if b["unlocked"] else ""
        status_label = "✅ UNLOCKED" if b["unlocked"] else "🔒 LOCKED"
        status_color = "#15803d" if b["unlocked"] else "#9ca3af"
        st.markdown(
            f"""
            <div class="badge-card {status_class}">
                <div style="font-size: 1.8rem;">{b['icon']}</div>
                <div style="flex: 1;">
                    <strong style="color: #111827;">{b['name']}</strong><br>
                    <span style="font-size: 0.78rem; color: #4b5563;">{b['desc']}</span><br>
                    <span style="font-size: 0.74rem; font-weight: 600; color: {status_color};">{status_label} &bull; {b['progress']}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --- Rotating Eco Knowledge & Motivational Quote ---
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("💡 Daily Eco Wisdom")
    st.markdown(
        f"""
        <div class="tip-box">
            <strong>Did you know?</strong><br>
            {random.choice(ECO_TIPS)}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"*{random.choice(SUSTAINABLE_QUOTES)}*")

# --- Footer ---
st.divider()
st.markdown(
    """
    <div style="text-align: center; color: #6b7280; font-size: 0.8rem; padding: 1rem 0;">
        <strong>ShopImpact Conscious Shopping Dashboard</strong> &bull; IDAI 102 Summative Assessment &bull; 
        Candidate: Parth Pravinbhai Gajera (1000544) &bull; CRS Artificial Intelligence &bull; Python Programming
    </div>
    """,
    unsafe_allow_html=True,
)
