import base64
import html
import io
import math
import os
import random
from datetime import date
import pandas as pd
from PIL import Image, ImageDraw
import streamlit as st
import streamlit.components.v1 as components

try:
    import altair as alt
    HAS_ALTAIR = True
except Exception:
    HAS_ALTAIR = False

SA_ASSET_3D_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "3d")

@st.cache_data(show_spinner=False)
def load_sa_asset_b64(rel_path: str) -> str:
    full = os.path.join(SA_ASSET_3D_DIR, rel_path.replace("/", os.sep))
    if not os.path.isfile(full):
        return ""
    with Image.open(full) as im:
        im = im.convert("RGBA")
        im.thumbnail((112, 112), Image.Resampling.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, format="PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")

def render_sa_3d(rel_path: str, alt_text: str, size: int = 56, fallback: str = "") -> str:
    uri = load_sa_asset_b64(rel_path)
    if uri:
        return f'<img src="{uri}" class="asset-3d" alt="{html.escape(alt_text)}" style="width:{size}px; height:{size}px; object-fit:contain; display:inline-block; filter:drop-shadow(0 6px 10px rgba(24,48,30,0.16));"/>'
    return f'<span style="font-size:{int(size*0.5)}px;">{fallback}</span>'

st.set_page_config(
    page_title="ShopImpact — Conscious Shopping Companion",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="auto",
)

def render_html(html_str: str):
    clean = "\n".join(line.strip() for line in html_str.splitlines() if line.strip())
    st.markdown(clean, unsafe_allow_html=True)

def render_section_header(kicker: str, title: str, subtitle: str = ""):
    sub_html = f'<p class="sec-sub">{html.escape(subtitle)}</p>' if subtitle else ""
    ornament_svg = (
        '<svg width="18" height="14" viewBox="0 0 18 14" xmlns="http://www.w3.org/2000/svg" style="display:block;">'
        '<path d="M9 1 C13 3.5, 16 7.5, 9 13 C2 7.5, 5 3.5, 9 1 Z" fill="currentColor" opacity="0.85"/>'
        '</svg>'
    )
    render_html(f"""
    <div class="sec-wrap">
      <div class="sec-divider">
        <span class="sec-line"></span>
        <span class="sec-ornament">{ornament_svg}</span>
        <span class="sec-line"></span>
      </div>
      <div class="eyebrow" style="margin-top:0.65rem;">{html.escape(kicker)}</div>
      <h3 class="sec-title">{html.escape(title)}</h3>
      {sub_html}
    </div>
    """)

# ------------------------------------------------------------------------------
# DOMAIN DATA: CATEGORIES, MULTIPLIERS & CIRCULAR SWAPS
# ------------------------------------------------------------------------------

CATEGORIES = {
    "Fast Fashion Apparel": {"multiplier": 0.42, "rating": "High Carbon", "tier": "⚠️ High", "icon": "👗", "fact": "Synthetic polyester spinning and chemical dyeing create heavy industrial greenhouse footprints."},
    "Footwear & Leather": {"multiplier": 0.65, "rating": "Very High", "tier": "🚨 Heavy", "icon": "👞", "fact": "Bovine cattle methane and chromium tanning drive intense greenhouse gas emissions."},
    "Consumer Electronics": {"multiplier": 0.55, "rating": "High Carbon", "tier": "🚨 Heavy", "icon": "📱", "fact": "Silicon semiconductor fabrication and rare-earth mining account for ~80% of lifecycle CO₂."},
    "Refurbished Tech": {"multiplier": 0.11, "rating": "Low Carbon", "tier": "🌾 Conscious", "icon": "♻️", "fact": "Eliminates virgin mineral extraction; accounts only for diagnostics, clean transport, and testing."},
    "Second-Hand / Thrift": {"multiplier": 0.05, "rating": "Minimal Impact", "tier": "🌿 Ultra-Green", "icon": "🧥", "fact": "Pure circular economy; original manufacturing emissions are 100% amortized."},
    "Packaged Groceries": {"multiplier": 0.38, "rating": "Medium-High", "tier": "⚠️ High", "icon": "🛒", "fact": "Industrial food processing and multi-layer plastic packaging add embodied supply-chain carbon."},
    "Local / Organic Food": {"multiplier": 0.08, "rating": "Low Carbon", "tier": "🌿 Ultra-Green", "icon": "🥗", "fact": "Zero long-haul cold-chain freight and regenerative organic soil practices without synthetic nitrates."},
    "Home & Plastics": {"multiplier": 0.46, "rating": "High Carbon", "tier": "⚠️ High", "icon": "📦", "fact": "Virgin petroleum feedstocks and high-temperature polymer molding drive heavy footprint."},
    "Zero-Waste Reusables": {"multiplier": 0.07, "rating": "Minimal Impact", "tier": "🌿 Ultra-Green", "icon": "🌿", "fact": "Durable steel and bamboo displace hundreds of single-use disposable plastics across their lifespan."},
}

QUICK_PURCHASES = [
    {"name": "Fair-Trade Coffee / Tea", "price": 4.50, "category": "Local / Organic Food", "brand": "Local Roaster", "is_ethical": True, "icon": "☕", "img": "purchases/coffee_cup.png"},
    {"name": "Local Organic Lunch", "price": 12.00, "category": "Local / Organic Food", "brand": "Farmers Co-op", "is_ethical": True, "icon": "🥗", "img": "purchases/organic_bowl.png"},
    {"name": "Thrifted Vintage Jacket", "price": 32.00, "category": "Second-Hand / Thrift", "brand": "Community Thrift", "is_ethical": True, "icon": "🧥", "img": "purchases/vintage_jacket.png"},
    {"name": "Refurbished Tech Gadget", "price": 85.00, "category": "Refurbished Tech", "brand": "Back Market", "is_ethical": True, "icon": "📱", "img": "purchases/refurb_phone.png"},
    {"name": "Fast-Fashion Top", "price": 55.00, "category": "Fast Fashion Apparel", "brand": "High-Street Retail", "is_ethical": False, "icon": "👗", "img": "purchases/fast_top.png"},
    {"name": "Leather Footwear", "price": 130.00, "category": "Footwear & Leather", "brand": "City Leather Co.", "is_ethical": False, "icon": "👞", "img": "purchases/leather_shoe.png"},
]

ETHICAL_ALTERNATIVES = {
    "Fast Fashion Apparel": [
        {"brand": "Patagonia Worn Wear", "perk": "100% organic cotton, Fair Trade sewing & free lifelong repairs", "saving": "65%"},
        {"brand": "Depop / Local Thrift", "perk": "Extends existing garment life; zero new factory emissions", "saving": "92%"},
    ],
    "Footwear & Leather": [
        {"brand": "Allbirds / Veja", "perk": "Sugarcane SweetFoam & wild-harvested Amazonian rubber", "saving": "52%"},
        {"brand": "Will's Vegan Store", "perk": "Bio-based agricultural grain waste; 100% plastic-free packaging", "saving": "70%"},
    ],
    "Consumer Electronics": [
        {"brand": "Back Market Refurbished", "perk": "Certified renew tech avoids toxic raw mineral mining", "saving": "82%"},
        {"brand": "Fairphone Modular", "perk": "Repairable modular build with 5-year guaranteed spare parts", "saving": "60%"},
    ],
    "Refurbished Tech": [{"brand": "Certified Renewed Hub", "perk": "Optimal circular loop! Extends hardware life by 3+ years", "saving": "Optimal"}],
    "Second-Hand / Thrift": [{"brand": "Community Thrift Center", "perk": "Top-tier circular reuse; zero new factory footprint", "saving": "Optimal"}],
    "Packaged Groceries": [
        {"brand": "Local Farmers Market", "perk": "Seasonal crops, zero air-miles & plastic-free baskets", "saving": "58%"},
        {"brand": "Bulk Food Co-op", "perk": "Bring-your-own container pantry essentials with zero waste", "saving": "45%"},
    ],
    "Local / Organic Food": [{"brand": "Community CSA Farm", "perk": "Regenerative soil farming preserving local groundwater", "saving": "Optimal"}],
    "Home & Plastics": [
        {"brand": "Zero-Waste Refill Station", "perk": "Refill bulk cleaners in reusable glass jars", "saving": "75%"},
        {"brand": "Bamboo & Steel Essentials", "perk": "Fast-growing renewable bamboo; fully biodegradable", "saving": "68%"},
    ],
    "Zero-Waste Reusables": [{"brand": "Circular Home Refill", "perk": "Gold standard zero-waste; keeps oceans and landfills clean", "saving": "Optimal"}],
}

ECO_MASCOTS = {
    "Shelly the Sea Turtle 🐢": "Wisdom, clean oceans & circular longevity",
    "Pip the Forest Fox 🦊": "Agile thrifting, clever reuse & finding vintage gems",
    "Barnaby the Eco Owl 🦉": "Footprint analytics, science & carbon budget discipline",
    "Bumble the Pollinator 🐝": "Local organic farmers, seasonal harvest & biodiversity",
    "Bao the Bamboo Panda 🐼": "Zero-waste reusables, gentle living & compostable goods",
}

ECO_TIPS = [
    "Buying a single cotton shirt second-hand saves ~2,700 liters of drinking water.",
    "Keeping your smartphone for 4 years instead of 2 cuts its manufacturing emissions by 50%.",
    "Package-free shampoo bars prevent roughly 3 plastic bottles from landfills each year.",
    "Refurbished laptops save up to 190 kg of CO₂ and 1,200 kg of raw mined minerals.",
    "Shopping at a local farmers market eliminates long-haul cold-chain logistics emissions.",
    "Bamboo grows up to 90 cm per day without synthetic pesticides, making it an ideal plastic swap.",
    "Washing clothes on cold cycles reduces laundry carbon footprint by up to 75% per load.",
    "Circular repair programs extend product lifespans by an average of 3.2 years per item.",
]

# ------------------------------------------------------------------------------
# BOTANICAL SVG HERO LANDSCAPE (Ecovista-Inspired Welcome Artwork + Man & Turtle)
# ------------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def render_welcome_landscape_svg(dark=False):
    """Layered flat-botanical SVG horizon with wind turbines, sunlit trees, cottages, shopper & turtle."""
    sky_top = "#18271E" if dark else "#FAFCE8"
    sky_bot = "#1F3325" if dark else "#E1F1DB"
    sun_ray = "#2E4632" if dark else "#F6EEBA"
    hill1 = "#294630" if dark else "#CDE3BA"
    hill2 = "#213D27" if dark else "#A7CE84"
    hill3 = "#1B3321" if dark else "#6A9E4B"
    hill4 = "#142719" if dark else "#3C6B32"
    path_col = "#364B2C" if dark else "#EDE197"
    house_wall = "#D9E5D6" if dark else "#FFFDF8"
    house_roof = "#A95043"
    tree_gold = "#CCA845" if dark else "#DCC150"
    tree_pine = "#112217" if dark else "#224628"
    card_stroke = "#364F3B" if dark else "#FFFFFF"
    win_fill = "rgba(19,28,23,0.62)" if dark else "rgba(255,255,255,0.62)"
    win_kicker = "#8DC06F" if dark else "#4E7E36"
    win_title = "#ECF3EA" if dark else "#13261B"
    win_sub = "#B7CCBC" if dark else "#46604E"

    svg_str = f"""
    <svg viewBox="0 0 1120 330" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="eco-sky" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="{sky_top}"/>
          <stop offset="100%" stop-color="{sky_bot}"/>
        </linearGradient>
      </defs>
      <style>
        @keyframes spin-turb {{ from {{ transform: rotate(0deg); }} to {{ transform: rotate(360deg); }} }}
        @keyframes balloon-drift {{ 0%, 100% {{ transform: translateY(0px); }} 50% {{ transform: translateY(-7px); }} }}
        .turb-a {{ animation: spin-turb 14s linear infinite; transform-origin: 410px 186px; }}
        .turb-b {{ animation: spin-turb 19s linear infinite; transform-origin: 270px 218px; }}
        .balloon {{ animation: balloon-drift 4.5s ease-in-out infinite; }}
      </style>

      <!-- Morning Botanical Sky & Soft Solar Beams -->
      <rect width="1120" height="330" fill="url(#eco-sky)"/>
      <polygon points="1030,0 1120,0 1120,165 650,330 430,330" fill="{sun_ray}" opacity="0.42"/>
      <circle cx="1015" cy="48" r="34" fill="#F2DC78" opacity="0.65"/>

      <!-- Drifting Hot Air Balloon & Silhouette Birds -->
      <g class="balloon">
        <ellipse cx="1062" cy="82" rx="11" ry="14" fill="#A66BB0" stroke="#743E7D" stroke-width="1"/>
        <path d="M 1054 88 L 1058 100 M 1070 88 L 1066 100" stroke="#4D6655" stroke-width="1"/>
        <rect x="1057" y="99" width="10" height="6" rx="1.5" fill="#7D5A44"/>
      </g>
      <path d="M 140 62 Q 146 56 152 62 Q 158 56 164 62 M 185 78 Q 190 73 195 78 Q 200 73 205 78" fill="none" stroke="#5A7A63" stroke-width="1.6" stroke-linecap="round"/>

      <!-- Layered Flat Rolling Botanical Hills -->
      <path d="M 0 218 Q 190 175 430 205 T 890 185 T 1120 198 L 1120 330 L 0 330 Z" fill="{hill1}"/>
      <path d="M 0 238 Q 260 202 520 226 T 1120 196 L 1120 330 L 0 330 Z" fill="{hill2}"/>

      <!-- Far Horizon Windmills -->
      <line x1="150" y1="215" x2="150" y2="256" stroke="#224428" stroke-width="2"/>
      <path d="M 150 215 L 138 202 M 150 215 L 164 214 M 150 215 L 146 229" stroke="#224428" stroke-width="2" stroke-linecap="round"/>
      <line x1="270" y1="218" x2="270" y2="262" stroke="#1E3C24" stroke-width="2.5"/>
      <g class="turb-b">
        <path d="M 270 218 L 270 193 M 270 218 L 292 229 M 270 218 L 250 232" stroke="#1E3C24" stroke-width="2.4" stroke-linecap="round"/>
      </g>

      <!-- Main Foreground Meadow & Golden Sunlit Field -->
      <path d="M 0 264 Q 360 250 740 258 T 1120 242 L 1120 330 L 0 330 Z" fill="{hill3}"/>
      <polygon points="460,295 860,275 880,298 465,310" fill="{path_col}" opacity="0.88"/>
      <path d="M 0 294 Q 440 278 780 288 T 1120 262 L 1120 330 L 0 330 Z" fill="{hill4}"/>

      <!-- Valley Cottages on Left Horizon -->
      <g>
        <rect x="48" y="246" width="24" height="16" fill="{house_wall}"/>
        <polygon points="45,246 60,237 75,246" fill="{house_roof}"/>
        <rect x="82" y="240" width="38" height="22" fill="{house_wall}"/>
        <polygon points="79,240 101,228 123,240" fill="{house_roof}"/>
        <rect x="130" y="242" width="44" height="20" fill="{house_wall}"/>
        <polygon points="127,242 152,231 177,242" fill="{house_roof}"/>
        <rect x="92" y="248" width="6" height="8" fill="#5B6E61"/>
        <rect x="142" y="248" width="6" height="7" fill="#5B6E61"/>
      </g>

      <!-- Hero Wind Turbine -->
      <polygon points="407,186 413,186 416,282 404,282" fill="#183020"/>
      <ellipse cx="416" cy="282" rx="20" ry="4" fill="#183020" opacity="0.55"/>
      <g class="turb-a">
        <path d="M 410 186 L 434 152 L 414 188 Z" fill="#1D3A26"/>
        <path d="M 410 186 L 368 179 L 408 189 Z" fill="#1D3A26"/>
        <path d="M 410 186 L 424 226 L 408 188 Z" fill="#1D3A26"/>
        <circle cx="410" cy="186" r="4" fill="#3B6239"/>
      </g>

      <!-- Mindful Shopper Man + Companion Sea Turtle on Sunlit Eco Path -->
      <g transform="translate(540, 224)">
        <!-- Man's soft shadow -->
        <ellipse cx="22" cy="70" rx="18" ry="4.5" fill="#13261B" opacity="0.28"/>
        <!-- Legs walking -->
        <line x1="17" y1="45" x2="12" y2="68" stroke="#233A2D" stroke-width="5" stroke-linecap="round"/>
        <line x1="25" y1="45" x2="31" y2="68" stroke="#2F4E3C" stroke-width="5" stroke-linecap="round"/>
        <!-- Olive Coat / Torso -->
        <path d="M 10 22 Q 21 17 32 22 L 34 48 L 10 48 Z" fill="#4E7E36"/>
        <!-- Canvas Reusable Eco Tote Bag -->
        <rect x="28" y="34" width="14" height="17" rx="2.5" fill="#F2E4B5" stroke="#8C7343" stroke-width="1.3"/>
        <path d="M 31 34 Q 35 27 39 34" fill="none" stroke="#8C7343" stroke-width="1.4"/>
        <circle cx="35" cy="43" r="2.8" fill="#4E7E36"/>
        <!-- Head + Friendly Hair -->
        <circle cx="21" cy="11" r="7.5" fill="#E8B892"/>
        <path d="M 14 9 Q 21 1 28 9 Z" fill="#2A2623"/>
        <line x1="28" y1="25" x2="35" y2="35" stroke="#4E7E36" stroke-width="4" stroke-linecap="round"/>

        <!-- Companion Turtle walking beside him -->
        <g transform="translate(52, 50)">
          <ellipse cx="14" cy="20" rx="14" ry="3.5" fill="#13261B" opacity="0.25"/>
          <ellipse cx="6" cy="18" rx="3" ry="4" fill="#6DA452"/>
          <ellipse cx="21" cy="18" rx="3" ry="4" fill="#6DA452"/>
          <path d="M 2 15 Q 14 0 26 15 Z" fill="#3D6B35" stroke="#1E3C24" stroke-width="1.5"/>
          <ellipse cx="14" cy="15" rx="12" ry="3.5" fill="#D9B44A"/>
          <circle cx="29" cy="12" r="5" fill="#77B15A" stroke="#1E3C24" stroke-width="1.3"/>
          <circle cx="31" cy="11" r="1.2" fill="#13261B"/>
        </g>
      </g>

      <!-- Right Botanical Grove (Autumn Birch & Deep Pine) -->
      <g>
        <ellipse cx="860" cy="230" rx="36" ry="32" fill="#D1B24C" opacity="0.92"/>
        <ellipse cx="888" cy="212" rx="32" ry="34" fill="{tree_gold}" opacity="0.92"/>
        <path d="M 862 285 L 862 225 M 862 246 L 882 226 M 862 252 L 844 236" stroke="#2B2118" stroke-width="3" stroke-linecap="round"/>
        <!-- Slender Golden Conifer -->
        <polygon points="942,102 918,248 966,248" fill="{tree_gold}" opacity="0.95"/>
        <rect x="940" y="102" width="4" height="186" fill="#291E15"/>
        <!-- Tall Deep Evergreen Fir -->
        <polygon points="1010,126 968,266 1052,266" fill="{tree_pine}"/>
        <polygon points="1010,104 978,195 1042,195" fill="#2B5530"/>
        <ellipse cx="972" cy="266" rx="75" ry="20" fill="#234227"/>
      </g>

      <!-- Crisp Editorial Inner Window Border Like Reference Hero -->
      <rect x="74" y="22" width="972" height="196" rx="18" fill="{win_fill}" stroke="{card_stroke}" stroke-width="1.6"/>
      <text x="560" y="64" text-anchor="middle" fill="{win_kicker}" font-size="13" font-weight="800" letter-spacing="1.4" font-family="sans-serif">CONSCIOUS SHOPPING COMPANION • ECO STUDIO</text>
      <text x="560" y="108" text-anchor="middle" fill="{win_title}" font-size="34" font-weight="900" font-family="sans-serif">Illuminating Everyday Choices</text>
      <text x="560" y="148" text-anchor="middle" fill="{win_title}" font-size="34" font-weight="900" font-family="sans-serif">with Sustainable Action</text>
      <text x="560" y="182" text-anchor="middle" fill="{win_sub}" font-size="15" font-weight="600" font-family="sans-serif">Track real CO₂e footprints, meet your animated companion, and turn low-waste picks into collectible Turtle art.</text>
    </svg>
    """.strip()
    b64 = base64.b64encode(svg_str.encode("utf-8")).decode("ascii")
    return f'<img src="data:image/svg+xml;base64,{b64}" alt="ShopImpact Botanical Horizon" style="width:100%; height:auto; display:block; border-radius:22px; border:1px solid rgba(78,126,54,0.14); box-shadow:0 12px 36px rgba(24,48,30,0.08);"/>'

