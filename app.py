import html
import math
import random
from datetime import date, datetime
import pandas as pd
from PIL import Image, ImageDraw
import streamlit as st

st.set_page_config(page_title="ShopImpact — Conscious Shopping Companion", page_icon="🌱", layout="wide")

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
    {"name": "Fair-Trade Coffee / Tea", "price": 4.50, "category": "Local / Organic Food", "is_ethical": True, "icon": "☕", "co2": 0.36},
    {"name": "Local Organic Lunch", "price": 12.00, "category": "Local / Organic Food", "is_ethical": True, "icon": "🥗", "co2": 0.96},
    {"name": "Thrifted Vintage Jacket", "price": 32.00, "category": "Second-Hand / Thrift", "is_ethical": True, "icon": "🧥", "co2": 1.60},
    {"name": "Refurbished Tech Gadget", "price": 85.00, "category": "Refurbished Tech", "is_ethical": True, "icon": "📱", "co2": 9.35},
    {"name": "Fast-Fashion Top", "price": 55.00, "category": "Fast Fashion Apparel", "is_ethical": False, "icon": "👗", "co2": 23.10},
    {"name": "Leather Footwear", "price": 130.00, "category": "Footwear & Leather", "is_ethical": False, "icon": "👞", "co2": 84.50},
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
    <ellipse cx="110" cy="208" rx="42" ry="12" fill="url(#bio-pedestal)" stroke="{glow_color}" stroke-width="2"/>
    <path d="M 80 210 L 68 238 C 68 244 152 244 152 238 L 140 210 Z" fill="url(#bio-pedestal)" stroke="#0f172a" stroke-width="2"/>
    <ellipse cx="110" cy="238" rx="46" ry="13" fill="#0f172a" stroke="{glow_color}" stroke-width="2.5"/>

    <!-- Centerpiece Typography Badge Inside Base -->
    <text x="110" y="235" text-anchor="middle" fill="#ffffff" font-size="13" font-weight="900" font-family="sans-serif">{pct:.0f}% BUDGET</text>
    <text x="110" y="248" text-anchor="middle" fill="{status_color}" font-size="8.0" font-weight="800" font-family="sans-serif" letter-spacing="0.5">{status_text}</text>

    <!-- Bottom Readout Caption -->
    <text x="110" y="275" text-anchor="middle" fill="#94a3b8" font-size="11" font-weight="700" font-family="sans-serif">{co2_tot:.1f} / {budget_limit} kg CO₂e</text>
    <text x="110" y="292" text-anchor="middle" fill="{status_color}" font-size="9.5" font-weight="700" font-family="sans-serif">Remaining: {max(0.0, budget_limit - co2_tot):.1f} kg</text>
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
    t = HeadlessTurtle(240, 240)
    cx, cy = 120, 100
    if art_type == "leaf":
        t.penup(); t.goto(120, 215); t.heading = 90; t.color = (74, 122, 92, 255); t.width = 5; t.pendown(); t.forward(45)
        leaf_pts = []
        for step in range(21):
            frac = step / 20.0
            y = 175 - frac * 140
            x = 120 + math.sin(frac * math.pi) * 48
            leaf_pts.append((x, y))
        for step in range(20, -1, -1):
            frac = step / 20.0
            y = 175 - frac * 140
            x = 120 - math.sin(frac * math.pi) * 48
            leaf_pts.append((x, y))
        t.draw.polygon(leaf_pts, fill=(16, 185, 129, 240), outline=(5, 150, 105, 255))
        t.penup(); t.goto(120, 175); t.heading = 90; t.color = (5, 150, 105, 255); t.width = 3; t.pendown(); t.forward(140)
        for y_pos in [145, 120, 95, 70]:
            t.penup(); t.goto(120, y_pos); t.heading = 40; t.width = 2; t.pendown(); t.forward(30)
            t.penup(); t.goto(120, y_pos); t.heading = 140; t.pendown(); t.forward(30)
    elif art_type == "footprint":
        t.draw.ellipse([(cx - 24, cy + 25), (cx + 24, cy + 75)], fill=(16, 185, 129, 230), outline=(5, 150, 105, 255), width=2)
        foot_pts = [
            (cx - 20, cy + 35), (cx - 14, cy - 5), (cx - 28, cy - 35), (cx - 15, cy - 65),
            (cx + 20, cy - 65), (cx + 32, cy - 35), (cx + 18, cy - 5), (cx + 20, cy + 35)
        ]
        t.draw.polygon(foot_pts, fill=(16, 185, 129, 230), outline=(5, 150, 105, 255))
        t.draw.ellipse([(cx - 28, cy - 65), (cx + 32, cy - 15)], fill=(16, 185, 129, 230), outline=(5, 150, 105, 255), width=2)
        for tx, ty, tr in [(-16, -78, 10), (1, -83, 8.5), (15, -80, 7.5), (27, -73, 6.5), (37, -64, 5.5)]:
            t.draw.ellipse([(cx + tx - tr, cy + ty - tr), (cx + tx + tr, cy + ty + tr)], fill=(52, 211, 153, 240), outline=(5, 150, 105, 255), width=2)
    else:  # badge rosette
        r_pts_l = [(cx - 24, cy + 26), (cx - 52, cy + 126), (cx - 32, cy + 112), (cx - 12, cy + 120), (cx - 6, cy + 28)]
        t.draw.polygon(r_pts_l, fill=(5, 150, 105, 255), outline=(4, 120, 87, 255))
        t.draw.line([(cx - 24, cy + 26), (cx - 32, cy + 112)], fill=(52, 211, 153, 200), width=2)
        r_pts_r = [(cx + 6, cy + 28), (cx + 12, cy + 120), (cx + 32, cy + 112), (cx + 52, cy + 126), (cx + 24, cy + 26)]
        t.draw.polygon(r_pts_r, fill=(4, 120, 87, 255), outline=(6, 95, 70, 255))
        t.draw.line([(cx + 24, cy + 26), (cx + 32, cy + 112)], fill=(52, 211, 153, 200), width=2)
        rosette_pts = []
        for i in range(64):
            ang = i * (math.pi / 32)
            r = 58 if i % 2 == 0 else 50
            rosette_pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
        t.draw.polygon(rosette_pts, fill=(245, 158, 11, 255), outline=(180, 83, 9, 255))
        t.draw.ellipse([(cx - 48, cy - 48), (cx + 48, cy + 48)], fill=(251, 191, 36, 255), outline=(217, 119, 6, 255), width=2)
        t.draw.ellipse([(cx - 41, cy - 41), (cx + 41, cy + 41)], fill=(6, 95, 70, 255), outline=(4, 120, 87, 255), width=2)
        for j in range(12):
            s_ang = j * (2 * math.pi / 12)
            sx = cx + 37 * math.cos(s_ang)
            sy = cy + 37 * math.sin(s_ang)
            t.draw.ellipse([(sx - 2, sy - 2), (sx + 2, sy + 2)], fill=(254, 240, 138, 255))
        t.draw.ellipse([(cx - 30, cy - 30), (cx + 30, cy + 30)], fill=(254, 243, 199, 255), outline=(217, 119, 6, 255), width=2)
        star_pts = []
        for k in range(10):
            ang = -math.pi / 2 + k * (math.pi / 5)
            sr = 19 if k % 2 == 0 else 8.0
            star_pts.append((cx + sr * math.cos(ang), cy + sr * math.sin(ang)))
        t.draw.polygon(star_pts, fill=(217, 119, 6, 255), outline=(146, 64, 14, 255))
        star_inner = []
        for k in range(10):
            ang = -math.pi / 2 + k * (math.pi / 5)
            sr = 15 if k % 2 == 0 else 6.0
            star_inner.append((cx + sr * math.cos(ang), cy + sr * math.sin(ang)))
        t.draw.polygon(star_inner, fill=(245, 158, 11, 255))
    return t.img

