"""What the controlled test changes in the spec rows of the 34 corpus tables, in every version alike, and the lists that the
names-hidden gate (gates.py, gate b) refuses.

A spec value is replaced only when it names a brand, a brand's own trademarked feature, or a brand's chip, or when it
is advertising text; the replacement keeps the measured part of the value and drops the trade name. The same
replacement is shown with names shown and with names hidden, so the two versions of a table still differ only in the
Name and Brand lines. Keys are the table id, then the product's letter in experiment/assortments.py (before the
letters are shuffled), then the spec key.
"""

SCRUB = {
    "sr_laptops_02": {
        "B": {"cpu": "8-core ARM chip", "display": '13.6" IPS'},          # Apple M2, Liquid Retina
    },
    "sr_smartphones_01": {
        "D": {"camera": "50MP"},                                            # Sony IMX890 (a Sony part)
        "E": {"camera": "50MP dual OIS"},                                   # Sony IMX890
    },
    "sr_smartphones_02": {
        "A": {"display": '6.4" AMOLED 120Hz'},                              # Super AMOLED (Samsung)
        "B": {"display": '6.7" OLED 144Hz'},                                # pOLED (Motorola)
        "E": {"display": '4.7" LCD'},                                       # Retina HD (Apple)
    },
    "sr_tvs_01": {
        "B": {"hdr": "HDR10"},                                              # HDR10 Pro (LG)
    },
    "sr_tvs_02": {
        "A": {"panel": "Mini-LED QLED"},                                    # Neo QLED (Samsung)
        "B": {"panel": "Quantum Dot LED"},                                  # QNED, NanoCell (LG)
    },
    "sr_headphones_03": {
        "D": {"driver": "45mm dynamic"},                                    # STELLAR.45 (Beyerdynamic)
    },
    "sr_running_shoes_01": {
        "A": {"cushioning": "EVA-blend foam"},                              # ReactX (Nike)
        "B": {"cushioning": "TPU-bead foam"},                               # BOOST (Adidas)
        "C": {"cushioning": "EVA-blend foam"},                              # FF BLAST PLUS (ASICS)
        "D": {"cushioning": "EVA foam"},                                    # Fresh Foam X (New Balance)
    },
    "sr_running_shoes_02": {
        "B": {"traction": "rubber lugs"},                                   # Contagrip MA (Salomon)
        "E": {"traction": "sticky rubber"},                                 # TrailTack (Brooks)
    },
    "sr_coffee_makers_02": {
        "A": {"pressure": "N/A (centrifugal)"},                             # Centrifusion (Nespresso)
        "E": {"milk": "auto frother"},                                      # LatteGo (Philips)
    },
    "sr_earbuds_01": {
        "A": {"anc": "adaptive"},                                           # "2x improvement" (advertising text)
        "B": {"codec": "proprietary/AAC"},                                  # SSC (Samsung Seamless Codec)
        "C": {"anc": "adaptive"},                                           # "industry leading" (advertising text)
    },
    "sr_earbuds_02": {
        "C": {"anc": "-50dB"},                                              # QuietSmart 3.0 (EarFun, the real brand behind Sonance)
    },
    "sr_earbuds_03": {
        "B": {"fit": "twist-in"},                                           # TwistLock (JBL)
    },
    "sr_smartwatches_01": {
        "B": {"sensors": "multi-sensor/ECG", "display": "AMOLED"},          # BioActive, Super AMOLED (Samsung)
        "C": {"sensors": "SpO2/nap/energy score"},                          # Body Battery (Garmin)
    },
    "sr_portable_speakers_01": {
        "B": {"power": "N/A"},                                              # "N/A (Bose)" prints the brand
    },
    "sr_keyboards_01": {
        "A": {"switches": "tactile quiet", "connectivity": "BT/2.4GHz receiver/USB"},   # Logitech proprietary, Logi Bolt
        "B": {"switches": "clicky (green)"},                                # Razer Green
        "D": {"features": "8000Hz/software/RGB"},                           # iCUE (Corsair)
        "E": {"switches": "linear (red)"},                                  # HyperX Red
    },
    "sr_blenders_01": {
        "B": {"speeds": "3 + auto programs"},                               # Auto-iQ (Ninja)
    },
    "sr_tablets_01": {
        "A": {"display": '10.9" IPS', "processor": "hexa-core"},             # Liquid Retina, A14 Bionic (Apple)
        "B": {"processor": "octa-core"},                                    # Exynos 1380 (Samsung)
    },
    "sr_cameras_01": {
        "A": {"af": "hybrid phase-detect AF"},                              # Dual Pixel CMOS AF II (Canon)
        "C": {"sensor": "26.1MP APS-C"},                                    # X-Trans (Fujifilm)
    },
}
# Added after the second reading of the tables (20 November 2026, 6:42 PM Central): spec values that name a
# maker's own feature, unit or method, by confidence. Merged into SCRUB below.
SCRUB_LANE1 = {
    "sr_robot_vacuums_01": {"D": {"navigation": "camera", "suction": "not stated"}},   # 360 Vis Nav; Dyson's air watts
    "sr_earbuds_02": {"D": {"anc": "none"}},                                # Adaptive Sound (Google Pixel Buds)
    "sr_smartphones_01": {"C": {"camera": "50MP"}},                         # Octa PD (Google Pixel 8)
    "sr_earbuds_03": {"E": {"fit": "ear fin"},                              # Arc Supporter (Sony)
                      "A": {"fit": "ear wing"}},                            # wingtip (Beats), low confidence
    "sr_coffee_makers_02": {"A": {"pressure": "N/A"}},                      # centrifugal: the Nespresso Vertuo method
    "sr_smartwatches_01": {"E": {"sensors": "ECG/stress/SpO2"}},            # EDA (Fitbit), low confidence
    "sr_headphones_02": {"C": {"driver": "40mm"}},                          # DLC (Soundcore, behind Sonique), low
    "sr_running_shoes_02": {"D": {"traction": "rubber compound"},           # graphene (inov-8, behind Terravolt), low
                            "C": {"traction": "sticky rubber lugs"}},       # Vibram Megagrip (a component maker)
    "sr_keyboards_01": {"D": {"switches": "linear (red)"},                  # Cherry MX Red (a component maker)
                        "C": {"switches": "pre-lubed tactile (hot-swap)"}},  # Cherry MX compatible
}
for _t, _prods in SCRUB_LANE1.items():
    for _letter, _vals in _prods.items():
        SCRUB.setdefault(_t, {}).setdefault(_letter, {}).update(_vals)