# ------------------------------------------------------------------------------
# ANIMATED SVG LIVING BIOSPHERE & 5 MASCOT ENGINE (Ecovista Palette)
# ------------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def render_animated_biosphere_svg(used_pct, co2_tot, budget_limit, width=185, height=238):
    pct = min(150.0, max(0.0, round(float(used_pct), 1)))
    co2_tot = round(float(co2_tot), 1)
    if pct <= 50.0:
        sky_top, sky_bot = "#F2F9EC", "#D4E9C9"
        ring_col, canopy_col, hill_col = "#4E7E36", "#6DA452", "#92C273"
        status_text, status_col = "PRISTINE BIOSPHERE", "#3F6E2C"
    elif pct <= 85.0:
        sky_top, sky_bot = "#EDF6E6", "#CCE2BE"
        ring_col, canopy_col, hill_col = "#5E9143", "#7FB462", "#A4CD88"
        status_text, status_col = "BALANCED ECOSYSTEM", "#4E7E36"
    elif pct <= 100.0:
        sky_top, sky_bot = "#FCF6E6", "#F2DFB4"
        ring_col, canopy_col, hill_col = "#C88C28", "#DCA746", "#BFA054"
        status_text, status_col = "BUDGET WARNING", "#B07514"
    else:
        sky_top, sky_bot = "#FBECE9", "#EFC5BD"
        ring_col, canopy_col, hill_col = "#C45B4D", "#B84C3F", "#9E463B"
        status_text, status_col = "CARBON OVERLOAD", "#B24436"

    return f"""
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 220 278" width="{width}" height="{height}" style="display:block; margin:0 auto;">
      <defs>
        <linearGradient id="bs-sky" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="{sky_top}"/><stop offset="100%" stop-color="{sky_bot}"/>
        </linearGradient>
        <clipPath id="bs-clip"><circle cx="110" cy="96" r="78"/></clipPath>
      </defs>
      <style>
        @keyframes b-sway {{ 0%, 100% {{ transform: rotate(0deg); }} 50% {{ transform: rotate(2.4deg); }} }}
        @keyframes b-spore {{ 0% {{ transform: translateY(0); opacity: 0.8; }} 100% {{ transform: translateY(-38px); opacity: 0; }} }}
        .b-sway {{ animation: b-sway 4s ease-in-out infinite; transform-origin: 110px 132px; }}
        .b-sp1 {{ animation: b-spore 3.6s infinite; }}
        .b-sp2 {{ animation: b-spore 2.9s infinite 1.2s; }}
      </style>
      <g clip-path="url(#bs-clip)">
        <rect x="30" y="16" width="160" height="160" fill="url(#bs-sky)"/>
        <circle cx="144" cy="56" r="14" fill="#E8CA5B" opacity="0.85"/>
        <path d="M 30 144 Q 75 118 118 128 T 190 124 L 190 180 L 30 180 Z" fill="{hill_col}" opacity="0.7"/>
        <path d="M 30 150 Q 95 130 140 140 T 190 138 L 190 180 L 30 180 Z" fill="{ring_col}" opacity="0.9"/>
        <rect x="106" y="108" width="8" height="44" rx="3" fill="#6F4B2C"/>
        <g class="b-sway">
          <ellipse cx="110" cy="96" rx="28" ry="21" fill="{canopy_col}"/>
          <ellipse cx="94" cy="90" rx="18" ry="14" fill="{ring_col}" opacity="0.9"/>
          <ellipse cx="125" cy="90" rx="17" ry="13" fill="{canopy_col}"/>
          <circle cx="101" cy="86" r="2.6" fill="#FAF0B5"/>
          <circle cx="120" cy="89" r="2.4" fill="#FAF0B5"/>
        </g>
        <circle class="b-sp1" cx="84" cy="126" r="2.5" fill="{ring_col}"/>
        <circle class="b-sp2" cx="136" cy="132" r="2.2" fill="#E8CA5B"/>
      </g>
      <circle cx="110" cy="96" r="78" fill="none" stroke="{ring_col}" stroke-width="2.6"/>
      <path d="M 54 62 A 72 72 0 0 1 98 28" fill="none" stroke="#FFFFFF" stroke-width="3.5" stroke-linecap="round" opacity="0.65"/>

      <!-- Clean Matte Botanical Base & Unobstructed Pill Plaque -->
      <path d="M 80 174 L 68 198 L 152 198 L 140 174 Z" fill="#233829"/>
      <rect x="58" y="188" width="104" height="24" rx="12" fill="#18281D" stroke="{ring_col}" stroke-width="2"/>
      <text x="110" y="204" text-anchor="middle" fill="#FFFFFF" font-size="11" font-weight="800" font-family="sans-serif">{pct:.0f}% BUDGET</text>
      <text x="110" y="232" text-anchor="middle" fill="{status_col}" font-size="8.6" font-weight="800" font-family="sans-serif" letter-spacing="0.6">{status_text}</text>
      <text x="110" y="250" text-anchor="middle" fill="#647869" font-size="10.8" font-weight="700" font-family="sans-serif">{co2_tot:.1f} / {budget_limit} kg CO₂e</text>
      <text x="110" y="266" text-anchor="middle" fill="{status_col}" font-size="9.5" font-weight="700" font-family="sans-serif">Remaining: {max(0.0, budget_limit - co2_tot):.1f} kg</text>
    </svg>
    """

class HeadlessTurtle:
    """Pure mathematical Python Turtle kinematics engine (SVG paths + Pillow vertex rasterizer)."""
    def __init__(self, w=280, h=280):
        self.w, self.h = w, h
        self.img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        self.draw = ImageDraw.Draw(self.img)
        self.x, self.y, self.heading = w / 2, h / 2, 90.0
        self.down, self.color, self.width = True, (78, 126, 54, 255), 3
        self.svg_paths = []
        self._cur_pts = []

    def _flush_svg_stroke(self):
        if len(self._cur_pts) >= 2:
            d = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in self._cur_pts)
            r, g, b, a = self.color
            op = round(a / 255.0, 2)
            self.svg_paths.append(
                f'<path d="{d}" fill="none" stroke="rgb({r},{g},{b})" stroke-opacity="{op}" '
                f'stroke-width="{self.width}" stroke-linecap="round" stroke-linejoin="round"/>'
            )
        self._cur_pts = []

    def setheading(self, angle): self.heading = float(angle) % 360.0
    def left(self, a): self.heading = (self.heading + float(a)) % 360.0
    def right(self, a): self.heading = (self.heading - float(a)) % 360.0

    def penup(self):
        self._flush_svg_stroke()
        self.down = False

    def pendown(self):
        self.down = True
        self._cur_pts = [(self.x, self.y)]

    def forward(self, d):
        rad = math.radians(self.heading)
        nx, ny = self.x + d * math.cos(rad), self.y - d * math.sin(rad)
        if self.down:
            self.draw.line([(self.x, self.y), (nx, ny)], fill=self.color, width=self.width)
            if not self._cur_pts:
                self._cur_pts.append((self.x, self.y))
            self._cur_pts.append((nx, ny))
        self.x, self.y = nx, ny

    def goto(self, x, y):
        if self.down:
            self.draw.line([(self.x, self.y), (x, y)], fill=self.color, width=self.width)
            if not self._cur_pts:
                self._cur_pts.append((self.x, self.y))
            self._cur_pts.append((x, y))
        else:
            self._flush_svg_stroke()
        self.x, self.y = float(x), float(y)

    def arc(self, r, ext, steps=18):
        sl = (2.0 * math.pi * r * (abs(ext) / 360.0)) / max(1, steps)
        step_ang = float(ext) / max(1, steps)
        for _ in range(steps):
            self.forward(sl)
            self.left(step_ang)

    def fill_turtle_poly(self, pts, fill_rgba=None, outline_rgba=None, outline_w=2):
        """Renders a pure-math turtle vertex polygon onto the canvas without primitive shortcuts."""
        if len(pts) < 3:
            return
        if fill_rgba is not None:
            self.draw.polygon(pts, fill=fill_rgba)
        if outline_rgba is not None:
            self.draw.line(list(pts) + [pts[0]], fill=outline_rgba, width=outline_w)

    def pts_to_svg(self, pts):
        return " ".join(f"{px:.1f},{py:.1f}" for px, py in pts)

    def trace_oval_pts(self, cx, cy, rx, ry, rot_deg=0.0, steps=32):
        rr = math.radians(rot_deg)
        ca, sa = math.cos(rr), math.sin(rr)
        pts = []
        for i in range(steps):
            t = (i / float(steps)) * 2.0 * math.pi
            lx, ly = rx * math.cos(t), ry * math.sin(t)
            pts.append((cx + lx * ca - ly * sa, cy + lx * sa + ly * ca))
        return pts

    def trace_superellipse_pts(self, cx, cy, rx, ry, power=2.5, rot_deg=0.0, steps=40):
        rr = math.radians(rot_deg)
        ca, sa = math.cos(rr), math.sin(rr)
        exp = 2.0 / max(0.5, float(power))
        pts = []
        for i in range(steps):
            t = (i / float(steps)) * 2.0 * math.pi
            ct, st_v = math.cos(t), math.sin(t)
            lx = rx * math.copysign(abs(ct) ** exp, ct)
            ly = ry * math.copysign(abs(st_v) ** exp, st_v)
            pts.append((cx + lx * ca - ly * sa, cy + lx * sa + ly * ca))
        return pts

    def trace_bezier_pts(self, p0, p1, p2, p3, steps=22):
        pts = []
        for i in range(steps + 1):
            u = i / float(steps)
            v = 1.0 - u
            px = (v**3)*p0[0] + 3*(v**2)*u*p1[0] + 3*v*(u**2)*p2[0] + (u**3)*p3[0]
            py = (v**3)*p0[1] + 3*(v**2)*u*p1[1] + 3*v*(u**2)*p2[1] + (u**3)*p3[1]
            pts.append((px, py))
        return pts

    def trace_star_pts(self, cx, cy, r_outer, r_inner, points=5):
        pts = []
        self.heading = 90.0
        step_deg = 180.0 / points
        for k in range(points * 2):
            r = r_outer if k % 2 == 0 else r_inner
            rad = math.radians(self.heading)
            pts.append((cx + r * math.cos(rad), cy - r * math.sin(rad)))
            self.right(step_deg)
        return pts

    def trace_scallop_ring_pts(self, cx, cy, r_base, amp, lobes=16, steps=96):
        pts = []
        for i in range(steps):
            ang = (i / float(steps)) * 2.0 * math.pi
            r = r_base + amp * math.cos(lobes * ang)
            pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
        return pts

    def trace_turtle_shell_scutes(self, cx, cy, hex_rx=22, hex_ry=18, outer_rx=44, outer_ry=37):
        hex_pts = []
        self.svg_paths = []
        self.color = (26, 62, 34, 195)
        self.width = 2
        for k in range(6):
            ang = math.radians(k * 60 + 30)
            hx, hy = cx + hex_rx * math.cos(ang), cy + hex_ry * math.sin(ang)
            ox, oy = cx + outer_rx * math.cos(ang), cy + outer_ry * math.sin(ang)
            hex_pts.append((hx, hy))
            self.penup()
            self.goto(hx, hy)
            self.pendown()
            self.goto(ox, oy)
        self.penup()
        return self.pts_to_svg(hex_pts), "\n".join(self.svg_paths)