def calculate_carbon(price, category, is_ethical):
    rate = CATEGORIES.get(category, {"multiplier": 0.35})["multiplier"]
    base = price * rate
    return round(base * 0.70 if is_ethical else base, 2)

def get_equivalency(carbon_kg):
    miles = int(carbon_kg * 2.4)
    charges = int(carbon_kg * 121)
    tree_months = round((carbon_kg / 21.0) * 12, 1)
    return miles, charges, tree_months

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
    total_spend = sum(p["price"] for p in purchases)
    total_co2 = sum(p["carbon_kg"] for p in purchases)
    ethical_count = sum(1 for p in purchases if p.get("is_ethical", False))
    avg_intensity = (total_co2 / total_spend) if total_spend > 0 else 0.0
    co2_saved = max(0.0, round(total_spend * 0.45 - total_co2, 1))
    zero_waste_count = sum(1 for p in purchases if "Zero-Waste" in p["category"] or "Thrift" in p["category"])

    badges = [
        {
            "id": "starter",
            "name": "Seed Starter",
            "icon": "🌱",
            "desc": "Log your 1st conscious purchase in the dashboard",
            "unlocked": total_items >= 1,
            "progress": f"{min(total_items, 1)}/1 item"
        },
        {
            "id": "low_impact",
            "name": "Low Impact Shopper",
            "icon": "🍃",
            "desc": "Maintain carbon intensity ≤ 0.25 kg/$ (min 2 items)",
            "unlocked": total_items >= 2 and avg_intensity <= 0.25,
            "progress": f"{avg_intensity:.2f} kg/$ (Goal ≤ 0.25)" if total_items >= 2 else f"{total_items}/2 items required"
        },
        {
            "id": "ethical_pioneer",
            "name": "Conscious Pioneer",
            "icon": "♻️",
            "desc": "Choose 3+ verified circular, thrift, or ethical items",
            "unlocked": ethical_count >= 3,
            "progress": f"{ethical_count}/3 ethical items"
        },
        {
            "id": "eco_saver",
            "name": "Eco Saver of the Month",
            "icon": "🌟",
            "desc": "Save 10+ kg CO₂ vs standard retail baseline",
            "unlocked": co2_saved >= 10.0 and total_items >= 1,
            "progress": f"{co2_saved:.1f}/10.0 kg CO₂ saved"
        },
        {
            "id": "zero_waste",
            "name": "Zero-Waste Hero",
            "icon": "🏆",
            "desc": "Log 2+ zero-waste or second-hand thrift items",
            "unlocked": zero_waste_count >= 2,
            "progress": f"{zero_waste_count}/2 items"
        },
    ]
    return badges, total_spend, total_co2, avg_intensity, co2_saved, ethical_count

