import base64
import html
import io
import math
import random
from datetime import date
import pandas as pd
from PIL import Image, ImageDraw
import streamlit as st

try:
    import altair as alt
    HAS_ALTAIR = True
except ImportError:
    HAS_ALTAIR = False

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
    {"name": "Fair-Trade Coffee / Tea", "price": 4.50, "category": "Local / Organic Food", "brand": "Local Roaster", "is_ethical": True, "icon": "☕"},
    {"name": "Local Organic Lunch", "price": 12.00, "category": "Local / Organic Food", "brand": "Farmers Co-op", "is_ethical": True, "icon": "🥗"},
    {"name": "Thrifted Vintage Jacket", "price": 32.00, "category": "Second-Hand / Thrift", "brand": "Community Thrift", "is_ethical": True, "icon": "🧥"},
    {"name": "Refurbished Tech Gadget", "price": 85.00, "category": "Refurbished Tech", "brand": "Back Market", "is_ethical": True, "icon": "📱"},
    {"name": "Fast-Fashion Top", "price": 55.00, "category": "Fast Fashion Apparel", "brand": "High-Street Retail", "is_ethical": False, "icon": "👗"},
    {"name": "Leather Footwear", "price": 130.00, "category": "Footwear & Leather", "brand": "City Leather Co.", "is_ethical": False, "icon": "👞"},
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

SUSTAINABILITY_QUOTES = [
    "“The greatest threat to our planet is the belief that someone else will save it.” — Robert Swan",
    "“The most sustainable garment is the one already in your wardrobe — or thrifted from someone else's.” — Orsola de Castro",
    "“Small acts, when multiplied by millions of people, can transform the world.” — Howard Zinn",
    "“There is no such thing as ‘away’. When we throw anything away it must go somewhere.” — Annie Leonard",
    "“We do not inherit the Earth from our ancestors; we borrow it from our children.” — Native Proverb",
]

# ------------------------------------------------------------------------------
# BOTANICAL SVG HERO LANDSCAPE (Ecovista-Inspired Welcome Artwork + Man & Turtle)
# ------------------------------------------------------------------------------

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

def render_animated_biosphere_svg(used_pct, co2_tot, budget_limit, width=185, height=238):
    pct = min(150.0, max(0.0, float(used_pct)))
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