def _sa_face_expressions(t: HeadlessTurtle, hx, hy, eye_dx, mouth_dy, mood, skin_dark="#15261A", accent="#D69838", cheek_op="0.58", accessory_anchor_y=28):
    """Pure math-traced expressive faces & props across all 5 animated eco mascots."""
    elx, erx = hx - eye_dx, hx + eye_dx
    ey = hy - 2
    my = hy + mouth_dy
    if mood == "ecstatic":
        crown_pts = t.pts_to_svg(t.trace_star_pts(hx, accessory_anchor_y - 10, 9.5, 4.2, points=5))
        s1 = t.pts_to_svg(t.trace_star_pts(hx - 40, hy - 16, 7.5, 2.8, points=4))
        s2 = t.pts_to_svg(t.trace_star_pts(hx + 40, hy - 14, 6.2, 2.3, points=4))
        return (
            f'<g class="sprout"><line x1="{hx}" y1="{accessory_anchor_y + 2}" x2="{hx}" y2="{accessory_anchor_y - 8}" stroke="#B87E22" stroke-width="2.6"/>'
            f'<polygon points="{crown_pts}" fill="#E9B842" stroke="#9C6A12" stroke-width="1.2"/></g>'
            f'<rect x="{elx - 10}" y="{ey - 6}" width="20" height="12" rx="4" fill="#13251B" stroke="{accent}" stroke-width="2"/>'
            f'<rect x="{erx - 10}" y="{ey - 6}" width="20" height="12" rx="4" fill="#13251B" stroke="{accent}" stroke-width="2"/>'
            f'<line x1="{elx + 10}" y1="{ey - 1}" x2="{erx - 10}" y2="{ey - 1}" stroke="{accent}" stroke-width="2.4"/>'
            f'<line x1="{elx - 6}" y1="{ey - 3}" x2="{elx - 1}" y2="{ey + 2}" stroke="#FFFFFF" stroke-width="1.5" opacity="0.55" stroke-linecap="round"/>'
            f'<line x1="{erx - 6}" y1="{ey - 3}" x2="{erx - 1}" y2="{ey + 2}" stroke="#FFFFFF" stroke-width="1.5" opacity="0.55" stroke-linecap="round"/>'
            f'<ellipse cx="{elx - 5}" cy="{ey + 11}" rx="5" ry="2.8" fill="#EB7B89" opacity="{cheek_op}"/>'
            f'<ellipse cx="{erx + 5}" cy="{ey + 11}" rx="5" ry="2.8" fill="#EB7B89" opacity="{cheek_op}"/>'
            f'<path d="M {hx - 11} {my - 1} Q {hx} {my + 13} {hx + 11} {my - 1} Z" fill="#D45B6A" stroke="{skin_dark}" stroke-width="2" stroke-linejoin="round"/>'
            f'<g class="m-fx"><polygon points="{s1}" fill="#E9B842"/><polygon points="{s2}" fill="#E9B842"/></g>'
        )
    if mood == "happy":
        l1 = t.pts_to_svg(t.trace_oval_pts(hx - 7, accessory_anchor_y - 12, 7.5, 4.2, rot_deg=-28, steps=18))
        l2 = t.pts_to_svg(t.trace_oval_pts(hx + 7, accessory_anchor_y - 12, 7.5, 4.2, rot_deg=28, steps=18))
        return (
            f'<g class="sprout"><line x1="{hx}" y1="{accessory_anchor_y + 2}" x2="{hx}" y2="{accessory_anchor_y - 11}" stroke="#264729" stroke-width="2.4"/>'
            f'<polygon points="{l1}" fill="#6DA452" stroke="#264729" stroke-width="1.4"/>'
            f'<polygon points="{l2}" fill="#82BC64" stroke="#264729" stroke-width="1.4"/></g>'
            f'<g class="m-bk">'
            f'<circle cx="{elx}" cy="{ey}" r="5.6" fill="{skin_dark}"/><circle cx="{elx - 1.8}" cy="{ey - 2}" r="2.1" fill="#FFF"/><circle cx="{elx + 1.6}" cy="{ey + 1.5}" r="1.1" fill="#E9E4B0"/>'
            f'<circle cx="{erx}" cy="{ey}" r="5.6" fill="{skin_dark}"/><circle cx="{erx - 1.8}" cy="{ey - 2}" r="2.1" fill="#FFF"/><circle cx="{erx + 1.6}" cy="{ey + 1.5}" r="1.1" fill="#E9E4B0"/>'
            f'</g>'
            f'<ellipse cx="{elx - 5}" cy="{ey + 10}" rx="5.2" ry="3" fill="#EB7B89" opacity="{cheek_op}"/>'
            f'<ellipse cx="{erx + 5}" cy="{ey + 10}" rx="5.2" ry="3" fill="#EB7B89" opacity="{cheek_op}"/>'
            f'<path d="M {hx - 10} {my - 1} Q {hx} {my + 11} {hx + 10} {my - 1}" fill="none" stroke="{skin_dark}" stroke-width="2.8" stroke-linecap="round"/>'
        )
    if mood == "worried":
        return (
            f'<line x1="{elx - 6}" y1="{ey - 7}" x2="{elx + 5}" y2="{ey - 10}" stroke="{skin_dark}" stroke-width="2.2" stroke-linecap="round"/>'
            f'<line x1="{erx - 5}" y1="{ey - 10}" x2="{erx + 6}" y2="{ey - 7}" stroke="{skin_dark}" stroke-width="2.2" stroke-linecap="round"/>'
            f'<circle cx="{elx}" cy="{ey}" r="5.4" fill="{skin_dark}"/><circle cx="{elx - 1.6}" cy="{ey - 1.8}" r="1.8" fill="#FFF"/>'
            f'<circle cx="{erx}" cy="{ey}" r="5.4" fill="{skin_dark}"/><circle cx="{erx - 1.6}" cy="{ey - 1.8}" r="1.8" fill="#FFF"/>'
            f'<path d="M {hx - 9} {my + 4} Q {hx} {my - 4} {hx + 9} {my + 4}" fill="none" stroke="{skin_dark}" stroke-width="2.5" stroke-linecap="round"/>'
            f'<g class="m-sw"><path d="M {erx + 13} {ey - 8} C {erx + 13} {ey - 8}, {erx + 18} {ey - 1}, {erx + 18} {ey + 3} A 5 5 0 1 1 {erx + 8} {ey + 3} C {erx + 8} {ey - 1}, {erx + 13} {ey - 8}, {erx + 13} {ey - 8} Z" fill="#6EC5D8" stroke="#1E5F70" stroke-width="1.2"/></g>'
        )
    if mood == "alarmed":
        bx, by = hx + 33, accessory_anchor_y + 4
        return (
            f'<polygon points="{bx},{by - 12} {bx + 11},{by + 7} {bx - 11},{by + 7}" fill="#C45B4D" stroke="#7A281E" stroke-width="1.5" stroke-linejoin="round"/>'
            f'<line x1="{bx}" y1="{by - 6}" x2="{bx}" y2="{by + 1}" stroke="#FFFFFF" stroke-width="2.2" stroke-linecap="round"/>'
            f'<circle cx="{bx}" cy="{by + 4.3}" r="1.2" fill="#FFFFFF"/>'
            f'<circle cx="{elx}" cy="{ey}" r="6.2" fill="#FFFFFF" stroke="{skin_dark}" stroke-width="2"/><circle cx="{elx}" cy="{ey}" r="2.6" fill="{skin_dark}"/>'
            f'<circle cx="{erx}" cy="{ey}" r="6.2" fill="#FFFFFF" stroke="{skin_dark}" stroke-width="2"/><circle cx="{erx}" cy="{ey}" r="2.6" fill="{skin_dark}"/>'
            f'<ellipse cx="{hx}" cy="{my + 4}" rx="5.2" ry="6.6" fill="{skin_dark}"/>'
        )
    l1 = t.pts_to_svg(t.trace_oval_pts(hx - 6, accessory_anchor_y - 10, 6.5, 3.6, rot_deg=-28, steps=16))
    l2 = t.pts_to_svg(t.trace_oval_pts(hx + 6, accessory_anchor_y - 10, 6.5, 3.6, rot_deg=28, steps=16))
    return (
        f'<g class="sprout"><line x1="{hx}" y1="{accessory_anchor_y + 2}" x2="{hx}" y2="{accessory_anchor_y - 9}" stroke="#264729" stroke-width="2"/>'
        f'<polygon points="{l1}" fill="#6DA452" stroke="#264729" stroke-width="1.3"/>'
        f'<polygon points="{l2}" fill="#82BC64" stroke="#264729" stroke-width="1.3"/></g>'
        f'<path d="M {elx - 6} {ey + 1} Q {elx} {ey - 5} {elx + 6} {ey + 1}" fill="none" stroke="{skin_dark}" stroke-width="2.5" stroke-linecap="round"/>'
        f'<path d="M {erx - 6} {ey + 1} Q {erx} {ey - 5} {erx + 6} {ey + 1}" fill="none" stroke="{skin_dark}" stroke-width="2.5" stroke-linecap="round"/>'
        f'<path d="M {hx - 8} {my} Q {hx} {my + 6.5} {hx + 8} {my}" fill="none" stroke="{skin_dark}" stroke-width="2.2" stroke-linecap="round"/>'
    )

@st.cache_data(show_spinner=False)
def render_animated_avatar_svg(character="turtle", mood="happy", width=155, height=155):
    """Renders all 5 realistic animated eco mascots strictly from pure Python math & HeadlessTurtle kinematics."""
    if character in ["ecstatic", "happy", "mindful", "worried", "alarmed"]:
        mood, character = character, "turtle"
    ck = str(character).lower()
    c_type = "fox" if "fox" in ck else "owl" if "owl" in ck else "bee" if ("bee" in ck or "pollinator" in ck) else "panda" if "panda" in ck else "turtle"
    shiver = "shiver" if mood in ["worried", "alarmed"] else "bob"
    uid = f"sa_{c_type}_{mood}_{width}"
    aura_col = "#C45B4D" if mood == "alarmed" else ("#D69838" if mood in ("ecstatic", "worried") else "#5E9643")
    aura_op = "0.26" if mood in ("ecstatic", "alarmed") else "0.17"

    t = HeadlessTurtle(200, 200)
    parts = [
        f'<svg width="{width}" height="{height}" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg" style="max-width:100%; height:auto; display:block; margin:0 auto;">',
        '<defs>',
        f'<radialGradient id="{uid}_aura" cx="50%" cy="52%" r="50%"><stop offset="0%" stop-color="{aura_col}" stop-opacity="{aura_op}"/><stop offset="100%" stop-color="{aura_col}" stop-opacity="0"/></radialGradient>',
        f'<linearGradient id="{uid}_sh" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#6DA452"/><stop offset="55%" stop-color="#417232"/><stop offset="100%" stop-color="#224420"/></linearGradient>',
        f'<linearGradient id="{uid}_fox" x1="15%" y1="0%" x2="85%" y2="100%"><stop offset="0%" stop-color="#EB8E47"/><stop offset="55%" stop-color="#D46B2E"/><stop offset="100%" stop-color="#9B4318"/></linearGradient>',
        f'<linearGradient id="{uid}_owl" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#9A6842"/><stop offset="60%" stop-color="#764B2A"/><stop offset="100%" stop-color="#4B2E17"/></linearGradient>',
        f'<linearGradient id="{uid}_bee" x1="20%" y1="0%" x2="80%" y2="100%"><stop offset="0%" stop-color="#F6D15C"/><stop offset="55%" stop-color="#E3AC36"/><stop offset="100%" stop-color="#B87E1A"/></linearGradient>',
        f'<clipPath id="{uid}_beec"><polygon points="{t.pts_to_svg(t.trace_superellipse_pts(100, 118, 42, 48, power=2.4, steps=36))}"/></clipPath>',
        '</defs>',
        '<style>',
        '@keyframes av-bob { 0%, 100% { transform: translateY(0px); } 50% { transform: translateY(-6px); } }',
        '@keyframes av-shv { 0%, 100% { transform: translate(0,0); } 25% { transform: translate(-2px,1px); } 75% { transform: translate(2px,-1px); } }',
        '@keyframes wv-l { 0%, 100% { transform: rotate(0deg); } 50% { transform: rotate(18deg); } }',
        '@keyframes wv-r { 0%, 100% { transform: rotate(0deg); } 50% { transform: rotate(-18deg); } }',
        '@keyframes sp-s { 0%, 100% { transform: rotate(-7deg); } 50% { transform: rotate(7deg); } }',
        '@keyframes av-bk { 0%, 88%, 100% { transform: scaleY(1); } 94% { transform: scaleY(0.1); } }',
        '@keyframes av-sw { 0%, 100% { transform: translateY(0px); opacity: 0.9; } 50% { transform: translateY(5px); opacity: 0.45; } }',
        '@keyframes av-fx { 0%, 100% { opacity: 0.55; transform: translateY(0px); } 50% { opacity: 1; transform: translateY(-4px); } }',
        '.bob { animation: av-bob 2.5s ease-in-out infinite; }',
        '.shiver { animation: av-shv 0.22s infinite; }',
        '.wave-l { animation: wv-l 1.5s ease-in-out infinite; transform-origin: 54px 96px; }',
        '.wave-r { animation: wv-r 1.5s ease-in-out infinite; transform-origin: 146px 96px; }',
        '.sprout { animation: sp-s 2.1s ease-in-out infinite; transform-origin: 100px 30px; }',
        '.m-bk { transform-box: fill-box; transform-origin: center; animation: av-bk 4.1s infinite; }',
        '.m-sw { animation: av-sw 1.5s ease-in-out infinite; }',
        '.m-fx { animation: av-fx 2.1s ease-in-out infinite; }',
        '</style>',
        f'<circle cx="100" cy="104" r="90" fill="url(#{uid}_aura)"/>',
        '<ellipse cx="100" cy="178" rx="46" ry="7.5" fill="rgba(19,38,27,0.12)"/>',
        f'<g class="{shiver}">',
    ]

    if c_type == "fox":
        tail_top = t.trace_bezier_pts((132, 146), (176, 148), (190, 96), (164, 78), steps=20)
        tail_bot = t.trace_bezier_pts((164, 78), (144, 88), (134, 118), (126, 138), steps=20)
        tail_pts = t.pts_to_svg(tail_top + tail_bot)
        tip_pts = t.pts_to_svg(
            t.trace_bezier_pts((164, 78), (181, 88), (179, 108), (160, 110), steps=14)
            + t.trace_bezier_pts((160, 110), (154, 96), (156, 86), (164, 78), steps=12)
        )
        body_pts = t.pts_to_svg(t.trace_superellipse_pts(100, 132, 43, 40, power=2.5, steps=36))
        bib_pts = t.pts_to_svg(t.trace_superellipse_pts(100, 135, 25, 28, power=2.3, steps=28))
        paw_l = t.pts_to_svg(t.trace_oval_pts(74, 165, 13, 9, rot_deg=-8, steps=20))
        paw_r = t.pts_to_svg(t.trace_oval_pts(126, 165, 13, 9, rot_deg=8, steps=20))
        head_pts = t.pts_to_svg(t.trace_superellipse_pts(100, 66, 37, 29, power=2.3, steps=36))
        cheek_l = t.pts_to_svg(t.trace_oval_pts(80, 74, 17, 13, rot_deg=14, steps=22))
        cheek_r = t.pts_to_svg(t.trace_oval_pts(120, 74, 17, 13, rot_deg=-14, steps=22))
        ear_l = t.pts_to_svg(t.trace_bezier_pts((64, 52), (56, 22), (72, 16), (86, 40), steps=16))
        ear_r = t.pts_to_svg(t.trace_bezier_pts((136, 52), (144, 22), (128, 16), (114, 40), steps=16))
        parts += [
            f'<g class="wave-r" style="transform-origin:132px 142px;"><polygon points="{tail_pts}" fill="url(#{uid}_fox)" stroke="#7F3512" stroke-width="2.2" stroke-linejoin="round"/><polygon points="{tip_pts}" fill="#FFF9EC"/></g>',
            f'<polygon points="{body_pts}" fill="url(#{uid}_fox)" stroke="#7F3512" stroke-width="2.4" stroke-linejoin="round"/>',
            f'<polygon points="{bib_pts}" fill="#FDF2E4" stroke="#E0B18A" stroke-width="1.4"/>',
            f'<polygon points="{paw_l}" fill="#4B2B1C" stroke="#2D1910" stroke-width="1.8"/>',
            f'<polygon points="{paw_r}" fill="#4B2B1C" stroke="#2D1910" stroke-width="1.8"/>',
            f'<g class="wave-l"><polygon points="{t.pts_to_svg(t.trace_oval_pts(58, 122, 10, 18, rot_deg=24, steps=20))}" fill="#D46B2E" stroke="#7F3512" stroke-width="2"/></g>',
            f'<polygon points="{ear_l}" fill="#D46B2E" stroke="#7F3512" stroke-width="2.2" stroke-linejoin="round"/><polygon points="68,46 67,25 81,40" fill="#F4C7D2"/>',
            f'<polygon points="{ear_r}" fill="#D46B2E" stroke="#7F3512" stroke-width="2.2" stroke-linejoin="round"/><polygon points="132,46 133,25 119,40" fill="#F4C7D2"/>',
            f'<polygon points="{head_pts}" fill="url(#{uid}_fox)" stroke="#7F3512" stroke-width="2.4" stroke-linejoin="round"/>',
            f'<polygon points="{cheek_l}" fill="#FFF8EE"/><polygon points="{cheek_r}" fill="#FFF8EE"/>',
            '<path d="M 88 52 Q 100 44 112 52" fill="none" stroke="#F8C28B" stroke-width="2" stroke-linecap="round" opacity="0.65"/>',
            '<polygon points="94,70 106,70 100,77" fill="#1F241F"/>',
            '<line x1="65" y1="73" x2="80" y2="75" stroke="#7F3512" stroke-width="1.2"/><line x1="64" y1="79" x2="80" y2="79" stroke="#7F3512" stroke-width="1.2"/>',
            '<line x1="135" y1="73" x2="120" y2="75" stroke="#7F3512" stroke-width="1.2"/><line x1="136" y1="79" x2="120" y2="79" stroke="#7F3512" stroke-width="1.2"/>',
            _sa_face_expressions(t, 100, 62, 13, 19, mood, skin_dark="#1C261D", accessory_anchor_y=32),
        ]

    elif c_type == "owl":
        body_pts = t.pts_to_svg(t.trace_superellipse_pts(100, 122, 46, 44, power=2.6, steps=36))
        belly_pts = t.pts_to_svg(t.trace_superellipse_pts(100, 128, 32, 31, power=2.4, steps=28))
        wing_l = t.pts_to_svg(t.trace_oval_pts(55, 120, 13, 31, rot_deg=16, steps=24))
        wing_r = t.pts_to_svg(t.trace_oval_pts(145, 120, 13, 31, rot_deg=-16, steps=24))
        head_pts = t.pts_to_svg(t.trace_superellipse_pts(100, 62, 36, 30, power=2.5, steps=32))
        disc_l = t.pts_to_svg(t.trace_oval_pts(85, 60, 16, 16, steps=24))
        disc_r = t.pts_to_svg(t.trace_oval_pts(115, 60, 16, 16, steps=24))
        feathers_svg = "".join(
            f'<path d="M {fx - 7} {fy} Q {fx} {fy + 8} {fx + 7} {fy}" fill="none" stroke="#AD783B" stroke-width="2" stroke-linecap="round"/>'
            for fy, cols in [(114, [84, 100, 116]), (127, [78, 93, 107, 122]), (140, [86, 100, 114])]
            for fx in cols
        )
        parts += [
            '<line x1="56" y1="169" x2="144" y2="169" stroke="#5A4228" stroke-width="5.5" stroke-linecap="round"/>',
            '<ellipse cx="136" cy="166" rx="7" ry="3.5" fill="#6DA452" transform="rotate(-24 136 166)"/>',
            f'<g class="wave-l"><polygon points="{wing_l}" fill="#855632" stroke="#4B2E17" stroke-width="2.2"/></g>',
            f'<g class="wave-r"><polygon points="{wing_r}" fill="#855632" stroke="#4B2E17" stroke-width="2.2"/></g>',
            f'<polygon points="{body_pts}" fill="url(#{uid}_owl)" stroke="#4B2E17" stroke-width="2.5" stroke-linejoin="round"/>',
            f'<polygon points="{belly_pts}" fill="#FAF0D2" stroke="#B88442" stroke-width="1.8"/>',
            feathers_svg,
            '<polygon points="75,164 81,172 87,164" fill="#D99B38" stroke="#855712" stroke-width="1.4"/>',
            '<polygon points="113,164 119,172 125,164" fill="#D99B38" stroke="#855712" stroke-width="1.4"/>',
            '<polygon points="68,38 56,18 81,31" fill="#764B2A" stroke="#4B2E17" stroke-width="2" stroke-linejoin="round"/>',
            '<polygon points="132,38 144,18 119,31" fill="#764B2A" stroke="#4B2E17" stroke-width="2" stroke-linejoin="round"/>',
            f'<polygon points="{head_pts}" fill="url(#{uid}_owl)" stroke="#4B2E17" stroke-width="2.4"/>',
            f'<polygon points="{disc_l}" fill="#FAF0D2" stroke="#C98A32" stroke-width="2.2"/>',
            f'<polygon points="{disc_r}" fill="#FAF0D2" stroke="#C98A32" stroke-width="2.2"/>',
            '<polygon points="95,66 105,66 100,77" fill="#DF9E34" stroke="#8E5D12" stroke-width="1.4" stroke-linejoin="round"/>',
            _sa_face_expressions(t, 100, 62, 15, 20, mood, skin_dark="#18281D", accessory_anchor_y=28),
        ]

    elif c_type == "bee":
        wl_top = t.pts_to_svg(t.trace_oval_pts(64, 72, 30, 16, rot_deg=-34, steps=24))
        wr_top = t.pts_to_svg(t.trace_oval_pts(136, 72, 30, 16, rot_deg=34, steps=24))
        wl_bot = t.pts_to_svg(t.trace_oval_pts(62, 98, 21, 11, rot_deg=-16, steps=20))
        wr_bot = t.pts_to_svg(t.trace_oval_pts(138, 98, 21, 11, rot_deg=16, steps=20))
        body_pts = t.pts_to_svg(t.trace_superellipse_pts(100, 118, 42, 48, power=2.4, steps=36))
        head_pts = t.pts_to_svg(t.trace_superellipse_pts(100, 62, 29, 25, power=2.4, steps=28))
        parts += [
            f'<g class="wave-l"><polygon points="{wl_top}" fill="#E6F4FA" opacity="0.88" stroke="#6B98B3" stroke-width="1.6"/><polygon points="{wl_bot}" fill="#E6F4FA" opacity="0.82" stroke="#6B98B3" stroke-width="1.4"/><line x1="84" y1="84" x2="48" y2="62" stroke="#8FB8CE" stroke-width="1.2"/></g>',
            f'<g class="wave-r"><polygon points="{wr_top}" fill="#E6F4FA" opacity="0.88" stroke="#6B98B3" stroke-width="1.6"/><polygon points="{wr_bot}" fill="#E6F4FA" opacity="0.82" stroke="#6B98B3" stroke-width="1.4"/><line x1="116" y1="84" x2="152" y2="62" stroke="#8FB8CE" stroke-width="1.2"/></g>',
            '<polygon points="95,164 105,164 100,179" fill="#1F2E24"/>',
            f'<polygon points="{body_pts}" fill="url(#{uid}_bee)" stroke="#6F4B2C" stroke-width="2.4"/>',
            f'<g clip-path="url(#{uid}_beec)">'
            '<path d="M 52 104 Q 100 116 148 104" fill="none" stroke="#1E2B22" stroke-width="11"/>'
            '<path d="M 52 130 Q 100 142 148 130" fill="none" stroke="#1E2B22" stroke-width="11"/>'
            '<path d="M 58 152 Q 100 162 142 152" fill="none" stroke="#1E2B22" stroke-width="9"/>'
            '</g>',
            f'<polygon points="{body_pts}" fill="none" stroke="#6F4B2C" stroke-width="2.4"/>',
            '<ellipse cx="100" cy="86" rx="28" ry="8" fill="#5E4326"/>',
            '<path d="M 90 42 Q 78 21 67 25 M 110 42 Q 122 21 133 25" fill="none" stroke="#1F2E24" stroke-width="2.4" stroke-linecap="round"/>',
            '<circle cx="67" cy="25" r="4.5" fill="#E3AC36" stroke="#6F4B2C" stroke-width="1.2"/>',
            '<circle cx="133" cy="25" r="4.5" fill="#E3AC36" stroke="#6F4B2C" stroke-width="1.2"/>',
            f'<polygon points="{head_pts}" fill="url(#{uid}_bee)" stroke="#6F4B2C" stroke-width="2.3"/>',
            _sa_face_expressions(t, 100, 62, 12, 13, mood, skin_dark="#18281D", accessory_anchor_y=34),
        ]

    elif c_type == "panda":
        body_pts = t.pts_to_svg(t.trace_superellipse_pts(100, 132, 46, 42, power=2.5, steps=36))
        head_pts = t.pts_to_svg(t.trace_superellipse_pts(100, 64, 37, 31, power=2.4, steps=32))
        patch_l = t.pts_to_svg(t.trace_oval_pts(85, 60, 11, 13.5, rot_deg=-16, steps=22))
        patch_r = t.pts_to_svg(t.trace_oval_pts(115, 60, 11, 13.5, rot_deg=16, steps=22))
        arm_l = t.pts_to_svg(t.trace_oval_pts(55, 104, 13, 24, rot_deg=-28, steps=22))
        arm_r = t.pts_to_svg(t.trace_oval_pts(145, 104, 13, 24, rot_deg=28, steps=22))
        bamboo_leaf1 = t.pts_to_svg(t.trace_oval_pts(160, 102, 11, 4.5, rot_deg=-26, steps=18))
        bamboo_leaf2 = t.pts_to_svg(t.trace_oval_pts(161, 118, 9.5, 4, rot_deg=22, steps=18))
        parts += [
            f'<polygon points="{body_pts}" fill="#FFFDF8" stroke="#1F2E24" stroke-width="2.5"/>',
            '<path d="M 55 112 Q 100 130 145 112 L 143 136 Q 100 150 57 136 Z" fill="#1F2E24"/>',
            f'<g class="wave-l"><polygon points="{arm_l}" fill="#1F2E24"/></g>',
            f'<g class="wave-r"><polygon points="{arm_r}" fill="#1F2E24"/></g>',
            '<ellipse cx="64" cy="166" rx="14" ry="10" fill="#1F2E24"/><ellipse cx="64" cy="166" rx="6" ry="4" fill="#E8B8C0"/>',
            '<ellipse cx="136" cy="166" rx="14" ry="10" fill="#1F2E24"/><ellipse cx="136" cy="166" rx="6" ry="4" fill="#E8B8C0"/>',
            '<circle cx="67" cy="39" r="14" fill="#1F2E24"/><circle cx="133" cy="39" r="14" fill="#1F2E24"/>',
            f'<polygon points="{head_pts}" fill="#FFFDF8" stroke="#1F2E24" stroke-width="2.4"/>',
            f'<polygon points="{patch_l}" fill="#1F2E24"/><polygon points="{patch_r}" fill="#1F2E24"/>',
            '<ellipse cx="100" cy="73" rx="5.5" ry="3.8" fill="#1F2E24"/>',
            '<line x1="150" y1="88" x2="150" y2="148" stroke="#4E7E36" stroke-width="4.5" stroke-linecap="round"/>',
            '<line x1="147" y1="108" x2="153" y2="108" stroke="#DCEBD4" stroke-width="1.6"/>',
            '<line x1="147" y1="128" x2="153" y2="128" stroke="#DCEBD4" stroke-width="1.6"/>',
            f'<polygon points="{bamboo_leaf1}" fill="#6DA452" stroke="#355D28" stroke-width="1.2"/>',
            f'<polygon points="{bamboo_leaf2}" fill="#82BC64" stroke="#355D28" stroke-width="1.2"/>',
            _sa_face_expressions(t, 100, 62, 15, 20, mood, skin_dark="#FFFFFF" if mood in ("happy", "worried") else "#18281D", cheek_op="0.52", accessory_anchor_y=30),
        ]

    else:
        hl_pts = t.pts_to_svg(t.trace_oval_pts(64, 152, 13, 20, rot_deg=-24, steps=24))
        hr_pts = t.pts_to_svg(t.trace_oval_pts(136, 152, 13, 20, rot_deg=24, steps=24))
        fl_pts = t.pts_to_svg(t.trace_oval_pts(48, 102, 15, 27, rot_deg=-34, steps=26))
        fr_pts = t.pts_to_svg(t.trace_oval_pts(152, 102, 15, 27, rot_deg=34, steps=26))
        sh_outer = t.pts_to_svg(t.trace_superellipse_pts(100, 124, 52, 46, power=2.3, steps=36))
        sh_mid = t.pts_to_svg(t.trace_superellipse_pts(100, 124, 41, 35, power=2.3, steps=32))
        hex_pts, ribs_svg = t.trace_turtle_shell_scutes(100, 124, hex_rx=22, hex_ry=18, outer_rx=43, outer_ry=36)
        head_pts = t.pts_to_svg(t.trace_superellipse_pts(100, 59, 26, 23, power=2.2, steps=28))
        shell_stroke = "#E9B842" if mood == "ecstatic" else "#234F26"
        parts += [
            f'<polygon points="{hl_pts}" fill="#5A8F44" stroke="#234F26" stroke-width="2" stroke-linejoin="round"/>',
            f'<polygon points="{hr_pts}" fill="#5A8F44" stroke="#234F26" stroke-width="2" stroke-linejoin="round"/>',
            '<polygon points="94,164 106,164 100,179" fill="#5A8F44" stroke="#234F26" stroke-width="1.8" stroke-linejoin="round"/>',
            f'<g class="wave-l"><polygon points="{fl_pts}" fill="#77AD5C" stroke="#234F26" stroke-width="2" stroke-linejoin="round"/></g>',
            f'<g class="wave-r"><polygon points="{fr_pts}" fill="#77AD5C" stroke="#234F26" stroke-width="2" stroke-linejoin="round"/></g>',
            f'<polygon points="{sh_outer}" fill="url(#{uid}_sh)" stroke="#1D4020" stroke-width="2.8" stroke-linejoin="round"/>',
            f'<polygon points="{sh_mid}" fill="#5A8F44" stroke="#264E29" stroke-width="1.8" stroke-linejoin="round"/>',
            ribs_svg,
            f'<polygon points="{hex_pts}" fill="#95C47A" stroke="{shell_stroke}" stroke-width="2.2" stroke-linejoin="round"/>',
            '<path d="M 68 96 Q 82 86 104 86" fill="none" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round" opacity="0.42"/>',
            f'<polygon points="{head_pts}" fill="#95C47A" stroke="#234F26" stroke-width="2.2" stroke-linejoin="round"/>',
            _sa_face_expressions(t, 100, 59, 12, 9, mood, skin_dark="#15261A", accessory_anchor_y=30),
        ]

    parts.append("</g></svg>")
    return "".join(parts)