# ------------------------------------------------------------------------------
# SESSION STATE INITIALIZATION (Clean Defaults, 100% Local Volatile Memory)
# ------------------------------------------------------------------------------

if "dark_theme" not in st.session_state: st.session_state.dark_theme = True
if "onboarded" not in st.session_state:
    if st.query_params.get("onboarded") in ["true", "1"]:
        st.session_state.onboarded = True
    else:
        st.session_state.onboarded = False

if "user_name" not in st.session_state: st.session_state.user_name = "Parth Gajera"
if "user_mascot" not in st.session_state: st.session_state.user_mascot = "Pip the Forest Fox 🦊"
if "carbon_budget" not in st.session_state: st.session_state.carbon_budget = 150
if "recent_art" not in st.session_state: st.session_state.recent_art = None
if "mascot_mood" not in st.session_state: st.session_state.mascot_mood = "ecstatic"
if "mascot_message" not in st.session_state:
    st.session_state.mascot_message = "CLEVER THRIFT MASTER! Pip put on gold sunglasses! 'Vintage Denim Jacket' is a circular gem!"
if "nav_view" not in st.session_state: st.session_state.nav_view = "📊 Dashboard"
if "last_logged" not in st.session_state: st.session_state.last_logged = None
if "purchases" not in st.session_state:
    if st.query_params.get("demo") in ["true", "1"]:
        st.session_state.purchases = [
            {"time": "14:20", "date": "2026-11-12", "year": "2026", "month": "2026-11", "item": "Vintage Denim Jacket", "category": "Second-Hand / Thrift", "price": 35.0, "co2": 1.22, "ethical": True, "saved": 14.53},
            {"time": "14:22", "date": "2026-11-12", "year": "2026", "month": "2026-11", "item": "Organic CSA Harvest Box", "category": "Local / Organic Food", "price": 42.0, "co2": 2.35, "ethical": True, "saved": 16.55},
            {"time": "14:25", "date": "2026-11-12", "year": "2026", "month": "2026-11", "item": "Certified Renewed ThinkPad", "category": "Refurbished Tech", "price": 280.0, "co2": 21.56, "ethical": True, "saved": 104.44},
        ]
        st.session_state.recent_art = "badge"
    else:
        st.session_state.purchases = []
if "confirm_reset" not in st.session_state: st.session_state.confirm_reset = False

# ------------------------------------------------------------------------------
# DUAL-THEME HIGH-CONTRAST CSS ENGINE
# ------------------------------------------------------------------------------

if st.session_state.dark_theme:
    render_html("""
    <style>
    .stApp { background-color: #0c120e !important; color: #f8fafc !important; }
    h1, h2, h3, h4, h5, p, span, label { color: #f8fafc !important; }
    [data-testid="stSidebar"] { background-color: #080d0a !important; border-right: 1.5px solid #1e2d22 !important; }
    [data-testid="stSidebar"] * { color: #f8fafc !important; }
    .tip-box { background: linear-gradient(135deg, #13271c, #162a1e) !important; border: 1.5px solid #34d399 !important; border-radius: 14px; padding: 1.1rem 1.3rem; color: #f8fafc !important; margin: 0.8rem 0; box-shadow: 0 4px 14px rgba(0,0,0,0.3); }
    .swap-card { background: #152219 !important; border: 1.5px solid #2d3e32 !important; border-radius: 12px; padding: 1rem; color: #f8fafc !important; margin-bottom: 0.5rem; }
    .badge-on { background: linear-gradient(135deg, #064e3b, #047857) !important; border: 2px solid #34d399 !important; border-radius: 14px; padding: 1rem; color: #ffffff !important; margin-bottom: 0.8rem; box-shadow: 0 4px 15px rgba(52, 211, 153, 0.2); }
    .badge-off { background: #1e293b !important; border: 2px dashed #475569 !important; border-radius: 14px; padding: 1rem; color: #94a3b8 !important; filter: grayscale(100%); opacity: 0.6; margin-bottom: 0.8rem; }
    .reaction-bubble { border-radius: 14px; padding: 1.1rem 1.3rem; border: 1.5px solid #34d399; background: #162a1e; color: #f8fafc; box-shadow: 0 4px 16px rgba(0,0,0,0.25); }
    .avatar-card { display: flex; flex-direction: column; align-items: center; justify-content: center; margin-bottom: 1.2rem; text-align: center; }
    .avatar-circle { width: 92px; height: 92px; border-radius: 50%; border: 3px solid #34d399; overflow: hidden; background: #13271c; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 16px rgba(52, 211, 153, 0.3); margin: 0 auto; }
    .rank-pill { font-size: 0.8rem; background: #064e3b; color: #34d399; border: 1px solid #059669; padding: 0.2rem 0.65rem; border-radius: 99px; font-weight: 700; display: inline-block; margin-top: 0.35rem; }
    .vessel-chip { background: #162a1e; border: 1.5px solid #2d6a4f; border-radius: 12px; padding: 0.75rem; text-align: center; margin-bottom: 0.5rem; transition: transform 0.15s ease; }
    .vessel-chip:hover { border-color: #34d399; transform: translateY(-2px); }
    .sim-card { background: #122017; border: 1.5px solid #2d6a4f; border-radius: 14px; padding: 1.2rem; margin: 1rem 0; box-shadow: 0 4px 18px rgba(0,0,0,0.25); }
    </style>
    """)