def render_animated_avatar_svg(character="turtle", mood="happy", width=155, height=155):
    if character in ["ecstatic", "happy", "mindful", "worried", "alarmed"]:
        mood, character = character, "turtle"
    ck = str(character).lower()
    c_type = "fox" if "fox" in ck else "owl" if "owl" in ck else "bee" if ("bee" in ck or "pollinator" in ck) else "panda" if "panda" in ck else "turtle"
    shiver = "shiver" if mood in ["worried", "alarmed"] else "bob"

    svg = f"""<svg width="{width}" height="{height}" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg" style="max-width:100%; height:auto;">
    <style>
      @keyframes av-bob {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-6px); }} }}
      @keyframes av-shv {{ 0%, 100% {{ transform: translate(0,0); }} 25% {{ transform: translate(-2px,1px); }} 75% {{ transform: translate(2px,-1px); }} }}
      @keyframes wv-l {{ 0%, 100% {{ transform: rotate(0deg); }} 50% {{ transform: rotate(22deg); }} }}
      @keyframes wv-r {{ 0%, 100% {{ transform: rotate(0deg); }} 50% {{ transform: rotate(-22deg); }} }}
      @keyframes sp-s {{ 0%, 100% {{ transform: rotate(-8deg); }} 50% {{ transform: rotate(8deg); }} }}
      .bob {{ animation: av-bob 2.3s ease-in-out infinite; }}
      .shiver {{ animation: av-shv 0.22s infinite; }}
      .wave-l {{ animation: wv-l 1.4s ease-in-out infinite; transform-origin: 50px 85px; }}
      .wave-r {{ animation: wv-r 1.4s ease-in-out infinite; transform-origin: 150px 85px; }}
      .sprout {{ animation: sp-s 1.9s ease-in-out infinite; transform-origin: 100px 30px; }}
    </style><g class="{shiver}">"""

    if c_type == "fox":
        svg += """<path d="M 140 145 C 185 155 190 105 160 85 C 145 95 135 125 140 145 Z" fill="#D97336" stroke="#8E421B" stroke-width="2.4"/><path d="M 175 95 C 190 105 178 120 160 115 Z" fill="#FFFDF8"/><ellipse cx="100" cy="130" rx="46" ry="42" fill="#D97336" stroke="#8E421B" stroke-width="2.8"/><ellipse cx="100" cy="136" rx="28" ry="26" fill="#FDF2E6" stroke="#D97336" stroke-width="1.8"/><ellipse cx="70" cy="165" rx="14" ry="10" fill="#D97336" stroke="#8E421B" stroke-width="2"/><ellipse cx="130" cy="165" rx="14" ry="10" fill="#D97336" stroke="#8E421B" stroke-width="2"/><polygon points="55,42 75,18 85,46" fill="#D97336" stroke="#8E421B" stroke-width="2.4"/><polygon points="62,38 75,24 80,44" fill="#F4C7D2"/><polygon points="145,42 125,18 115,46" fill="#D97336" stroke="#8E421B" stroke-width="2.4"/><polygon points="138,38 125,24 120,44" fill="#F4C7D2"/><ellipse cx="100" cy="62" rx="34" ry="30" fill="#D97336" stroke="#8E421B" stroke-width="2.4"/><ellipse cx="82" cy="72" rx="16" ry="14" fill="#FFFDF8"/><ellipse cx="118" cy="72" rx="16" ry="14" fill="#FFFDF8"/><polygon points="96,72 104,72 100,78" fill="#1F2E24"/>"""
    elif c_type == "owl":
        svg += """<ellipse cx="100" cy="120" rx="50" ry="46" fill="#7D502D" stroke="#4D2F18" stroke-width="2.8"/><ellipse cx="100" cy="126" rx="34" ry="32" fill="#FAF0D2" stroke="#AD783B" stroke-width="2"/><path d="M 90 120 Q 100 128 110 120 M 85 135 Q 100 145 115 135" fill="none" stroke="#AD783B" stroke-width="2"/><g class="wave-l"><ellipse cx="54" cy="120" rx="14" ry="34" fill="#91603A" stroke="#4D2F18" stroke-width="2" transform="rotate(15 54 120)"/></g><g class="wave-r"><ellipse cx="146" cy="120" rx="14" ry="34" fill="#91603A" stroke="#4D2F18" stroke-width="2" transform="rotate(-15 146 120)"/></g><ellipse cx="78" cy="165" rx="12" ry="7" fill="#CE933A"/><ellipse cx="122" cy="165" rx="12" ry="7" fill="#CE933A"/><polygon points="70,36 60,16 80,30" fill="#7D502D" stroke="#4D2F18" stroke-width="2"/><polygon points="130,36 140,16 120,30" fill="#7D502D" stroke="#4D2F18" stroke-width="2"/><ellipse cx="100" cy="58" rx="36" ry="32" fill="#7D502D" stroke="#4D2F18" stroke-width="2.4"/><circle cx="85" cy="56" r="16" fill="#FAF0D2" stroke="#C98A32" stroke-width="2.4"/><circle cx="115" cy="56" r="16" fill="#FAF0D2" stroke="#C98A32" stroke-width="2.4"/><polygon points="96,65 104,65 100,75" fill="#DF9E34"/>"""
    elif c_type == "bee":
        svg += """<ellipse cx="72" cy="72" rx="28" ry="16" fill="#DCEEF7" opacity="0.85" stroke="#6B98B3" stroke-width="1.5" transform="rotate(-35 72 72)"/><ellipse cx="128" cy="72" rx="28" ry="16" fill="#DCEEF7" opacity="0.85" stroke="#6B98B3" stroke-width="1.5" transform="rotate(35 128 72)"/><ellipse cx="100" cy="115" rx="46" ry="54" fill="#E5B946" stroke="#6F4B2C" stroke-width="2.8"/><path d="M 60 98 Q 100 110 140 98" fill="none" stroke="#1F2E24" stroke-width="11" stroke-linecap="round"/><path d="M 64 125 Q 100 137 136 125" fill="none" stroke="#1F2E24" stroke-width="11" stroke-linecap="round"/><polygon points="96,168 104,168 100,182" fill="#1F2E24"/><path d="M 90 40 Q 80 20 70 24 M 110 40 Q 120 20 130 24" fill="none" stroke="#1F2E24" stroke-width="2.5"/><circle cx="68" cy="24" r="4.5" fill="#D69838"/><circle cx="132" cy="24" r="4.5" fill="#D69838"/><ellipse cx="100" cy="58" rx="28" ry="24" fill="#E5B946" stroke="#6F4B2C" stroke-width="2.4"/>"""
    elif c_type == "panda":
        svg += """<ellipse cx="100" cy="130" rx="48" ry="44" fill="#FFFDF8" stroke="#1F2E24" stroke-width="2.8"/><path d="M 54 115 Q 100 135 146 115 L 142 155 Q 100 170 58 155 Z" fill="#1F2E24"/><g class="wave-l"><ellipse cx="50" cy="98" rx="14" ry="26" fill="#1F2E24" transform="rotate(-30 50 98)"/></g><g class="wave-r"><ellipse cx="150" cy="98" rx="14" ry="26" fill="#1F2E24" transform="rotate(30 150 98)"/></g><ellipse cx="60" cy="165" rx="14" ry="10" fill="#1F2E24"/><ellipse cx="140" cy="165" rx="14" ry="10" fill="#1F2E24"/><circle cx="68" cy="38" r="15" fill="#1F2E24"/><circle cx="132" cy="38" r="15" fill="#1F2E24"/><ellipse cx="100" cy="62" rx="36" ry="32" fill="#FFFDF8" stroke="#1F2E24" stroke-width="2.5"/><ellipse cx="84" cy="58" rx="11" ry="14" fill="#1F2E24" transform="rotate(-15 84 58)"/><ellipse cx="116" cy="58" rx="11" ry="14" fill="#1F2E24" transform="rotate(15 116 58)"/><ellipse cx="100" cy="72" rx="5" ry="3.5" fill="#1F2E24"/><line x1="104" y1="74" x2="135" y2="82" stroke="#4E7E36" stroke-width="3"/><ellipse cx="132" cy="78" rx="6" ry="3" fill="#6DA452" transform="rotate(-20 132 78)"/>"""
    else:
        svg += """<ellipse cx="60" cy="155" rx="15" ry="22" fill="#5A8F44" stroke="#264729" stroke-width="2.4" transform="rotate(-25 60 155)"/><ellipse cx="140" cy="155" rx="15" ry="22" fill="#5A8F44" stroke="#264729" stroke-width="2.4" transform="rotate(25 140 155)"/><polygon points="95,160 105,160 100,180" fill="#5A8F44" stroke="#264729" stroke-width="2"/><g class="wave-l"><ellipse cx="48" cy="88" rx="17" ry="28" fill="#77AD5C" stroke="#264729" stroke-width="2.4" transform="rotate(-35 48 88)"/></g><g class="wave-r"><ellipse cx="152" cy="88" rx="17" ry="28" fill="#77AD5C" stroke="#264729" stroke-width="2.4" transform="rotate(35 152 88)"/></g><ellipse cx="100" cy="120" rx="54" ry="48" fill="#3D6B35" stroke="#264729" stroke-width="2.8"/><ellipse cx="100" cy="120" rx="42" ry="36" fill="#5A8F44" stroke="#264729" stroke-width="2"/><ellipse cx="100" cy="120" rx="26" ry="22" fill="#95C47A" stroke="#3D6B35" stroke-width="2"/><ellipse cx="100" cy="55" rx="28" ry="26" fill="#95C47A" stroke="#264729" stroke-width="2.4"/>"""

    if mood == "ecstatic":
        svg += """<g class="sprout"><line x1="100" y1="28" x2="100" y2="10" stroke="#C88C28" stroke-width="3"/><polygon points="100,4 103,11 110,11 105,15 107,22 100,18 93,22 95,15 90,11 97,11" fill="#E6B33A"/></g><path d="M 81 48 L 96 48 Q 96 58 88 58 Q 81 58 81 48 Z" fill="#18281D"/><path d="M 104 48 L 119 48 Q 119 58 112 58 Q 104 58 104 48 Z" fill="#18281D"/><line x1="96" y1="50" x2="104" y2="50" stroke="#18281D" stroke-width="2.5"/><path d="M 88 63 Q 100 76 112 63" fill="#C45B4D" stroke="#264729" stroke-width="2.2" stroke-linecap="round"/>"""
    elif mood == "happy":
        svg += """<g class="sprout"><line x1="100" y1="28" x2="100" y2="12" stroke="#264729" stroke-width="2.5"/><ellipse cx="94" cy="10" rx="7" ry="4.5" fill="#6DA452" stroke="#264729" stroke-width="1.5" transform="rotate(-30 94 10)"/><ellipse cx="106" cy="10" rx="7" ry="4.5" fill="#6DA452" stroke="#264729" stroke-width="1.5" transform="rotate(30 106 10)"/></g><circle cx="89" cy="51" r="4.8" fill="#18281D"/><circle cx="87" cy="49" r="1.6" fill="#FFF"/><circle cx="111" cy="51" r="4.8" fill="#18281D"/><circle cx="109" cy="49" r="1.6" fill="#FFF"/><path d="M 88 63 Q 100 74 112 63" fill="none" stroke="#18281D" stroke-width="2.8" stroke-linecap="round"/>"""
    elif mood == "alarmed":
        svg += """<polygon points="100,8 107,22 93,22" fill="#C45B4D" stroke="#852E24" stroke-width="1.5"/><circle cx="89" cy="52" r="6.5" fill="#FFF" stroke="#18281D" stroke-width="2"/><circle cx="89" cy="52" r="2.8" fill="#18281D"/><circle cx="111" cy="52" r="6.5" fill="#FFF" stroke="#18281D" stroke-width="2"/><circle cx="111" cy="52" r="2.8" fill="#18281D"/><ellipse cx="100" cy="69" rx="5.5" ry="7.5" fill="#18281D"/>"""
    elif mood == "worried":
        svg += """<circle cx="89" cy="53" r="5" fill="#18281D"/><circle cx="111" cy="53" r="5" fill="#18281D"/><path d="M 89 68 Q 100 59 111 68" fill="none" stroke="#18281D" stroke-width="2.6" stroke-linecap="round"/>"""
    else:
        svg += """<g class="sprout"><line x1="100" y1="28" x2="100" y2="14" stroke="#264729" stroke-width="2"/><ellipse cx="94" cy="12" rx="6" ry="4" fill="#6DA452" stroke="#264729" stroke-width="1.5" transform="rotate(-30 94 12)"/><ellipse cx="106" cy="12" rx="6" ry="4" fill="#6DA452" stroke="#264729" stroke-width="1.5" transform="rotate(30 106 12)"/></g><path d="M 84 52 Q 89 46 94 52 M 106 52 Q 111 46 116 52" fill="none" stroke="#18281D" stroke-width="2.4" stroke-linecap="round"/><path d="M 91 65 Q 100 71 109 65" fill="none" stroke="#18281D" stroke-width="2.2" stroke-linecap="round"/>"""

    return svg + "</g></svg>"

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
# CLOUD-SAFE HEADLESS TURTLE PILLOW GRAPHICS ENGINE (Harmonious Ecovista Tones)
# ------------------------------------------------------------------------------