def get_mascot_reaction(mascot_str, item_name, live_co2, mood, is_eth):
    name = mascot_str.split()[0]
    if mood == "ecstatic":
        return f"CLEVER ECO PICK! {name} put on gold sunglasses — '{item_name}' is a circular win!"
    if mood == "happy":
        return f"Wonderful green choice! '{item_name}' adds just {live_co2} kg CO₂e. {name} cheers you on!"
    if mood == "mindful":
        return f"Recorded '{item_name}' ({live_co2} kg CO₂e). Check smarter swaps below to lighten your total."
    if mood == "worried":
        return f"Getting heavy! '{item_name}' emitted {live_co2} kg CO₂e. Try a swap below to rebalance."
    return f"CARBON SPIKE ALERT: '{item_name}' created {live_co2} kg CO₂e! Swap one item to stay green."

# ------------------------------------------------------------------------------
# TURTLE ART VAULT (100% Pure Math HeadlessTurtle Vertex Rasterization)
# ------------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def _render_turtle_art_png_cached(art_type="leaf"):
    """Draws 280x280 botanical art strictly from HeadlessTurtle math vertex equations."""
    w, h = 280, 280
    t = HeadlessTurtle(w, h)
    cx, cy = 140, 136

    if art_type == "preview":
        t.fill_turtle_poly(t.trace_oval_pts(cx, cy, 90, 90, steps=48), (226, 240, 216, 185), (109, 164, 82, 175), 2)
        t.fill_turtle_poly(t.trace_oval_pts(cx, cy, 74, 74, steps=40), None, (109, 164, 82, 95), 1)
        for deg in range(0, 360, 30):
            t.penup(); t.goto(cx, cy); t.setheading(deg); t.forward(94); t.color = (109, 164, 82, 135); t.width = 2; t.pendown(); t.forward(9)
        t.penup()
        for k in range(1, 28):
            ang = math.radians(k * 137.508)
            r = 7.2 * math.sqrt(k)
            sx, sy = cx + r * math.cos(ang), cy + r * math.sin(ang)
            t.fill_turtle_poly(t.trace_oval_pts(sx, sy, 4.2, 4.2, steps=12), (78, 126, 54, 210), (45, 84, 38, 220), 1)
        seed_pts = t.trace_bezier_pts((cx, cy - 36), (cx + 22, cy - 12), (cx + 18, cy + 20), (cx, cy + 32), steps=18)
        seed_pts += t.trace_bezier_pts((cx, cy + 32), (cx - 18, cy + 20), (cx - 22, cy - 12), (cx, cy - 36), steps=18)
        t.fill_turtle_poly(seed_pts, (109, 164, 82, 170), (62, 107, 53, 215), 2)
        buf = io.BytesIO(); t.img.save(buf, format="PNG"); return buf.getvalue()

    if art_type == "leaf":
        t.fill_turtle_poly(t.trace_oval_pts(cx, cy, 102, 102, steps=56), (232, 243, 224, 242), (78, 126, 54, 225), 3)
        t.fill_turtle_poly(t.trace_oval_pts(cx - 16, cy - 32, 36, 36, steps=32), (235, 206, 98, 130))
        t.penup(); t.goto(cx - 4, cy + 84); t.setheading(84); t.color = (45, 84, 38, 255); t.width = 4; t.pendown(); t.forward(50)
        leaf_r = t.trace_bezier_pts((cx - 2, cy + 56), (cx + 56, cy + 26), (cx + 54, cy - 36), (cx + 12, cy - 66), steps=24)
        leaf_l = t.trace_bezier_pts((cx + 12, cy - 66), (cx - 40, cy - 34), (cx - 44, cy + 24), (cx - 2, cy + 56), steps=24)
        t.fill_turtle_poly(leaf_r + leaf_l, (78, 126, 54, 245), (45, 84, 38, 255), 2)
        lit_mid = t.trace_bezier_pts((cx - 2, cy + 56), (cx + 10, cy + 8), (cx + 14, cy - 32), (cx + 12, cy - 66), steps=20)
        t.fill_turtle_poly(lit_mid + leaf_l, (133, 180, 108, 215))
        side_leaf = t.trace_bezier_pts((cx - 2, cy + 42), (cx - 38, cy + 30), (cx - 58, cy + 4), (cx - 30, cy + 8), steps=14)
        side_leaf += t.trace_bezier_pts((cx - 30, cy + 8), (cx - 16, cy + 16), (cx - 6, cy + 28), (cx - 2, cy + 42), steps=10)
        t.fill_turtle_poly(side_leaf, (156, 198, 126, 238), (62, 107, 53, 255), 2)
        t.penup(); t.goto(cx, cy + 54); t.setheading(84); t.color = (245, 250, 240, 225); t.width = 2; t.pendown(); t.forward(112)
        for iy, xo in [(cy + 28, 3), (cy + 4, 8), (cy - 20, 10)]:
            t.penup(); t.goto(cx + xo, iy); t.setheading(40); t.pendown(); t.arc(38, 32, steps=10)
            t.penup(); t.goto(cx + xo, iy); t.setheading(140); t.pendown(); t.arc(38, -32, steps=10)

    elif art_type == "footprint":
        t.fill_turtle_poly(t.trace_oval_pts(cx, cy, 102, 102, steps=56), (235, 243, 226, 242), (78, 126, 54, 225), 3)
        for deg in range(0, 360, 30):
            rad = math.radians(deg)
            px, py = cx + 94 * math.cos(rad), cy + 94 * math.sin(rad)
            t.fill_turtle_poly(t.trace_oval_pts(px, py, 7.5, 4.2, rot_deg=deg + 45, steps=14), (133, 180, 108, 240), (62, 107, 53, 210), 1)
        t.fill_turtle_poly(t.trace_superellipse_pts(cx - 2, cy + 42, 21, 24, power=2.3, steps=28), (78, 126, 54, 245))
        sole_r = t.trace_bezier_pts((cx - 18, cy + 34), (cx - 12, cy), (cx - 30, cy - 28), (cx - 14, cy - 58), steps=18)
        sole_t = t.trace_bezier_pts((cx - 14, cy - 58), (cx, cy - 66), (cx + 22, cy - 56), (cx + 28, cy - 30), steps=14)
        sole_l = t.trace_bezier_pts((cx + 28, cy - 30), (cx + 16, cy - 2), (cx + 18, cy + 26), (cx + 14, cy + 40), steps=16)
        t.fill_turtle_poly(sole_r + sole_t + sole_l, (78, 126, 54, 245), (45, 84, 38, 230), 2)
        t.fill_turtle_poly(t.trace_oval_pts(cx, cy - 36, 26, 22, rot_deg=-8, steps=26), (102, 154, 76, 235))
        for tx, ty, tr in [(-20, -76, 9.5), (-1, -83, 8.2), (14, -79, 7.2), (25, -71, 6.2), (34, -60, 5.2)]:
            t.fill_turtle_poly(t.trace_oval_pts(cx + tx, cy + ty, tr, tr * 1.15, rot_deg=tx * 0.6, steps=18), (109, 164, 82, 245), (255, 253, 245, 225), 2)

    elif art_type == "traveler":
        t.fill_turtle_poly(t.trace_oval_pts(cx, cy, 102, 102, steps=56), (238, 246, 232, 245), (78, 126, 54, 225), 3)
        hill_arc = t.trace_bezier_pts((cx - 96, cy + 28), (cx - 32, cy + 8), (cx + 42, cy + 12), (cx + 96, cy + 32), steps=24)
        hill_bot = t.trace_oval_pts(cx, cy, 98, 98, steps=48)
        hill_clip = [p for p in hill_bot if p[1] >= cy + 26]
        t.fill_turtle_poly(hill_arc + list(reversed(hill_clip)), (167, 206, 132, 220))
        t.fill_turtle_poly(t.trace_oval_pts(cx + 40, cy - 50, 22, 22, steps=28), (232, 200, 92, 175))
        t.penup(); t.goto(cx - 18, cy + 20); t.color = (36, 58, 44, 255); t.width = 7; t.pendown(); t.goto(cx - 28, cy + 62)
        t.penup(); t.goto(cx - 6, cy + 20); t.color = (48, 76, 58, 255); t.width = 7; t.pendown(); t.goto(cx + 6, cy + 62)
        t.penup()
        t.fill_turtle_poly([(cx - 30, cy - 24), (cx + 4, cy - 24), (cx + 8, cy + 22), (cx - 32, cy + 22)], (78, 126, 54, 255), (36, 58, 44, 255), 2)
        t.fill_turtle_poly(t.trace_oval_pts(cx - 13, cy - 42, 12, 12, steps=22), (232, 184, 146, 255))
        hair_pts = t.trace_bezier_pts((cx - 26, cy - 44), (cx - 20, cy - 59), (cx - 4, cy - 59), (cx, cy - 44), steps=14)
        t.fill_turtle_poly(hair_pts, (42, 38, 35, 255))
        t.fill_turtle_poly([(cx + 4, cy - 4), (cx + 26, cy - 4), (cx + 26, cy + 22), (cx + 4, cy + 22)], (242, 228, 181, 255), (140, 115, 67, 255), 2)
        sh_dome = t.trace_bezier_pts((cx + 26, cy + 56), (cx + 34, cy + 32), (cx + 62, cy + 32), (cx + 70, cy + 56), steps=18)
        t.fill_turtle_poly(sh_dome, (61, 107, 53, 255), (30, 60, 36, 255), 2)
        t.fill_turtle_poly(t.trace_oval_pts(cx + 73, cy + 51, 8, 7, steps=16), (119, 177, 90, 255), (30, 60, 36, 255), 1)

    else:
        cm = 114
        t.fill_turtle_poly([(cx - 24, cm + 26), (cx - 52, cm + 136), (cx - 30, cm + 118), (cx - 10, cm + 128), (cx - 4, cm + 28)], (78, 126, 54, 255), (45, 84, 38, 255), 2)
        t.fill_turtle_poly([(cx + 4, cm + 28), (cx + 10, cm + 128), (cx + 30, cm + 118), (cx + 52, cm + 136), (cx + 24, cm + 26)], (61, 107, 53, 255), (38, 72, 34, 255), 2)
        t.fill_turtle_poly(t.trace_scallop_ring_pts(cx, cm, 59, 6, lobes=24, steps=96), (214, 152, 56, 255), (235, 194, 96, 255), 2)
        t.fill_turtle_poly(t.trace_oval_pts(cx, cm, 50, 50, steps=44), (228, 172, 72, 255), (168, 110, 30, 255), 2)
        t.fill_turtle_poly(t.trace_oval_pts(cx, cm, 41, 41, steps=40), (45, 84, 38, 255), (149, 196, 122, 240), 2)
        t.fill_turtle_poly(t.trace_oval_pts(cx, cm, 29, 29, steps=36), (250, 244, 212, 255), (196, 136, 40, 255), 2)
        t.fill_turtle_poly(t.trace_star_pts(cx, cm, 20, 8, points=5), (200, 140, 40, 255), (138, 86, 20, 255), 2)

    buf = io.BytesIO()
    t.img.save(buf, format="PNG")
    return buf.getvalue()