else:
    render_html("""
    <style>
    .stApp { background-color: #fcfbf9 !important; color: #0f172a !important; }
    h1, h2, h3, h4, h5, p, span, label { color: #0f172a !important; }
    [data-testid="stSidebar"] { background-color: #f4f1eb !important; border-right: 1.5px solid #e5dfd5 !important; }
    [data-testid="stSidebar"] * { color: #0f172a !important; }
    .tip-box { background: linear-gradient(135deg, #f0fdf4, #ecfdf5) !important; border: 1.5px solid #86efac !important; border-radius: 14px; padding: 1.1rem 1.3rem; color: #14532d !important; margin: 0.8rem 0; box-shadow: 0 2px 10px rgba(0,0,0,0.04); }
    .swap-card { background: #ffffff !important; border: 1.5px solid #e2e8f0 !important; border-radius: 12px; padding: 1rem; color: #0f172a !important; box-shadow: 0 2px 8px rgba(0,0,0,0.04); margin-bottom: 0.5rem; }
    .badge-on { background: linear-gradient(135deg, #1b4332, #2d6a4f) !important; border: 2px solid #52b788 !important; border-radius: 14px; padding: 1rem; color: #ffffff !important; box-shadow: 0 4px 14px rgba(45,106,79,0.18); margin-bottom: 0.8rem; }
    .badge-off { background: #f1f5f9 !important; border: 2px dashed #cbd5e1 !important; border-radius: 14px; padding: 1rem; color: #64748b !important; filter: grayscale(100%); opacity: 0.6; margin-bottom: 0.8rem; }
    .reaction-bubble { border-radius: 14px; padding: 1.1rem 1.3rem; border: 1.5px solid #86efac; background: #f0fdf4; color: #14532d; box-shadow: 0 2px 12px rgba(0,0,0,0.05); }
    .avatar-card { display: flex; flex-direction: column; align-items: center; justify-content: center; margin-bottom: 1.2rem; text-align: center; }
    .avatar-circle { width: 92px; height: 92px; border-radius: 50%; border: 3px solid #10b981; overflow: hidden; background: #ecfdf5; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 14px rgba(16, 185, 129, 0.2); margin: 0 auto; }
    .rank-pill { font-size: 0.8rem; background: #ecfdf5; color: #047857; border: 1px solid #10b981; padding: 0.2rem 0.65rem; border-radius: 99px; font-weight: 700; display: inline-block; margin-top: 0.35rem; }
    .vessel-chip { background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 12px; padding: 0.75rem; text-align: center; margin-bottom: 0.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.04); transition: transform 0.15s ease; }
    .vessel-chip:hover { border-color: #10b981; transform: translateY(-2px); }
    .sim-card { background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 14px; padding: 1.2rem; margin: 1rem 0; box-shadow: 0 2px 10px rgba(0,0,0,0.04); }
    </style>
    """)

# ------------------------------------------------------------------------------
# SCREEN 1: WELCOME & ONBOARDING (Clean, Visual, Standalone First-Run in Dark Mode)
# ------------------------------------------------------------------------------