class HeadlessTurtle:
    """Pure Python Turtle vector engine executing on Pillow canvases without Tkinter dependencies."""
    def __init__(self, w=280, h=280):
        self.w, self.h = w, h
        self.img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        self.draw = ImageDraw.Draw(self.img)
        self.x, self.y, self.heading = w / 2, h / 2, 90
        self.down, self.color, self.width = True, (78, 126, 54, 255), 3

    def forward(self, d):
        rad = math.radians(self.heading)
        nx, ny = self.x + d * math.cos(rad), self.y - d * math.sin(rad)
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

def draw_vector_art(art_type="leaf"):
    """Draws soft organic 280x280 botanical art (Leaf, Step, Rosette, Traveler Man & Turtle) via HeadlessTurtle."""
    w, h = 280, 280
    t = HeadlessTurtle(w, h)
    cx, cy = 140, 136

    if art_type == "preview":
        t.draw.ellipse([(cx - 88, cy - 88), (cx + 88, cy + 88)], fill=(224, 238, 214, 170), outline=(109, 164, 82, 160), width=2)
        for deg in range(0, 360, 30):
            rad = math.radians(deg)
            t.draw.line([(cx + 94 * math.cos(rad), cy + 94 * math.sin(rad)), (cx + 102 * math.cos(rad), cy + 102 * math.sin(rad))], fill=(109, 164, 82, 120), width=2)
        seed = [(cx, cy - 38), (cx + 20, cy - 8), (cx + 14, cy + 26), (cx, cy + 34), (cx - 14, cy + 26), (cx - 20, cy - 8)]
        t.draw.polygon(seed, fill=(109, 164, 82, 190), outline=(62, 107, 53, 210))
        return t.img

    if art_type == "leaf":
        t.draw.ellipse([(cx - 102, cy - 102), (cx + 102, cy + 102)], fill=(232, 243, 224, 240), outline=(78, 126, 54, 220), width=3)
        t.draw.ellipse([(cx - 52, cy - 68), (cx + 20, cy + 4)], fill=(235, 206, 98, 135))
        t.penup(); t.goto(cx - 4, cy + 84); t.heading = 84; t.color = (45, 84, 38, 255); t.width = 4; t.pendown(); t.forward(50)
        leaf_r, leaf_l = [], []
        for s in range(25):
            f = s / 24.0
            y = (cy + 56) - f * 120
            c, ln = math.sin(f * math.pi) * 42, math.sin(f * math.pi * 0.7) * 14
            leaf_r.append((cx + ln + c, y))
            leaf_l.append((cx + ln - c * 0.9, y))
        t.draw.polygon(leaf_r + list(reversed(leaf_l)), fill=(78, 126, 54, 245), outline=(45, 84, 38, 255))
        lit = [(cx + math.sin((s/24.0)*math.pi*0.7)*14, (cy+56)-(s/24.0)*120) for s in range(25)] + list(reversed(leaf_l))
        t.draw.polygon(lit, fill=(133, 180, 108, 220))
        t.draw.polygon([(cx - 2, cy + 42), (cx - 42, cy + 22), (cx - 58, cy + 4), (cx - 28, cy + 10), (cx - 4, cy + 30)], fill=(156, 198, 126, 240), outline=(62, 107, 53, 255))
        t.penup(); t.goto(cx, cy + 54); t.heading = 84; t.color = (245, 250, 240, 220); t.width = 2; t.pendown(); t.forward(112)
        for iy in [cy + 28, cy + 4, cy - 20]:
            xo = 8 if iy < cy + 10 else 3
            t.penup(); t.goto(cx + xo, iy); t.heading = 40; t.pendown(); t.forward(22)
            t.penup(); t.goto(cx + xo, iy); t.heading = 140; t.pendown(); t.forward(20)

    elif art_type == "footprint":
        t.draw.ellipse([(cx - 102, cy - 102), (cx + 102, cy + 102)], fill=(235, 243, 226, 240), outline=(78, 126, 54, 220), width=3)
        for deg in range(0, 360, 45):
            rad = math.radians(deg)
            px, py = cx + 96 * math.cos(rad), cy + 96 * math.sin(rad)
            t.draw.ellipse([(px - 6, py - 6), (px + 6, py + 6)], fill=(133, 180, 108, 240), outline=(62, 107, 53, 210))
        t.draw.ellipse([(cx - 24, cy + 20), (cx + 20, cy + 68)], fill=(78, 126, 54, 245))
        foot = [(cx - 20, cy + 32), (cx - 12, cy - 4), (cx - 28, cy - 32), (cx - 14, cy - 60), (cx + 16, cy - 60), (cx + 28, cy - 32), (cx + 14, cy - 4), (cx + 16, cy + 32)]
        t.draw.polygon(foot, fill=(78, 126, 54, 245))
        t.draw.ellipse([(cx - 28, cy - 62), (cx + 28, cy - 16)], fill=(95, 146, 70, 245))
        for tx, ty, tr in [(-20, -76, 9.5), (-1, -83, 8.2), (14, -79, 7.2), (25, -71, 6.2), (34, -60, 5.2)]:
            t.draw.ellipse([(cx + tx - tr, cy + ty - tr), (cx + tx + tr, cy + ty + tr)], fill=(109, 164, 82, 245), outline=(255, 253, 245, 220), width=2)

    elif art_type == "traveler":
        # Mindful Shopper Man walking with Reusable Tote & Baby Turtle inside Morning Botanical Horizon
        t.draw.ellipse([(cx - 102, cy - 102), (cx + 102, cy + 102)], fill=(238, 246, 232, 245), outline=(78, 126, 54, 220), width=3)
        t.draw.pieslice([(cx - 98, cy + 18), (cx + 98, cy + 108)], 0, 180, fill=(167, 206, 132, 220))
        t.draw.ellipse([(cx + 18, cy - 72), (cx + 62, cy - 28)], fill=(232, 200, 92, 170))
        # Shopper Man (Left-Center)
        t.draw.line([(cx - 18, cy + 20), (cx - 28, cy + 62)], fill=(36, 58, 44, 255), width=7)
        t.draw.line([(cx - 6, cy + 20), (cx + 6, cy + 62)], fill=(48, 76, 58, 255), width=7)
        t.draw.polygon([(cx - 30, cy - 24), (cx + 4, cy - 24), (cx + 8, cy + 22), (cx - 32, cy + 22)], fill=(78, 126, 54, 255))
        t.draw.ellipse([(cx - 25, cy - 54), (cx - 1, cy - 30)], fill=(232, 184, 146, 255))
        t.draw.pieslice([(cx - 26, cy - 56), (cx, cy - 38)], 180, 360, fill=(42, 38, 35, 255))
        t.draw.rectangle([(cx + 4, cy - 4), (cx + 26, cy + 22)], fill=(242, 228, 181, 255), outline=(140, 115, 67, 255), width=2)
        # Turtle Companion (Right)
        t.draw.pieslice([(cx + 26, cy + 36), (cx + 70, cy + 72)], 180, 360, fill=(61, 107, 53, 255))
        t.draw.ellipse([(cx + 66, cy + 44), (cx + 80, cy + 58)], fill=(119, 177, 90, 255))

    else:  # Warm Botanical Wheat-Gold & Olive Rosette
        cm = 114
        t.draw.polygon([(cx - 24, cm + 26), (cx - 52, cm + 136), (cx - 30, cm + 118), (cx - 10, cm + 128), (cx - 4, cm + 28)], fill=(78, 126, 54, 255))
        t.draw.polygon([(cx + 4, cm + 28), (cx + 10, cm + 128), (cx + 30, cm + 118), (cx + 52, cm + 136), (cx + 24, cm + 26)], fill=(61, 107, 53, 255))
        r_pts = [(cx + (64 if i % 2 == 0 else 54) * math.cos(i * math.pi / 32), cm + (64 if i % 2 == 0 else 54) * math.sin(i * math.pi / 32)) for i in range(64)]
        t.draw.polygon(r_pts, fill=(214, 152, 56, 255), outline=(235, 194, 96, 255))
        t.draw.ellipse([(cx - 52, cm - 52), (cx + 52, cm + 52)], fill=(228, 172, 72, 255), outline=(168, 110, 30, 255), width=2)
        t.draw.ellipse([(cx - 42, cm - 42), (cx + 42, cm + 42)], fill=(45, 84, 38, 255), outline=(149, 196, 122, 240), width=2)
        t.draw.ellipse([(cx - 30, cm - 30), (cx + 30, cm + 30)], fill=(250, 244, 212, 255), outline=(196, 136, 40, 255), width=2)
        sp = [(cx + (20 if k % 2 == 0 else 8) * math.cos(-math.pi / 2 + k * math.pi / 5), cm + (20 if k % 2 == 0 else 8) * math.sin(-math.pi / 2 + k * math.pi / 5)) for k in range(10)]
        t.draw.polygon(sp, fill=(200, 140, 40, 255), outline=(138, 86, 20, 255))

    return t.img