@st.cache_data(show_spinner=False)
def get_turtle_art_data_uri(art_type="leaf"):
    return "data:image/png;base64," + base64.b64encode(_render_turtle_art_png_cached(art_type)).decode("ascii")

# ------------------------------------------------------------------------------
# DOMAIN LOGIC, STREAK, BADGE & OPTIMIZER HELPERS
# ------------------------------------------------------------------------------

def calculate_carbon(price, category, is_ethical):
    rate = CATEGORIES.get(category, {"multiplier": 0.35})["multiplier"]
    base = price * rate
    return round(base * 0.70 if is_ethical else base, 2)

def get_equivalency(carbon_kg):
    return int(carbon_kg * 2.4), int(carbon_kg * 121), round((carbon_kg / 21.0) * 12, 1)

def compute_eco_streak(purchases):
    cur = 0
    for p in reversed(purchases):
        if p.get("is_ethical", False): cur += 1
        else: break
    best, run = 0, 0
    for p in purchases:
        run = (run + 1) if p.get("is_ethical", False) else 0
        best = max(best, run)
    return cur, best

def get_collected_arts(purchases):
    earned = set()
    if len(purchases) >= 2:
        earned.add("traveler")
    for p in purchases:
        eth, co2 = p.get("is_ethical", False), p.get("carbon_kg", 0.0)
        if eth and co2 <= 3.0: earned.add("badge")
        elif eth: earned.add("leaf")
        elif co2 <= 10.0: earned.add("footprint")
    return earned

def get_user_eco_rank(purchases):
    n, eth = len(purchases), sum(1 for p in purchases if p.get("is_ethical", False))
    if n == 0: return "🌱 Eco Novice"
    if eth >= 5 or (n >= 5 and eth >= 3): return "👑 Biosphere Master"
    if eth >= 2 or n >= 3: return "🌿 Conscious Pioneer"
    return "🌾 Mindful Forager"

def evaluate_badges(purchases):
    total_items = len(purchases)
    total_spend = sum(p.get("price", 0.0) for p in purchases)
    total_co2 = sum(p.get("carbon_kg", 0.0) for p in purchases)
    ethical_count = sum(1 for p in purchases if p.get("is_ethical", False))
    avg_int = (total_co2 / total_spend) if total_spend > 0 else 0.0
    co2_saved = max(0.0, round(total_spend * 0.45 - total_co2, 1))
    zw_cnt = sum(1 for p in purchases if "Zero-Waste" in p.get("category", "") or "Thrift" in p.get("category", ""))

    badges = [
        {"id": "starter", "name": "Seed Starter", "icon": "🌱", "img": "badges/starter.png", "desc": "Log your 1st conscious purchase in the dashboard", "unlocked": total_items >= 1, "progress": f"{min(total_items, 1)}/1 item", "pct": 100 if total_items >= 1 else 0},
        {"id": "low_impact", "name": "Low Impact Shopper", "icon": "🍃", "img": "badges/budget.png", "desc": "Maintain carbon intensity ≤ 0.25 kg/$ (min 2 items)", "unlocked": total_items >= 2 and avg_int <= 0.25, "progress": f"{avg_int:.2f} kg/$ (Goal ≤ 0.25)" if total_items >= 2 else f"{total_items}/2 items required", "pct": 100 if (total_items >= 2 and avg_int <= 0.25) else (max(10, min(95, int((0.25 / max(avg_int, 0.26)) * 100))) if total_items >= 2 else int((total_items / 2) * 100))},
        {"id": "ethical_pioneer", "name": "Conscious Pioneer", "icon": "♻️", "img": "badges/circular.png", "desc": "Choose 3+ verified circular, thrift, or ethical items", "unlocked": ethical_count >= 3, "progress": f"{ethical_count}/3 ethical items", "pct": min(100, int((ethical_count / 3.0) * 100))},
        {"id": "eco_saver", "name": "Eco Saver of the Month", "icon": "🌟", "img": "badges/collector.png", "desc": "Save 10+ kg CO₂ vs standard retail baseline", "unlocked": co2_saved >= 10.0 and total_items >= 1, "progress": f"{co2_saved:.1f}/10.0 kg CO₂ saved", "pct": min(100, int((co2_saved / 10.0) * 100)) if total_items >= 1 else 0},
        {"id": "zero_waste", "name": "Zero-Waste Hero", "icon": "🏆", "img": "badges/champion.png", "desc": "Log 2+ zero-waste or second-hand thrift items", "unlocked": zw_cnt >= 2, "progress": f"{zw_cnt}/2 items", "pct": min(100, int((zw_cnt / 2.0) * 100))},
    ]
    return badges, total_spend, total_co2, avg_int, co2_saved, ethical_count

def get_next_badge_nudge(badges):
    locked = [b for b in badges if not b["unlocked"]]
    if not locked:
        return "🏆 All 5 Milestone Badges Unlocked!", 100
    best = max(locked, key=lambda b: b["pct"])
    return f"Next: {best['icon']} {best['name']} ({best['progress']})", best["pct"]

def find_top_swap_opportunity(purchases):
    non_eth = [(i, p) for i, p in enumerate(purchases) if not p.get("is_ethical", False) and p.get("carbon_kg", 0.0) > 0]
    if not non_eth:
        return None
    idx, item = max(non_eth, key=lambda pair: pair[1].get("carbon_kg", 0.0))
    cur_co2, cat = item.get("carbon_kg", 0.0), item.get("category", "Fast Fashion Apparel")
    alt_map = {
        "Consumer Electronics": "Refurbished Tech",
        "Fast Fashion Apparel": "Second-Hand / Thrift",
        "Footwear & Leather": "Second-Hand / Thrift",
        "Packaged Groceries": "Local / Organic Food",
        "Home & Plastics": "Zero-Waste Reusables",
    }
    target_cat = alt_map.get(cat, "Second-Hand / Thrift")
    alt_co2 = calculate_carbon(item.get("price", 30.0), target_cat, True)
    saved = max(0.0, round(cur_co2 - alt_co2, 2))
    swaps = ETHICAL_ALTERNATIVES.get(cat, [{"brand": "Local Circular Hub"}])
    return {"index": idx, "item": item, "target_cat": target_cat, "brand_suggestion": swaps[0]["brand"], "cur_co2": cur_co2, "alt_co2": alt_co2, "saved_diff": saved, "pct_drop": int(round((saved / cur_co2) * 100)) if cur_co2 > 0 else 0}

def build_eco_scorecard_markdown(user_name, eco_rank, budget, spend_tot, co2_tot, saved_tot, badges, streak, top_cat):
    unlocked = [b["name"] for b in badges if b["unlocked"]]
    return f"""# ShopImpact Conscious Shopping Scorecard

- **Shopper:** {user_name} ({eco_rank})
- **Report Date:** {date.today()}
- **Monthly Target:** {budget} kg CO2e

## Summary Metrics
- **Total Spend:** ${spend_tot:,.2f}
- **Carbon Footprint:** {co2_tot:.1f} kg CO2e
- **Carbon Avoided:** {saved_tot:.1f} kg CO2e
- **Eco Streak:** {streak}x
- **Top Impact Category:** {top_cat}

## Unlocked Badges ({len(unlocked)} of {len(badges)})
{chr(10).join('- ' + n for n in unlocked) if unlocked else '- Log purchases to unlock milestones!'}
"""

def evaluate_feedback_for_item(mascot_str, item_name, live_co2, is_ethical):
    if is_ethical and live_co2 <= 3.0:
        mood, art = "ecstatic", "badge"
    elif is_ethical or live_co2 <= 10.0:
        mood, art = "happy", ("leaf" if is_ethical else "footprint")
    elif live_co2 <= 25.0:
        mood, art = "mindful", None
    elif live_co2 <= 50.0:
        mood, art = "worried", None
    else:
        mood, art = "alarmed", None
    return mood, get_mascot_reaction(mascot_str, item_name, live_co2, mood, is_ethical), art

def add_purchase(purchases_list, item_name, product_type, brand, price, purchase_date, is_ethical, mascot_str):
    live_co2 = calculate_carbon(float(price), product_type, bool(is_ethical))
    record = {
        "id": len(purchases_list) + 1, "item": item_name.strip(), "category": product_type,
        "brand": brand.strip() if brand and brand.strip() else "Unspecified",
        "price": round(float(price), 2), "carbon_kg": float(live_co2),
        "date": str(purchase_date), "is_ethical": bool(is_ethical),
    }
    purchases_list.append(record)
    mood, msg, art = evaluate_feedback_for_item(mascot_str, record["item"], live_co2, is_ethical)
    return record, mood, msg, art

def set_purchase_toast(item_name: str, co2_kg: float, is_eth: bool, prefix: str = "Logged"):
    if is_eth:
        st.session_state.pending_toast = (f"{prefix} '{item_name}' (+{co2_kg:.2f} kg CO₂e) • Ethical 30% cut applied", "🌿")
    elif co2_kg >= 30.0:
        st.session_state.pending_toast = (f"{prefix} '{item_name}' (+{co2_kg:.2f} kg CO₂e) • Heavy footprint — check swaps", "⚠️")
    else:
        st.session_state.pending_toast = (f"{prefix} '{item_name}' (+{co2_kg:.2f} kg CO₂e) added to ledger", "✅")

def _log_purchase_event(item_name, product_type, brand, price, purchase_date, is_ethical, prefix="Logged", celebrate=()):
    rec, mood, msg, art = add_purchase(
        st.session_state.purchases, item_name, product_type, brand, price, purchase_date, is_ethical, st.session_state.user_mascot
    )
    st.session_state.last_logged = rec
    st.session_state.mascot_mood, st.session_state.mascot_message, st.session_state.recent_art = mood, msg, art
    set_purchase_toast(rec["item"], rec["carbon_kg"], rec["is_ethical"], prefix=prefix)
    if mood in celebrate:
        st.balloons()
    st.rerun()

# ------------------------------------------------------------------------------
# SESSION STATE INITIALIZATION (Purchases stored in a Python list in session)
# ------------------------------------------------------------------------------

_ctx_theme = getattr(getattr(st.context, "theme", None), "type", None)
if "dark_theme" not in st.session_state:
    _qp_t = st.query_params.get("theme")
    st.session_state.dark_theme = (_qp_t == "dark") if _qp_t in ("light", "dark") else (_ctx_theme == "dark")
elif "sa_dark_toggle" in st.session_state and st.session_state.sa_dark_toggle != st.session_state.dark_theme:
    st.session_state.dark_theme = st.session_state.sa_dark_toggle
elif _ctx_theme in ("light", "dark") and _ctx_theme != st.session_state.get("_last_ctx_theme"):
    st.session_state.dark_theme = (_ctx_theme == "dark")
st.session_state._last_ctx_theme = _ctx_theme
st.session_state.sa_dark_toggle = st.session_state.dark_theme
if "onboarded" not in st.session_state:
    st.session_state.onboarded = st.query_params.get("onboarded") in ["true", "1"]
if "user_name" not in st.session_state: st.session_state.user_name = "Parth Gajera"
if "user_mascot" not in st.session_state: st.session_state.user_mascot = "Pip the Forest Fox 🦊"
if "carbon_budget" not in st.session_state: st.session_state.carbon_budget = 150
if "recent_art" not in st.session_state: st.session_state.recent_art = None
if "mascot_mood" not in st.session_state: st.session_state.mascot_mood = "mindful"
if "mascot_message" not in st.session_state:
    st.session_state.mascot_message = "Ready when you are! Log a purchase below to track CO₂ and unlock botanical art."
if "nav_view" not in st.session_state:
    st.session_state.nav_view = "Wall of Badges" if st.query_params.get("view") == "badges" else "Dashboard"
if "last_logged" not in st.session_state: st.session_state.last_logged = None
if "confirm_reset" not in st.session_state: st.session_state.confirm_reset = False
if "pending_toast" not in st.session_state: st.session_state.pending_toast = None

if "purchases" not in st.session_state:
    st.session_state.purchases = []
    dm = st.query_params.get("demo")
    if dm in ["true", "1"]:
        for args in [
            ("Vintage Denim Jacket", "Second-Hand / Thrift", "Community Thrift", 35.0, "2026-11-12", True),
            ("Organic CSA Harvest Box", "Local / Organic Food", "Local Farmers Market", 42.0, "2026-11-12", True),
            ("Certified Renewed ThinkPad", "Refurbished Tech", "Back Market Refurbished", 280.0, "2026-11-12", True),
        ]:
            st.session_state.last_logged, *_ = add_purchase(st.session_state.purchases, *args, st.session_state.user_mascot)
        st.session_state.mascot_mood, st.session_state.mascot_message, st.session_state.recent_art = "ecstatic", "CLEVER ECO PICK! Pip put on gold sunglasses — 'Vintage Denim Jacket' is a circular win!", "badge"
    elif dm == "test12":
        for args in [
            ("Fair-Trade Coffee", "Local / Organic Food", "Local Roaster", 4.50, "2026-11-01", True),
            ("Bamboo Water Bottle", "Zero-Waste Reusables", "Klean Kanteen", 24.00, "2026-11-02", True),
            ("Vintage Denim Jacket", "Second-Hand / Thrift", "Goodwill Thrift", 32.00, "2026-11-03", True),
            ("Plastic Storage Bin Set", "Home & Plastics", "MegaMart", 28.00, "2026-11-04", False),
            ("Fast-Fashion Sweater", "Fast Fashion Apparel", "Urban Fast Retail", 45.00, "2026-11-05", False),
            ("Organic Produce Box", "Local / Organic Food", "Farmers Co-op", 38.00, "2026-11-06", True),
            ("Weekly Packaged Snacks", "Packaged Groceries", "SuperMart", 22.00, "2026-11-07", False),
            ("Refurbished Laptop", "Refurbished Tech", "Back Market", 280.00, "2026-11-08", True),
            ("Thrifted Wool Coat", "Second-Hand / Thrift", "Depop Thrift", 48.00, "2026-11-09", True),
            ("Running Shoes (Leather)", "Footwear & Leather", "City Leather Co.", 130.00, "2026-11-10", False),
            ("Modular Smartphone", "Consumer Electronics", "TechCorp", 320.00, "2026-11-11", False),
            ("Glass Pantry Jar Pack", "Zero-Waste Reusables", "Refill Hub", 18.00, "2026-11-12", True),
        ]:
            rec, m, msg, art = add_purchase(st.session_state.purchases, *args, st.session_state.user_mascot)
            st.session_state.last_logged, st.session_state.mascot_mood, st.session_state.mascot_message, st.session_state.recent_art = rec, m, msg, art

# ------------------------------------------------------------------------------
# UNIFIED TOKENIZED CSS (Cached per Light/Dark Mode for Instant Reruns)
# ------------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def get_theme_tokens(dark: bool) -> dict:
    return {
        "bg": "#131C17" if dark else "#F5F9F3",
        "side": "#18241D" if dark else "#EAF1E6",
        "surface": "#1C2921" if dark else "#FFFFFF",
        "soft": "#24342A" if dark else "#EDF4EA",
        "ink": "#ECF3EA" if dark else "#13261B",
        "muted": "#A3B9A9" if dark else "#526859",
        "accent": "#6CA452" if dark else "#4E7E36",
        "accent_hv": "#5B8E44" if dark else "#3D6628",
        "accent_soft": "#263B2C" if dark else "#DCEBD4",
        "border": "rgba(190, 218, 185, 0.14)" if dark else "rgba(45, 78, 43, 0.11)",
        "shadow": "0 8px 28px rgba(0, 0, 0, 0.24)" if dark else "0 8px 28px rgba(24, 48, 30, 0.055)",
        "gold_bg": "rgba(214, 152, 56, 0.16)" if dark else "#FAF2D8",
        "gold_ink": "#F2CA6B" if dark else "#8A5E14",
        "alert_info_bg": "#1F3025" if dark else "#EAF3E6",
        "alert_warn_bg": "#2E2716" if dark else "#FDF4E1",
        "alert_err_bg": "#361D20" if dark else "#FBECEB",
    }