if not st.session_state.onboarded:
    render_html("<h1 style='text-align: center; color: #34d399; margin-top: 1rem; margin-bottom: 0;'>🌱 Meet ShopImpact</h1><p style='text-align: center; color: #94a3b8; font-size: 1.15rem; margin-bottom: 2.2rem;'>Your playful, conscious shopping companion.</p>")

    c1, c2 = st.columns([1.1, 0.9], gap="large")
    with c1:
        st.subheader("Set Your Goals & Avatar")
        u_name = st.text_input("Your Shopper Name (Required):", value=st.session_state.user_name)
        m_choice = st.selectbox("Choose Your Eco Mascot Spirit (Required):", options=list(ECO_MASCOTS.keys()))
        b_choice = st.slider("Monthly Sustainable Carbon Target (kg CO₂e):", min_value=50, max_value=300, value=st.session_state.carbon_budget, step=10, help="Standard Paris-aligned conscious shopper target is 100-150 kg.")

        st.caption(f"✨ **{m_choice.split()[0]}**: {ECO_MASCOTS[m_choice]}")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 Enter ShopImpact Dashboard →", type="primary", width="stretch"):
            st.session_state.user_name = u_name.strip() if u_name.strip() else "Shopper"
            st.session_state.user_mascot = m_choice
            st.session_state.carbon_budget = b_choice
            st.session_state.onboarded = True
            c_name = m_choice.split()[0]
            st.session_state.mascot_message = f"Welcome {st.session_state.user_name}! I am {c_name}. I react live to every purchase you make and guide you toward greener habits!"
            st.rerun()

    with c2:
        render_html(render_animated_avatar_svg(m_choice, "happy", 220, 220))
        render_html(f"""
        <div style="background: #13271c; border: 1.5px solid #34d399; border-radius: 14px; padding: 1.1rem; color: #f8fafc; margin-top: 0.8rem;">
            <strong style="color: #34d399;">What you'll experience inside:</strong>
            <ul style="margin: 0.5rem 0 0 1.2rem; padding: 0; line-height: 1.6; color: #e2e8f0;">
                <li>🌍 <strong>Living Biosphere Globe:</strong> 60 FPS animated SVG terrarium reflecting your carbon health</li>
                <li>⚡ <strong>Tactile Quick Chips:</strong> one-click instant logging for common purchases</li>
                <li>🔄 <strong>Contextual Swaps:</strong> verified ethical alternatives right after logging</li>
                <li>🏆 <strong>Living Wall of Badges:</strong> watch grayscale badges turn into radiant colors</li>
                <li>🐾 <strong>Reactive Spirit Mascot:</strong> {m_choice.split()[0]} celebrates your green habits live!</li>
            </ul>
        </div>
        """)

# ------------------------------------------------------------------------------
# SCREEN 2: MAIN DASHBOARD & TABS
# ------------------------------------------------------------------------------