def image_to_png_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def image_to_data_uri(img):
    return "data:image/png;base64," + base64.b64encode(image_to_png_bytes(img)).decode("ascii")

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
        {"id": "starter", "name": "Seed Starter", "icon": "🌱", "desc": "Log your 1st conscious purchase in the dashboard", "unlocked": total_items >= 1, "progress": f"{min(total_items, 1)}/1 item", "pct": 100 if total_items >= 1 else 0},
        {"id": "low_impact", "name": "Low Impact Shopper", "icon": "🍃", "desc": "Maintain carbon intensity ≤ 0.25 kg/$ (min 2 items)", "unlocked": total_items >= 2 and avg_int <= 0.25, "progress": f"{avg_int:.2f} kg/$ (Goal ≤ 0.25)" if total_items >= 2 else f"{total_items}/2 items required", "pct": 100 if (total_items >= 2 and avg_int <= 0.25) else (max(10, min(95, int((0.25 / max(avg_int, 0.26)) * 100))) if total_items >= 2 else int((total_items / 2) * 100))},
        {"id": "ethical_pioneer", "name": "Conscious Pioneer", "icon": "♻️", "desc": "Choose 3+ verified circular, thrift, or ethical items", "unlocked": ethical_count >= 3, "progress": f"{ethical_count}/3 ethical items", "pct": min(100, int((ethical_count / 3.0) * 100))},
        {"id": "eco_saver", "name": "Eco Saver of the Month", "icon": "🌟", "desc": "Save 10+ kg CO₂ vs standard retail baseline", "unlocked": co2_saved >= 10.0 and total_items >= 1, "progress": f"{co2_saved:.1f}/10.0 kg CO₂ saved", "pct": min(100, int((co2_saved / 10.0) * 100)) if total_items >= 1 else 0},
        {"id": "zero_waste", "name": "Zero-Waste Hero", "icon": "🏆", "desc": "Log 2+ zero-waste or second-hand thrift items", "unlocked": zw_cnt >= 2, "progress": f"{zw_cnt}/2 items", "pct": min(100, int((zw_cnt / 2.0) * 100))},
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