# Trade names and chip names that identify a brand. Gate b refuses a names-hidden prompt that holds any of them; the
# scrub above removes every one that the 34 tables print in their spec rows. Matched case-sensitively, whole words.
TRADEMARKS = [
    "Liquid Retina", "Retina", "Bionic", "Apple M2", "M2", "Super AMOLED", "pOLED", "Neo QLED", "QNED", "NanoCell",
    "HDR10 Pro", "STELLAR", "ReactX", "BOOST", "FF BLAST", "Fresh Foam", "Contagrip", "TrailTack", "Centrifusion",
    "centrifusion", "LatteGo", "SSC", "QuietSmart", "TwistLock", "twistlock", "BioActive", "Body Battery", "Razer",
    "HyperX", "iCUE", "Bolt", "Auto-iQ", "Exynos", "Tensor", "Dual Pixel", "X-Trans", "IMX890", "Galaxy", "Sonicare",
    "AirPods", "MagSafe", "Roomba", "Nighthawk", "Inspiron", "Pavilion", "VivoBook", "IdeaPad", "MacBook", "XPS",
    # the second reading
    "360 vision", "AW", "Octa PD", "adaptive sound", "Adaptive Sound", "arc support", "centrifugal", "wingtip", "EDA",
    "DLC", "graphene", "graphene-enhanced", "Cherry", "Vibram", "Megagrip",
]

# Advertising text: phrases that praise a product without a measured value. Gate b refuses them in a names-hidden
# prompt (matched case-insensitively).
AD_PHRASES = [
    "trusted name", "industry leading", "industry-leading", "legendary", "iconic", "reliability", "best-in-class",
    "world-class", "premium", "ecosystem", "2x improvement", "award-winning", "no markups", "professional-grade",
    "military-grade", "american icon", "audiophile-grade",
]
