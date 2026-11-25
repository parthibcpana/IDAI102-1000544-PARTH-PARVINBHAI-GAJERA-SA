import html
import io
import math
import random
from datetime import date, datetime
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
    initial_sidebar_state="expanded",
)

def render_html(html_str: str):
    clean = "\n".join(line.strip() for line in html_str.splitlines() if line.strip())
    st.markdown(clean, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# DOMAIN DATA: CATEGORIES, MULTIPLIERS & CIRCULAR SWAPS
# ------------------------------------------------------------------------------

CATEGORIES = {
    "Fast Fashion Apparel": {
        "multiplier": 0.42,
        "rating": "High Carbon",
        "tier": "⚠️ High",
        "icon": "👗",
        "fact": "Synthetic polyester spinning and chemical dyeing create heavy industrial greenhouse footprints."
    },
    "Footwear & Leather": {
        "multiplier": 0.65,
        "rating": "Very High",
        "tier": "🚨 Heavy",
        "icon": "👞",
        "fact": "Bovine cattle methane and chromium tanning drive intense greenhouse gas emissions."
    },
    "Consumer Electronics": {
        "multiplier": 0.55,
        "rating": "High Carbon",
        "tier": "🚨 Heavy",
        "icon": "📱",
        "fact": "Silicon semiconductor fabrication and rare-earth mining account for ~80% of lifecycle CO₂."
    },
    "Refurbished Tech": {
        "multiplier": 0.11,
        "rating": "Low Carbon",
        "tier": "🌾 Conscious",
        "icon": "♻️",
        "fact": "Eliminates virgin mineral extraction; accounts only for diagnostics, clean transport, and testing."
    },
    "Second-Hand / Thrift": {
        "multiplier": 0.05,
        "rating": "Minimal Impact",
        "tier": "🌿 Ultra-Green",
        "icon": "🧥",
        "fact": "Pure circular economy; original manufacturing emissions are 100% amortized."
    },
    "Packaged Groceries": {
        "multiplier": 0.38,
        "rating": "Medium-High",
        "tier": "⚠️ High",
        "icon": "🛒",
        "fact": "Industrial food processing and multi-layer plastic packaging add embodied supply-chain carbon."
    },
    "Local / Organic Food": {
        "multiplier": 0.08,
        "rating": "Low Carbon",
        "tier": "🌿 Ultra-Green",
        "icon": "🥗",
        "fact": "Zero long-haul cold-chain freight and regenerative organic soil practices without synthetic nitrates."
    },
    "Home & Plastics": {
        "multiplier": 0.46,
        "rating": "High Carbon",
        "tier": "⚠️ High",
        "icon": "📦",
        "fact": "Virgin petroleum feedstocks and high-temperature polymer molding drive heavy footprint."
    },
    "Zero-Waste Reusables": {
        "multiplier": 0.07,
        "rating": "Minimal Impact",
        "tier": "🌿 Ultra-Green",
        "icon": "🌿",
        "fact": "Durable steel and bamboo displace hundreds of single-use disposable plastics across their lifespan."
    },
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
    "Refurbished Tech": [
        {"brand": "Certified Renewed Hub", "perk": "Optimal circular loop! Extends hardware life by 3+ years", "saving": "Optimal"},
    ],
    "Second-Hand / Thrift": [
        {"brand": "Community Thrift Center", "perk": "Top-tier circular reuse; zero new factory footprint", "saving": "Optimal"},
    ],
    "Packaged Groceries": [
        {"brand": "Local Farmers Market", "perk": "Seasonal crops, zero air-miles & plastic-free baskets", "saving": "58%"},
        {"brand": "Bulk Food Co-op", "perk": "Bring-your-own container pantry essentials with zero waste", "saving": "45%"},
    ],
    "Local / Organic Food": [
        {"brand": "Community CSA Farm", "perk": "Regenerative soil farming preserving local groundwater", "saving": "Optimal"},
    ],
    "Home & Plastics": [
        {"brand": "Zero-Waste Refill Station", "perk": "Refill bulk cleaners in reusable glass jars", "saving": "75%"},
        {"brand": "Bamboo & Steel Essentials", "perk": "Fast-growing renewable bamboo; fully biodegradable", "saving": "68%"},
    ],
    "Zero-Waste Reusables": [
        {"brand": "Circular Home Refill", "perk": "Gold standard zero-waste; keeps oceans and landfills clean", "saving": "Optimal"},
    ],
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
# 60 FPS ANIMATED SVG LIVING BIOSPHERE / CARBON GLOBE ENGINE
# ------------------------------------------------------------------------------

def render_animated_biosphere_svg(used_pct, co2_tot, budget_limit, width=210, height=300):
    """Renders a living glass terrarium globe reflecting live carbon budget health."""
    pct = min(150.0, max(0.0, float(used_pct)))
    
    if pct <= 50.0:
        sky_top, sky_bot = "#064e3b", "#022c22"
        glow_color = "#34d399"
        canopy_color = "#10b981"
        terrain_color = "#047857"
        status_text = "PRISTINE BIOSPHERE"
        status_color = "#34d399"
    elif pct <= 85.0:
        sky_top, sky_bot = "#1e3a1e", "#0f2014"
        glow_color = "#10b981"
        canopy_color = "#22c55e"
        terrain_color = "#15803d"
        status_text = "BALANCED ECOSYSTEM"
        status_color = "#4ade80"
    elif pct <= 100.0:
        sky_top, sky_bot = "#3b2606", "#201402"
        glow_color = "#f59e0b"
        canopy_color = "#d97706"
        terrain_color = "#92400e"
        status_text = "BUDGET WARNING"
        status_color = "#fbbf24"
    else:
        sky_top, sky_bot = "#450a0a", "#1c0404"
        glow_color = "#ef4444"
        canopy_color = "#b91c1c"
        terrain_color = "#7f1d1d"
        status_text = "CARBON OVERLOAD"
        status_color = "#f87171"

    return f"""
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 220 310" width="{width}" height="{height}" style="display: block; margin: 0 auto; filter: drop-shadow(0 8px 24px rgba(16, 185, 129, 0.25));">
    <defs>
        <radialGradient id="bio-sky" cx="50%" cy="40%" r="60%">
            <stop offset="0%" stop-color="{sky_top}"/>
            <stop offset="100%" stop-color="{sky_bot}"/>
        </radialGradient>
        <linearGradient id="bio-glass" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#ffffff" stop-opacity="0.35"/>
            <stop offset="25%" stop-color="#34d399" stop-opacity="0.10"/>
            <stop offset="70%" stop-color="#ffffff" stop-opacity="0.05"/>
            <stop offset="100%" stop-color="{glow_color}" stop-opacity="0.25"/>
        </linearGradient>
        <linearGradient id="bio-pedestal" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#1e293b"/>
            <stop offset="50%" stop-color="#0f172a"/>
            <stop offset="100%" stop-color="#020617"/>
        </linearGradient>
        <clipPath id="globe-clip">
            <circle cx="110" cy="115" r="85"/>
        </clipPath>
    </defs>
    <style>
        @keyframes canopy-sway {{
            0%, 100% {{ transform: rotate(0deg); }}
            50% {{ transform: rotate(2.5deg); }}
        }}
        @keyframes spore-float {{
            0% {{ transform: translateY(0px) translateX(0px); opacity: 0.8; }}
            50% {{ transform: translateY(-30px) translateX(10px); opacity: 0.3; }}
            100% {{ transform: translateY(-55px) translateX(-5px); opacity: 0; }}
        }}
        @keyframes sun-pulse {{
            0%, 100% {{ transform: scale(1); opacity: 0.85; }}
            50% {{ transform: scale(1.15); opacity: 1.0; }}
        }}
        .sway {{ animation: canopy-sway 4s ease-in-out infinite; transform-origin: 110px 145px; }}
        .spore-1 {{ animation: spore-float 3.5s infinite; }}
        .spore-2 {{ animation: spore-float 2.8s infinite 1.2s; }}
        .sun {{ animation: sun-pulse 3s ease-in-out infinite; transform-origin: 145px 70px; }}
    </style>

    <!-- Globe Interior (Clipped to Spherical Circle) -->
    <g clip-path="url(#globe-clip)">
        <!-- Atmospheric Sky -->
        <rect x="25" y="30" width="170" height="170" fill="url(#bio-sky)"/>

        <!-- Radiant Celestial Sun / Eco Beacon -->
        <circle class="sun" cx="145" cy="70" r="16" fill="{glow_color}" opacity="0.85"/>
        <circle cx="145" cy="70" r="9" fill="#ffffff" opacity="0.95"/>

        <!-- Ambient Rolling Terrarium Hills -->
        <path d="M 25 170 Q 65 140 110 152 T 195 148 L 195 205 L 25 205 Z" fill="{terrain_color}" opacity="0.6"/>
        <path d="M 25 175 Q 85 152 130 164 T 195 160 L 195 205 L 25 205 Z" fill="{terrain_color}"/>

        <!-- Ancient Living Tree of Biosphere -->
        <path d="M 105 178 C 106 155 103 140 107 132 C 109 128 111 128 113 132 C 117 140 114 155 115 178 Z" fill="#78350f"/>
        <!-- Swaying Canopy Foliage -->
        <g class="sway">
            <ellipse cx="110" cy="114" rx="32" ry="24" fill="{canopy_color}" opacity="0.9"/>
            <ellipse cx="94" cy="108" rx="20" ry="16" fill="{canopy_color}"/>
            <ellipse cx="126" cy="108" rx="20" ry="16" fill="{canopy_color}"/>
            <circle cx="110" cy="94" r="16" fill="#34d399" opacity="0.85"/>
            <!-- Blossom Spores -->
            <circle cx="98" cy="102" r="2.8" fill="#fef08a"/>
            <circle cx="122" cy="102" r="2.8" fill="#fef08a"/>
            <circle cx="110" cy="114" r="2.8" fill="#fef08a"/>
        </g>

        <!-- Floating Life Spores / Bio-particles -->
        <circle class="spore-1" cx="85" cy="145" r="2.8" fill="{glow_color}"/>
        <circle class="spore-2" cx="135" cy="155" r="2.4" fill="#fef08a"/>

        <!-- Glass Shadow Inner Curvature -->
        <circle cx="110" cy="115" r="83" fill="none" stroke="{glow_color}" stroke-width="2.5" opacity="0.3"/>
    </g>

    <!-- Outer Glass Globe Orb -->
    <circle cx="110" cy="115" r="85" fill="url(#bio-glass)" stroke="{glow_color}" stroke-width="3"/>

    <!-- Specular Highlight Sheen (Simulating 3D Curved Glass Reflections) -->
    <path d="M 50 75 A 80 80 0 0 1 100 38" fill="none" stroke="#ffffff" stroke-width="4.5" stroke-linecap="round" opacity="0.55"/>
    <circle cx="150" cy="155" r="4.0" fill="#ffffff" opacity="0.35"/>

    <!-- Brass / Obsidian Pedestal Base -->
    <ellipse cx="110" cy="208" rx="42" ry="11" fill="url(#bio-pedestal)" stroke="{glow_color}" stroke-width="2"/>
    <path d="M 80 210 L 66 238 C 66 244 154 244 154 238 L 140 210 Z" fill="url(#bio-pedestal)" stroke="#0f172a" stroke-width="2"/>
    <rect x="60" y="220" width="100" height="26" rx="13" fill="#0f172a" stroke="{glow_color}" stroke-width="2.2"/>

    <!-- Centerpiece Typography Badge Inside Base -->
    <text x="110" y="237" text-anchor="middle" fill="#ffffff" font-size="11.5" font-weight="900" font-family="sans-serif">{pct:.0f}% BUDGET</text>
    <text x="110" y="264" text-anchor="middle" fill="{status_color}" font-size="8.2" font-weight="800" font-family="sans-serif" letter-spacing="0.6">{status_text}</text>

    <!-- Bottom Readout Caption -->
    <text x="110" y="283" text-anchor="middle" fill="#64748b" font-size="10.8" font-weight="700" font-family="sans-serif">{co2_tot:.1f} / {budget_limit} kg CO₂e</text>
    <text x="110" y="299" text-anchor="middle" fill="{status_color}" font-size="9.5" font-weight="700" font-family="sans-serif">Remaining: {max(0.0, budget_limit - co2_tot):.1f} kg</text>
    </svg>
    """

# ------------------------------------------------------------------------------
# 5-CHARACTER ANIMATED SVG MASCOT AVATAR ENGINE
# ------------------------------------------------------------------------------

def render_animated_avatar_svg(character="turtle", mood="happy", width=180, height=180):
    if character in ["ecstatic", "happy", "mindful", "worried", "alarmed"]:
        mood = character
        character = "turtle"

    char_key = str(character).lower()
    if "fox" in char_key: c_type = "fox"
    elif "owl" in char_key: c_type = "owl"
    elif "bee" in char_key or "pollinator" in char_key: c_type = "bee"
    elif "panda" in char_key: c_type = "panda"
    else: c_type = "turtle"

    shiver_class = "shiver" if mood in ["worried", "alarmed"] else "bob"
    
    svg = f"""<svg width="{width}" height="{height}" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg" style="max-width: 100%; height: auto; filter: drop-shadow(0 6px 16px rgba(0,0,0,0.25));">
    <style>
    @keyframes avatar-bob {{ 0%, 100% {{ transform: translateY(0px); }} 50% {{ transform: translateY(-7px); }} }}
    @keyframes flipper-wave-l {{ 0%, 100% {{ transform: rotate(0deg); }} 50% {{ transform: rotate(24deg); }} }}
    @keyframes flipper-wave-r {{ 0%, 100% {{ transform: rotate(0deg); }} 50% {{ transform: rotate(-24deg); }} }}
    @keyframes sprout-sway {{ 0%, 100% {{ transform: rotate(-8deg); }} 50% {{ transform: rotate(8deg); }} }}
    @keyframes eye-blink {{ 0%, 90%, 100% {{ transform: scaleY(1); }} 95% {{ transform: scaleY(0.1); }} }}
    @keyframes sweat-drip {{ 0% {{ opacity: 0; transform: translateY(-4px); }} 40% {{ opacity: 1; transform: translateY(0px); }} 80% {{ opacity: 0; transform: translateY(7px); }} 100% {{ opacity: 0; transform: translateY(7px); }} }}
    @keyframes avatar-shiver {{ 0%, 100% {{ transform: translate(0, 0); }} 25% {{ transform: translate(-2.5px, 1.5px); }} 75% {{ transform: translate(2.5px, -1.5px); }} }}
    @keyframes wing-buzz {{ 0%, 100% {{ transform: scaleY(1); }} 50% {{ transform: scaleY(0.7) skewX(4deg); }} }}
    .bob {{ animation: avatar-bob 2.2s ease-in-out infinite; transform-origin: center; }}
    .shiver {{ animation: avatar-shiver 0.2s infinite; }}
    .wave-l {{ animation: flipper-wave-l 1.3s ease-in-out infinite; transform-origin: 50px 85px; }}
    .wave-r {{ animation: flipper-wave-r 1.3s ease-in-out infinite; transform-origin: 150px 85px; }}
    .sprout {{ animation: sprout-sway 1.8s ease-in-out infinite; transform-origin: 100px 30px; }}
    .blink {{ animation: eye-blink 3.8s infinite; transform-origin: 100px 50px; }}
    .sweat {{ animation: sweat-drip 1.2s infinite; }}
    .wings {{ animation: wing-buzz 0.15s ease-in-out infinite; transform-origin: 100px 90px; }}
    </style>
    <g class="{shiver_class}">"""

    if c_type == "fox":
        svg += """
        <path d="M 140 145 C 185 155 190 105 160 85 C 145 95 135 125 140 145 Z" fill="#ea580c" stroke="#9a3412" stroke-width="2.5"/>
        <path d="M 175 95 C 190 105 178 120 160 115 Z" fill="#ffffff"/>
        <ellipse cx="100" cy="130" rx="46" ry="42" fill="#ea580c" stroke="#9a3412" stroke-width="3"/>
        <ellipse cx="100" cy="136" rx="28" ry="26" fill="#ffedd5" stroke="#ea580c" stroke-width="2"/>
        <ellipse cx="70" cy="165" rx="14" ry="10" fill="#ea580c" stroke="#9a3412" stroke-width="2"/>
        <ellipse cx="130" cy="165" rx="14" ry="10" fill="#ea580c" stroke="#9a3412" stroke-width="2"/>
        <polygon points="55,42 75,18 85,46" fill="#ea580c" stroke="#9a3412" stroke-width="2.5"/>
        <polygon points="62,38 75,24 80,44" fill="#fbcfe8"/>
        <polygon points="145,42 125,18 115,46" fill="#ea580c" stroke="#9a3412" stroke-width="2.5"/>
        <polygon points="138,38 125,24 120,44" fill="#fbcfe8"/>
        <ellipse cx="100" cy="62" rx="34" ry="30" fill="#ea580c" stroke="#9a3412" stroke-width="2.5"/>
        <ellipse cx="82" cy="72" rx="16" ry="14" fill="#ffffff"/>
        <ellipse cx="118" cy="72" rx="16" ry="14" fill="#ffffff"/>
        <polygon points="96,72 104,72 100,78" fill="#1e293b"/>
        """
    elif c_type == "owl":
        svg += """
        <ellipse cx="100" cy="120" rx="50" ry="46" fill="#78350f" stroke="#451a03" stroke-width="3"/>
        <ellipse cx="100" cy="126" rx="34" ry="32" fill="#fef3c7" stroke="#b45309" stroke-width="2"/>
        <path d="M 90 120 Q 100 128 110 120 M 85 135 Q 100 145 115 135" fill="none" stroke="#b45309" stroke-width="2"/>
        <g class="wave-l">
        <ellipse cx="54" cy="120" rx="14" ry="34" fill="#92400e" stroke="#451a03" stroke-width="2" transform="rotate(15 54 120)"/>
        </g>
        <g class="wave-r">
        <ellipse cx="146" cy="120" rx="14" ry="34" fill="#92400e" stroke="#451a03" stroke-width="2" transform="rotate(-15 146 120)"/>
        </g>
        <ellipse cx="78" cy="165" rx="12" ry="7" fill="#d97706"/>
        <ellipse cx="122" cy="165" rx="12" ry="7" fill="#d97706"/>
        <polygon points="70,36 60,16 80,30" fill="#78350f" stroke="#451a03" stroke-width="2"/>
        <polygon points="130,36 140,16 120,30" fill="#78350f" stroke="#451a03" stroke-width="2"/>
        <ellipse cx="100" cy="58" rx="36" ry="32" fill="#78350f" stroke="#451a03" stroke-width="2.5"/>
        <circle cx="85" cy="56" r="16" fill="#fef3c7" stroke="#d97706" stroke-width="2.5"/>
        <circle cx="115" cy="56" r="16" fill="#fef3c7" stroke="#d97706" stroke-width="2.5"/>
        <line x1="99" y1="56" x2="101" y2="56" stroke="#d97706" stroke-width="2.5"/>
        <polygon points="96,65 104,65 100,75" fill="#f59e0b"/>
        """
    elif c_type == "bee":
        svg += """
        <g class="wings">
        <ellipse cx="72" cy="72" rx="28" ry="16" fill="#bae6fd" opacity="0.8" stroke="#0284c7" stroke-width="1.5" transform="rotate(-35 72 72)"/>
        <ellipse cx="128" cy="72" rx="28" ry="16" fill="#bae6fd" opacity="0.8" stroke="#0284c7" stroke-width="1.5" transform="rotate(35 128 72)"/>
        </g>
        <ellipse cx="100" cy="115" rx="46" ry="54" fill="#fbbf24" stroke="#78350f" stroke-width="3"/>
        <path d="M 60 98 Q 100 110 140 98" fill="none" stroke="#1e293b" stroke-width="11" stroke-linecap="round"/>
        <path d="M 64 125 Q 100 137 136 125" fill="none" stroke="#1e293b" stroke-width="11" stroke-linecap="round"/>
        <polygon points="96,168 104,168 100,182" fill="#1e293b"/>
        <path d="M 90 40 Q 80 20 70 24" fill="none" stroke="#1e293b" stroke-width="2.5"/>
        <circle cx="68" cy="24" r="4.5" fill="#f59e0b"/>
        <path d="M 110 40 Q 120 20 130 24" fill="none" stroke="#1e293b" stroke-width="2.5"/>
        <circle cx="132" cy="24" r="4.5" fill="#f59e0b"/>
        <ellipse cx="100" cy="58" rx="28" ry="24" fill="#fbbf24" stroke="#78350f" stroke-width="2.5"/>
        """
    elif c_type == "panda":
        svg += """
        <ellipse cx="100" cy="130" rx="48" ry="44" fill="#ffffff" stroke="#1e293b" stroke-width="3"/>
        <path d="M 54 115 Q 100 135 146 115 L 142 155 Q 100 170 58 155 Z" fill="#1e293b"/>
        <g class="wave-l">
        <ellipse cx="50" cy="98" rx="14" ry="26" fill="#1e293b" transform="rotate(-30 50 98)"/>
        </g>
        <g class="wave-r">
        <ellipse cx="150" cy="98" rx="14" ry="26" fill="#1e293b" transform="rotate(30 150 98)"/>
        </g>
        <ellipse cx="60" cy="165" rx="14" ry="10" fill="#1e293b"/>
        <ellipse cx="140" cy="165" rx="14" ry="10" fill="#1e293b"/>
        <circle cx="68" cy="38" r="15" fill="#1e293b"/>
        <circle cx="132" cy="38" r="15" fill="#1e293b"/>
        <ellipse cx="100" cy="62" rx="36" ry="32" fill="#ffffff" stroke="#1e293b" stroke-width="2.5"/>
        <ellipse cx="84" cy="58" rx="11" ry="14" fill="#1e293b" transform="rotate(-15 84 58)"/>
        <ellipse cx="116" cy="58" rx="11" ry="14" fill="#1e293b" transform="rotate(15 116 58)"/>
        <ellipse cx="100" cy="72" rx="5" ry="3.5" fill="#1e293b"/>
        <line x1="104" y1="74" x2="135" y2="82" stroke="#16a34a" stroke-width="3"/>
        <ellipse cx="132" cy="78" rx="6" ry="3" fill="#22c55e" transform="rotate(-20 132 78)"/>
        """
    else:  # turtle
        svg += """
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

    if mood == "ecstatic":
        svg += """
        <g class="sprout">
        <line x1="100" y1="28" x2="100" y2="10" stroke="#d97706" stroke-width="3"/>
        <polygon points="100,4 103,11 110,11 105,15 107,22 100,18 93,22 95,15 90,11 97,11" fill="#f59e0b"/>
        </g>
        <path d="M 81 48 L 96 48 Q 96 58 88 58 Q 81 58 81 48 Z" fill="#1e293b"/>
        <path d="M 104 48 L 119 48 Q 119 58 112 58 Q 104 58 104 48 Z" fill="#1e293b"/>
        <line x1="96" y1="50" x2="104" y2="50" stroke="#1e293b" stroke-width="2.5"/>
        <line x1="84" y1="51" x2="93" y2="51" stroke="#94a3b8" stroke-width="1.2"/>
        <line x1="107" y1="51" x2="116" y2="51" stroke="#94a3b8" stroke-width="1.2"/>
        <ellipse cx="79" cy="64" rx="6" ry="3.5" fill="#f43f5e" opacity="0.6"/>
        <ellipse cx="121" cy="64" rx="6" ry="3.5" fill="#f43f5e" opacity="0.6"/>
        <path d="M 88 63 Q 100 77 112 63" fill="#f43f5e" stroke="#1b4332" stroke-width="2.5" stroke-linecap="round"/>
        """
    elif mood == "happy":
        svg += """
        <g class="sprout">
        <line x1="100" y1="28" x2="100" y2="12" stroke="#1b4332" stroke-width="2.5"/>
        <ellipse cx="94" cy="10" rx="7" ry="4.5" fill="#52b788" stroke="#1b4332" stroke-width="1.5" transform="rotate(-30 94 10)"/>
        <ellipse cx="106" cy="10" rx="7" ry="4.5" fill="#52b788" stroke="#1b4332" stroke-width="1.5" transform="rotate(30 106 10)"/>
        </g>
        <g class="blink">
        <circle cx="89" cy="51" r="5" fill="#1b4332"/>
        <circle cx="87" cy="49" r="1.8" fill="#ffffff"/>
        <circle cx="111" cy="51" r="5" fill="#1b4332"/>
        <circle cx="109" cy="49" r="1.8" fill="#ffffff"/>
        </g>
        <ellipse cx="81" cy="63" rx="5.5" ry="3.5" fill="#fb7185" opacity="0.6"/>
        <ellipse cx="119" cy="63" rx="5.5" ry="3.5" fill="#fb7185" opacity="0.6"/>
        <path d="M 88 63 Q 100 75 112 63" fill="none" stroke="#1b4332" stroke-width="3" stroke-linecap="round"/>
        """
    elif mood == "alarmed":
        svg += """
        <polygon points="100,8 107,22 93,22" fill="#ef4444" stroke="#991b1b" stroke-width="1.5"/>
        <text x="98" y="20" font-size="9" font-weight="bold" fill="#ffffff">!</text>
        <circle cx="89" cy="52" r="7" fill="#ffffff" stroke="#1b4332" stroke-width="2"/>
        <circle cx="89" cy="52" r="3" fill="#1b4332"/>
        <circle cx="111" cy="52" r="7" fill="#ffffff" stroke="#1b4332" stroke-width="2"/>
        <circle cx="111" cy="52" r="3" fill="#1b4332"/>
        <ellipse cx="100" cy="69" rx="6" ry="8" fill="#1b4332"/>
        <g class="sweat">
        <path d="M 125 36 Q 130 45 125 50 Q 120 45 125 36" fill="#38bdf8" stroke="#0284c7" stroke-width="1.2"/>
        <path d="M 75 36 Q 80 45 75 50 Q 70 45 75 36" fill="#38bdf8" stroke="#0284c7" stroke-width="1.2"/>
        </g>
        """
    elif mood == "worried":
        svg += """
        <circle cx="89" cy="53" r="5.5" fill="#1b4332"/>
        <circle cx="111" cy="53" r="5.5" fill="#1b4332"/>
        <path d="M 89 68 Q 100 59 111 68" fill="none" stroke="#1b4332" stroke-width="2.8" stroke-linecap="round"/>
        <g class="sweat">
        <path d="M 124 38 Q 128 47 124 51 Q 120 47 124 38" fill="#38bdf8" stroke="#0284c7" stroke-width="1.2"/>
        </g>
        """
    else:  # mindful
        svg += """
        <g class="sprout">
        <line x1="100" y1="28" x2="100" y2="14" stroke="#1b4332" stroke-width="2"/>
        <ellipse cx="94" cy="12" rx="6" ry="4" fill="#52b788" stroke="#1b4332" stroke-width="1.5" transform="rotate(-30 94 12)"/>
        <ellipse cx="106" cy="12" rx="6" ry="4" fill="#52b788" stroke="#1b4332" stroke-width="1.5" transform="rotate(30 106 12)"/>
        </g>
        <path d="M 84 52 Q 89 46 94 52" fill="none" stroke="#1b4332" stroke-width="2.5" stroke-linecap="round"/>
        <path d="M 106 52 Q 111 46 116 52" fill="none" stroke="#1b4332" stroke-width="2.5" stroke-linecap="round"/>
        <path d="M 91 65 Q 100 71 109 65" fill="none" stroke="#1b4332" stroke-width="2.2" stroke-linecap="round"/>
        """

    svg += "</g></svg>"
    return svg

def get_mascot_reaction(mascot_str, item_name, live_co2, mood, is_eth):
    name = mascot_str.split()[0]
    m = mascot_str.lower()
    if mood == "ecstatic":
        if "fox" in m:
            return f"CLEVER THRIFT MASTER! {name} put on gold sunglasses! '{item_name}' is a legendary circular treasure!"
        elif "owl" in m:
            return f"SCHOLARLY PRECISION! {name} adjusted golden spectacles! '{item_name}' has an optimal low footprint!"
        elif "bee" in m:
            return f"POLLINATOR HARVEST! {name} is buzzing with joy in gold sunglasses! '{item_name}' restores the biosphere!"
        elif "panda" in m:
            return f"ULTIMATE ZERO-WASTE! {name} put on gold sunglasses! '{item_name}' preserves our bamboo forests!"
        else:
            return f"LEGENDARY ECO-CHOICE! {name} put on gold sunglasses! '{item_name}' has virtually zero factory emissions!"
    elif mood == "happy":
        return f"Wonderful green purchase! '{item_name}' logged at only {live_co2} kg CO₂e! {name} is waving happily!"
    elif mood == "mindful":
        return f"Recorded '{item_name}' ({live_co2} kg CO₂e). {name} notes a balanced choice. Explore greener swaps below!"
    elif mood == "worried":
        return f"Whew, getting heavy! '{item_name}' generated {live_co2} kg CO₂e. {name} feels the carbon heat!"
    else:  # alarmed
        return f"🚨 CARBON SPIKE ALERT! That item created {live_co2} kg CO₂e! {name} is shivering! Adopt a greener swap below to balance your budget!"

# ------------------------------------------------------------------------------
# IN-MEMORY PROCEDURAL HEADLESS TURTLE VECTOR ENGINE
# ------------------------------------------------------------------------------

class HeadlessTurtle:
    """Pure Python Turtle vector engine executing on Pillow canvases without Tkinter dependencies."""
    def __init__(self, w=220, h=220):
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

def draw_vector_art(art_type="leaf"):
    """Generates layered 280x280 RGBA botanical vector artworks via HeadlessTurtle & Pillow."""
    w, h = 280, 280
    t = HeadlessTurtle(w, h)
    cx, cy = 140, 134

    if art_type == "preview":
        # Gentle muted botanical emblem for initial empty session
        t.draw.ellipse([(cx - 88, cy - 88), (cx + 88, cy + 88)], fill=(16, 48, 32, 95), outline=(52, 211, 153, 90), width=2)
        for deg in range(0, 360, 30):
            rad = math.radians(deg)
            x1, y1 = cx + 96 * math.cos(rad), cy + 96 * math.sin(rad)
            x2, y2 = cx + 104 * math.cos(rad), cy + 104 * math.sin(rad)
            t.draw.line([(x1, y1), (x2, y2)], fill=(52, 211, 153, 80), width=2)
        t.draw.ellipse([(cx - 32, cy - 32), (cx + 32, cy + 32)], fill=(16, 185, 129, 70), outline=(52, 211, 153, 120), width=2)
        seed_pts = [(cx, cy - 42), (cx + 22, cy - 10), (cx + 16, cy + 28), (cx, cy + 38), (cx - 16, cy + 28), (cx - 22, cy - 10)]
        t.draw.polygon(seed_pts, fill=(52, 211, 153, 110), outline=(167, 243, 208, 160))
        return t.img

    if art_type == "leaf":
        # Warm solar botanical shield + orbital turtle ticks + shaded twin leaf sprout + dew droplets
        t.draw.ellipse([(cx - 106, cy - 106), (cx + 106, cy + 106)], fill=(16, 62, 38, 175), outline=(52, 211, 153, 200), width=3)
        t.draw.ellipse([(cx - 94, cy - 94), (cx + 94, cy + 94)], fill=(20, 83, 45, 145), outline=(110, 231, 183, 130), width=2)
        for deg in range(0, 360, 15):
            rad = math.radians(deg)
            r1 = 100
            r2 = 109 if deg % 45 == 0 else 104
            col = (251, 191, 36, 220) if deg % 45 == 0 else (52, 211, 153, 140)
            t.draw.line([(cx + r1 * math.cos(rad), cy + r1 * math.sin(rad)), (cx + r2 * math.cos(rad), cy + r2 * math.sin(rad))], fill=col, width=3 if deg % 45 == 0 else 2)

        # Warm glowing sun behind leaf
        t.draw.ellipse([(cx - 56, cy - 72), (cx + 18, cy + 2)], fill=(251, 191, 36, 55))
        t.draw.ellipse([(cx - 46, cy - 62), (cx + 8, cy - 8)], fill=(253, 224, 71, 80))

        # Main Turtle curved stem
        t.penup(); t.goto(cx - 4, cy + 88); t.heading = 84; t.color = (167, 243, 208, 255); t.width = 5; t.pendown()
        t.forward(55)

        # Main primary right/center sculptural leaf
        leaf_r, leaf_l = [], []
        for step in range(25):
            frac = step / 24.0
            y = (cy + 58) - frac * 124
            curve = math.sin(frac * math.pi) * 44
            lean = math.sin(frac * math.pi * 0.7) * 14
            leaf_r.append((cx + lean + curve, y))
            leaf_l.append((cx + lean - curve * 0.9, y))
        main_poly = leaf_r + list(reversed(leaf_l))
        t.draw.polygon(main_poly, fill=(16, 185, 129, 245), outline=(5, 150, 105, 255))
        # Lighter sun-lit left facet shading inside leaf
        highlight_poly = [(cx + math.sin((s/24.0)*math.pi*0.7)*14, (cy+58)-(s/24.0)*124) for s in range(25)] + list(reversed(leaf_l))
        t.draw.polygon(highlight_poly, fill=(52, 211, 153, 210))

        # Secondary smaller sprout leaf angled left
        t.draw.polygon([(cx - 2, cy + 44), (cx - 42, cy + 24), (cx - 60, cy + 4), (cx - 28, cy + 10), (cx - 4, cy + 32)], fill=(110, 231, 183, 235), outline=(16, 185, 129, 255))

        # Midrib and curved veins via Turtle steps
        t.penup(); t.goto(cx, cy + 56); t.heading = 84; t.color = (6, 78, 59, 240); t.width = 3; t.pendown()
        t.forward(116)
        for idx_y in [cy + 30, cy + 6, cy - 18, cy - 40]:
            x_off = 8 if idx_y < cy + 10 else 3
            t.penup(); t.goto(cx + x_off, idx_y); t.heading = 38; t.width = 2; t.pendown(); t.forward(24)
            t.penup(); t.goto(cx + x_off, idx_y); t.heading = 140; t.pendown(); t.forward(22)

        # Specular shimmering dew droplets
        for dx, dy, dr in [(cx - 16, cy - 16, 5), (cx + 18, cy + 10, 4), (cx - 38, cy + 16, 3.5)]:
            t.draw.ellipse([(dx - dr, dy - dr), (dx + dr, dy + dr)], fill=(236, 253, 245, 240), outline=(52, 211, 153, 255), width=1)
            t.draw.ellipse([(dx - dr * 0.4, dy - dr * 0.5), (dx + 0.5, dy - 0.5)], fill=(255, 255, 255, 255))

    elif art_type == "footprint":
        # Concentric circular nature medallion with 8 radial petals drawn by Turtle
        t.draw.ellipse([(cx - 108, cy - 108), (cx + 108, cy + 108)], fill=(6, 78, 59, 190), outline=(52, 211, 153, 220), width=3)
        t.draw.ellipse([(cx - 94, cy - 94), (cx + 94, cy + 94)], fill=(17, 56, 38, 210), outline=(16, 185, 129, 160), width=2)
        for deg in range(0, 360, 45):
            rad = math.radians(deg)
            px, py = cx + 99 * math.cos(rad), cy + 99 * math.sin(rad)
            t.draw.ellipse([(px - 7, py - 7), (px + 7, py + 7)], fill=(52, 211, 153, 210), outline=(254, 240, 138, 190), width=1)

        # Anatomical eco-footprint centered cleanly
        t.draw.ellipse([(cx - 26, cy + 20), (cx + 22, cy + 72)], fill=(16, 185, 129, 240), outline=(167, 243, 208, 220), width=2)
        foot_pts = [
            (cx - 22, cy + 32), (cx - 14, cy - 6), (cx - 30, cy - 34), (cx - 16, cy - 62),
            (cx + 18, cy - 62), (cx + 30, cy - 34), (cx + 16, cy - 6), (cx + 18, cy + 32)
        ]
        t.draw.polygon(foot_pts, fill=(16, 185, 129, 240), outline=(167, 243, 208, 220))
        t.draw.ellipse([(cx - 30, cy - 64), (cx + 30, cy - 16)], fill=(16, 185, 129, 240), outline=(167, 243, 208, 220), width=2)
        # Inner emerald highlight arch
        t.draw.ellipse([(cx - 15, cy - 48), (cx + 16, cy - 22)], fill=(52, 211, 153, 180))
        for tx, ty, tr in [(-20, -78, 10.5), (-1, -85, 9.0), (14, -81, 8.0), (26, -73, 7.0), (36, -62, 5.8)]:
            t.draw.ellipse([(cx + tx - tr, cy + ty - tr), (cx + tx + tr, cy + ty + tr)], fill=(52, 211, 153, 245), outline=(236, 253, 245, 220), width=2)

    else:  # Grand 32-Point Gold-Emerald Scalloped Rosette Championship Medallion
        cy_m = 114
        # Soft radial starburst rays behind ribbon & rosette
        for deg in range(0, 360, 20):
            rad = math.radians(deg)
            rx, ry = cx + 114 * math.cos(rad), cy_m + 114 * math.sin(rad)
            t.draw.line([(cx, cy_m), (rx, ry)], fill=(251, 191, 36, 55), width=3)

        # Twin Swallowtail Ribbons
        r_pts_l = [(cx - 26, cy_m + 28), (cx - 56, cy_m + 142), (cx - 34, cy_m + 124), (cx - 12, cy_m + 134), (cx - 6, cy_m + 30)]
        t.draw.polygon(r_pts_l, fill=(5, 150, 105, 255), outline=(16, 185, 129, 255))
        t.draw.line([(cx - 24, cy_m + 32), (cx - 34, cy_m + 124)], fill=(110, 231, 183, 220), width=2)

        r_pts_r = [(cx + 6, cy_m + 30), (cx + 12, cy_m + 134), (cx + 34, cy_m + 124), (cx + 56, cy_m + 142), (cx + 26, cy_m + 28)]
        t.draw.polygon(r_pts_r, fill=(4, 120, 87, 255), outline=(16, 185, 129, 255))
        t.draw.line([(cx + 24, cy_m + 32), (cx + 34, cy_m + 124)], fill=(110, 231, 183, 220), width=2)

        # 64-vertex Scalloped Gold Starburst Gear
        rosette_pts = []
        for i in range(64):
            ang = i * (math.pi / 32)
            r = 68 if i % 2 == 0 else 58
            rosette_pts.append((cx + r * math.cos(ang), cy_m + r * math.sin(ang)))
        t.draw.polygon(rosette_pts, fill=(245, 158, 11, 255), outline=(253, 224, 71, 255))
        t.draw.ellipse([(cx - 56, cy_m - 56), (cx + 56, cy_m + 56)], fill=(251, 191, 36, 255), outline=(180, 83, 9, 255), width=2)
        t.draw.ellipse([(cx - 47, cy_m - 47), (cx + 47, cy_m + 47)], fill=(6, 78, 59, 255), outline=(52, 211, 153, 230), width=2)
        for j in range(16):
            s_ang = j * (2 * math.pi / 16)
            sx, sy = cx + 41 * math.cos(s_ang), cy_m + 41 * math.sin(s_ang)
            t.draw.ellipse([(sx - 2.3, sy - 2.3), (sx + 2.3, sy + 2.3)], fill=(254, 240, 138, 255))
        t.draw.ellipse([(cx - 33, cy_m - 33), (cx + 33, cy_m + 33)], fill=(254, 249, 195, 255), outline=(217, 119, 6, 255), width=2)

        star_pts, star_inner = [], []
        for k in range(10):
            ang = -math.pi / 2 + k * (math.pi / 5)
            sr = 22 if k % 2 == 0 else 9.0
            si = 16 if k % 2 == 0 else 6.5
            star_pts.append((cx + sr * math.cos(ang), cy_m + sr * math.sin(ang)))
            star_inner.append((cx + si * math.cos(ang), cy_m + si * math.sin(ang)))
        t.draw.polygon(star_pts, fill=(217, 119, 6, 255), outline=(146, 64, 14, 255))
        t.draw.polygon(star_inner, fill=(251, 191, 36, 255))

    return t.img

def image_to_png_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def calculate_carbon(price, category, is_ethical):
    rate = CATEGORIES.get(category, {"multiplier": 0.35})["multiplier"]
    base = price * rate
    return round(base * 0.70 if is_ethical else base, 2)

def get_equivalency(carbon_kg):
    miles = int(carbon_kg * 2.4)
    charges = int(carbon_kg * 121)
    tree_months = round((carbon_kg / 21.0) * 12, 1)
    return miles, charges, tree_months

def compute_eco_streak(purchases):
    """Returns consecutive recent ethical purchases ending at latest entry, plus overall max streak."""
    cur_streak = 0
    for p in reversed(purchases):
        if p.get("is_ethical", p.get("ethical", False)):
            cur_streak += 1
        else:
            break
    best, run = 0, 0
    for p in purchases:
        if p.get("is_ethical", p.get("ethical", False)):
            run += 1
            best = max(best, run)
        else:
            run = 0
    return cur_streak, best

def get_collected_arts(purchases):
    """Deterministically identifies which Turtle artworks (leaf, footprint, badge) are earned in session."""
    earned = set()
    for p in purchases:
        eth = p.get("is_ethical", p.get("ethical", False))
        co2 = p.get("carbon_kg", p.get("co2", 0.0))
        if eth and co2 <= 3.0:
            earned.add("badge")
        elif eth:
            earned.add("leaf")
        elif co2 <= 10.0:
            earned.add("footprint")
    return earned

def get_user_eco_rank(purchases):
    count = len(purchases)
    ethical = sum(1 for p in purchases if p.get("is_ethical", False))
    if count == 0:
        return "🌱 Eco Novice"
    elif ethical >= 5 or (count >= 5 and ethical >= 3):
        return "👑 Biosphere Master"
    elif ethical >= 2 or count >= 3:
        return "🌿 Conscious Pioneer"
    else:
        return "🌾 Mindful Forager"

def evaluate_badges(purchases):
    total_items = len(purchases)
    total_spend = sum(p.get("price", 0.0) for p in purchases)
    total_co2 = sum(p.get("carbon_kg", p.get("co2", 0.0)) for p in purchases)
    ethical_count = sum(1 for p in purchases if p.get("is_ethical", p.get("ethical", False)))
    avg_intensity = (total_co2 / total_spend) if total_spend > 0 else 0.0
    co2_saved = max(0.0, round(total_spend * 0.45 - total_co2, 1))
    zero_waste_count = sum(1 for p in purchases if "Zero-Waste" in p.get("category", "") or "Thrift" in p.get("category", ""))

    badges = [
        {
            "id": "starter",
            "name": "Seed Starter",
            "icon": "🌱",
            "desc": "Log your 1st conscious purchase in the dashboard",
            "unlocked": total_items >= 1,
            "progress": f"{min(total_items, 1)}/1 item",
            "pct": 100 if total_items >= 1 else 0,
        },
        {
            "id": "low_impact",
            "name": "Low Impact Shopper",
            "icon": "🍃",
            "desc": "Maintain carbon intensity ≤ 0.25 kg/$ (min 2 items)",
            "unlocked": total_items >= 2 and avg_intensity <= 0.25,
            "progress": f"{avg_intensity:.2f} kg/$ (Goal ≤ 0.25)" if total_items >= 2 else f"{total_items}/2 items required",
            "pct": 100 if (total_items >= 2 and avg_intensity <= 0.25) else (max(10, min(95, int((0.25 / max(avg_intensity, 0.26)) * 100))) if total_items >= 2 else int((total_items / 2) * 100)),
        },
        {
            "id": "ethical_pioneer",
            "name": "Conscious Pioneer",
            "icon": "♻️",
            "desc": "Choose 3+ verified circular, thrift, or ethical items",
            "unlocked": ethical_count >= 3,
            "progress": f"{ethical_count}/3 ethical items",
            "pct": min(100, int((ethical_count / 3.0) * 100)),
        },
        {
            "id": "eco_saver",
            "name": "Eco Saver of the Month",
            "icon": "🌟",
            "desc": "Save 10+ kg CO₂ vs standard retail baseline",
            "unlocked": co2_saved >= 10.0 and total_items >= 1,
            "progress": f"{co2_saved:.1f}/10.0 kg CO₂ saved",
            "pct": min(100, int((co2_saved / 10.0) * 100)) if total_items >= 1 else 0,
        },
        {
            "id": "zero_waste",
            "name": "Zero-Waste Hero",
            "icon": "🏆",
            "desc": "Log 2+ zero-waste or second-hand thrift items",
            "unlocked": zero_waste_count >= 2,
            "progress": f"{zero_waste_count}/2 items",
            "pct": min(100, int((zero_waste_count / 2.0) * 100)),
        },
    ]
    return badges, total_spend, total_co2, avg_intensity, co2_saved, ethical_count

def get_next_badge_nudge(badges):
    """Returns encouraging progress label and completion % for the next locked badge."""
    locked = [b for b in badges if not b["unlocked"]]
    if not locked:
        return "🏆 All 5 Milestone Badges Unlocked! You are a Biosphere Legend!", 100
    best = max(locked, key=lambda b: b["pct"])
    return f"🎯 Next Milestone: {best['icon']} {best['name']} ({best['progress']})", best["pct"]

def find_top_swap_opportunity(purchases):
    """Finds the single highest-CO2 non-ethical item to offer a live 1-click Green Switch."""
    non_eth = [
        (idx, p) for idx, p in enumerate(purchases)
        if not p.get("is_ethical", p.get("ethical", False)) and p.get("carbon_kg", p.get("co2", 0.0)) > 0
    ]
    if not non_eth:
        return None
    idx, item = max(non_eth, key=lambda pair: pair[1].get("carbon_kg", pair[1].get("co2", 0.0)))
    cur_co2 = item.get("carbon_kg", item.get("co2", 0.0))
    cat = item.get("category", "Fast Fashion Apparel")
    # Suggest greener category target
    alt_cat_map = {
        "Consumer Electronics": "Refurbished Tech",
        "Fast Fashion Apparel": "Second-Hand / Thrift",
        "Footwear & Leather": "Second-Hand / Thrift",
        "Packaged Groceries": "Local / Organic Food",
        "Home & Plastics": "Zero-Waste Reusables",
    }
    target_cat = alt_cat_map.get(cat, "Second-Hand / Thrift")
    alt_co2 = calculate_carbon(item.get("price", 30.0), target_cat, True)
    saved_diff = max(0.0, round(cur_co2 - alt_co2, 2))
    pct_drop = int(round((saved_diff / cur_co2) * 100)) if cur_co2 > 0 else 0
    swaps = ETHICAL_ALTERNATIVES.get(cat, [{"brand": "Local Circular Hub", "saving": "70%"}])
    return {
        "index": idx,
        "item": item,
        "target_cat": target_cat,
        "brand_suggestion": swaps[0]["brand"],
        "cur_co2": cur_co2,
        "alt_co2": alt_co2,
        "saved_diff": saved_diff,
        "pct_drop": pct_drop,
    }

def build_eco_scorecard_markdown(user_name, eco_rank, budget, spend_tot, co2_tot, saved_tot, badges, streak, top_cat):
    unlocked_names = [b["name"] for b in badges if b["unlocked"]]
    return f"""# ShopImpact Personal Conscious Shopping Scorecard

- **Shopper:** {user_name} ({eco_rank})
- **Report Generated:** {date.today()}
- **Monthly Carbon Target:** {budget} kg CO2e

## Summary Metrics
- **Total Logged Spend:** ${spend_tot:,.2f}
- **Total Carbon Footprint:** {co2_tot:.1f} kg CO2e
- **Carbon Avoided vs Normal Average:** {saved_tot:.1f} kg CO2e (~{round(saved_tot / 1.75, 1)} tree-months saved)
- **Current Green Choice Streak:** {streak}x in a row
- **Highest Impact Category:** {top_cat}

## Unlocked Achievement Badges ({len(unlocked_names)} of {len(badges)})
{chr(10).join('- ' + n for n in unlocked_names) if unlocked_names else '- Ready for your first milestone!'}

*Generated locally by ShopImpact Conscious Shopping Companion (IDAI 102).*
"""

def evaluate_feedback_for_item(mascot_str, item_name, live_co2, is_ethical):
    """Computes mascot mood, reaction message, and Turtle art trigger for a logged purchase."""
    if is_ethical and live_co2 <= 3.0:
        mood, art = "ecstatic", "badge"
    elif is_ethical or live_co2 <= 10.0:
        mood = "happy"
        art = "leaf" if is_ethical else "footprint"
    elif live_co2 <= 25.0:
        mood, art = "mindful", None
    elif live_co2 <= 50.0:
        mood, art = "worried", None
    else:
        mood, art = "alarmed", None
    msg = get_mascot_reaction(mascot_str, item_name, live_co2, mood, is_ethical)
    return mood, msg, art

def add_purchase(purchases_list, item_name, product_type, brand, price, purchase_date, is_ethical, mascot_str):
    """Appends a new purchase dict to the purchases Python list and returns feedback state."""
    live_co2 = calculate_carbon(float(price), product_type, bool(is_ethical))
    record = {
        "id": len(purchases_list) + 1,
        "item": item_name.strip(),
        "category": product_type,
        "brand": brand.strip() if brand and brand.strip() else "Unspecified",
        "price": round(float(price), 2),
        "carbon_kg": float(live_co2),
        "date": str(purchase_date),
        "is_ethical": bool(is_ethical),
    }
    purchases_list.append(record)
    mood, msg, art = evaluate_feedback_for_item(mascot_str, record["item"], live_co2, is_ethical)
    return record, mood, msg, art

# ------------------------------------------------------------------------------
# SESSION STATE INITIALIZATION (Purchases stored in a Python list in session)
# ------------------------------------------------------------------------------

if "dark_theme" not in st.session_state:
    st.session_state.dark_theme = False if st.query_params.get("theme") == "light" else True
if "onboarded" not in st.session_state:
    st.session_state.onboarded = st.query_params.get("onboarded") in ["true", "1"]

if "user_name" not in st.session_state: st.session_state.user_name = "Parth Gajera"
if "user_mascot" not in st.session_state: st.session_state.user_mascot = "Pip the Forest Fox 🦊"
if "carbon_budget" not in st.session_state: st.session_state.carbon_budget = 150
if "recent_art" not in st.session_state: st.session_state.recent_art = None
if "mascot_mood" not in st.session_state: st.session_state.mascot_mood = "mindful"
if "mascot_message" not in st.session_state:
    st.session_state.mascot_message = "Ready when you are! Log a purchase below to see your live CO₂ footprint and earn Turtle art."
if "nav_view" not in st.session_state:
    st.session_state.nav_view = "🏆 Wall of Badges" if st.query_params.get("view") == "badges" else "📊 Dashboard"
if "last_logged" not in st.session_state: st.session_state.last_logged = None

if "purchases" not in st.session_state:
    # Core Python list storing every purchase dictionary (product type, price, brand, date)
    st.session_state.purchases = []
    demo_mode = st.query_params.get("demo")
    if demo_mode in ["true", "1"]:
        sample_items = [
            ("Vintage Denim Jacket", "Second-Hand / Thrift", "Community Thrift", 35.0, "2026-11-12", True),
            ("Organic CSA Harvest Box", "Local / Organic Food", "Local Farmers Market", 42.0, "2026-11-12", True),
            ("Certified Renewed ThinkPad", "Refurbished Tech", "Back Market Refurbished", 280.0, "2026-11-12", True),
        ]
        for args in sample_items:
            rec, mood, msg, art = add_purchase(st.session_state.purchases, *args, st.session_state.user_mascot)
            st.session_state.last_logged = rec
        st.session_state.mascot_mood, st.session_state.mascot_message, st.session_state.recent_art = "ecstatic", "CLEVER THRIFT MASTER! Pip put on gold sunglasses! 'Vintage Denim Jacket' is a circular gem!", "badge"
    elif demo_mode == "test12":
        # 12 sample purchases covering expensive, cheap, eco, and non-eco items
        test_12_items = [
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
        ]
        for args in test_12_items:
            rec, mood, msg, art = add_purchase(st.session_state.purchases, *args, st.session_state.user_mascot)
            st.session_state.last_logged = rec
            st.session_state.mascot_mood, st.session_state.mascot_message, st.session_state.recent_art = mood, msg, art

if "confirm_reset" not in st.session_state: st.session_state.confirm_reset = False

# ------------------------------------------------------------------------------
# DUAL-THEME BOTANICAL GRADIENT CSS ENGINE (Dark Emerald & Creamy Light Mode)
# ------------------------------------------------------------------------------

if st.session_state.dark_theme:
    render_html("""
    <style>
    .stApp {
        background: radial-gradient(circle at 18% 10%, #143322 0%, #09130d 52%, #050a07 100%) !important;
        color: #f8fafc !important;
    }
    [data-testid="stHeader"] {
        background: rgba(8, 20, 13, 0.85) !important;
        backdrop-filter: blur(8px);
        border-bottom: 1px solid rgba(52, 211, 153, 0.16) !important;
    }
    h1, h2, h3, h4, h5, p, span, label { color: #f1f5f9 !important; }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d2217 0%, #07100b 100%) !important;
        border-right: 1.5px solid rgba(52, 211, 153, 0.25) !important;
    }
    [data-testid="stSidebar"] * { color: #f1f5f9 !important; }
    [data-testid="stSidebarCollapseButton"] button, [data-testid="collapsedControl"] button {
        background: linear-gradient(135deg, #133623, #0b2216) !important;
        border: 1.5px solid #34d399 !important;
        border-radius: 10px !important;
        color: #34d399 !important;
        box-shadow: 0 2px 10px rgba(52, 211, 153, 0.22) !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(155deg, rgba(19, 54, 35, 0.56), rgba(9, 24, 15, 0.72)) !important;
        border: 1.5px solid rgba(52, 211, 153, 0.28) !important;
        border-radius: 16px !important;
        box-shadow: 0 6px 22px rgba(0, 0, 0, 0.24) !important;
    }
    [data-testid="stBaseButton-primary"], button[kind="primary"] {
        background: linear-gradient(135deg, #059669, #10b981) !important;
        border: 1.5px solid #34d399 !important;
        border-radius: 10px !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 14px rgba(16, 185, 129, 0.28) !important;
    }
    [data-testid="stBaseButton-primary"] *, button[kind="primary"] * { color: #ffffff !important; }
    [data-testid="stBaseButton-secondary"], button[kind="secondary"],
    [data-testid="stDownloadButton"] button, [data-testid="stFormSubmitButton"] button {
        background: linear-gradient(135deg, #133120, #0c2015) !important;
        border: 1.5px solid rgba(52, 211, 153, 0.36) !important;
        border-radius: 10px !important;
        color: #ecfdf5 !important;
        font-weight: 600 !important;
    }
    [data-testid="stBaseButton-secondary"]:hover, button[kind="secondary"]:hover,
    [data-testid="stDownloadButton"] button:hover, [data-testid="stFormSubmitButton"] button:hover {
        background: linear-gradient(135deg, #19422b, #102b1c) !important;
        border-color: #34d399 !important;
    }
    [data-testid="stExpander"] {
        background: linear-gradient(145deg, rgba(17, 46, 30, 0.65), rgba(10, 26, 17, 0.78)) !important;
        border: 1.5px solid rgba(52, 211, 153, 0.26) !important;
        border-radius: 14px !important;
    }
    .top-banner {
        background: linear-gradient(135deg, rgba(19, 54, 35, 0.92), rgba(10, 29, 19, 0.96));
        border: 1.5px solid rgba(52, 211, 153, 0.35);
        border-radius: 16px;
        padding: 0.9rem 1.3rem;
        margin-bottom: 1.1rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 6px 24px rgba(0, 0, 0, 0.28);
    }
    .hero-card {
        background: linear-gradient(145deg, rgba(20, 56, 37, 0.92), rgba(9, 25, 16, 0.96));
        border: 1.5px solid rgba(52, 211, 153, 0.34);
        border-radius: 18px;
        padding: 1.1rem 1.2rem;
        min-height: 365px;
        box-shadow: 0 8px 26px rgba(0, 0, 0, 0.32);
        margin-bottom: 0.6rem;
    }
    .card-kicker {
        display: inline-block;
        white-space: nowrap;
        font-size: 0.68rem;
        font-weight: 800;
        letter-spacing: 0.7px;
        text-transform: uppercase;
        color: #34d399 !important;
        background: rgba(6, 78, 59, 0.78);
        border: 1px solid rgba(52, 211, 153, 0.42);
        padding: 0.18rem 0.56rem;
        border-radius: 99px;
    }
    .streak-pill {
        display: inline-block;
        white-space: nowrap;
        font-size: 0.74rem;
        font-weight: 800;
        color: #fef08a !important;
        background: rgba(146, 64, 14, 0.45);
        border: 1px solid rgba(251, 191, 36, 0.45);
        padding: 0.2rem 0.65rem;
        border-radius: 99px;
    }
    .speech-cloud {
        position: relative;
        background: linear-gradient(145deg, #163d28, #102a1c);
        border: 1.5px solid #34d399;
        border-radius: 16px;
        padding: 0.95rem 1.1rem;
        color: #f8fafc !important;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.28);
        flex: 1;
    }
    .speech-cloud::before {
        content: "";
        position: absolute;
        left: -10px;
        top: 28px;
        border-width: 9px 10px 9px 0;
        border-style: solid;
        border-color: transparent #34d399 transparent transparent;
    }
    .speech-cloud::after {
        content: "";
        position: absolute;
        left: -8px;
        top: 29px;
        border-width: 8px 9px 8px 0;
        border-style: solid;
        border-color: transparent #163d28 transparent transparent;
    }
    .prog-track {
        width: 100%;
        height: 9px;
        background: rgba(15, 23, 42, 0.75);
        border-radius: 99px;
        overflow: hidden;
        border: 1px solid rgba(52, 211, 153, 0.28);
        margin-top: 0.35rem;
    }
    .prog-fill {
        height: 100%;
        background: linear-gradient(90deg, #10b981, #34d399, #fde047);
        border-radius: 99px;
        transition: width 0.4s ease;
    }
    .art-slot-on {
        background: rgba(6, 78, 59, 0.85);
        border: 1px solid #34d399;
        color: #ecfdf5 !important;
        border-radius: 10px;
        padding: 0.24rem 0.25rem;
        font-size: 0.69rem;
        font-weight: 700;
        text-align: center;
        white-space: nowrap;
    }
    .art-slot-off {
        background: rgba(15, 23, 42, 0.55);
        border: 1px dashed #475569;
        color: #94a3b8 !important;
        border-radius: 10px;
        padding: 0.24rem 0.25rem;
        font-size: 0.69rem;
        font-weight: 600;
        text-align: center;
        white-space: nowrap;
        opacity: 0.65;
    }
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, rgba(20, 56, 37, 0.88), rgba(10, 28, 18, 0.94)) !important;
        border: 1.5px solid rgba(52, 211, 153, 0.28) !important;
        border-radius: 14px !important;
        padding: 0.9rem 1rem !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.24) !important;
    }
    .tip-box { background: linear-gradient(135deg, #143723, #0f291a) !important; border: 1.5px solid #34d399 !important; border-radius: 14px; padding: 1.05rem 1.25rem; color: #f8fafc !important; margin: 0.8rem 0; box-shadow: 0 4px 16px rgba(0,0,0,0.3); }
    .swap-card { background: linear-gradient(145deg, #173a26, #0f2519) !important; border: 1.5px solid rgba(52, 211, 153, 0.32) !important; border-radius: 14px; padding: 1rem; color: #f8fafc !important; margin-bottom: 0.5rem; }
    .badge-on { background: linear-gradient(135deg, #065f46, #047857) !important; border: 2px solid #34d399 !important; border-radius: 14px; padding: 1rem; color: #ffffff !important; margin-bottom: 0.8rem; box-shadow: 0 4px 16px rgba(52, 211, 153, 0.22); }
    .badge-off { background: linear-gradient(145deg, #1a241e, #111814) !important; border: 2px dashed #475569 !important; border-radius: 14px; padding: 1rem; color: #94a3b8 !important; filter: grayscale(100%); opacity: 0.65; margin-bottom: 0.8rem; }
    .avatar-card { display: flex; flex-direction: column; align-items: center; justify-content: center; margin-bottom: 1rem; text-align: center; }
    .avatar-circle { width: 92px; height: 92px; border-radius: 50%; border: 3px solid #34d399; overflow: hidden; background: radial-gradient(circle, #17452c, #0a2015); display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 18px rgba(52, 211, 153, 0.35); margin: 0 auto; }
    .rank-pill { font-size: 0.8rem; background: #064e3b; color: #34d399 !important; border: 1px solid #10b981; padding: 0.22rem 0.7rem; border-radius: 99px; font-weight: 700; display: inline-block; margin-top: 0.35rem; }
    .vessel-chip { background: linear-gradient(145deg, #173a26, #0f2619); border: 1.5px solid rgba(52, 211, 153, 0.35); border-radius: 14px; padding: 0.75rem; text-align: center; margin-bottom: 0.5rem; min-height: 114px; display: flex; flex-direction: column; justify-content: center; transition: transform 0.18s ease, border-color 0.18s ease; box-shadow: 0 4px 14px rgba(0, 0, 0, 0.22); }
    .vessel-chip:hover { border-color: #34d399; transform: translateY(-3px); }
    .sim-card { background: linear-gradient(145deg, #153523, #0d2116); border: 1.5px solid rgba(52, 211, 153, 0.32); border-radius: 14px; padding: 1.15rem; margin: 0.6rem 0 1rem 0; box-shadow: 0 4px 18px rgba(0,0,0,0.25); }
    .optimizer-box { background: linear-gradient(135deg, rgba(20, 62, 40, 0.92), rgba(14, 42, 28, 0.95)); border: 1.5px solid #34d399; border-radius: 16px; padding: 1.1rem 1.3rem; margin: 0.8rem 0; box-shadow: 0 6px 22px rgba(0,0,0,0.28); }
    .mission-strip { background: linear-gradient(90deg, rgba(19, 54, 35, 0.85), rgba(13, 38, 25, 0.9)); border: 1px solid rgba(52, 211, 153, 0.32); border-radius: 12px; padding: 0.6rem 1rem; margin: 0.5rem 0 1rem 0; }
    </style>
    """)
else:
    render_html("""
    <style>
    .stApp {
        background: radial-gradient(circle at 82% 0%, #FDF9EE 0%, #F4ECDA 58%, #EAE0C8 100%) !important;
        color: #163323 !important;
    }
    [data-testid="stHeader"] {
        background: rgba(253, 249, 238, 0.88) !important;
        backdrop-filter: blur(8px);
        border-bottom: 1px solid #C8D6C0 !important;
    }
    [data-testid="stHeader"] * { color: #163323 !important; }
    h1, h2, h3, h4, h5, p, span, label { color: #163323 !important; }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #EFE5CF 0%, #E3D6BA 100%) !important;
        border-right: 1.5px solid #C5D1B8 !important;
    }
    [data-testid="stSidebar"] * { color: #163323 !important; }
    [data-testid="stSidebarCollapseButton"] button, [data-testid="collapsedControl"] button {
        background: linear-gradient(135deg, #FFFDF7, #E9F3E4) !important;
        border: 1.5px solid #2D6A4F !important;
        border-radius: 10px !important;
        color: #1B4332 !important;
        box-shadow: 0 2px 8px rgba(45, 106, 79, 0.16) !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(155deg, #FFFDF7 0%, #EBF4E5 100%) !important;
        border: 1.5px solid #9AC0A0 !important;
        border-radius: 16px !important;
        box-shadow: 0 6px 20px rgba(45, 106, 79, 0.08) !important;
    }
    [data-testid="stBaseButton-primary"], button[kind="primary"] {
        background: linear-gradient(135deg, #1B4332, #2D6A4F) !important;
        border: 1.5px solid #1B4332 !important;
        border-radius: 10px !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 12px rgba(27, 67, 50, 0.22) !important;
    }
    [data-testid="stBaseButton-primary"] *, button[kind="primary"] *,
    [data-testid="stBaseButton-primary"] p, button[kind="primary"] p {
        color: #ffffff !important;
    }
    [data-testid="stBaseButton-secondary"], button[kind="secondary"],
    [data-testid="stDownloadButton"] button, [data-testid="stFormSubmitButton"] button {
        background: linear-gradient(135deg, #FFFDF8, #E3EFE0) !important;
        border: 1.5px solid #40916C !important;
        border-radius: 10px !important;
        color: #143D2B !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 8px rgba(45, 106, 79, 0.09) !important;
    }
    [data-testid="stBaseButton-secondary"] *, button[kind="secondary"] *,
    [data-testid="stDownloadButton"] button *, [data-testid="stFormSubmitButton"] button * {
        color: #143D2B !important;
    }
    [data-testid="stBaseButton-secondary"]:hover, button[kind="secondary"]:hover,
    [data-testid="stDownloadButton"] button:hover, [data-testid="stFormSubmitButton"] button:hover {
        background: linear-gradient(135deg, #D5EAD8, #C2E2C7) !important;
        border-color: #1B4332 !important;
    }
    [data-testid="stExpander"] {
        background: linear-gradient(145deg, #FAF5E8, #EDF4E6) !important;
        border: 1.5px solid #A4C5A8 !important;
        border-radius: 14px !important;
    }
    .stTextInput input, .stNumberInput input, .stDateInput input,
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #FFFDF8 !important;
        color: #163323 !important;
        border-color: #9DC0A1 !important;
    }
    .top-banner {
        background: linear-gradient(135deg, #FFFDF8 0%, #EDF5E8 100%);
        border: 1.5px solid #9DC1A2;
        border-radius: 16px;
        padding: 0.9rem 1.3rem;
        margin-bottom: 1.1rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 16px rgba(45, 106, 79, 0.08);
    }
    .hero-card {
        background: linear-gradient(145deg, #FFFDF7 0%, #EDF5E7 100%);
        border: 1.5px solid #9AC0A0;
        border-radius: 18px;
        padding: 1.1rem 1.2rem;
        min-height: 365px;
        box-shadow: 0 6px 20px rgba(45, 106, 79, 0.09);
        margin-bottom: 0.6rem;
    }
    .card-kicker {
        display: inline-block;
        white-space: nowrap;
        font-size: 0.68rem;
        font-weight: 800;
        letter-spacing: 0.7px;
        text-transform: uppercase;
        color: #1B4332 !important;
        background: #DCEEE0;
        border: 1px solid #74C69D;
        padding: 0.18rem 0.56rem;
        border-radius: 99px;
    }
    .streak-pill {
        display: inline-block;
        white-space: nowrap;
        font-size: 0.74rem;
        font-weight: 800;
        color: #92400E !important;
        background: #FEF3C7;
        border: 1px solid #F59E0B;
        padding: 0.2rem 0.65rem;
        border-radius: 99px;
    }
    .speech-cloud {
        position: relative;
        background: linear-gradient(145deg, #FFFDF9, #EAF5E4);
        border: 1.5px solid #52B788;
        border-radius: 16px;
        padding: 0.95rem 1.1rem;
        color: #163323 !important;
        box-shadow: 0 4px 14px rgba(45, 106, 79, 0.08);
        flex: 1;
    }
    .speech-cloud::before {
        content: "";
        position: absolute;
        left: -10px;
        top: 28px;
        border-width: 9px 10px 9px 0;
        border-style: solid;
        border-color: transparent #52B788 transparent transparent;
    }
    .speech-cloud::after {
        content: "";
        position: absolute;
        left: -8px;
        top: 29px;
        border-width: 8px 9px 8px 0;
        border-style: solid;
        border-color: transparent #FFFDF9 transparent transparent;
    }
    .prog-track {
        width: 100%;
        height: 9px;
        background: #E2DAC4;
        border-radius: 99px;
        overflow: hidden;
        border: 1px solid #B6CEB7;
        margin-top: 0.35rem;
    }
    .prog-fill {
        height: 100%;
        background: linear-gradient(90deg, #2D6A4F, #40916C, #52B788);
        border-radius: 99px;
        transition: width 0.4s ease;
    }
    .art-slot-on {
        background: #D8EFE0;
        border: 1px solid #2D6A4F;
        color: #143D2B !important;
        border-radius: 10px;
        padding: 0.24rem 0.25rem;
        font-size: 0.69rem;
        font-weight: 700;
        text-align: center;
        white-space: nowrap;
    }
    .art-slot-off {
        background: #EFE9D8;
        border: 1px dashed #B5AA92;
        color: #6B7263 !important;
        border-radius: 10px;
        padding: 0.24rem 0.25rem;
        font-size: 0.69rem;
        font-weight: 600;
        text-align: center;
        white-space: nowrap;
        opacity: 0.78;
    }
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #FFFDF7, #EDF5E7) !important;
        border: 1.5px solid #A4C6A8 !important;
        border-radius: 14px !important;
        padding: 0.9rem 1rem !important;
        box-shadow: 0 3px 12px rgba(45, 106, 79, 0.08) !important;
    }
    [data-testid="stMetricValue"] * { color: #143D2B !important; }
    [data-testid="stMetricLabel"] * { color: #365944 !important; font-weight: 700 !important; }
    [data-testid="stMetricDelta"] {
        background: #DFF0E3 !important;
        border: 1px solid #74C69D !important;
        border-radius: 99px !important;
        padding: 0.14rem 0.55rem !important;
        width: fit-content !important;
    }
    [data-testid="stMetricDelta"] div, [data-testid="stMetricDelta"] span {
        color: #14532D !important;
    }
    [data-testid="stMetricDelta"] svg {
        color: #14532D !important;
    }
    .tip-box { background: linear-gradient(135deg, #FFFDF8, #E7F3E4) !important; border: 1.5px solid #74C69D !important; border-radius: 14px; padding: 1.05rem 1.25rem; color: #143D2B !important; margin: 0.8rem 0; box-shadow: 0 2px 10px rgba(45, 106, 79, 0.07); }
    .swap-card { background: linear-gradient(145deg, #FFFDF7, #EFF6EB) !important; border: 1.5px solid #A6C8AA !important; border-radius: 14px; padding: 1rem; color: #163323 !important; box-shadow: 0 2px 10px rgba(45, 106, 79, 0.06); margin-bottom: 0.5rem; }
    .badge-on { background: linear-gradient(135deg, #1B4332, #2D6A4F) !important; border: 2px solid #52B788 !important; border-radius: 14px; padding: 1rem; color: #ffffff !important; box-shadow: 0 4px 14px rgba(45,106,79,0.2); margin-bottom: 0.8rem; }
    .badge-on, .badge-on * { color: #ffffff !important; }
    .badge-off { background: linear-gradient(145deg, #F6F0E1, #EBE2CD) !important; border: 2px dashed #BFB59D !important; border-radius: 14px; padding: 1rem; color: #64748b !important; filter: grayscale(85%); opacity: 0.72; margin-bottom: 0.8rem; }
    .avatar-card { display: flex; flex-direction: column; align-items: center; justify-content: center; margin-bottom: 1rem; text-align: center; }
    .avatar-circle { width: 92px; height: 92px; border-radius: 50%; border: 3px solid #2D6A4F; overflow: hidden; background: radial-gradient(circle, #FFFDF8, #D8EFE0); display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 14px rgba(45, 106, 79, 0.22); margin: 0 auto; }
    .rank-pill { font-size: 0.8rem; background: #D8EFE0; color: #1B4332 !important; border: 1px solid #40916C; padding: 0.22rem 0.7rem; border-radius: 99px; font-weight: 700; display: inline-block; margin-top: 0.35rem; }
    .vessel-chip { background: linear-gradient(145deg, #FFFDF7, #EBF4E6); border: 1.5px solid #A4C5A8; border-radius: 14px; padding: 0.75rem; text-align: center; margin-bottom: 0.5rem; min-height: 114px; display: flex; flex-direction: column; justify-content: center; box-shadow: 0 3px 10px rgba(45, 106, 79, 0.07); transition: transform 0.18s ease, border-color 0.18s ease; }
    .vessel-chip:hover { border-color: #2D6A4F; transform: translateY(-3px); }
    .sim-card { background: linear-gradient(145deg, #FFFDF7, #EDF5E7); border: 1.5px solid #A4C5A8; border-radius: 14px; padding: 1.15rem; margin: 0.6rem 0 1rem 0; box-shadow: 0 3px 10px rgba(45, 106, 79, 0.06); }
    .optimizer-box { background: linear-gradient(135deg, #FFFDF7, #E2F1DE); border: 1.5px solid #40916C; border-radius: 16px; padding: 1.1rem 1.3rem; margin: 0.8rem 0; box-shadow: 0 4px 16px rgba(45, 106, 79, 0.1); }
    .mission-strip { background: linear-gradient(90deg, #FFFDF7, #E7F2E2); border: 1px solid #9CC0A1; border-radius: 12px; padding: 0.6rem 1rem; margin: 0.5rem 0 1rem 0; }
    </style>
    """)

# ------------------------------------------------------------------------------
# SCREEN 1: WELCOME & ONBOARDING
# ------------------------------------------------------------------------------

if not st.session_state.onboarded:
    title_col = "#34d399" if st.session_state.dark_theme else "#1B4332"
    sub_col = "#94a3b8" if st.session_state.dark_theme else "#4A6355"
    card_bg = "linear-gradient(145deg, #153724, #0d2216)" if st.session_state.dark_theme else "linear-gradient(145deg, #FFFDF7, #EAF4E4)"
    card_bd = "#34d399" if st.session_state.dark_theme else "#52B788"

    render_html(f"<h1 style='text-align: center; color: {title_col}; margin-top: 1rem; margin-bottom: 0;'>🌱 Meet ShopImpact</h1><p style='text-align: center; color: {sub_col}; font-size: 1.12rem; margin-bottom: 2rem;'>Your playful, conscious shopping companion.</p>")

    c1, c2 = st.columns([1.1, 0.9], gap="large")
    with c1:
        st.subheader("Set Your Goals & Avatar")
        u_name = st.text_input("Your Shopper Name (Required):", value=st.session_state.user_name)
        m_choice = st.selectbox("Choose Your Eco Mascot Spirit (Required):", options=list(ECO_MASCOTS.keys()))
        b_choice = st.slider("Monthly Sustainable Carbon Target (kg CO₂e):", min_value=50, max_value=300, value=st.session_state.carbon_budget, step=10, help="Standard conscious shopper monthly target is 100 to 150 kg CO₂e.")

        st.caption(f"✨ **{m_choice.split()[0]}**: {ECO_MASCOTS[m_choice]}")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 Enter ShopImpact Dashboard →", type="primary", width="stretch"):
            st.session_state.user_name = u_name.strip() if u_name.strip() else "Shopper"
            st.session_state.user_mascot = m_choice
            st.session_state.carbon_budget = b_choice
            st.session_state.onboarded = True
            c_name = m_choice.split()[0]
            st.session_state.mascot_message = f"Welcome {st.session_state.user_name}! I am {c_name}. Log a purchase below to track CO₂ live and unlock Turtle artwork!"
            st.rerun()

    with c2:
        render_html(render_animated_avatar_svg(m_choice, "happy", 210, 210))
        render_html(f"""
        <div style="background: {card_bg}; border: 1.5px solid {card_bd}; border-radius: 16px; padding: 1.1rem 1.25rem; margin-top: 0.6rem;">
            <strong style="color: {title_col};">What you'll experience inside:</strong>
            <ul style="margin: 0.5rem 0 0 1.2rem; padding: 0; line-height: 1.65;">
                <li>🌍 <strong>Living Biosphere Globe:</strong> 60 FPS animated terrarium reflecting your monthly CO₂ health</li>
                <li>⚡ <strong>6 Quick-Log Chips & Streak:</strong> instant logging with live eco streaks and missions</li>
                <li>🔄 <strong>What-If Green Switch:</strong> swap high-CO₂ items in 1 click to see emissions drop</li>
                <li>🐢 <strong>Turtle Art Collector Vault:</strong> earn layered Eco Leaf, Step & Gold Rosette art</li>
                <li>🏆 <strong>Living Wall of Badges:</strong> watch grayscale achievements ignite into color</li>
            </ul>
        </div>
        """)

# ------------------------------------------------------------------------------
# SCREEN 2: MAIN COMMAND STUDIO & WALL OF BADGES
# ------------------------------------------------------------------------------

else:
    badges, spend_tot, co2_tot, avg_int, saved_tot, eth_cnt = evaluate_badges(st.session_state.purchases)
    unlocked_num = sum(1 for b in badges if b["unlocked"])
    cur_streak, best_streak = compute_eco_streak(st.session_state.purchases)
    earned_arts = get_collected_arts(st.session_state.purchases)
    nudge_text, nudge_pct = get_next_badge_nudge(badges)
    accent_hex = "#34d399" if st.session_state.dark_theme else "#1B4332"
    muted_hex = "#94a3b8" if st.session_state.dark_theme else "#4B6356"

    # Sidebar Profile Card, Live Progress Summary, Navigation & Theme Switch
    with st.sidebar:
        rank_title = get_user_eco_rank(st.session_state.purchases)
        avatar_svg_mini = render_animated_avatar_svg(st.session_state.user_mascot, st.session_state.mascot_mood, 82, 82)
        
        render_html(f"""
        <div class="avatar-card">
            <div class="avatar-circle">
                {avatar_svg_mini}
            </div>
            <div style="font-size: 1.2rem; font-weight: 800; margin-top: 0.55rem;">{html.escape(st.session_state.user_name)}</div>
            <div class="rank-pill">{rank_title}</div>
            <div style="font-size: 0.8rem; margin-top: 0.35rem; opacity: 0.85;">{st.session_state.user_mascot}</div>
            <div style="font-size: 0.78rem; opacity: 0.78;">Target: {st.session_state.carbon_budget} kg CO₂e/mo</div>
        </div>
        """)

        # Quick Progress Snapshot directly in Sidebar
        render_html(f"""
        <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(52, 211, 153, 0.3); border-radius: 12px; padding: 0.65rem 0.8rem; margin-bottom: 0.8rem; font-size: 0.78rem;">
            <div style="display: flex; justify-content: space-between; font-weight: 700;">
                <span>🏆 Badges: {unlocked_num}/{len(badges)}</span>
                <span>🔥 Streak: {cur_streak}x</span>
            </div>
            <div class="prog-track"><div class="prog-fill" style="width: {int((unlocked_num/len(badges))*100)}%;"></div></div>
            <div style="margin-top: 0.35rem; opacity: 0.85;">🎨 Turtle Art Vault: {len(earned_arts)}/3 earned</div>
        </div>
        """)

        if st.button("⚙️ Edit Profile / Avatar", width="stretch"):
            st.session_state.onboarded = False
            st.rerun()

        st.markdown("---")
        st.session_state.nav_view = st.radio(
            "Navigation:",
            ["📊 Dashboard", "🏆 Wall of Badges"],
            index=1 if st.session_state.nav_view == "🏆 Wall of Badges" else 0,
        )

        dark_toggle = st.toggle("🌙 Obsidian Emerald Dark Mode", value=st.session_state.dark_theme)
        if dark_toggle != st.session_state.dark_theme:
            st.session_state.dark_theme = dark_toggle
            st.rerun()

        st.markdown("---")
        st.caption(f"💡 *{random.choice(ECO_TIPS)}*")

        # Guarded Session Reset Modal
        if not st.session_state.confirm_reset:
            if st.button("🗑️ Reset / Clear All Purchases", width="stretch"):
                st.session_state.confirm_reset = True
                st.rerun()
        else:
            st.warning("⚠️ Clear all logged purchases?")
            r_c1, r_c2 = st.columns(2)
            if r_c1.button("Yes, Clear", type="primary", width="stretch"):
                st.session_state.purchases = []
                st.session_state.last_logged = None
                st.session_state.recent_art = None
                st.session_state.mascot_mood = "mindful"
                st.session_state.confirm_reset = False
                c_name = st.session_state.user_mascot.split()[0]
                st.session_state.mascot_message = f"All purchases cleared! {c_name} is ready for your fresh eco-conscious start."
                st.rerun()
            if r_c2.button("Cancel", width="stretch"):
                st.session_state.confirm_reset = False
                st.rerun()

    # --------------------------------------------------------------------------
    # TOP COMMAND HEADER & SYNCED QUICK SWITCHER (Accessible even if sidebar closed)
    # --------------------------------------------------------------------------
    h_left, h_right = st.columns([1.95, 1.25])
    with h_left:
        render_html(f"""
        <div class="top-banner">
            <div>
                <div style="font-size: 1.25rem; font-weight: 800; color: {accent_hex};">🌱 ShopImpact Studio</div>
                <div style="font-size: 0.82rem; color: {muted_hex};">Welcome back, <strong>{html.escape(st.session_state.user_name)}</strong> • Saved <strong>{saved_tot:.1f} kg CO₂e</strong> vs retail average</div>
            </div>
            <div style="text-align: right;">
                <span class="streak-pill">🔥 {cur_streak}x Eco Streak</span>
            </div>
        </div>
        """)
    with h_right:
        b1_c, b2_c = st.columns(2)
        with b1_c:
            if st.button("📊 Dashboard", type="primary" if st.session_state.nav_view == "📊 Dashboard" else "secondary", width="stretch", key="top_nav_dash"):
                st.session_state.nav_view = "📊 Dashboard"
                st.rerun()
        with b2_c:
            if st.button(f"🏆 Badges ({unlocked_num}/{len(badges)})", type="primary" if st.session_state.nav_view == "🏆 Wall of Badges" else "secondary", width="stretch", key="top_nav_badges"):
                st.session_state.nav_view = "🏆 Wall of Badges"
                st.rerun()

    # --------------------------------------------------------------------------
    # VIEW: 📊 DASHBOARD
    # --------------------------------------------------------------------------
    if st.session_state.nav_view == "📊 Dashboard":
        c_name = st.session_state.user_mascot.split()[0]
        msg_esc = html.escape(st.session_state.mascot_message)
        b_lim = max(st.session_state.carbon_budget, 1)
        used_pct = (co2_tot / b_lim) * 100.0
        capped_pct = min(100, int(round(used_pct)))

        # SYMMETRICAL 3-PANEL HERO STUDIO: Biosphere | Companion & Speech Cloud | Turtle Collector Vault
        col_bio, col_mid, col_art = st.columns([1.0, 1.34, 1.06], gap="medium")

        with col_bio:
            with st.container(border=True):
                render_html(f"""
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.2rem;">
                    <span class="card-kicker">🌍 Living Biosphere</span>
                    <span style="font-size:0.76rem; font-weight:700; white-space:nowrap; color:{accent_hex};">{used_pct:.0f}% used</span>
                </div>
                """)
                render_html(render_animated_biosphere_svg(used_pct, co2_tot, b_lim, width=195, height=255))
                render_html(f"""
                <div class="prog-track" style="margin-top:0.2rem;">
                    <div class="prog-fill" style="width:{capped_pct}%;"></div>
                </div>
                <div style="font-size:0.76rem; color:{muted_hex}; margin-top:0.35rem; text-align:center;">
                    {co2_tot:.1f} / {b_lim} kg monthly carbon budget
                </div>
                """)

        with col_mid:
            with st.container(border=True):
                mission_done = "✅ Daily Mission Complete!" if eth_cnt >= 1 else "🌱 Mission: Log 1 circular or organic item"
                render_html(f"""
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.4rem; margin-bottom:0.55rem;">
                    <span class="card-kicker">🐾 Companion Studio</span>
                    <span style="font-size:0.74rem; font-weight:700; color:{accent_hex};">{mission_done}</span>
                </div>
                <div style="display:flex; align-items:center; gap:0.85rem; margin:0.35rem 0 0.7rem 0;">
                    <div style="flex:0 0 125px; text-align:center;">
                        {render_animated_avatar_svg(st.session_state.user_mascot, st.session_state.mascot_mood, 125, 125)}
                    </div>
                    <div class="speech-cloud">
                        <div style="font-size:0.86rem; font-weight:800; color:{accent_hex}; margin-bottom:0.2rem;">{c_name} says:</div>
                        <div style="font-size:0.86rem; line-height:1.45;">"{msg_esc}"</div>
                    </div>
                </div>
                <div style="padding-top:0.45rem; border-top:1px solid rgba(52, 211, 153, 0.22);">
                    <div style="display:flex; justify-content:space-between; font-size:0.78rem; font-weight:700;">
                        <span>{nudge_text}</span>
                        <span style="color:{accent_hex};">{nudge_pct}%</span>
                    </div>
                    <div class="prog-track"><div class="prog-fill" style="width:{nudge_pct}%;"></div></div>
                    <div style="font-size:0.74rem; color:{muted_hex}; margin-top:0.35rem;">
                        ✨ Best Streak: <strong>{best_streak}x</strong> • Eco Rank: <strong>{rank_title}</strong>
                    </div>
                </div>
                """)

        with col_art:
            with st.container(border=True):
                render_html(f"""
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.35rem;">
                    <span class="card-kicker">🐢 Turtle Vault</span>
                    <span style="font-size:0.76rem; font-weight:700; white-space:nowrap; color:{accent_hex};">{len(earned_arts)}/3 earned</span>
                </div>
                """)
                active_art_key = st.session_state.recent_art if st.session_state.recent_art else "preview"
                art_img = draw_vector_art(active_art_key)
                art_titles = {
                    "preview": "Seed Canvas (Log Eco Pick to Unlock)",
                    "leaf": "Botanical Eco Leaf 🌿",
                    "footprint": "Earth Step Footprint 👣",
                    "badge": "Championship Eco Rosette ⭐",
                }
                c_img_pad1, c_img_mid, c_img_pad2 = st.columns([0.15, 1.0, 0.15])
                with c_img_mid:
                    st.image(art_img, width=155, caption=art_titles.get(active_art_key, "Turtle Vector Art"))

                s1, s2, s3 = st.columns(3)
                with s1:
                    cls = "art-slot-on" if "leaf" in earned_arts else "art-slot-off"
                    render_html(f"<div class='{cls}'>🌿 Leaf</div>")
                with s2:
                    cls = "art-slot-on" if "footprint" in earned_arts else "art-slot-off"
                    render_html(f"<div class='{cls}'>👣 Step</div>")
                with s3:
                    cls = "art-slot-on" if "badge" in earned_arts else "art-slot-off"
                    render_html(f"<div class='{cls}'>⭐ Medal</div>")

                if st.session_state.recent_art:
                    st.download_button(
                        "🎨 Save Turtle Art (.png)",
                        image_to_png_bytes(art_img),
                        f"shopimpact_{active_art_key}.png",
                        "image/png",
                        width="stretch",
                    )

        st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)

        # 4 PRIMARY KPI METRIC CARDS
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total Spend", f"${spend_tot:,.2f}", f"{len(st.session_state.purchases)} items recorded")
        k2.metric("Carbon Footprint", f"{co2_tot:.1f} kg", f"{avg_int:.2f} kg/$ intensity", delta_color="inverse")
        k3.metric("Carbon Avoided", f"{saved_tot:.1f} kg", "Vs standard 0.45 kg/$")
        trees_tot = round(co2_tot / 21.0, 1)
        k4.metric("Trees to Offset", f"{trees_tot} Trees", "21 kg CO₂/tree/year", delta_color="inverse")

        # MOTIVATIONAL REAL-WORLD STORY STRIP
        if st.session_state.purchases:
            eq_miles, eq_charges, eq_tree_mo = get_equivalency(saved_tot)
            eth_pct = int(round((eth_cnt / max(len(st.session_state.purchases), 1)) * 100))
            render_html(f"""
            <div class="mission-strip" style="display:flex; justify-content:space-between; flex-wrap:wrap; gap:0.6rem; font-size:0.84rem;">
                <span>🌱 <strong>Ethical Share:</strong> {eth_cnt}/{len(st.session_state.purchases)} buys ({eth_pct}% conscious)</span>
                <span>🚗 <strong>Avoided Impact:</strong> Equal to skipping <strong>{eq_miles:,}</strong> petrol car miles or powering <strong>{eq_charges:,}</strong> phone charges!</span>
            </div>
            """)

        # TACTILE QUICK-PURCHASE CHIPS (1-Click Instant Logging)
        st.subheader("⚡ Quick-Log Common Purchases")
        st.caption("One-click logging for everyday purchases. Instantly updates CO₂ math, mascot reaction, Biosphere glow, and streak.")

        chip_cols = st.columns(6)
        for i, qp in enumerate(QUICK_PURCHASES):
            chip_co2 = calculate_carbon(qp["price"], qp["category"], qp["is_ethical"])
            with chip_cols[i]:
                render_html(f"""
                <div class="vessel-chip">
                    <div style="font-size: 1.8rem;">{qp['icon']}</div>
                    <div style="font-weight: 800; font-size: 0.82rem; margin-top: 0.2rem;">{qp['name']}</div>
                    <div style="color: {accent_hex}; font-weight: 700; font-size: 0.78rem;">${qp['price']:.2f} • {chip_co2:.1f} kg</div>
                </div>
                """)
                if st.button(f"+ Add {qp['name'].split()[0]}", key=f"chip_btn_{i}", width="stretch"):
                    new_item, mood, msg, art = add_purchase(
                        st.session_state.purchases, qp["name"], qp["category"], qp["brand"],
                        qp["price"], date.today(), qp["is_ethical"], st.session_state.user_mascot
                    )
                    st.session_state.last_logged = new_item
                    st.session_state.mascot_mood, st.session_state.mascot_message, st.session_state.recent_art = mood, msg, art
                    if mood == "ecstatic":
                        st.balloons()
                    st.rerun()

        st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)

        # CUSTOM PURCHASE LOGGING FORM
        st.subheader("🛒 Log a Custom Planned Purchase")
        st.caption("Record custom purchases into your active Python list. Certified circular or ethical items receive an automatic 30% footprint discount.")

        with st.form("custom_log_form", clear_on_submit=True):
            f1, f2, f3 = st.columns([1.2, 1.2, 1.0])
            with f1:
                item_name = st.text_input("Item Description (Required)", placeholder="e.g. Organic Cotton Tee, USB-C Cable")
                cat_choice = st.selectbox("Product Category (Required)", options=list(CATEGORIES.keys()))
            with f2:
                brand_val = st.text_input("Brand or Vendor (Optional)", placeholder="e.g. Patagonia, Back Market, Local Store")
                price_val = st.number_input("Purchase Price ($) (Required)", min_value=1.0, max_value=5000.0, value=45.0, step=5.0)
            with f3:
                date_val = st.date_input("Purchase Date (Required)", value=date.today())
                is_eth = st.checkbox("🌱 Certified Circular / Thrift / Ethical", help="Applies a 30% footprint discount because reusing goods avoids virgin factory production.")

            c_info = CATEGORIES[cat_choice]
            tip_msg = random.choice(ECO_TIPS)
            render_html(f"""
            <div class="tip-box">
                <div style="display: flex; gap: 0.8rem; align-items: flex-start;">
                    <div style="font-size: 1.75rem; line-height: 1;">💡</div>
                    <div>
                        <div style="font-weight: 700; font-size: 0.94rem;">Category Insight ({c_info['tier']}):</div>
                        <div style="font-size: 0.87rem; margin-top: 0.15rem; opacity: 0.92;">{c_info['fact']}</div>
                        <div style="font-size: 0.83rem; margin-top: 0.35rem; color: {accent_hex}; font-weight: 600;">🌿 Eco Tip: {tip_msg}</div>
                    </div>
                </div>
            </div>
            """)

            if st.form_submit_button("🌿 Record Purchase in Active Ledger", width="stretch"):
                if not item_name.strip():
                    st.error("Please enter an item description before recording.")
                else:
                    new_rec, mood, msg, art = add_purchase(
                        st.session_state.purchases, item_name, cat_choice, brand_val,
                        price_val, date_val, is_eth, st.session_state.user_mascot
                    )
                    st.session_state.last_logged = new_rec
                    st.session_state.mascot_mood, st.session_state.mascot_message, st.session_state.recent_art = mood, msg, art
                    if mood in ["ecstatic", "happy"]:
                        st.balloons()
                    st.rerun()

        # INTERACTIVE CARBON IMPACT & TREE OFFSET SIMULATOR
        with st.expander("🌲 Interactive Carbon & Tree Offset Simulator", expanded=False):
            render_html(f"""
            <div class="sim-card">
                <h4 style="margin: 0; color: {accent_hex};">🧮 Pre-Purchase Footprint & Tree Offset Simulator</h4>
                <p style="font-size: 0.86rem; color: {muted_hex}; margin: 0.25rem 0 0 0;">Slide any spend level before buying to see car miles, phone charges, and tree sequestration months.</p>
            </div>
            """)
            sim_c1, sim_c2 = st.columns([1.2, 1.0])
            with sim_c1:
                sim_dollars = st.slider("Simulate Dollar Spend ($):", min_value=5.0, max_value=500.0, value=75.0, step=5.0)
                sim_cat_choice = st.selectbox("Simulate Category:", options=list(CATEGORIES.keys()), key="sim_cat")
                sim_is_eth = st.checkbox("Certified Circular / Thrift / Ethical?", value=True, key="sim_eth")
                sim_co2 = calculate_carbon(sim_dollars, sim_cat_choice, sim_is_eth)
                s_miles, s_charges, s_trees = get_equivalency(sim_co2)
            with sim_c2:
                sim_card_bg = "linear-gradient(145deg, #163a26, #0d2217)" if st.session_state.dark_theme else "linear-gradient(145deg, #FFFDF7, #E7F3E4)"
                sim_card_bd = "#34d399" if st.session_state.dark_theme else "#52B788"
                render_html(f"""
                <div style="background: {sim_card_bg}; border: 1.5px solid {sim_card_bd}; border-radius: 14px; padding: 1rem;">
                    <div style="font-size: 0.84rem; color: {muted_hex};">Estimated Carbon Footprint:</div>
                    <div style="font-size: 1.8rem; font-weight: 800; color: {accent_hex};">{sim_co2:.2f} kg CO₂e</div>
                    <div style="font-size: 0.82rem; margin-top: 0.45rem; line-height: 1.55;">
                        🚗 ~<strong>{s_miles:,}</strong> petrol car miles<br>
                        📱 ~<strong>{s_charges:,}</strong> smartphone recharges<br>
                        🌲 ~<strong>{s_trees}</strong> tree-months of sequestration
                    </div>
                </div>
                """)
                if st.button("➕ Add Simulated Item to Tracker", width="stretch"):
                    sim_item, mood, msg, art = add_purchase(
                        st.session_state.purchases, f"Simulated: {sim_cat_choice.split()[0]} (${sim_dollars:.0f})",
                        sim_cat_choice, "Simulation Tool", sim_dollars, date.today(), sim_is_eth, st.session_state.user_mascot
                    )
                    st.session_state.last_logged = sim_item
                    st.session_state.mascot_mood, st.session_state.mascot_message, st.session_state.recent_art = mood, msg, art
                    st.rerun()

        # CONTEXTUAL GREENER SWAPS (Appears reactively right after a purchase is logged)
        if st.session_state.last_logged:
            last = st.session_state.last_logged
            st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
            st.subheader(f"🌱 Greener Alternatives for '{last['item']}' ({last['category']})")
            
            sc1, sc2 = st.columns([1.0, 2.0], gap="medium")
            with sc1:
                render_html(render_animated_avatar_svg(st.session_state.user_mascot, "happy", 115, 115))
                st.caption(f"💡 **{c_name}'s Insight:** You logged **{last['carbon_kg']} kg CO₂e**. Adopting a circular swap cuts product emissions dramatically!")
                st.markdown(f"<div style='font-size: 0.81rem; font-style: italic; color: {muted_hex}; margin-top: 0.35rem;'>{random.choice(SUSTAINABILITY_QUOTES)}</div>", unsafe_allow_html=True)
            
            with sc2:
                swaps = ETHICAL_ALTERNATIVES.get(last["category"], [])
                sw_cols = st.columns(len(swaps))
                for idx, sw in enumerate(swaps):
                    with sw_cols[idx]:
                        render_html(f"""
                        <div class="swap-card">
                            <strong>{sw['brand']}</strong><br>
                            <span style="font-size: 0.84rem;">{sw['perk']}</span><br>
                            <span style="color: {accent_hex}; font-weight: 700; font-size: 0.81rem;">⚡ Carbon Cut: {sw['saving']}</span>
                        </div>
                        """)
                        b_name = sw['brand'].split('/')[0].strip()
                        if st.button(f"Adopt {b_name} 🌿", key=f"adopt_swap_{idx}", width="stretch"):
                            swap_rec, _, _, _ = add_purchase(
                                st.session_state.purchases, f"Greener Swap: {b_name} ({last['category']})",
                                last['category'], b_name, 35.0, date.today(), True, st.session_state.user_mascot
                            )
                            st.session_state.last_logged = swap_rec
                            st.session_state.mascot_mood = "ecstatic"
                            st.session_state.mascot_message = f"LEGENDARY CHOICE! You adopted {b_name}! {c_name} celebrates your active biosphere restoration!"
                            st.session_state.recent_art = "badge"
                            st.balloons()
                            st.rerun()

        # PERSONALIZED "WHAT-IF GREEN SWITCH" OPTIMIZER (Shows real savings on user's heaviest item!)
        swap_opp = find_top_swap_opportunity(st.session_state.purchases)
        if swap_opp:
            it = swap_opp["item"]
            op_l, op_r = st.columns([2.1, 0.9], gap="medium")
            with op_l:
                render_html(f"""
                <div class="optimizer-box">
                    <div style="font-size:0.75rem; font-weight:800; color:{accent_hex}; text-transform:uppercase; letter-spacing:0.6px;">💡 What-If Carbon Optimizer</div>
                    <div style="font-size:1.0rem; font-weight:700; margin-top:0.2rem;">
                        Your heaviest footprint item is <em>"{html.escape(it['item'])}"</em> ({swap_opp['cur_co2']} kg CO₂e).
                    </div>
                    <div style="font-size:0.86rem; color:{muted_hex}; margin-top:0.2rem;">
                        Switching to <strong>{swap_opp['target_cat']}</strong> ({swap_opp['brand_suggestion']}) drops it to <strong>{swap_opp['alt_co2']} kg</strong> (saves <strong>{swap_opp['saved_diff']} kg CO₂</strong> / <strong>-{swap_opp['pct_drop']}%</strong>).
                    </div>
                </div>
                """)
            with op_r:
                st.markdown("<div style='height:0.9rem;'></div>", unsafe_allow_html=True)
                if st.button(f"🔄 Swap Item (-{swap_opp['saved_diff']} kg)", type="primary", width="stretch", key="opt_swap_btn"):
                    target_rec = st.session_state.purchases[swap_opp["index"]]
                    target_rec["item"] = f"Swapped: {target_rec['item']} (Circular)"
                    target_rec["category"] = swap_opp["target_cat"]
                    target_rec["brand"] = swap_opp["brand_suggestion"].split('/')[0].strip()
                    target_rec["carbon_kg"] = swap_opp["alt_co2"]
                    target_rec["is_ethical"] = True
                    st.session_state.last_logged = target_rec
                    st.session_state.mascot_mood = "ecstatic"
                    st.session_state.mascot_message = f"SMART SWITCH! Swapping saved {swap_opp['saved_diff']} kg CO₂ instantly!"
                    st.session_state.recent_art = "badge"
                    st.toast(f"Swapped to eco option: saved {swap_opp['saved_diff']} kg CO₂!", icon="🌱")
                    st.balloons()
                    st.rerun()

        st.markdown("---")

        # PERIOD FILTER, INTERACTIVE CHARTS & ENHANCED LEDGER
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

        for p in filtered_data:
            if "carbon_kg" not in p and "co2" in p: p["carbon_kg"] = p["co2"]
            if "is_ethical" not in p and "ethical" in p: p["is_ethical"] = p["ethical"]
            if "price" not in p: p["price"] = 0.0
            if "category" not in p: p["category"] = "General"
            if "item" not in p: p["item"] = "Purchase"
            if "brand" not in p: p["brand"] = "Unspecified"
            if "date" not in p: p["date"] = str(date.today())

        col_g1, col_g2 = st.columns([1.05, 1.35], gap="large")
        top_cat_name = "None yet"
        with col_g1:
            st.markdown(f"**Emissions by Category ({period_label})**")
            if filtered_data:
                df = pd.DataFrame(filtered_data)
                cat_agg = df.groupby("category", as_index=False).agg(
                    carbon_kg=("carbon_kg", "sum"),
                    spend=("price", "sum"),
                    items=("item", "count"),
                ).sort_values("carbon_kg", ascending=False)
                top_cat_name = f"{cat_agg.iloc[0]['category']} ({cat_agg.iloc[0]['carbon_kg']:.1f} kg)"
                cat_agg["tier_color"] = cat_agg["category"].map(
                    lambda c: "High Carbon" if CATEGORIES.get(c, {}).get("multiplier", 0.3) >= 0.4 else "Low / Conscious"
                )

                if HAS_ALTAIR:
                    bar = alt.Chart(cat_agg).mark_bar(cornerRadiusEnd=6, size=22).encode(
                        x=alt.X("carbon_kg:Q", title="Carbon Footprint (kg CO₂e)"),
                        y=alt.Y("category:N", sort="-x", title=None, axis=alt.Axis(labelLimit=200)),
                        color=alt.Color(
                            "tier_color:N",
                            scale=alt.Scale(
                                domain=["Low / Conscious", "High Carbon"],
                                range=["#10b981", "#f59e0b"],
                            ),
                            legend=alt.Legend(orient="top", title=None),
                        ),
                        tooltip=[
                            alt.Tooltip("category:N", title="Product Type"),
                            alt.Tooltip("items:Q", title="Items"),
                            alt.Tooltip("spend:Q", title="Spend ($)", format="$,.2f"),
                            alt.Tooltip("carbon_kg:Q", title="CO₂ (kg)", format=".2f"),
                        ],
                    ).properties(height=280)
                    st.altair_chart(bar, width="stretch")

                    # Eco vs Conventional Split Donut Chart
                    split_df = pd.DataFrame([
                        {"Type": "Ethical / Circular", "CO2": float(df[df["is_ethical"]]["carbon_kg"].sum())},
                        {"Type": "Conventional", "CO2": float(df[~df["is_ethical"]]["carbon_kg"].sum())},
                    ])
                    split_df = split_df[split_df["CO2"] > 0]
                    if not split_df.empty:
                        st.markdown("**Ethical vs. Conventional CO₂ Share**")
                        donut = alt.Chart(split_df).mark_arc(innerRadius=44, outerRadius=78).encode(
                            theta=alt.Theta("CO2:Q"),
                            color=alt.Color(
                                "Type:N",
                                scale=alt.Scale(domain=["Ethical / Circular", "Conventional"], range=["#10b981", "#e11d48"]),
                                legend=alt.Legend(orient="right", title=None),
                            ),
                            tooltip=[alt.Tooltip("Type:N"), alt.Tooltip("CO2:Q", title="kg CO₂e", format=".2f")],
                        ).properties(height=180)
                        st.altair_chart(donut, width="stretch")
                else:
                    st.bar_chart(df.groupby("category")["carbon_kg"].sum().sort_values(ascending=False), color="#2d6a4f")
            else:
                st.info("No purchases recorded yet for this period. Plan and log your first purchase above!")

        with col_g2:
            st.markdown(f"**Transaction Ledger ({len(filtered_data)} records)**")
            if filtered_data:
                s_c1, s_c2 = st.columns([1.4, 1.0])
                with s_c1:
                    search_q = st.text_input("Search ledger:", placeholder="Filter by item or brand...", label_visibility="collapsed", key="ledger_search")
                with s_c2:
                    eth_only = st.checkbox("Eco picks only", value=False, key="ledger_eth_only")

                view_rows = filtered_data
                if search_q.strip():
                    q_low = search_q.strip().lower()
                    view_rows = [r for r in view_rows if q_low in r["item"].lower() or q_low in r["brand"].lower() or q_low in r["category"].lower()]
                if eth_only:
                    view_rows = [r for r in view_rows if r["is_ethical"]]

                if view_rows:
                    df_view = pd.DataFrame(view_rows)[["date", "item", "category", "brand", "price", "carbon_kg", "is_ethical"]]
                    df_view.columns = ["Date", "Item", "Product Type", "Brand", "Price ($)", "CO₂ (kg)", "Ethical?"]
                    max_co2 = max(float(df_view["CO₂ (kg)"].max()), 1.0)
                    st.dataframe(
                        df_view,
                        width="stretch",
                        hide_index=True,
                        column_config={
                            "Price ($)": st.column_config.NumberColumn("Price ($)", format="$%.2f"),
                            "CO₂ (kg)": st.column_config.ProgressColumn("CO₂ (kg)", format="%.2f kg", min_value=0, max_value=max_co2),
                            "Ethical?": st.column_config.CheckboxColumn("Eco?"),
                        },
                    )
                else:
                    df_view = pd.DataFrame(filtered_data)[["date", "item", "category", "brand", "price", "carbon_kg", "is_ethical"]]
                    df_view.columns = ["Date", "Item", "Product Type", "Brand", "Price ($)", "CO₂ (kg)", "Ethical?"]
                    st.info("No rows match that search filter.")
                
                # Action Controls: Undo | Export CSV | Download Scorecard Report
                u_col1, u_col2, u_col3 = st.columns(3)
                with u_col1:
                    if st.button("↩️ Undo Last Purchase", width="stretch", help="Roll back the most recent logged purchase"):
                        popped = st.session_state.purchases.pop()
                        prev = st.session_state.purchases[-1] if st.session_state.purchases else None
                        st.session_state.last_logged = prev
                        if prev:
                            mood, msg, art = evaluate_feedback_for_item(
                                st.session_state.user_mascot, prev["item"], prev["carbon_kg"], prev["is_ethical"]
                            )
                            st.session_state.mascot_mood, st.session_state.mascot_message, st.session_state.recent_art = mood, msg, art
                        else:
                            st.session_state.mascot_mood = "mindful"
                            st.session_state.mascot_message = f"Removed '{popped['item']}'. Log your next purchase above!"
                            st.session_state.recent_art = None
                        st.toast(f"Removed '{popped['item']}' from ledger", icon="↩️")
                        st.rerun()
                with u_col2:
                    st.download_button("📥 Export CSV", df_view.to_csv(index=False).encode("utf-8"), f"shopimpact_{period_label.lower().replace(' ', '_')}.csv", "text/csv", width="stretch")
                with u_col3:
                    report_md = build_eco_scorecard_markdown(
                        st.session_state.user_name, rank_title, st.session_state.carbon_budget,
                        spend_tot, co2_tot, saved_tot, badges, cur_streak, top_cat_name
                    )
                    st.download_button("📄 Eco Scorecard", report_md.encode("utf-8"), "shopimpact_scorecard.md", "text/markdown", width="stretch")
            else:
                st.caption("No records available to export yet. Log a quick chip or custom item above.")

    # --------------------------------------------------------------------------
    # VIEW: 🏆 WALL OF BADGES & TURTLE ART VAULT
    # --------------------------------------------------------------------------
    elif st.session_state.nav_view == "🏆 Wall of Badges":
        st.title("🏆 Wall of Badges & Eco Fame")
        st.caption("Unlocked achievements glow in vibrant emerald gradient. Locked badges stay monochrome grayscale until earned.")

        st.metric("Badges Unlocked", f"{unlocked_num} of {len(badges)}", f"{int((unlocked_num/len(badges))*100)}% Complete")
        st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)

        b_c1, b_c2 = st.columns(2, gap="large")
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

        st.markdown("---")
        st.subheader("🐢 Procedural Turtle Vector Art Vault")
        st.caption(f"Collect all 3 botanical emblems drawn in-memory by our HeadlessTurtle Pillow engine ({len(earned_arts)}/3 unlocked).")

        v1, v2, v3 = st.columns(3, gap="medium")
        art_specs = [
            ("leaf", "Botanical Eco Leaf", "Unlocked by ethical or organic purchases"),
            ("footprint", "Earth Step Medallion", "Unlocked by low-footprint buys (<= 10 kg)"),
            ("badge", "Championship Rosette", "Unlocked by ultra-green picks (<= 3 kg) or swaps"),
        ]
        for col_v, (ak, title_a, desc_a) in zip([v1, v2, v3], art_specs):
            with col_v:
                with st.container(border=True):
                    unlocked_art = ak in earned_arts
                    img_show = draw_vector_art(ak if unlocked_art else "preview")
                    st.image(img_show, width=180, caption=f"{'✨ ' if unlocked_art else '🔒 '}{title_a}")
                    st.caption(desc_a)

st.divider()
footer_col = "#94a3b8" if st.session_state.dark_theme else "#4A6355"
render_html(f"""
<div style="text-align: center; color: {footer_col}; font-size: 0.8rem; padding: 0.8rem 0;">
    <strong>ShopImpact Conscious Shopping Dashboard</strong> • IDAI 102: Python Programming<br>
    Candidate: <strong>Parth Pravinbhai Gajera</strong> (ID: <code>1000544</code>) • CRS: Artificial Intelligence
</div>
""")