# ------------------------------------------------------------------------------
# SESSION STATE INITIALIZATION (Purchases stored in a Python list in session)
# ------------------------------------------------------------------------------

if "dark_theme" not in st.session_state:
    st.session_state.dark_theme = st.query_params.get("theme") == "dark"
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
# UNIFIED TOKENIZED CSS (Airy Flat Botanical Palette, Zero Harsh Boxes, Mobile-Ready)
# ------------------------------------------------------------------------------

is_dark = st.session_state.dark_theme
T = {
    "bg": "#131C17" if is_dark else "#F5F9F3",
    "side": "#18241D" if is_dark else "#EAF1E6",
    "surface": "#1C2921" if is_dark else "#FFFFFF",
    "soft": "#24342A" if is_dark else "#EDF4EA",
    "ink": "#ECF3EA" if is_dark else "#13261B",
    "muted": "#A3B9A9" if is_dark else "#526859",
    "accent": "#6CA452" if is_dark else "#4E7E36",
    "accent_hv": "#5B8E44" if is_dark else "#3D6628",
    "accent_soft": "#263B2C" if is_dark else "#DCEBD4",
    "border": "rgba(190, 218, 185, 0.14)" if is_dark else "rgba(45, 78, 43, 0.11)",
    "shadow": "0 8px 28px rgba(0, 0, 0, 0.24)" if is_dark else "0 8px 28px rgba(24, 48, 30, 0.055)",
    "gold_bg": "rgba(214, 152, 56, 0.16)" if is_dark else "#FAF2D8",
    "gold_ink": "#F2CA6B" if is_dark else "#8A5E14",
}