@st.cache_data(show_spinner=False)
def get_app_css(dark: bool) -> str:
    tk = get_theme_tokens(dark)
    return ("""
<style>
  :root {{
    --bg: {bg}; --side: {side}; --surface: {surface}; --soft: {soft};
    --ink: {ink}; --muted: {muted}; --accent: {accent}; --accent-hv: {accent_hv};
    --accent-soft: {accent_soft}; --border: {border}; --shadow: {shadow};
  }}
  .stApp {{ background: var(--bg) !important; color: var(--ink) !important; }}
  [data-testid="stHeader"] {{ background: transparent !important; }}
  [data-testid="stMain"] h1, [data-testid="stMain"] h2, [data-testid="stMain"] h3, [data-testid="stMain"] h4, [data-testid="stMain"] h5,
  [data-testid="stMain"] p, [data-testid="stMain"] span, [data-testid="stMain"] label, [data-testid="stSidebar"] * {{ color: var(--ink) !important; }}
  [data-testid="stSidebar"] {{ background: var(--side) !important; border-right: 1px solid var(--border) !important; }}
  [data-testid="stSidebarCollapseButton"] button, [data-testid="collapsedControl"] button {{
    background: var(--surface) !important; border: 1px solid var(--border) !important;
    border-radius: 12px !important; color: var(--ink) !important; box-shadow: var(--shadow) !important;
  }}

  /* Soft organic buttons */
  [data-testid="stBaseButton-primary"], button[kind="primary"] {{
    background: #4E7E36 !important; border: none !important; border-radius: 99px !important;
    color: #FFFFFF !important; font-weight: 700 !important; padding: 0.45rem 1.1rem !important;
    box-shadow: 0 4px 12px rgba(78, 126, 54, 0.22) !important;
  }}
  [data-testid="stBaseButton-primary"]:hover, button[kind="primary"]:hover {{ background: #3D6529 !important; }}
  [data-testid="stBaseButton-primary"] *, button[kind="primary"] * {{ color: #FFFFFF !important; }}

  [role="dialog"], div:has(> [role="dialog"]),
  [data-testid="stDialog"] [role="dialog"], [data-testid="stDialog"] [role="dialog"] > div,
  [data-testid="stModal"] [role="dialog"], [data-testid="stModal"] [role="dialog"] > div,
  div[data-baseweb="modal"] [role="dialog"] {{
    background: {surface} !important; background-color: {surface} !important;
    color: {ink} !important; border: 1px solid {border} !important; border-radius: 22px !important;
  }}
  [role="dialog"] *, div:has(> [role="dialog"]) *, [data-testid="stDialog"] *, [data-testid="stModal"] * {{ color: {ink} !important; }}
  [role="dialog"] [data-testid="stBaseButton-primary"] *, [role="dialog"] button[kind="primary"] * {{ color: #FFFFFF !important; }}
  [role="dialog"] button[aria-label="Close"] svg, [data-testid="stDialog"] button[aria-label="Close"] svg, [data-testid="stModal"] button[aria-label="Close"] svg {{
    color: {ink} !important; fill: currentColor !important;
  }}
  div[data-baseweb="popover"], div[data-baseweb="popover"] > div, div[data-baseweb="popover"] > div > div,
  [data-testid="stVirtualDropdown"], [data-testid="stVirtualDropdown"] > div,
  [data-testid="stSelectboxVirtualDropdown"], [data-testid="stSelectboxVirtualDropdown"] > div,
  [data-testid="stSelectboxVirtualDropdown"] [role="listbox"],
  div[data-baseweb="menu"], ul[data-baseweb="menu"], [role="listbox"], [role="listbox"] > div, [role="option"] {{
    background: {surface} !important; background-color: {surface} !important; color: {ink} !important; border-color: {border} !important;
  }}
  [data-testid="stSelectboxVirtualDropdown"] {{ border: 1px solid {border} !important; border-radius: 12px !important; box-shadow: {shadow} !important; }}
  div[data-baseweb="popover"] *, [data-testid="stSelectboxVirtualDropdown"] *, [role="listbox"] *, [role="option"] *, div[data-baseweb="menu"] * {{ color: {ink} !important; }}
  [role="option"]:hover, [role="option"][aria-selected="true"], [role="option"][data-focused="true"], [role="option"][data-selected="true"],
  [role="option"]:hover *, [role="option"][aria-selected="true"] *, [role="option"][data-focused="true"] *, [role="option"][data-selected="true"] * {{
    background: {accent_soft} !important; background-color: {accent_soft} !important; color: {ink} !important;
  }}

  /* Calendar & DatePicker Popover */
  [data-baseweb="calendar"], [data-baseweb="calendar"] > div, [data-baseweb="datepicker"], [data-baseweb="datepicker"] > div,
  [data-baseweb="calendar-header"], [data-baseweb="month"], [data-baseweb="week"],
  [data-baseweb="calendar"] [role="grid"], [data-baseweb="calendar"] [role="row"], [data-baseweb="calendar"] [role="columnheader"], [data-baseweb="calendar"] [role="gridcell"] {{
    background: var(--surface) !important; background-color: var(--surface) !important; color: var(--ink) !important;
  }}
  [data-baseweb="calendar"] * {{ color: var(--ink) !important; }}
  [data-baseweb="calendar"] button {{ background: transparent !important; color: var(--ink) !important; }}
  [data-baseweb="calendar"] button svg {{ fill: var(--ink) !important; color: var(--ink) !important; }}
  [data-baseweb="calendar"] [role="gridcell"] > div, [data-baseweb="calendar"] [data-baseweb="day"] {{ background: transparent !important; color: var(--ink) !important; }}
  [data-baseweb="calendar"] [role="gridcell"]:hover > div, [data-baseweb="calendar"] [data-baseweb="day"]:hover {{ background: var(--accent-soft) !important; background-color: var(--accent-soft) !important; color: var(--ink) !important; }}
  [data-baseweb="calendar"] [aria-selected="true"], [data-baseweb="calendar"] [aria-selected="true"] > div, [data-baseweb="calendar"] [aria-selected="true"] * {{
    background: var(--accent) !important; background-color: var(--accent) !important; color: #FFFFFF !important;
  }}

  /* Theme-Safe Alerts & High-Contrast Toast Pop-ups */
  [data-testid="stAlert"], [data-testid="stAlertContainer"], div[role="alert"], .stAlert {{
    background: {alert_info_bg} !important; background-color: {alert_info_bg} !important;
    color: var(--ink) !important; border: 1px solid var(--border) !important; border-left: 4px solid var(--accent) !important; border-radius: 14px !important;
  }}
  [data-testid="stAlert"]:has([data-testid="stAlertContentWarning"]), [data-testid="stAlertContainer"]:has([data-testid="stAlertContentWarning"]) {{
    background: {alert_warn_bg} !important; background-color: {alert_warn_bg} !important; border-left-color: #D69838 !important;
  }}
  [data-testid="stAlert"]:has([data-testid="stAlertContentError"]), [data-testid="stAlertContainer"]:has([data-testid="stAlertContentError"]) {{
    background: {alert_err_bg} !important; background-color: {alert_err_bg} !important; border-left-color: #C45B4D !important;
  }}
  [data-testid="stAlert"] *, [data-testid="stAlertContainer"] *, div[role="alert"] *, .stAlert * {{ color: var(--ink) !important; }}
  [data-testid="stAlert"] svg, div[role="alert"] svg {{ fill: var(--accent) !important; color: var(--accent) !important; }}
  [data-testid="stAlert"]:has([data-testid="stAlertContentWarning"]) svg {{ fill: #D69838 !important; color: #D69838 !important; }}

  [data-testid="stToastContainer"] {{ z-index: 999999 !important; }}
  [data-testid="stToast"] {{
    background: {surface} !important; background-color: {surface} !important; color: {ink} !important;
    border: 1.5px solid {accent} !important; border-radius: 16px !important; box-shadow: 0 12px 32px rgba(0, 0, 0, 0.28) !important;
  }}
  [data-testid="stToast"] > div, [data-testid="stToast"] [data-testid="stMarkdownContainer"],
  [data-testid="stToast"] p, [data-testid="stToast"] span, [data-testid="stToast"] div {{ background: transparent !important; color: {ink} !important; font-weight: 600 !important; }}
  [data-testid="stToast"] button svg {{ color: {muted} !important; fill: {muted} !important; }}

  [data-testid="stForm"], [data-testid="stExpander"] {{ background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: 20px !important; }}
  [data-testid="stExpander"] summary, [data-testid="stExpander"] summary * {{ background: transparent !important; color: var(--ink) !important; }}

  [data-testid="stBaseButton-secondary"], button[kind="secondary"], [data-testid="stDownloadButton"] button, [data-testid="stFormSubmitButton"] button {{
    background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: 99px !important;
    color: var(--ink) !important; font-weight: 600 !important; box-shadow: 0 2px 8px rgba(24, 48, 30, 0.04) !important;
  }}
  [data-testid="stBaseButton-secondary"]:hover, button[kind="secondary"]:hover, [data-testid="stDownloadButton"] button:hover, [data-testid="stFormSubmitButton"] button:hover {{
    background: var(--accent-soft) !important; border-color: var(--accent) !important;
  }}
  [data-testid="stBaseButton-secondary"] *, button[kind="secondary"] *, [data-testid="stDownloadButton"] button *, [data-testid="stFormSubmitButton"] button * {{ color: var(--ink) !important; }}

  /* Form inputs (React Aria + BaseWeb) */
  [data-testid="stSelectbox"] .react-aria-ComboBox [role="group"], [data-testid="stTextInputRootElement"], [data-testid="stDateInputField"],
  [data-testid="stSelectbox"] [data-baseweb="select"] > div, [data-testid="stDateInput"] [data-baseweb="input"], [data-testid="stDateInput"] [data-baseweb="base-input"],
  [data-testid="stTextInput"] [data-baseweb="input"], [data-testid="stTextInput"] [data-baseweb="base-input"],
  [data-testid="stNumberInput"] [data-baseweb="input"], [data-testid="stNumberInput"] [data-baseweb="base-input"],
  [data-baseweb="select"] > div, [data-baseweb="input"], [data-baseweb="base-input"] {{
    background: {surface} !important; background-color: {surface} !important; color: {ink} !important; border: 1px solid {border} !important; border-radius: 12px !important;
  }}
  [data-testid="stSelectbox"] .react-aria-ComboBox [role="group"] *, [data-testid="stTextInputRootElement"] *, [data-testid="stDateInputField"] *,
  [data-testid="stNumberInputContainer"] *, [data-testid="stNumberInputContainer"] input, [data-baseweb="select"] > div *, [data-baseweb="input"] input, [data-baseweb="base-input"] input {{
    background: transparent !important; background-color: transparent !important; color: {ink} !important; -webkit-text-fill-color: {ink} !important; caret-color: {ink} !important;
  }}
  [data-testid="stTextInputRootElement"] input::placeholder, [data-testid="stSelectbox"] input::placeholder {{
    color: {muted} !important; -webkit-text-fill-color: {muted} !important; opacity: 0.78 !important;
  }}
  [data-testid="stSelectbox"] svg, [data-testid="stDateInput"] svg, [data-baseweb="select"] svg, .stDateInput svg {{ color: {ink} !important; fill: {ink} !important; }}
  [data-testid="stNumberInputContainer"], .stNumberInput div[data-baseweb="input"] {{ background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: 12px !important; }}
  [data-testid="stNumberInputStepDown"], [data-testid="stNumberInputStepUp"], .stNumberInput button {{ background: var(--soft) !important; color: var(--ink) !important; border-color: var(--border) !important; }}
  [data-testid="stNumberInputStepDown"] svg, [data-testid="stNumberInputStepUp"] svg, .stNumberInput button svg {{ fill: var(--ink) !important; color: var(--ink) !important; }}

  .asset-3d {{ transition: transform 0.25s cubic-bezier(.22,1,.36,1), filter 0.25s ease; }}
  .studio-grid {{ display: grid; grid-template-columns: 1fr 1.38fr 1fr; gap: 18px; align-items: stretch; margin: 0.4rem 0 1.1rem 0; }}
  .studio-panel {{
    background: var(--surface); border: 1px solid var(--border); border-radius: 22px; padding: 1.25rem 1.35rem; box-shadow: var(--shadow);
    display: flex; flex-direction: column; justify-content: space-between; transition: transform 0.22s ease, box-shadow 0.22s ease;
  }}
  .studio-panel:hover {{ transform: translateY(-3px); }}
  .eyebrow {{ font-size: 0.72rem; font-weight: 800; letter-spacing: 0.9px; text-transform: uppercase; color: var(--accent) !important; margin-bottom: 0.25rem; }}
  .soft-bar {{ width: 100%; height: 7px; background: var(--soft); border-radius: 99px; overflow: hidden; margin-top: 0.4rem; }}
  .soft-fill {{ height: 100%; background: var(--accent); border-radius: 99px; transition: width 0.35s ease; }}

  .nav-head {{ display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 0.35rem; }}
  .streak-tag {{ background: {gold_bg}; color: {gold_ink} !important; font-size: 0.78rem; font-weight: 800; padding: 0.28rem 0.78rem; border-radius: 99px; white-space: nowrap; }}
  [data-testid="stMetric"] {{ background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: 20px !important; padding: 1.05rem 1.15rem !important; box-shadow: var(--shadow) !important; }}
  [data-testid="stMetricValue"] * {{ color: var(--ink) !important; }}
  [data-testid="stMetricLabel"] * {{ color: var(--muted) !important; font-weight: 700 !important; font-size: 0.84rem !important; }}
  [data-testid="stMetricDelta"] {{ background: var(--accent-soft) !important; border-radius: 99px !important; padding: 0.14rem 0.58rem !important; width: fit-content !important; }}
  [data-testid="stMetricDelta"] div, [data-testid="stMetricDelta"] span, [data-testid="stMetricDelta"] svg {{ color: var(--accent) !important; }}

  .soft-strip {{ background: var(--soft); border-radius: 16px; padding: 0.72rem 1.15rem; margin: 0.65rem 0 1rem 0; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; }}
  .st-key-optimizer_card {{ background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: 22px !important; padding: 0.45rem 0.65rem !important; box-shadow: var(--shadow) !important; }}
  .opt-flow {{ display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; }}
  .opt-stage {{ flex: 1 1 190px; background: var(--soft); border-radius: 16px; padding: 0.8rem 1rem; }}
  .chip-tile {{
    background: var(--surface); border: 1px solid var(--border); border-radius: 18px; padding: 0.7rem 0.35rem; text-align: center; height: 176px; margin-bottom: 0.55rem;
    display: flex; flex-direction: column; justify-content: center; align-items: center; box-shadow: var(--shadow); transition: transform 0.22s ease, border-color 0.22s ease;
  }}
  .chip-tile:hover {{ transform: translateY(-4px); border-color: var(--accent); }}
  .chip-tile:hover .asset-3d {{ transform: scale(1.1) rotate(-4deg); }}
  .swap-card {{ background: var(--surface); border: 1px solid var(--border); border-radius: 18px; padding: 1rem 1.1rem; box-shadow: var(--shadow); margin-bottom: 0.45rem; }}
  .badge-on {{ background: #4E7E36 !important; border-radius: 20px; padding: 1.15rem; color: #FFFFFF !important; margin-bottom: 0.85rem; box-shadow: 0 8px 24px rgba(78, 126, 54, 0.24); transition: transform 0.22s ease; }}
  .badge-on:hover {{ transform: translateY(-3px); }}
  .badge-on *, .badge-on h3, .badge-on p {{ color: #FFFFFF !important; }}
  .badge-off {{ background: var(--soft) !important; border: 1px dashed var(--border) !important; border-radius: 20px; padding: 1.15rem; opacity: 0.72; margin-bottom: 0.85rem; }}
  .avatar-circle {{ width: 88px; height: 88px; border-radius: 50%; border: 2.5px solid var(--accent); background: var(--surface); display: flex; align-items: center; justify-content: center; margin: 0 auto; overflow: hidden; box-shadow: var(--shadow); }}

  .sec-wrap {{ margin: 1.55rem 0 0.75rem 0; }}
  .sec-divider {{ display: flex; align-items: center; gap: 12px; opacity: 0.78; }}
  .sec-line {{ flex: 1; height: 1px; background: linear-gradient(90deg, transparent, var(--accent), transparent); opacity: 0.45; }}
  .sec-ornament {{ color: var(--accent) !important; background: var(--soft); border: 1px solid var(--border); padding: 5px 10px; border-radius: 99px; display: inline-flex; align-items: center; justify-content: center; }}
  .sec-title {{ margin: 0.12rem 0 0 0 !important; font-size: 1.4rem !important; font-weight: 800 !important; letter-spacing: -0.35px; color: var(--ink) !important; }}
  .sec-sub {{ margin: 0.18rem 0 0 0 !important; font-size: 0.86rem; color: var(--muted) !important; }}

  @media (max-width: 920px) {{ .studio-grid {{ grid-template-columns: 1fr !important; }} .nav-head {{ flex-direction: column; align-items: flex-start; }} }}
</style>
""").format(**tk).strip()

is_dark = st.session_state.dark_theme
T = get_theme_tokens(is_dark)
st.markdown(get_app_css(is_dark), unsafe_allow_html=True)

@st.fragment
def _render_offset_simulator(tokens: dict):
    """Isolated interactive simulator so slider adjustments respond instantaneously without full-app reruns."""
    sc1, sc2 = st.columns([1.2, 1.0])
    sim_d = sc1.slider("Simulate Dollar Spend ($):", 5.0, 500.0, 75.0, 5.0)
    sim_c = sc1.selectbox("Simulate Category:", list(CATEGORIES.keys()), key="sim_cat")
    sim_e = sc1.checkbox("Certified Circular / Ethical?", True, key="sim_eth")
    s_co2 = calculate_carbon(sim_d, sim_c, sim_e)
    sm, sch, st_m = get_equivalency(s_co2)
    render_html(f"<div style='background:{tokens['soft']}; border-radius:16px; padding:1rem;'><div class='eyebrow'>Estimated CO₂</div><div style='font-size:1.75rem; font-weight:800; color:{tokens['accent']};'>{s_co2:.2f} kg</div><div style='font-size:0.84rem; margin-top:0.35rem;'>~{sm:,} car miles • ~{sch:,} phone charges • ~{st_m} tree-mo</div></div>")
    if sc2.button("+ Add Simulated Item to Tracker", width="stretch"):
        _log_purchase_event(f"Simulated: {sim_c.split()[0]} (${sim_d:.0f})", sim_c, "Simulation Tool", sim_d, date.today(), sim_e)

