import html
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
    "Fast Fashion Apparel": {"multiplier": 0.42, "rating": "High Carbon", "tier": "⚠️ High", "icon": "👗", "fact": "Synthetic polyester spinning and chemical dyeing create heavy industrial footprints."},
    "Footwear & Leather": {"multiplier": 0.65, "rating": "Very High", "tier": "🚨 Heavy", "icon": "👞", "fact": "Bovine cattle methane and chromium tanning drive intense greenhouse gas footprints."},
    "Consumer Electronics": {"multiplier": 0.55, "rating": "High Carbon", "tier": "🚨 Heavy", "icon": "📱", "fact": "Silicon semiconductor fabrication and rare-earth mining account for ~80% of lifecycle CO₂."},
    "Refurbished Tech": {"multiplier": 0.11, "rating": "Low Carbon", "tier": "🌾 Conscious", "icon": "♻️", "fact": "Eliminates virgin mineral extraction; accounts only for diagnostics, parts, and clean transport."},
    "Second-Hand / Thrift": {"multiplier": 0.05, "rating": "Minimal Impact", "tier": "🌿 Ultra-Green", "icon": "🧥", "fact": "Pure circular economy; original manufacturing emissions are 100% amortized."},
    "Packaged Groceries": {"multiplier": 0.38, "rating": "Medium-High", "tier": "⚠️ High", "icon": "🛒", "fact": "Industrial food processing and multi-layer plastic packaging add embodied carbon."},
    "Local / Organic Food": {"multiplier": 0.08, "rating": "Low Carbon", "tier": "🌿 Ultra-Green", "icon": "🥗", "fact": "Zero long-haul air freight and regenerative organic soil practices without synthetic nitrates."},
    "Home & Plastics": {"multiplier": 0.46, "rating": "High Carbon", "tier": "⚠️ High", "icon": "📦", "fact": "Virgin petroleum feedstocks and high-temperature molding drive lifecycle footprint."},
    "Zero-Waste Reusables": {"multiplier": 0.07, "rating": "Minimal Impact", "tier": "🌿 Ultra-Green", "icon": "🌿", "fact": "Durable steel and bamboo displace hundreds of single-use disposable plastics."},
}