render_html(f"""
<style>
  :root {{
    --bg: {T['bg']}; --side: {T['side']}; --surface: {T['surface']}; --soft: {T['soft']};
    --ink: {T['ink']}; --muted: {T['muted']}; --accent: {T['accent']}; --accent-hv: {T['accent_hv']};
    --accent-soft: {T['accent_soft']}; --border: {T['border']}; --shadow: {T['shadow']};
  }}
  .stApp {{ background: var(--bg) !important; color: var(--ink) !important; }}
  [data-testid="stHeader"] {{ background: transparent !important; }}
  h1, h2, h3, h4, h5, p, span, label, [data-testid="stSidebar"] * {{ color: var(--ink) !important; }}
  [data-testid="stSidebar"] {{ background: var(--side) !important; border-right: 1px solid var(--border) !important; }}
  [data-testid="stSidebarCollapseButton"] button, [data-testid="collapsedControl"] button {{
    background: var(--surface) !important; border: 1px solid var(--border) !important;
    border-radius: 12px !important; color: var(--ink) !important; box-shadow: var(--shadow) !important;
  }}

  /* Soft organic buttons — olive moss primary & sunlit parchment secondary */
  [data-testid="stBaseButton-primary"], button[kind="primary"] {{
    background: var(--accent) !important; border: none !important; border-radius: 99px !important;
    color: #FFFFFF !important; font-weight: 700 !important; padding: 0.45rem 1.1rem !important;
    box-shadow: 0 4px 12px rgba(78, 126, 54, 0.20) !important;
  }}
  [data-testid="stBaseButton-primary"]:hover, button[kind="primary"]:hover {{ background: var(--accent-hv) !important; }}
  [data-testid="stBaseButton-primary"] *, button[kind="primary"] * {{ color: #FFFFFF !important; }}

  [data-testid="stBaseButton-secondary"], button[kind="secondary"],
  [data-testid="stDownloadButton"] button, [data-testid="stFormSubmitButton"] button {{
    background: var(--surface) !important; border: 1px solid var(--border) !important;
    border-radius: 99px !important; color: var(--ink) !important; font-weight: 600 !important;
    box-shadow: 0 2px 8px rgba(24, 48, 30, 0.04) !important;
  }}
  [data-testid="stBaseButton-secondary"]:hover, button[kind="secondary"]:hover,
  [data-testid="stDownloadButton"] button:hover, [data-testid="stFormSubmitButton"] button:hover {{
    background: var(--accent-soft) !important; border-color: var(--accent) !important;
  }}
  [data-testid="stBaseButton-secondary"] *, button[kind="secondary"] *,
  [data-testid="stDownloadButton"] button *, [data-testid="stFormSubmitButton"] button * {{ color: var(--ink) !important; }}

  /* Form inputs */
  .stTextInput input, .stNumberInput input, .stDateInput input,
  .stSelectbox div[data-baseweb="select"] > div {{
    background: var(--surface) !important; color: var(--ink) !important;
    border: 1px solid var(--border) !important; border-radius: 12px !important;
  }}

  /* Seamless Equal-Height Hero Panorama Grid (replaces boxed containers!) */
  .studio-grid {{
    display: grid; grid-template-columns: 1fr 1.38fr 1fr; gap: 18px;
    align-items: stretch; margin: 0.4rem 0 1.1rem 0;
  }}
  .studio-panel {{
    background: var(--surface); border: 1px solid var(--border); border-radius: 22px;
    padding: 1.25rem 1.35rem; box-shadow: var(--shadow);
    display: flex; flex-direction: column; justify-content: space-between;
  }}
  .eyebrow {{
    font-size: 0.72rem; font-weight: 800; letter-spacing: 0.9px; text-transform: uppercase;
    color: var(--accent) !important; margin-bottom: 0.25rem;
  }}
  .soft-bar {{ width: 100%; height: 7px; background: var(--soft); border-radius: 99px; overflow: hidden; margin-top: 0.4rem; }}
  .soft-fill {{ height: 100%; background: var(--accent); border-radius: 99px; transition: width 0.35s ease; }}

  /* Open Top Header & KPI Cards without double borders */
  .nav-head {{ display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 0.35rem; }}
  .streak-tag {{
    background: {T['gold_bg']}; color: {T['gold_ink']} !important; font-size: 0.78rem;
    font-weight: 800; padding: 0.28rem 0.78rem; border-radius: 99px; white-space: nowrap;
  }}
  [data-testid="stMetric"] {{
    background: var(--surface) !important; border: 1px solid var(--border) !important;
    border-radius: 20px !important; padding: 1.05rem 1.15rem !important; box-shadow: var(--shadow) !important;
  }}
  [data-testid="stMetricValue"] * {{ color: var(--ink) !important; }}
  [data-testid="stMetricLabel"] * {{ color: var(--muted) !important; font-weight: 700 !important; font-size: 0.84rem !important; }}
  [data-testid="stMetricDelta"] {{
    background: var(--accent-soft) !important; border-radius: 99px !important;
    padding: 0.14rem 0.58rem !important; width: fit-content !important;
  }}
  [data-testid="stMetricDelta"] div, [data-testid="stMetricDelta"] span, [data-testid="stMetricDelta"] svg {{
    color: var(--accent) !important;
  }}

  /* Soft organic strips & tiles (Zero jagged boxes) */
  .soft-strip {{
    background: var(--soft); border-radius: 16px; padding: 0.72rem 1.15rem; margin: 0.65rem 0 1rem 0;
    display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;
  }}
  .optimizer-panel {{
    background: var(--soft); border: 1px solid var(--border); border-left: 4px solid var(--accent);
    border-radius: 18px; padding: 1.05rem 1.25rem; margin: 0.75rem 0;
  }}
  .chip-tile {{
    background: var(--surface); border: 1px solid var(--border); border-radius: 18px;
    padding: 0.7rem 0.45rem; text-align: center; height: 118px; margin-bottom: 0.45rem;
    display: flex; flex-direction: column; justify-content: center; box-shadow: var(--shadow);
  }}
  .swap-card {{
    background: var(--surface); border: 1px solid var(--border); border-radius: 18px;
    padding: 1rem 1.1rem; box-shadow: var(--shadow); margin-bottom: 0.45rem;
  }}
  .badge-on {{
    background: var(--accent) !important; border-radius: 20px; padding: 1.15rem;
    color: #FFFFFF !important; margin-bottom: 0.85rem; box-shadow: 0 8px 24px rgba(78, 126, 54, 0.22);
  }}
  .badge-on *, .badge-on h3, .badge-on p {{ color: #FFFFFF !important; }}
  .badge-off {{
    background: var(--soft) !important; border: 1px dashed var(--border) !important;
    border-radius: 20px; padding: 1.15rem; opacity: 0.68; margin-bottom: 0.85rem;
  }}
  .avatar-circle {{
    width: 88px; height: 88px; border-radius: 50%; border: 2.5px solid var(--accent);
    background: var(--surface); display: flex; align-items: center; justify-content: center;
    margin: 0 auto; overflow: hidden; box-shadow: var(--shadow);
  }}

  /* Editorial Botanical Section Dividers (Replaces plain HR dividers) */
  .sec-wrap {{ margin: 1.55rem 0 0.75rem 0; }}
  .sec-divider {{ display: flex; align-items: center; gap: 12px; opacity: 0.78; }}
  .sec-line {{
    flex: 1; height: 1px;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
    opacity: 0.45;
  }}
  .sec-ornament {{
    color: var(--accent) !important; background: var(--soft); border: 1px solid var(--border);
    padding: 5px 10px; border-radius: 99px; display: inline-flex; align-items: center; justify-content: center;
  }}
  .sec-title {{
    margin: 0.12rem 0 0 0 !important; font-size: 1.4rem !important; font-weight: 800 !important;
    letter-spacing: -0.35px; color: var(--ink) !important;
  }}
  .sec-sub {{ margin: 0.18rem 0 0 0 !important; font-size: 0.86rem; color: var(--muted) !important; }}

  /* Responsive Phone & Tablet Breakpoints */
  @media (max-width: 920px) {{
    .studio-grid {{ grid-template-columns: 1fr !important; }}
    .nav-head {{ flex-direction: column; align-items: flex-start; }}
  }}
</style>
""")

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
            new_it, mood, msg, art = add_purchase(st.session_state.purchases, m_item, m_cat, m_brand, m_price, m_date, m_eth, st.session_state.user_mascot)
            st.session_state.last_logged = new_it
            st.session_state.mascot_mood, st.session_state.mascot_message, st.session_state.recent_art = mood, msg, art
            st.rerun()