@st.dialog("Log a New Planned Purchase")
def open_main_log_dialog():
    """Instant first-view custom purchase logging modal triggered from the top Studio bar."""
    st.caption("Enter purchase details below to update your live monthly CO₂ footprint and rewards right away.")
    m_item = st.text_input("Item Description (Required)", placeholder="e.g. Organic Cotton Tee, USB-C Cable", key="modal_item")
    mc1, mc2 = st.columns(2)
    m_cat = mc1.selectbox("Product Category", options=list(CATEGORIES.keys()), key="modal_cat")
    m_brand = mc2.text_input("Brand or Vendor (Optional)", placeholder="e.g. Patagonia, Back Market", key="modal_brand")
    mc3, mc4 = st.columns(2)
    m_price = mc3.number_input("Purchase Price ($)", min_value=1.0, max_value=5000.0, value=45.0, step=5.0, key="modal_price")
    m_date = mc4.date_input("Purchase Date", value=date.today(), key="modal_date")
    m_eth = st.checkbox("Certified Circular, Thrift, or Ethical (30% CO₂ discount)", key="modal_eth")
    ci_m = CATEGORIES[m_cat]
    st.caption(f"Insight ({ci_m['tier'].split()[-1]}): {ci_m['fact']}")
    if st.button("Record Purchase", type="primary", width="stretch", key="modal_submit_btn"):
        if not m_item.strip():
            st.error("Please enter an item description before recording.")
        else:
            _log_purchase_event(m_item, m_cat, m_brand, m_price, m_date, m_eth)

# ------------------------------------------------------------------------------
# SCREEN 1: WELCOME & ONBOARDING (Ecovista-Inspired Landscape + Man & Turtle)
# ------------------------------------------------------------------------------

if st.session_state.get("pending_toast"):
    _t_msg, _t_ico = st.session_state.pending_toast
    st.session_state.pending_toast = None
    st.toast(_t_msg, icon=_t_ico)

if not st.session_state.onboarded:
    render_html(render_welcome_landscape_svg(dark=is_dark))
    st.markdown("<div style='height:0.65rem;'></div>", unsafe_allow_html=True)

    c1, c2 = st.columns([1.25, 0.85], gap="large")
    with c1:
        st.subheader("Begin Your Conscious Shopping Journey")
        u_name = st.text_input("Your Shopper Name (Required):", value=st.session_state.user_name)
        m_choice = st.selectbox("Choose Your Eco Companion (Required):", options=list(ECO_MASCOTS.keys()))
        b_choice = st.slider("Monthly Sustainable Carbon Target (kg CO₂e):", min_value=50, max_value=300, value=st.session_state.carbon_budget, step=10)
        st.caption(f"✨ **{m_choice.split()[0]}:** {ECO_MASCOTS[m_choice]}")
        if st.button("🚀 Enter ShopImpact Dashboard →", type="primary", width="stretch"):
            st.session_state.user_name = u_name.strip() if u_name.strip() else "Shopper"
            st.session_state.user_mascot = m_choice
            st.session_state.carbon_budget = b_choice
            st.session_state.onboarded = True
            st.session_state.mascot_message = f"Welcome {st.session_state.user_name}! I am {m_choice.split()[0]}. Log a purchase to track live CO₂ and unlock botanical Turtle artwork!"
            st.rerun()

    with c2:
        render_html(f"""
        <div class="studio-panel" style="align-items:center; text-align:center;">
          {render_animated_avatar_svg(m_choice, "happy", 160, 160)}
          <div style="text-align:left; width:100%; font-size:0.88rem; line-height:1.6; color:{T['muted']};">
            <div class="eyebrow">Inside Your Eco Studio</div>
            <div>• <strong>Living Biosphere:</strong> natural garden dome synced to your monthly budget</div>
            <div>• <strong>What-If Green Switch:</strong> cut heavy items with 1-click circular swaps</div>
            <div>• <strong>Turtle Art Collector:</strong> collect Eco Leaf, Traveler Man &amp; Rosette PNGs</div>
          </div>
        </div>
        """)

# ------------------------------------------------------------------------------
# SCREEN 2: MAIN COMMAND STUDIO & WALL OF BADGES
# ------------------------------------------------------------------------------