else:
    # Sidebar Profile Card: Circular Avatar, Name, Eco-Rank, and Goals
    with st.sidebar:
        rank_title = get_user_eco_rank(st.session_state.purchases)
        avatar_svg_mini = render_animated_avatar_svg(st.session_state.user_mascot, st.session_state.mascot_mood, 86, 86)
        
        render_html(f"""
        <div class="avatar-card">
            <div class="avatar-circle">
                {avatar_svg_mini}
            </div>
            <div style="font-size: 1.25rem; font-weight: 800; margin-top: 0.6rem;">{html.escape(st.session_state.user_name)}</div>
            <div class="rank-pill">{rank_title}</div>
            <div style="font-size: 0.82rem; margin-top: 0.35rem; opacity: 0.85;">{st.session_state.user_mascot.split('—')[0].strip()}</div>
            <div style="font-size: 0.8rem; opacity: 0.7;">Budget: {st.session_state.carbon_budget} kg CO₂e/mo</div>
        </div>
        """)

        if st.button("⚙️ Edit Profile / Avatar", width="stretch"):
            st.session_state.onboarded = False
            st.rerun()

        st.markdown("---")
        st.session_state.nav_view = st.radio("Navigation:", ["📊 Dashboard", "🏆 Wall of Badges"])

        dark_toggle = st.toggle("🌙 High-Contrast Dark Mode", value=st.session_state.dark_theme)
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
                st.session_state.mascot_message = f"All purchases cleared. {c_name} is ready for your first eco-conscious log!"
                st.rerun()
            if r_c2.button("Cancel", width="stretch"):
                st.session_state.confirm_reset = False
                st.rerun()

    # --------------------------------------------------------------------------
    # VIEW: 📊 DASHBOARD
    # --------------------------------------------------------------------------
    if st.session_state.nav_view == "📊 Dashboard":
        c_name = st.session_state.user_mascot.split()[0]
        msg_esc = html.escape(st.session_state.mascot_message)

        # Calculate current active totals
        badges, spend_tot, co2_tot, avg_int, saved_tot, eth_cnt = evaluate_badges(st.session_state.purchases)
        b_lim = max(st.session_state.carbon_budget, 1)
        used_pct = (co2_tot / b_lim) * 100.0

        # DUAL VISUAL FEEDBACK HERO: 60 FPS Biosphere Terrarium + Interactive Mascot
        col_bio, col_mascot = st.columns([1.1, 1.9], gap="large")
        with col_bio:
            render_html(render_animated_biosphere_svg(used_pct, co2_tot, b_lim, width=210, height=300))
        
        with col_mascot:
            if st.session_state.recent_art:
                m_sub1, m_sub2 = st.columns([1.4, 1.0])
                with m_sub1:
                    render_html(render_animated_avatar_svg(st.session_state.user_mascot, st.session_state.mascot_mood, 150, 150))
                    render_html(f"""
                    <div class="reaction-bubble" style="margin-top: 0.6rem;">
                        <div style="font-size: 1.05rem; font-weight: 800; color: #34d399;">{c_name}'s Live Reaction:</div>
                        <div style="font-size: 0.92rem; margin-top: 0.25rem;">"{msg_esc}"</div>
                    </div>
                    """)
                with m_sub2:
                    art_img = draw_vector_art(st.session_state.recent_art)
                    art_label = {"leaf": "Eco Leaf 🌿", "footprint": "Low Footprint 👣", "badge": "Eco Badge ⭐"}.get(st.session_state.recent_art, "Eco Choice")
                    st.image(art_img, width=135, caption=f"{c_name} generated: {art_label}")
            else:
                render_html(render_animated_avatar_svg(st.session_state.user_mascot, st.session_state.mascot_mood, 150, 150))
                render_html(f"""
                <div class="reaction-bubble" style="margin-top: 0.6rem;">
                    <div style="font-size: 1.05rem; font-weight: 800; color: #34d399;">{c_name}'s Live Reaction:</div>
                    <div style="font-size: 0.92rem; margin-top: 0.25rem;">"{msg_esc}"</div>
                </div>
                """)

        st.markdown("<br>", unsafe_allow_html=True)

        # 4 PRIMARY KPI METRIC CARDS
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total Spend", f"${spend_tot:,.2f}", f"{len(st.session_state.purchases)} items recorded")
        k2.metric("Carbon Footprint", f"{co2_tot:.1f} kg", f"{avg_int:.2f} kg/$ intensity", delta_color="inverse")
        k3.metric("Carbon Avoided", f"{saved_tot:.1f} kg", "Vs standard 0.45 kg/$")
        trees_tot = round(co2_tot / 21.0, 1)
        k4.metric("Trees to Offset", f"{trees_tot} Trees", "21 kg CO₂/tree/year", delta_color="inverse")

        st.markdown("<br>", unsafe_allow_html=True)

        # TACTILE QUICK-PURCHASE CHIPS (1-Click Instant Logging)
        st.subheader("⚡ Quick-Log Common Purchases")
        st.caption("One-click tactile logging for routine conscious purchases. Automatically updates carbon, mascot, and biosphere.")

        chip_cols = st.columns(6)
        for i, qp in enumerate(QUICK_PURCHASES):
            with chip_cols[i]:
                render_html(f"""
                <div class="vessel-chip">
                    <div style="font-size: 1.8rem;">{qp['icon']}</div>
                    <div style="font-weight: 800; font-size: 0.82rem; margin-top: 0.2rem;">{qp['name']}</div>
                    <div style="color: #34d399; font-weight: 700; font-size: 0.78rem;">${qp['price']:.2f} • {qp['co2']:.1f} kg</div>
                </div>
                """)
                if st.button(f"+ Add {qp['name'].split()[0]}", key=f"chip_btn_{i}", width="stretch"):
                    new_item = {
                        "id": len(st.session_state.purchases) + 1,
                        "item": qp["name"],
                        "category": qp["category"],
                        "brand": "Quick Log",
                        "price": qp["price"],
                        "carbon_kg": qp["co2"],
                        "date": str(date.today()),
                        "is_ethical": qp["is_ethical"],
                    }
                    st.session_state.purchases.append(new_item)
                    st.session_state.last_logged = new_item

                    if qp["is_ethical"] and qp["co2"] <= 2.0:
                        st.session_state.mascot_mood = "ecstatic"
                        st.session_state.mascot_message = get_mascot_reaction(st.session_state.user_mascot, qp["name"], qp["co2"], "ecstatic", True)
                        st.session_state.recent_art = "badge"
                        st.balloons()
                    elif qp["is_ethical"]:
                        st.session_state.mascot_mood = "happy"
                        st.session_state.mascot_message = get_mascot_reaction(st.session_state.user_mascot, qp["name"], qp["co2"], "happy", True)
                        st.session_state.recent_art = "leaf"
                    else:
                        st.session_state.mascot_mood = "mindful" if qp["co2"] <= 25.0 else "worried"
                        st.session_state.mascot_message = get_mascot_reaction(st.session_state.user_mascot, qp["name"], qp["co2"], st.session_state.mascot_mood, False)
                        st.session_state.recent_art = None
                    st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # CUSTOM PURCHASE LOGGING FORM
        st.subheader("🛒 Log a Custom Planned Purchase")
        st.caption("Record custom purchases into your active ledger. Certified circular goods receive an automatic 30% footprint discount.")

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
                is_eth = st.checkbox("🌱 Certified Circular / Thrift / Ethical", help="Applies a 30% footprint discount: accounts for avoiding raw extraction and virgin factory manufacturing.")

            c_info = CATEGORIES[cat_choice]
            tip_msg = random.choice(ECO_TIPS)
            render_html(f"""
            <div class="tip-box">
                <div style="display: flex; gap: 0.8rem; align-items: flex-start;">
                    <div style="font-size: 1.8rem; line-height: 1;">💡</div>
                    <div>
                        <div style="font-weight: 700; font-size: 0.95rem;">Category Context ({c_info['tier']}):</div>
                        <div style="font-size: 0.88rem; margin-top: 0.15rem; opacity: 0.9;">{c_info['fact']}</div>
                        <div style="font-size: 0.84rem; margin-top: 0.4rem; color: #34d399; font-weight: 600;">🌿 Eco Wisdom: {tip_msg}</div>
                    </div>
                </div>
            </div>
            """)

            if st.form_submit_button("🌿 Record Purchase in Active Ledger", width="stretch"):
                if not item_name.strip():
                    st.error("Please enter an item description before recording.")
                else:
                    live_co2 = calculate_carbon(price_val, cat_choice, is_eth)
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
                    
                    if is_eth and live_co2 <= 3.0:
                        st.session_state.mascot_mood = "ecstatic"
                        st.session_state.mascot_message = get_mascot_reaction(st.session_state.user_mascot, item_name, live_co2, "ecstatic", is_eth)
                        st.session_state.recent_art = "badge"
                        st.balloons()
                    elif is_eth or live_co2 <= 10.0:
                        st.session_state.mascot_mood = "happy"
                        st.session_state.mascot_message = get_mascot_reaction(st.session_state.user_mascot, item_name, live_co2, "happy", is_eth)
                        st.session_state.recent_art = "leaf" if is_eth else "footprint"
                        st.balloons()
                    elif live_co2 <= 25.0:
                        st.session_state.mascot_mood = "mindful"
                        st.session_state.mascot_message = get_mascot_reaction(st.session_state.user_mascot, item_name, live_co2, "mindful", is_eth)
                        st.session_state.recent_art = None
                    elif live_co2 <= 50.0:
                        st.session_state.mascot_mood = "worried"
                        st.session_state.mascot_message = get_mascot_reaction(st.session_state.user_mascot, item_name, live_co2, "worried", is_eth)
                        st.session_state.recent_art = None
                    else:
                        st.session_state.mascot_mood = "alarmed"
                        st.session_state.mascot_message = get_mascot_reaction(st.session_state.user_mascot, item_name, live_co2, "alarmed", is_eth)
                        st.session_state.recent_art = None
                    st.rerun()

        # INTERACTIVE CARBON IMPACT & TREE OFFSET SIMULATOR (Analogous to Cup Converter in FA2)
        with st.expander("🌲 Interactive Carbon & Tree Offset Simulator", expanded=False):
            render_html("""
            <div class="sim-card">
                <h4 style="margin: 0; color: #34d399;">🧮 Instant Ecological Footprint & Offset Simulator</h4>
                <p style="font-size: 0.88rem; color: #94a3b8; margin: 0.3rem 0 0.8rem 0;">Test hypothetical shopping budgets and compute car miles, phone recharges, and tree sequestration equivalents.</p>
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
                render_html(f"""
                <div style="background: #13271c; border: 1.5px solid #2d6a4f; border-radius: 12px; padding: 1rem; color: #f8fafc;">
                    <div style="font-size: 0.85rem; color: #94a3b8;">Estimated Carbon Footprint:</div>
                    <div style="font-size: 1.8rem; font-weight: 800; color: #34d399;">{sim_co2:.2f} kg CO₂e</div>
                    <div style="font-size: 0.82rem; margin-top: 0.5rem; line-height: 1.5;">
                        🚗 ~<strong>{s_miles:,}</strong> petrol car miles<br>
                        📱 ~<strong>{s_charges:,}</strong> smartphone recharges<br>
                        🌲 ~<strong>{s_trees}</strong> tree-months of sequestration
                    </div>
                </div>
                """)
                if st.button("➕ Add Simulated Item to Tracker", width="stretch"):
                    sim_item = {
                        "id": len(st.session_state.purchases) + 1,
                        "item": f"Simulated: {sim_cat_choice.split()[0]} (${sim_dollars:.0f})",
                        "category": sim_cat_choice,
                        "brand": "Simulation Tool",
                        "price": float(sim_dollars),
                        "carbon_kg": float(sim_co2),
                        "date": str(date.today()),
                        "is_ethical": sim_is_eth,
                    }
                    st.session_state.purchases.append(sim_item)
                    st.session_state.last_logged = sim_item
                    st.session_state.mascot_mood = "happy" if sim_is_eth else "mindful"
                    st.session_state.mascot_message = f"Simulated purchase recorded! {sim_dollars:.0f}$ logged at {sim_co2:.1f} kg CO₂e."
                    st.rerun()

        # CONTEXTUAL GREENER SWAPS (Appears reactively right after a purchase is logged)
        if st.session_state.last_logged:
            last = st.session_state.last_logged
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader(f"🌱 Greener Alternatives for '{last['item']}' ({last['category']})")
            
            sc1, sc2 = st.columns([1.1, 2.0], gap="medium")
            with sc1:
                render_html(render_animated_avatar_svg(st.session_state.user_mascot, "happy", 130, 130))
                st.caption(f"💡 **{c_name}'s Insight**: You logged **{last['carbon_kg']} kg CO₂e**. Adopting a verified circular swap can reduce emissions by up to 92%!")
                st.markdown(f"<div style='font-size: 0.82rem; font-style: italic; color: #94a3b8; margin-top: 0.4rem;'>{random.choice(SUSTAINABILITY_QUOTES)}</div>", unsafe_allow_html=True)
            
            with sc2:
                swaps = ETHICAL_ALTERNATIVES.get(last["category"], [])
                sw_cols = st.columns(len(swaps))
                for idx, sw in enumerate(swaps):
                    with sw_cols[idx]:
                        render_html(f"""
                        <div class="swap-card">
                            <strong>{sw['brand']}</strong><br>
                            <span style="font-size: 0.85rem;">{sw['perk']}</span><br>
                            <span style="color: #34d399; font-weight: 700; font-size: 0.82rem;">⚡ Carbon Cut: {sw['saving']}</span>
                        </div>
                        """)
                        b_name = sw['brand'].split('/')[0].strip()
                        if st.button(f"Adopt {b_name} 🌿", key=f"adopt_swap_{idx}", width="stretch"):
                            swap_co2 = calculate_carbon(35.0, last['category'], True)
                            st.session_state.purchases.append({
                                "id": len(st.session_state.purchases) + 1,
                                "item": f"Greener Swap: {b_name} ({last['category']})",
                                "category": last['category'],
                                "brand": b_name,
                                "price": 35.0,
                                "carbon_kg": swap_co2,
                                "date": str(date.today()),
                                "is_ethical": True,
                            })
                            st.session_state.mascot_mood = "ecstatic"
                            st.session_state.mascot_message = f"LEGENDARY CHOICE! You adopted {b_name}! {c_name} celebrates your active biosphere restoration!"
                            st.session_state.recent_art = "badge"
                            st.balloons()
                            st.rerun()

        st.markdown("---")

        # PERIOD FILTER & TRANSACTION LEDGER
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
                st.dataframe(df_view, width="stretch", hide_index=True)
                
                # Undo Last Purchase and CSV Download row
                u_col1, u_col2 = st.columns(2)
                with u_col1:
                    if st.button("↩️ Undo Last Purchase", width="stretch", help="Roll back the most recent logged purchase"):
                        popped = st.session_state.purchases.pop()
                        st.session_state.last_logged = st.session_state.purchases[-1] if st.session_state.purchases else None
                        st.toast(f"Removed '{popped['item']}' from ledger", icon="↩️")
                        st.rerun()
                with u_col2:
                    st.download_button("📥 Export CSV", df_view.to_csv(index=False).encode("utf-8"), f"shopimpact_{period_label.lower().replace(' ', '_')}.csv", "text/csv", width="stretch")
            else:
                st.caption("No records available to export. Your recorded purchases will appear here.")

    # --------------------------------------------------------------------------
    # VIEW: 🏆 WALL OF BADGES
    # --------------------------------------------------------------------------
    elif st.session_state.nav_view == "🏆 Wall of Badges":
        st.title("🏆 Wall of Badges & Eco Fame")
        st.caption("Unlocked achievements glow in vibrant emerald color. Locked badges stay in monochrome black & white until earned!")

        badges, _, _, _, _, _ = evaluate_badges(st.session_state.purchases)
        unlocked_num = sum(1 for b in badges if b["unlocked"])

        st.metric("Badges Unlocked", f"{unlocked_num} of {len(badges)}", f"{int((unlocked_num/len(badges))*100)}% Complete")
        st.markdown("<br>", unsafe_allow_html=True)

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

st.divider()
render_html("""
<div style="text-align: center; color: #94a3b8; font-size: 0.8rem; padding: 0.8rem 0;">
    <strong>ShopImpact Conscious Shopping Dashboard</strong> • IDAI 102: Python Programming<br>
    Candidate: <strong>Parth Pravinbhai Gajera</strong> (ID: <code>1000544</code>) • CRS: Artificial Intelligence
</div>
""")