ETHICAL_ALTERNATIVES = {
    "Fast Fashion Apparel": [
        {"brand": "Patagonia", "perk": "100% organic cotton, Fair Trade sewing & free lifelong repairs", "saving": "65%"},
        {"brand": "Depop / Thrift", "perk": "Extends existing garment life; zero new factory emissions", "saving": "92%"},
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
        {"brand": "Local Community Thrift", "perk": "Top-tier circular reuse; zero new factory footprint", "saving": "Optimal"},
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
    
    svg = f"""<svg width="{width}" height="{height}" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg" style="max-width: 100%; height: auto;">
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

# Backwards compatibility alias
render_animated_turtle_svg = render_animated_avatar_svg

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
        return f"Recorded '{item_name}' ({live_co2} kg CO₂e). {name} notes a balanced choice. Take a look at greener swaps below!"
    elif mood == "worried":
        return f"Whew, getting heavy! '{item_name}' generated {live_co2} kg CO₂e. {name} feels the carbon heat!"
    else:  # alarmed
        return f"🚨 CARBON SPIKE ALERT! That single item created {live_co2} kg CO₂e! {name} is shivering! Adopt a greener swap below to balance your budget!"

class HeadlessTurtle:
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
    t = HeadlessTurtle(220, 220)
    if art_type == "leaf":
        t.penup(); t.goto(110, 195); t.heading = 90; t.color = (64, 145, 108, 255); t.pendown(); t.forward(30)
        t.color = (45, 106, 79, 255); t.arc(80, 58); t.left(122); t.arc(80, 58)
        t.penup(); t.goto(110, 165); t.heading = 90; t.color = (82, 183, 136, 255); t.width = 2; t.pendown(); t.forward(70)
        for y, ang in [(140, 45), (140, 135), (115, 45), (115, 135), (90, 45), (90, 135)]:
            t.penup(); t.goto(110, y); t.heading = ang; t.pendown(); t.forward(15)
    elif art_type == "footprint":
        t.penup(); t.goto(110, 185); t.heading = 90; t.color = (45, 106, 79, 255); t.pendown()
        t.arc(50, 40); t.arc(18, -50); t.arc(42, 70); t.arc(26, 90); t.arc(62, 45); t.arc(24, 80); t.goto(110, 185)
        for tx, ty, r in [(95, 68, 6), (106, 58, 8), (118, 60, 7), (129, 65, 5), (138, 73, 4)]:
            t.draw.ellipse([(tx-r, ty-r), (tx+r, ty+r)], fill=(82, 183, 136, 220), outline=(45, 106, 79, 255), width=2)
    else:  # badge rosette
        t.draw.ellipse([(65, 48), (155, 138)], fill=(254, 243, 199, 240), outline=(217, 119, 6, 255), width=3)
        t.draw.ellipse([(77, 60), (143, 126)], fill=(236, 253, 245, 240), outline=(5, 150, 105, 255), width=2)
        t.penup(); t.goto(92, 134); t.heading = 250; t.pendown(); t.color = (5, 150, 105, 255)
        t.forward(40); t.left(120); t.forward(16); t.left(120); t.forward(36)
        t.penup(); t.goto(128, 134); t.heading = 290; t.pendown()
        t.forward(40); t.right(120); t.forward(16); t.right(120); t.forward(36)
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

# Session state initialization - Starts completely CLEAN with zero seed data, Dark Mode by default
if "dark_theme" not in st.session_state: st.session_state.dark_theme = True
if "onboarded" not in st.session_state: st.session_state.onboarded = False
if "user_name" not in st.session_state: st.session_state.user_name = "Parth Gajera"
if "user_mascot" not in st.session_state: st.session_state.user_mascot = "Shelly the Sea Turtle 🐢"
if "carbon_budget" not in st.session_state: st.session_state.carbon_budget = 150
if "recent_art" not in st.session_state: st.session_state.recent_art = None
if "mascot_mood" not in st.session_state: st.session_state.mascot_mood = "mindful"
if "mascot_message" not in st.session_state:
    st.session_state.mascot_message = "Welcome! I am your eco companion. I react live to every purchase you make and guide you toward greener habits!"
if "nav_view" not in st.session_state: st.session_state.nav_view = "📊 Dashboard"
if "last_logged" not in st.session_state: st.session_state.last_logged = None
if "purchases" not in st.session_state: st.session_state.purchases = []

# Apply Comprehensive Dual-Theme Styling (Default: High-Contrast Dark Mode)
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
    .reaction-bubble { border-radius: 14px; padding: 1rem 1.3rem; border: 1.5px solid #34d399; background: #162a1e; color: #f8fafc; }
    .avatar-card { display: flex; flex-direction: column; align-items: center; justify-content: center; margin-bottom: 1.2rem; text-align: center; }
    .avatar-circle { width: 92px; height: 92px; border-radius: 50%; border: 3px solid #34d399; overflow: hidden; background: #13271c; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 16px rgba(52, 211, 153, 0.3); margin: 0 auto; }
    .rank-pill { font-size: 0.8rem; background: #064e3b; color: #34d399; border: 1px solid #059669; padding: 0.2rem 0.65rem; border-radius: 99px; font-weight: 700; display: inline-block; margin-top: 0.35rem; }
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
    .reaction-bubble { border-radius: 14px; padding: 1rem 1.3rem; border: 1.5px solid #86efac; background: #f0fdf4; color: #14532d; }
    .avatar-card { display: flex; flex-direction: column; align-items: center; justify-content: center; margin-bottom: 1.2rem; text-align: center; }
    .avatar-circle { width: 92px; height: 92px; border-radius: 50%; border: 3px solid #10b981; overflow: hidden; background: #ecfdf5; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 14px rgba(16, 185, 129, 0.2); margin: 0 auto; }
    .rank-pill { font-size: 0.8rem; background: #ecfdf5; color: #047857; border: 1px solid #10b981; padding: 0.2rem 0.65rem; border-radius: 99px; font-weight: 700; display: inline-block; margin-top: 0.35rem; }
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
                <li>⚡ <strong>Lifecycle Multiplier Engine:</strong> scientific emissions factors by category</li>
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

    if st.sidebar.button("⚙️ Edit Profile / Avatar", width="stretch"):
        st.session_state.onboarded = False
        st.rerun()

    st.sidebar.markdown("---")
    st.session_state.nav_view = st.sidebar.radio("Navigation:", ["📊 Dashboard", "🏆 Wall of Badges"])

    dark_toggle = st.sidebar.toggle("🌙 High-Contrast Dark Mode", value=st.session_state.dark_theme)
    if dark_toggle != st.session_state.dark_theme:
        st.session_state.dark_theme = dark_toggle
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.caption(f"💡 *{random.choice(ECO_TIPS)}*")

    if st.sidebar.button("🗑️ Reset / Clear All Purchases", width="stretch"):
        st.session_state.purchases = []
        st.session_state.last_logged = None
        st.session_state.recent_art = None
        st.session_state.mascot_mood = "mindful"
        c_name = st.session_state.user_mascot.split()[0]
        st.session_state.mascot_message = f"All purchases cleared. {c_name} is ready for your first eco-conscious log!"
        st.rerun()

    # --------------------------------------------------------------------------
    # VIEW: 📊 DASHBOARD
    # --------------------------------------------------------------------------
    if st.session_state.nav_view == "📊 Dashboard":
        c_name = st.session_state.user_mascot.split()[0]
        msg_esc = html.escape(st.session_state.mascot_message)

        # Interactive Mascot Reaction & Optional Turtle Graphic Reward
        if st.session_state.recent_art:
            col_m1, col_m2, col_m3 = st.columns([0.65, 2.35, 1.0])
            with col_m1:
                render_html(render_animated_avatar_svg(st.session_state.user_mascot, st.session_state.mascot_mood, 140, 140))
            with col_m2:
                render_html(f"""
                <div class="reaction-bubble">
                    <div style="font-size: 1.1rem; font-weight: 800;">{c_name}'s Live Reaction:</div>
                    <div style="font-size: 0.95rem; margin-top: 0.2rem;">"{msg_esc}"</div>
                </div>
                """)
            with col_m3:
                art_img = draw_vector_art(st.session_state.recent_art)
                art_label = {"leaf": "Eco Leaf 🌿", "footprint": "Low Footprint 👣", "badge": "Eco Badge ⭐"}.get(st.session_state.recent_art, "Eco Choice")
                st.image(art_img, width=130, caption=f"Shelly drew: {art_label}")
        else:
            col_m1, col_m2 = st.columns([0.65, 3.35])
            with col_m1:
                render_html(render_animated_avatar_svg(st.session_state.user_mascot, st.session_state.mascot_mood, 140, 140))
            with col_m2:
                render_html(f"""
                <div class="reaction-bubble">
                    <div style="font-size: 1.1rem; font-weight: 800;">{c_name}'s Live Reaction:</div>
                    <div style="font-size: 0.95rem; margin-top: 0.2rem;">"{msg_esc}"</div>
                </div>
                """)

        st.markdown("<br>", unsafe_allow_html=True)

        # Log a Purchase Form
        st.subheader("🛒 Log a Planned Purchase")
        st.caption("Record purchases into your active ledger. Certified circular goods receive an automatic 30% footprint discount.")

        with st.form("quick_log_form", clear_on_submit=True):
            f1, f2, f3 = st.columns([1.2, 1.2, 1.0])
            with f1:
                item_name = st.text_input("Item Description (Required)", placeholder="e.g. Vintage Denim Jacket, USB Charger")
                cat_choice = st.selectbox("Product Category (Required)", options=list(CATEGORIES.keys()))
            with f2:
                brand_val = st.text_input("Brand or Vendor (Optional)", placeholder="e.g. Patagonia, Zara, Back Market")
                price_val = st.number_input("Purchase Price ($) (Required)", min_value=1.0, max_value=5000.0, value=45.0, step=5.0)
            with f3:
                date_val = st.date_input("Purchase Date (Required)", value=date.today())
                is_eth = st.checkbox("🌱 Certified Circular / Thrift / Ethical (Optional)", help="Applies a 30% footprint discount: accounts for avoiding raw extraction and virgin factory manufacturing.")

            # Dynamic Actionable Eco Tip & Category Insight Box (Replaces old estimate pill)
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
                    
                    # 5-Stage Multi-Level Mascot Reaction Engine with Avatar Personalization
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

        # Explanatory Standard Guide Expander
        with st.expander("ℹ️ Understanding Carbon Standards & Scoring Logic", expanded=False):
            st.markdown(
                r"""
                ShopImpact uses calibrated lifecycle assessment (LCA) standards based on GHG Protocol and DEFRA data:
                - **🌿 Ultra-Green (≤ 0.10 kg/$)**: Second-Hand, Community Thrift, Zero-Waste Reusables, Organic Local Food. Original manufacturing emissions are amortized.
                - **🌾 Conscious (0.11 - 0.35 kg/$)**: Certified Refurbished Electronics, repairable modular tech, bulk pantry foods.
                - **⚠️ High Carbon (0.36 - 0.50 kg/$)**: Fast fashion apparel, virgin single-use plastics, multi-layer packaged foods.
                - **🚨 Carbon Heavy (> 0.50 kg/$)**: Virgin leather footwear, new flagship consumer electronics with intensive silicon semiconductor manufacturing.
                - **🌱 Certified Circular Tag**: Bypasses virgin mining/processing, applying an automatic 30% emissions reduction credit.
                """
            )

        # Contextual Greener Swaps: Appears reactively right after a purchase is logged
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
                        if st.button(f"Adopt {b_name} 🌿", key=f"adopt_swap_{idx}"):
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

        badges, spend_tot, co2_tot, avg_int, saved_tot, eth_cnt = evaluate_badges(filtered_data)
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
        pct = min(100, max(0, int((co2_tot / b_lim) * 100))) if b_lim > 0 else 0
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
                st.dataframe(df_view, width="stretch", hide_index=True)
                st.download_button("📥 Export CSV", df_view.to_csv(index=False).encode("utf-8"), f"shopimpact_{period_label.lower().replace(' ', '_')}.csv", "text/csv")
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
    <strong>ShopImpact Conscious Shopping Dashboard</strong> • Summative Assessment (60 Marks)<br>
    Candidate: <strong>Parth Pravinbhai Gajera</strong> (ID: <code>1000544</code>) • CRS: Artificial Intelligence • IDAI 102
</div>
""")