else:
    badges, spend_tot, co2_tot, avg_int, saved_tot, eth_cnt = evaluate_badges(st.session_state.purchases)
    unlocked_num = sum(1 for b in badges if b["unlocked"])
    rank_title = get_user_eco_rank(st.session_state.purchases)
    cur_streak, best_streak = compute_eco_streak(st.session_state.purchases)
    earned_arts = get_collected_arts(st.session_state.purchases)
    nudge_text, nudge_pct = get_next_badge_nudge(badges)

    with st.sidebar:
        render_html(f"""
        <div style="text-align:center; margin-bottom:0.8rem;">
          <div class="avatar-circle">{render_animated_avatar_svg(st.session_state.user_mascot, st.session_state.mascot_mood, 74, 74)}</div>
          <div style="font-size:1.12rem; font-weight:800; margin-top:0.5rem;">{html.escape(st.session_state.user_name)}</div>
          <div style="font-size:0.78rem; font-weight:700; color:{T['accent']};">{rank_title}</div>
          <div style="font-size:0.76rem; opacity:0.78;">Target: {st.session_state.carbon_budget} kg CO₂e/mo</div>
        </div>
        <div style="background:{T['surface']}; border:1px solid {T['border']}; border-radius:14px; padding:0.65rem 0.8rem; margin-bottom:0.8rem; font-size:0.78rem;">
          <div style="display:flex; justify-content:space-between; font-weight:700;">
            <span>🏆 {unlocked_num}/{len(badges)} Badges</span><span>🔥 {cur_streak}x Streak</span>
          </div>
          <div class="soft-bar"><div class="soft-fill" style="width:{int((unlocked_num/len(badges))*100)}%;"></div></div>
          <div style="margin-top:0.35rem; color:{T['muted']};">🐢 Turtle Art: {len(earned_arts)}/4 earned</div>
        </div>
        """)
        if st.button("Edit Profile", width="stretch"):
            st.session_state.onboarded = False
            st.rerun()

        st.markdown("---")
        sa_nav_opts = ["Dashboard", "Wall of Badges"]
        if st.session_state.get("sidebar_nav_radio") not in sa_nav_opts:
            st.session_state.sidebar_nav_radio = st.session_state.nav_view
        def _sync_sa_nav():
            st.session_state.nav_view = st.session_state.sidebar_nav_radio
        def _switch_sa_view(target: str):
            st.session_state.nav_view = target
            st.session_state.sidebar_nav_radio = target
        st.radio("Navigation", sa_nav_opts, key="sidebar_nav_radio", on_change=_sync_sa_nav)
        st.toggle("Forest Dusk Dark Mode", key="sa_dark_toggle")
        _theme_sync_js = """<script>
        (function(){
          const p = document.querySelector('[data-testid="stApp"]') ? window : window.parent;
          if (!p || p._saThemeHook) return;
          p._saThemeHook = true;
          function findInp(){
            let inp = p.document.querySelector('input[aria-label="Forest Dusk Dark Mode"]');
            if (!inp) {
              const lbl = Array.from(p.document.querySelectorAll('[data-testid="stSidebar"] label')).find(el => (el.innerText || "").includes("Forest Dusk Dark Mode"));
              if (lbl) inp = lbl.querySelector('input[type="checkbox"]') || lbl.closest('[data-testid="stCheckbox"]')?.querySelector('input');
            }
            return inp;
          }
          p.document.addEventListener("click", function(ev){
            if (!ev.isTrusted) return;
            const item = ev.target && ev.target.closest && ev.target.closest('[data-testid^="stMainMenuItem-theme-"]');
            if (item) {
              const id = item.getAttribute("data-testid") || "";
              const wantDark = id.endsWith("Dark") ? true : id.endsWith("Light") ? false : p.matchMedia("(prefers-color-scheme: dark)").matches;
              setTimeout(function(){
                const inp = findInp();
                if (inp && Boolean(inp.checked) !== wantDark) inp.click();
              }, 80);
              return;
            }
            const tgl = ev.target && ev.target.closest && ev.target.closest('[data-testid="stSidebar"] [data-testid="stCheckbox"]');
            if (tgl && (tgl.innerText || "").includes("Forest Dusk Dark Mode")) {
              setTimeout(function(){
                const inp = findInp();
                const btn = p.document.querySelector('[data-testid="stMainMenuButton"]');
                if (!inp || !btn) return;
                const want = inp.checked ? "Dark" : "Light";
                const stEl = p.document.createElement("style");
                stEl.textContent = '[data-testid="stMainMenuPopover"]{opacity:0!important;pointer-events:none!important;}';
                p.document.head.appendChild(stEl);
                btn.click();
                setTimeout(function(){
                  const mItem = p.document.querySelector('[data-testid="stMainMenuItem-theme-' + want + '"]');
                  if (mItem) mItem.click();
                  setTimeout(function(){
                    if (p.document.querySelector('[data-testid="stMainMenuPopover"]')) btn.click();
                    stEl.remove();
                  }, 30);
                }, 40);
              }, 60);
            }
          }, true);
        })();
        </script>"""
        try:
            st.html(_theme_sync_js, unsafe_allow_javascript=True)
        except TypeError:
            components.html(_theme_sync_js, height=0)

        st.markdown("---")
        eco_tip_cur = ECO_TIPS[len(st.session_state.purchases) % len(ECO_TIPS)]
        st.caption(f"*{eco_tip_cur}*")
        if not st.session_state.confirm_reset:
            if st.button("Reset Session", width="stretch"):
                st.session_state.confirm_reset = True
                st.rerun()
        else:
            st.warning("Clear all purchases?")
            rc1, rc2 = st.columns(2)
            if rc1.button("Yes", type="primary", width="stretch"):
                st.session_state.purchases, st.session_state.last_logged, st.session_state.recent_art = [], None, None
                st.session_state.mascot_mood, st.session_state.confirm_reset = "mindful", False
                st.session_state.mascot_message = "Cleared! Ready for your next mindful purchase."
                st.rerun()
            if rc2.button("Cancel", width="stretch"):
                st.session_state.confirm_reset = False
                st.rerun()

    # CLEAN TOP BAR WITH FIRST-VIEW LOG ACTION (Zero friction entry)
    h1, h2 = st.columns([1.65, 1.55])
    with h1:
        render_html(f"""
        <div class="nav-head">
          <div>
            <span style="font-size:1.45rem; font-weight:900; letter-spacing:-0.4px; color:{T['ink']};">ShopImpact</span>
            <span style="font-size:0.86rem; color:{T['muted']}; margin-left:0.65rem;">Welcome back, <strong>{html.escape(st.session_state.user_name)}</strong> • Saved {saved_tot:.1f} kg CO₂e</span>
          </div>
          <span class="streak-tag">{cur_streak}x Eco Streak</span>
        </div>
        """)
    with h2:
        n_log, n1, n2 = st.columns([1.25, 0.9, 1.05])
        if n_log.button("+ Log Purchase", type="primary", width="stretch", key="top_open_log_btn"):
            open_main_log_dialog()
        dash_lbl = "● Dashboard" if st.session_state.nav_view == "Dashboard" else "Dashboard"
        if n1.button(dash_lbl, type="secondary", width="stretch", key="top_nav_dash", on_click=_switch_sa_view, args=("Dashboard",)):
            pass
        badge_lbl = f"{'● ' if st.session_state.nav_view == 'Wall of Badges' else ''}Badges ({unlocked_num}/{len(badges)})"
        if n2.button(badge_lbl, type="secondary", width="stretch", key="top_nav_badges", on_click=_switch_sa_view, args=("Wall of Badges",)):
            pass

    # --------------------------------------------------------------------------
    # VIEW: DASHBOARD
    # --------------------------------------------------------------------------
    if st.session_state.nav_view == "Dashboard":
        c_name = st.session_state.user_mascot.split()[0]
        msg_esc = html.escape(st.session_state.mascot_message)
        b_lim = max(st.session_state.carbon_budget, 1)
        used_pct = (co2_tot / b_lim) * 100.0
        capped_pct = min(100, int(round(used_pct)))

        active_art = st.session_state.recent_art or "preview"
        art_uri = get_turtle_art_data_uri(active_art)
        art_titles = {"preview": "Seed Emblem (Log eco buy)", "leaf": "Botanical Eco Leaf", "footprint": "Earth Step Medallion", "traveler": "Mindful Walker & Turtle", "badge": "Championship Rosette"}
        mission_lbl = "Daily Eco Mission Complete" if eth_cnt >= 1 else "Goal: Log 1 circular purchase"

        # EQUAL-HEIGHT 3-CARD BOTANICAL STUDIO GRID
        render_html(f"""
        <div class="studio-grid">
          <div class="studio-panel">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <span class="eyebrow">Living Biosphere</span>
              <span style="font-size:0.78rem; font-weight:700; color:{T['muted']};">{used_pct:.0f}% used</span>
            </div>
            {render_animated_biosphere_svg(used_pct, co2_tot, b_lim, 178, 226)}
            <div class="soft-bar"><div class="soft-fill" style="width:{capped_pct}%;"></div></div>
          </div>

          <div class="studio-panel">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:4px;">
              <span class="eyebrow">Companion Studio</span>
              <span style="font-size:0.75rem; font-weight:700; color:{T['accent']};">{mission_lbl}</span>
            </div>
            <div style="display:flex; align-items:center; gap:1rem; margin:0.4rem 0;">
              <div style="flex:0 0 116px; text-align:center;">{render_animated_avatar_svg(st.session_state.user_mascot, st.session_state.mascot_mood, 116, 116)}</div>
              <div style="background:{T['soft']}; border-radius:16px; padding:0.9rem 1rem; font-size:0.86rem; line-height:1.45; flex:1;">
                <div style="font-weight:800; color:{T['accent']}; margin-bottom:0.2rem;">{c_name} says:</div>
                "{msg_esc}"
              </div>
            </div>
            <div style="border-top:1px solid {T['border']}; padding-top:0.55rem;">
              <div style="display:flex; justify-content:space-between; font-size:0.78rem; font-weight:700;">
                <span>{nudge_text}</span><span style="color:{T['accent']};">{nudge_pct}%</span>
              </div>
              <div class="soft-bar"><div class="soft-fill" style="width:{nudge_pct}%;"></div></div>
            </div>
          </div>

          <div class="studio-panel" style="align-items:center; text-align:center;">
            <div style="display:flex; justify-content:space-between; width:100%; align-items:center;">
              <span class="eyebrow">Turtle Art Collector</span>
              <span style="font-size:0.78rem; font-weight:700; color:{T['muted']};">{len(earned_arts)}/4 unlocked</span>
            </div>
            <img src="{art_uri}" alt="Procedural Turtle Art" style="width:152px; height:152px; object-fit:contain; margin:0.2rem auto;"/>
            <div style="width:100%;">
              <div style="font-size:0.8rem; font-weight:700; color:{T['ink']}; margin-bottom:0.35rem;">{art_titles.get(active_art, 'Botanical Art')}</div>
              <div style="display:flex; justify-content:center; gap:6px; font-size:0.72rem; font-weight:700; color:{T['muted']};">
                <span style="padding:2px 9px; border-radius:99px; background:{T['accent_soft'] if 'leaf' in earned_arts else T['soft']};">Leaf</span>
                <span style="padding:2px 9px; border-radius:99px; background:{T['accent_soft'] if 'footprint' in earned_arts else T['soft']};">Step</span>
                <span style="padding:2px 9px; border-radius:99px; background:{T['accent_soft'] if 'badge' in earned_arts else T['soft']};">Medal</span>
              </div>
            </div>
          </div>
        </div>
        """)

        if st.session_state.recent_art:
            _, dl_col = st.columns([2.2, 1.0])
            dl_col.download_button("Download Earned Turtle Art (.png)", _render_turtle_art_png_cached(active_art), f"shopimpact_{active_art}.png", "image/png", width="stretch")

        # 4 KPI CARDS
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total Spend", f"${spend_tot:,.2f}", f"{len(st.session_state.purchases)} items recorded")
        k2.metric("Carbon Footprint", f"{co2_tot:.1f} kg", f"{avg_int:.2f} kg/$ intensity", delta_color="inverse")
        k3.metric("Carbon Avoided", f"{saved_tot:.1f} kg", "Vs standard 0.45 kg/$")
        k4.metric("Trees to Offset", f"{round(co2_tot / 21.0, 1)} Trees", "21 kg CO₂/tree/year", delta_color="inverse")

        miles_s, chg_s, _ = get_equivalency(saved_tot)
        eth_rate = int(round((eth_cnt / len(st.session_state.purchases)) * 100)) if st.session_state.purchases else 0
        render_html(f"""
        <div class="soft-strip">
          <div style="font-size:0.84rem;"><strong>Ethical Share:</strong> {eth_cnt}/{len(st.session_state.purchases)} buys ({eth_rate}% conscious)</div>
          <div style="font-size:0.84rem; color:{T['muted']};">Avoided impact equals skipping <strong>{miles_s:,}</strong> car miles or powering <strong>{chg_s:,}</strong> phone charges.</div>
        </div>
        """)

        # QUICK-LOG CHIPS
        render_section_header("Fast Entry", "Quick-Log Common Purchases", "One-tap logging with pre-calibrated category emission multipliers.")
        chip_cols = st.columns(6)
        for i, qp in enumerate(QUICK_PURCHASES):
            co2_c = calculate_carbon(qp["price"], qp["category"], qp["is_ethical"])
            with chip_cols[i]:
                render_html(f"""
                <div class="chip-tile">
                  <div>{render_sa_3d(qp.get('img', ''), qp['name'], 56, qp['icon'])}</div>
                  <div style="font-weight:800; font-size:0.8rem; margin-top:0.2rem;">{qp['name']}</div>
                  <div style="color:{T['accent']}; font-weight:700; font-size:0.76rem;">${qp['price']:.2f} • {co2_c:.1f} kg</div>
                </div>
                """)
                if st.button("+ Log", key=f"chip_btn_{i}", width="stretch"):
                    _log_purchase_event(qp["name"], qp["category"], qp["brand"], qp["price"], date.today(), qp["is_ethical"], celebrate=("ecstatic",))

        # CUSTOM LOGGING FORM
        render_section_header("Custom Purchase Log", "Log a Custom Planned Purchase", "Record any custom purchase into your active list; ethical picks apply a 30% CO₂ reduction.")
        with st.form("custom_log_form", clear_on_submit=True):
            f1, f2, f3 = st.columns([1.2, 1.2, 1.0])
            item_name = f1.text_input("Item Description (Required)", placeholder="e.g. Organic Cotton Tee, USB-C Cable")
            cat_choice = f1.selectbox("Product Category (Required)", options=list(CATEGORIES.keys()))
            brand_val = f2.text_input("Brand or Vendor (Optional)", placeholder="e.g. Patagonia, Back Market")
            price_val = f2.number_input("Purchase Price ($) (Required)", min_value=1.0, max_value=5000.0, value=45.0, step=5.0)
            date_val = f3.date_input("Purchase Date (Required)", value=date.today())
            is_eth = f3.checkbox("Certified Circular / Thrift / Ethical", help="Applies a 30% footprint discount.")

            ci = CATEGORIES[cat_choice]
            form_tip = ECO_TIPS[len(st.session_state.purchases) % len(ECO_TIPS)]
            render_html(f"<div style='background:{T['soft']}; border-radius:14px; padding:0.75rem 1rem; margin:0.5rem 0; font-size:0.85rem;'><strong>Insight ({ci['tier']}):</strong> {ci['fact']} <span style='color:{T['accent']}; font-weight:700;'>• Tip: {form_tip}</span></div>")
            if st.form_submit_button("Record Purchase in Active Ledger", width="stretch"):
                if not item_name.strip():
                    st.error("Please enter an item description before recording.")
                else:
                    _log_purchase_event(item_name, cat_choice, brand_val, price_val, date_val, is_eth, celebrate=("ecstatic", "happy"))

        with st.expander("Pre-Purchase Carbon & Tree Offset Simulator", expanded=False):
            _render_offset_simulator(T)

        # GREENER SWAPS
        if st.session_state.last_logged:
            last = st.session_state.last_logged
            render_section_header("Circular Alternatives", f"Greener Options for '{last['item']}'", f"Category: {last['category']}")
            sc1, sc2 = st.columns([1.0, 2.0], gap="medium")
            with sc1:
                render_html(render_animated_avatar_svg(st.session_state.user_mascot, "happy", 105, 105))
                st.caption(f"**{c_name}:** Logged **{last['carbon_kg']} kg CO₂e**. Consider a circular swap:")
            with sc2:
                swaps = ETHICAL_ALTERNATIVES.get(last["category"], [])
                sw_cols = st.columns(len(swaps))
                for idx, sw in enumerate(swaps):
                    with sw_cols[idx]:
                        render_html(f"<div class='swap-card'><strong>{sw['brand']}</strong><br><span style='font-size:0.83rem; color:{T['muted']};'>{sw['perk']}</span><br><strong style='color:{T['accent']}; font-size:0.8rem;'>Carbon Cut: {sw['saving']}</strong></div>")
                        b_name = sw["brand"].split("/")[0].strip()
                        if st.button(f"Adopt {b_name}", key=f"adopt_swap_{idx}", width="stretch"):
                            sr, _, _, _ = add_purchase(st.session_state.purchases, f"Greener Swap: {b_name} ({last['category']})", last["category"], b_name, 35.0, date.today(), True, st.session_state.user_mascot)
                            st.session_state.last_logged, st.session_state.mascot_mood, st.session_state.recent_art = sr, "ecstatic", "badge"
                            st.session_state.mascot_message = f"Adopted {b_name}! Great biosphere boost."
                            set_purchase_toast(sr["item"], sr["carbon_kg"], True, prefix="Adopted")
                            st.balloons()
                            st.rerun()

        # WHAT-IF CARBON OPTIMIZER STUDIO
        swap_opp = find_top_swap_opportunity(st.session_state.purchases)
        if swap_opp:
            it = swap_opp["item"]
            circ_icon = render_sa_3d("badges/circular.png", "Circular Swap", 40, "->")
            with st.container(border=True, key="optimizer_card"):
                op1, op2 = st.columns([2.2, 0.8], gap="medium", vertical_alignment="center")
                with op1:
                    render_html(f"""
                    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; margin-bottom:0.55rem;">
                      <span class="eyebrow" style="margin:0;">What-If Carbon Optimizer</span>
                      <span style="background:{T['accent_soft']}; color:{T['accent']}; font-size:0.75rem; font-weight:800; padding:2px 10px; border-radius:99px;">Potential Cut: -{swap_opp['saved_diff']} kg CO₂ (-{swap_opp['pct_drop']}%)</span>
                    </div>
                    <div class="opt-flow">
                      <div class="opt-stage">
                        <div style="font-size:0.72rem; font-weight:700; color:{T['muted']}; text-transform:uppercase;">Heaviest Current Item</div>
                        <div style="font-weight:800; font-size:0.94rem; margin-top:0.15rem;">{html.escape(it['item'])}</div>
                        <div style="font-size:0.8rem; color:{T['muted']};">{html.escape(it['category'])} • <strong>{swap_opp['cur_co2']} kg CO₂</strong></div>
                      </div>
                      <div style="text-align:center; padding:0 0.25rem;">{circ_icon}</div>
                      <div class="opt-stage" style="background:{T['accent_soft']};">
                        <div style="font-size:0.72rem; font-weight:700; color:{T['accent']}; text-transform:uppercase;">Circular Alternative</div>
                        <div style="font-weight:800; font-size:0.94rem; margin-top:0.15rem;">{html.escape(swap_opp['brand_suggestion'])}</div>
                        <div style="font-size:0.8rem; color:{T['muted']};">{html.escape(swap_opp['target_cat'])} • <strong style="color:{T['accent']};">{swap_opp['alt_co2']} kg CO₂</strong></div>
                      </div>
                    </div>
                    """)
                with op2:
                    if st.button(f"Swap Item (-{swap_opp['saved_diff']} kg)", type="primary", width="stretch", key="opt_swap_btn"):
                        tr = st.session_state.purchases[swap_opp["index"]]
                        tr["item"], tr["category"], tr["brand"], tr["carbon_kg"], tr["is_ethical"] = f"Swapped: {tr['item']} (Circular)", swap_opp["target_cat"], swap_opp["brand_suggestion"].split("/")[0].strip(), swap_opp["alt_co2"], True
                        st.session_state.last_logged, st.session_state.mascot_mood, st.session_state.recent_art = tr, "ecstatic", "badge"
                        st.session_state.mascot_message = f"Smart switch! Saved {swap_opp['saved_diff']} kg CO₂ instantly!"
                        st.session_state.pending_toast = (f"Smart switch! Saved {swap_opp['saved_diff']} kg CO₂e instantly!", "♻️")
                        st.rerun()
                    render_html(f"<div style='text-align:center; font-size:0.74rem; color:{T['muted']}; margin-top:0.3rem;'>Updates carbon log live</div>")

        render_section_header("Insights & Ledger", "Timeline Filter & Visual Carbon Analytics", "Review footprint shares by category, filter recorded items, or export your scorecard.")
        yrs = sorted({str(p["date"])[:4] for p in st.session_state.purchases}, reverse=True)
        mos = sorted({str(p["date"])[:7] for p in st.session_state.purchases}, reverse=True)
        f_opts = ["All Time"] + [f"Year {y}" for y in yrs] + mos
        p_choice = st.radio("Period", f_opts, horizontal=True, label_visibility="collapsed")
        if p_choice == "All Time":
            filtered, p_lbl = st.session_state.purchases, "All Time (Cumulative)"
        elif p_choice.startswith("Year "):
            yf = p_choice.replace("Year ", "")
            filtered, p_lbl = [p for p in st.session_state.purchases if str(p["date"]).startswith(yf)], f"Year {yf}"
        else:
            filtered, p_lbl = [p for p in st.session_state.purchases if str(p["date"]).startswith(p_choice)], f"Month {p_choice}"

        cg1, cg2 = st.columns([1.05, 1.35], gap="large")
        top_cat_name = "None"
        with cg1:
            st.markdown(f"**Emissions by Category ({p_lbl})**")
            if filtered:
                df = pd.DataFrame(filtered)
                cat_agg = df.groupby("category", as_index=False).agg(carbon_kg=("carbon_kg", "sum"), spend=("price", "sum"), items=("item", "count")).sort_values("carbon_kg", ascending=False)
                top_cat_name = f"{cat_agg.iloc[0]['category']} ({cat_agg.iloc[0]['carbon_kg']:.1f} kg)"
                cat_agg["tier"] = cat_agg["category"].map(lambda c: "High Carbon" if CATEGORIES.get(c, {}).get("multiplier", 0.3) >= 0.4 else "Low / Conscious")
                if HAS_ALTAIR:
                    bar = alt.Chart(cat_agg).mark_bar(cornerRadiusEnd=6, size=20).encode(
                        x=alt.X("carbon_kg:Q", title="Carbon Footprint (kg CO₂e)"),
                        y=alt.Y("category:N", sort="-x", title=None, axis=alt.Axis(labelLimit=200)),
                        color=alt.Color("tier:N", scale=alt.Scale(domain=["Low / Conscious", "High Carbon"], range=["#4E7E36", "#D69838"]), legend=alt.Legend(orient="top", title=None)),
                        tooltip=[alt.Tooltip("category:N", title="Category"), alt.Tooltip("items:Q", title="Items"), alt.Tooltip("spend:Q", format="$,.2f"), alt.Tooltip("carbon_kg:Q", format=".2f")],
                    ).configure(background="transparent").configure_axis(labelColor=T["ink"], titleColor=T["muted"], gridColor=T["border"]).configure_legend(labelColor=T["ink"]).properties(height=270)
                    st.altair_chart(bar, width="stretch")

                    split_df = pd.DataFrame([{"Type": "Ethical / Circular", "CO2": float(df[df["is_ethical"]]["carbon_kg"].sum())}, {"Type": "Conventional", "CO2": float(df[~df["is_ethical"]]["carbon_kg"].sum())}])
                    split_df = split_df[split_df["CO2"] > 0]
                    if not split_df.empty:
                        st.markdown("**Ethical vs. Conventional Share**")
                        donut = alt.Chart(split_df).mark_arc(innerRadius=44, outerRadius=76).encode(
                            theta="CO2:Q",
                            color=alt.Color("Type:N", scale=alt.Scale(domain=["Ethical / Circular", "Conventional"], range=["#4E7E36", "#C45B4D"]), legend=alt.Legend(orient="right", title=None)),
                            tooltip=[alt.Tooltip("Type:N"), alt.Tooltip("CO2:Q", format=".2f")],
                        ).configure(background="transparent").configure_legend(labelColor=T["ink"]).properties(height=175)
                        st.altair_chart(donut, width="stretch")
                else:
                    st.bar_chart(df.groupby("category")["carbon_kg"].sum().sort_values(ascending=False), color="#4E7E36")
            else:
                st.info("No purchases logged for this period yet.")

        with cg2:
            st.markdown(f"**Transaction Ledger ({len(filtered)} records)**")
            if filtered:
                s1, s2 = st.columns([1.4, 1.0])
                sq = s1.text_input("Search ledger:", placeholder="Filter by item or brand...", label_visibility="collapsed", key="ledger_search")
                eo = s2.checkbox("Eco picks only", value=False, key="ledger_eth_only")
                vrows = [r for r in filtered if (not sq.strip() or sq.strip().lower() in (r["item"] + r["brand"] + r["category"]).lower()) and (not eo or r["is_ethical"])]
                base_rows = vrows if vrows else filtered
                df_view = pd.DataFrame(base_rows)[["date", "item", "category", "brand", "price", "carbon_kg", "is_ethical"]]
                df_view.columns = ["Date", "Item", "Product Type", "Brand", "Price ($)", "CO₂ (kg)", "Ethical?"]
                if vrows:
                    st.dataframe(df_view, width="stretch", hide_index=True, column_config={"Price ($)": st.column_config.NumberColumn("Price ($)", format="$%.2f"), "CO₂ (kg)": st.column_config.ProgressColumn("CO₂ (kg)", format="%.2f kg", min_value=0, max_value=max(float(df_view["CO₂ (kg)"].max()), 1.0)), "Ethical?": st.column_config.CheckboxColumn("Eco?")})
                else:
                    st.info("No rows match that search filter.")

                u1, u2, u3 = st.columns(3)
                if u1.button("Undo Last Purchase", width="stretch"):
                    popped = st.session_state.purchases.pop()
                    prev = st.session_state.purchases[-1] if st.session_state.purchases else None
                    st.session_state.last_logged = prev
                    if prev:
                        st.session_state.mascot_mood, st.session_state.mascot_message, st.session_state.recent_art = evaluate_feedback_for_item(st.session_state.user_mascot, prev["item"], prev["carbon_kg"], prev["is_ethical"])
                    else:
                        st.session_state.mascot_mood, st.session_state.recent_art = "mindful", None
                        st.session_state.mascot_message = f"Removed '{popped['item']}'. Log your next purchase!"
                    st.rerun()
                u2.download_button("Export CSV", df_view.to_csv(index=False).encode("utf-8"), f"shopimpact_{p_lbl.lower().replace(' ', '_')}.csv", "text/csv", width="stretch")
                u3.download_button("Eco Scorecard", build_eco_scorecard_markdown(st.session_state.user_name, rank_title, st.session_state.carbon_budget, spend_tot, co2_tot, saved_tot, badges, cur_streak, top_cat_name).encode("utf-8"), "shopimpact_scorecard.md", "text/markdown", width="stretch")
            else:
                st.caption("No records to export yet.")

    # --------------------------------------------------------------------------
    # VIEW: WALL OF BADGES & TURTLE ART VAULT
    # --------------------------------------------------------------------------
    elif st.session_state.nav_view == "Wall of Badges":
        st.title("Wall of Badges & Eco Fame")
        st.caption("Unlocked milestones bloom in botanical olive-green while upcoming goals remain muted until achieved.")
        st.metric("Badges Unlocked", f"{unlocked_num} of {len(badges)}", f"{int((unlocked_num/len(badges))*100)}% Complete")

        bc1, bc2 = st.columns(2, gap="large")
        for i, b in enumerate(badges):
            b_img = render_sa_3d(b.get("img", "") if b["unlocked"] else "badges/locked.png", b["name"], 52, b["icon"] if b["unlocked"] else "🔒")
            with (bc1 if i % 2 == 0 else bc2):
                if b["unlocked"]:
                    render_html(f"<div class='badge-on'><div style='display:flex; gap:1rem; align-items:center;'><div style='width:62px; height:62px; border-radius:16px; background:rgba(255,255,255,0.18); display:flex; align-items:center; justify-content:center; flex-shrink:0;'>{b_img}</div><div><h3 style='margin:0;'>{b['name']}</h3><p style='margin:0.2rem 0; font-size:0.9rem;'>{b['desc']}</p><span style='background:rgba(255,255,255,0.22); font-weight:800; font-size:0.75rem; padding:0.2rem 0.65rem; border-radius:99px;'>UNLOCKED ({b['progress']})</span></div></div></div>")
                else:
                    render_html(f"<div class='badge-off'><div style='display:flex; gap:1rem; align-items:center;'><div style='width:62px; height:62px; border-radius:16px; background:{T['surface']}; border:1px solid {T['border']}; display:flex; align-items:center; justify-content:center; flex-shrink:0;'>{b_img}</div><div><h3 style='margin:0;'>{b['name']}</h3><p style='margin:0.2rem 0; font-size:0.9rem;'>{b['desc']}</p><span style='font-weight:700; font-size:0.75rem;'>LOCKED ({b['progress']})</span></div></div></div>")

        render_section_header("Procedural Vector Vault", "Turtle Art Collector Vault", f"Collect all 4 botanical emblems drawn in-memory by HeadlessTurtle + Pillow ({len(earned_arts)}/4 unlocked).")
        v_cols = st.columns(4, gap="medium")
        art_specs = [
            ("leaf", "Botanical Eco Leaf", "Ethical or organic picks"),
            ("footprint", "Earth Step Medallion", "Low footprint <= 10 kg"),
            ("traveler", "Mindful Man & Turtle", "Any 2+ logged items"),
            ("badge", "Championship Rosette", "Ultra-green <= 3 kg / swaps"),
        ]
        for col_v, (ak, title_a, desc_a) in zip(v_cols, art_specs):
            unlocked_art = ak in earned_arts
            img_u = get_turtle_art_data_uri(ak if unlocked_art else "preview")
            col_v.markdown(f"<div class='studio-panel' style='align-items:center; text-align:center; padding:1rem;'><img src='{img_u}' style='width:140px; height:140px;'/><div style='font-weight:800; font-size:0.86rem; margin-top:0.3rem;'>{title_a}</div><div style='font-size:0.76rem; color:{T['muted']};'>{'Unlocked • ' if unlocked_art else 'Locked • '}{desc_a}</div></div>", unsafe_allow_html=True)

render_html(f"<div style='text-align:center; color:{T['muted']}; font-size:0.8rem; padding:1.4rem 0 0.6rem 0;'><strong>ShopImpact Conscious Shopping Studio</strong> • IDAI 102 • Candidate: <strong>Parth Pravinbhai Gajera</strong> (1000544)</div>")