# ------------------------------------------------------------------------------
# SCREEN 1: WELCOME & ONBOARDING (Ecovista-Inspired Landscape + Man & Turtle)
# ------------------------------------------------------------------------------

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
        st.session_state.nav_view = st.radio("Navigation", ["Dashboard", "Wall of Badges"], index=1 if st.session_state.nav_view == "Wall of Badges" else 0)
        dark_toggle = st.toggle("Forest Dusk Dark Mode", value=st.session_state.dark_theme)
        if dark_toggle != st.session_state.dark_theme:
            st.session_state.dark_theme = dark_toggle
            st.rerun()

        st.markdown("---")
        st.caption(f"*{random.choice(ECO_TIPS)}*")
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
        if n1.button(dash_lbl, type="secondary", width="stretch", key="top_nav_dash"):
            st.session_state.nav_view = "Dashboard"
            st.rerun()
        badge_lbl = f"{'● ' if st.session_state.nav_view == 'Wall of Badges' else ''}Badges ({unlocked_num}/{len(badges)})"
        if n2.button(badge_lbl, type="secondary", width="stretch", key="top_nav_badges"):
            st.session_state.nav_view = "Wall of Badges"
            st.rerun()

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
        art_img = draw_vector_art(active_art)
        art_uri = image_to_data_uri(art_img)
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
            dl_col.download_button("Download Earned Turtle Art (.png)", image_to_png_bytes(art_img), f"shopimpact_{active_art}.png", "image/png", width="stretch")

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
                  <div style="font-size:1.55rem;">{qp['icon']}</div>
                  <div style="font-weight:800; font-size:0.8rem; margin-top:0.2rem;">{qp['name']}</div>
                  <div style="color:{T['accent']}; font-weight:700; font-size:0.76rem;">${qp['price']:.2f} • {co2_c:.1f} kg</div>
                </div>
                """)
                if st.button(f"+ Add {qp['name'].split()[0]}", key=f"chip_btn_{i}", width="stretch"):
                    new_it, mood, msg, art = add_purchase(st.session_state.purchases, qp["name"], qp["category"], qp["brand"], qp["price"], date.today(), qp["is_ethical"], st.session_state.user_mascot)
                    st.session_state.last_logged = new_it
                    st.session_state.mascot_mood, st.session_state.mascot_message, st.session_state.recent_art = mood, msg, art
                    if mood == "ecstatic": st.balloons()
                    st.rerun()

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
            render_html(f"<div style='background:{T['soft']}; border-radius:14px; padding:0.75rem 1rem; margin:0.5rem 0; font-size:0.85rem;'><strong>Insight ({ci['tier']}):</strong> {ci['fact']} <span style='color:{T['accent']}; font-weight:700;'>• Tip: {random.choice(ECO_TIPS)}</span></div>")
            if st.form_submit_button("Record Purchase in Active Ledger", width="stretch"):
                if not item_name.strip():
                    st.error("Please enter an item description before recording.")
                else:
                    new_it, mood, msg, art = add_purchase(st.session_state.purchases, item_name, cat_choice, brand_val, price_val, date_val, is_eth, st.session_state.user_mascot)
                    st.session_state.last_logged = new_it
                    st.session_state.mascot_mood, st.session_state.mascot_message, st.session_state.recent_art = mood, msg, art
                    if mood in ["ecstatic", "happy"]: st.balloons()
                    st.rerun()

        with st.expander("Pre-Purchase Carbon & Tree Offset Simulator", expanded=False):
            sc1, sc2 = st.columns([1.2, 1.0])
            sim_d = sc1.slider("Simulate Dollar Spend ($):", 5.0, 500.0, 75.0, 5.0)
            sim_c = sc1.selectbox("Simulate Category:", list(CATEGORIES.keys()), key="sim_cat")
            sim_e = sc1.checkbox("Certified Circular / Ethical?", True, key="sim_eth")
            s_co2 = calculate_carbon(sim_d, sim_c, sim_e)
            sm, sch, st_m = get_equivalency(s_co2)
            render_html(f"<div style='background:{T['soft']}; border-radius:16px; padding:1rem;'><div class='eyebrow'>Estimated CO₂</div><div style='font-size:1.75rem; font-weight:800; color:{T['accent']};'>{s_co2:.2f} kg</div><div style='font-size:0.84rem; margin-top:0.35rem;'>~{sm:,} car miles • ~{sch:,} phone charges • ~{st_m} tree-mo</div></div>")
            if sc2.button("+ Add Simulated Item to Tracker", width="stretch"):
                si, mood, msg, art = add_purchase(st.session_state.purchases, f"Simulated: {sim_c.split()[0]} (${sim_d:.0f})", sim_c, "Simulation Tool", sim_d, date.today(), sim_e, st.session_state.user_mascot)
                st.session_state.last_logged, st.session_state.mascot_mood, st.session_state.mascot_message, st.session_state.recent_art = si, mood, msg, art
                st.rerun()

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
                            st.balloons()
                            st.rerun()

        # WHAT-IF OPTIMIZER
        swap_opp = find_top_swap_opportunity(st.session_state.purchases)
        if swap_opp:
            it = swap_opp["item"]
            op1, op2 = st.columns([2.1, 0.9], gap="medium")
            op1.markdown(f"<div class='optimizer-panel'><div class='eyebrow'>What-If Carbon Optimizer</div><strong>Your heaviest item is \"{html.escape(it['item'])}\"</strong> ({swap_opp['cur_co2']} kg). Switching to <strong>{swap_opp['target_cat']}</strong> ({swap_opp['brand_suggestion']}) drops it to <strong>{swap_opp['alt_co2']} kg</strong> (saves <strong>{swap_opp['saved_diff']} kg</strong> / -{swap_opp['pct_drop']}%).</div>", unsafe_allow_html=True)
            with op2:
                st.markdown("<div style='height:0.65rem;'></div>", unsafe_allow_html=True)
                if st.button(f"Swap Item (-{swap_opp['saved_diff']} kg)", type="primary", width="stretch", key="opt_swap_btn"):
                    tr = st.session_state.purchases[swap_opp["index"]]
                    tr["item"], tr["category"], tr["brand"], tr["carbon_kg"], tr["is_ethical"] = f"Swapped: {tr['item']} (Circular)", swap_opp["target_cat"], swap_opp["brand_suggestion"].split("/")[0].strip(), swap_opp["alt_co2"], True
                    st.session_state.last_logged, st.session_state.mascot_mood, st.session_state.recent_art = tr, "ecstatic", "badge"
                    st.session_state.mascot_message = f"Smart switch! Saved {swap_opp['saved_diff']} kg CO₂ instantly!"
                    st.rerun()

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
            with (bc1 if i % 2 == 0 else bc2):
                if b["unlocked"]:
                    render_html(f"<div class='badge-on'><div style='display:flex; gap:1rem; align-items:center;'><div style='font-size:2.7rem;'>{b['icon']}</div><div><h3 style='margin:0;'>{b['name']}</h3><p style='margin:0.2rem 0; font-size:0.9rem;'>{b['desc']}</p><span style='background:rgba(255,255,255,0.2); font-weight:800; font-size:0.75rem; padding:0.2rem 0.65rem; border-radius:99px;'>UNLOCKED ({b['progress']})</span></div></div></div>")
                else:
                    render_html(f"<div class='badge-off'><div style='display:flex; gap:1rem; align-items:center;'><div style='font-size:2.7rem;'>🔒</div><div><h3 style='margin:0;'>{b['name']}</h3><p style='margin:0.2rem 0; font-size:0.9rem;'>{b['desc']}</p><span style='font-weight:700; font-size:0.75rem;'>LOCKED ({b['progress']})</span></div></div></div>")

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
            img_u = image_to_data_uri(draw_vector_art(ak if unlocked_art else "preview"))
            col_v.markdown(f"<div class='studio-panel' style='align-items:center; text-align:center; padding:1rem;'><img src='{img_u}' style='width:140px; height:140px;'/><div style='font-weight:800; font-size:0.86rem; margin-top:0.3rem;'>{title_a}</div><div style='font-size:0.76rem; color:{T['muted']};'>{'Unlocked • ' if unlocked_art else 'Locked • '}{desc_a}</div></div>", unsafe_allow_html=True)

render_html(f"<div style='text-align:center; color:{T['muted']}; font-size:0.8rem; padding:1.4rem 0 0.6rem 0;'><strong>ShopImpact Conscious Shopping Studio</strong> • IDAI 102 • Candidate: <strong>Parth Pravinbhai Gajera</strong> (1000544)</div>")
