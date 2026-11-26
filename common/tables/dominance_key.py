"""The order of every displayed attribute in the 34 corpus tables as the controlled test shows them (spec rows after scrub.py; no
description line), and the verdict each table's best product earns under strict dominance.

Gate a (gates.py) reads the rendered prompt, compares the best product with every other product on each displayed
attribute under these rules, and refuses a table whose computed verdict differs from the verdict written here, or whose
prompt shows an attribute that is not written here.

Rules (the value is the text shown after "key: " in the prompt):
  ("hi",)            a number, more is better; units converted (TB to GB, kg/oz/lbs to g, days to hours); a value with
                     no number counts as not stated
  ("lo",)            a number, less is better
  ("hi", "count")    a number whose unit words vary (425 phase-detect, 1053 point); the number alone is compared
  ("rank", {...})    an order written by hand, higher is better; a shown value missing from the map is refused
  ("set",)           a list split on "/"; the best product's list must hold every item of the other product's list
  ("ip",)            an IP code; dust digit and water digit each at least as high (X counts as 0)
  ("pref",)          no order: a matter of preference or of the buyer's use; the values must be equal
An attribute shown for the best product and not for another counts in the best product's favour; an attribute shown for
another product and not for the best breaks dominance. Price is checked apart: the best product's price must be at
most every other price (the price ladder holds that by construction). Reviews and the supplied information must be
equal across the products.

The rank orders are written here, by hand, with the reason beside each; a second reader classified the same
tables independently (study1b-64-models-on-34-tables/materials/attribute_rulings.csv), and the two readings are compared before any claim rests on the dominant set.
"""

DOM = "dominant"
WD = "weight-dependent"

HDR_RANK = {"Dolby Vision IQ/HDR10+": 4, "Dolby Vision/HDR10+": 3, "Dolby Vision/HDR10": 2, "HDR10+": 2, "HDR10/HLG": 1,
            "HDR10": 1}  # each listed format set holds the ones below it, apart from HLG (a broadcast format)

KEY = {
    "sr_laptops_01": {"verdict": WD, "attrs": {
        "cpu": ("rank", {"Ryzen 7 7840U": 3, "Ryzen 7 7730U": 2, "Ryzen 5 7530U": 1, "i5-1335U": 1}),  # by generation and core count
        "ram": ("hi",), "storage": ("hi",), "display": ("pref",), "battery": ("hi",)}},
    "sr_laptops_02": {"verdict": WD, "attrs": {
        "cpu": ("pref",),  # an ARM chip against x86 chips has no order without the buyer's use
        "ram": ("hi",), "storage": ("hi",), "display": ("pref",), "battery": ("hi",), "weight": ("lo",)}},
    "sr_laptops_03": {"verdict": WD, "attrs": {
        "cpu": ("pref",),  # i7-1195G7 (4 cores) against i5-1235U (10 cores): no order
        "ram": ("hi",), "storage": ("hi",), "display": ("pref",), "battery": ("hi",)}},
    "sr_smartphones_01": {"verdict": WD, "attrs": {
        "camera": ("pref",), "storage": ("hi",), "battery": ("hi",), "charging": ("hi",), "display": ("pref",)}},
    "sr_smartphones_02": {"verdict": WD, "attrs": {
        "camera": ("rank", {"64MP triple OIS": 3, "50MP triple": 2, "50MP OIS": 2, "64MP": 2, "12MP": 1}),  # megapixels, lenses and stabilisation each at least as high
        "storage": ("hi",), "battery": ("hi",), "charging": ("hi",), "display": ("pref",)}},
    "sr_smartphones_03": {"verdict": WD, "attrs": {
        "camera": ("pref",),  # one 200MP lens against three 50MP lenses: no order
        "storage": ("hi",), "battery": ("hi",), "charging": ("hi",)}},
    "sr_tvs_01": {"verdict": WD, "attrs": {
        "size": ("pref",), "resolution": ("pref",),
        "panel": ("pref",),  # IPS against VA trades viewing angle for contrast
        "hdr": ("rank", HDR_RANK), "refresh": ("hi",), "brightness": ("hi",)}},
    "sr_tvs_02": {"verdict": DOM, "attrs": {
        "size": ("pref",), "resolution": ("pref",),
        "panel": ("rank", {"Mini-LED Quantum Dot": 3, "Mini-LED QLED": 3, "Mini LED": 2, "Quantum Dot LED": 2,
                           "Full Array LED": 1}),  # local-dimming backlight and quantum-dot colour each count
        "hdr": ("rank", HDR_RANK), "refresh": ("hi",), "brightness": ("hi",), "dimming_zones": ("hi",)}},
    "sr_tvs_03": {"verdict": WD, "attrs": {
        "size": ("pref",), "resolution": ("pref",), "panel": ("pref",), "hdr": ("rank", HDR_RANK), "refresh": ("hi",)}},
    "sr_headphones_01": {"verdict": WD, "attrs": {
        "anc": ("hi",), "battery": ("hi",), "driver": ("pref",), "codec": ("set",), "weight": ("lo",)}},
    "sr_headphones_02": {"verdict": WD, "attrs": {
        "type": ("pref",), "battery": ("hi",), "driver": ("pref",), "codec": ("set",), "weight": ("lo",)}},
    "sr_headphones_03": {"verdict": WD, "attrs": {
        "type": ("pref",), "battery": ("hi",), "driver": ("pref",), "codec": ("pref",), "impedance": ("pref",)}},
    "sr_running_shoes_01": {"verdict": WD, "attrs": {
        "cushioning": ("pref",), "drop": ("pref",), "weight": ("lo",), "durability": ("hi",)}},
    "sr_running_shoes_02": {"verdict": WD, "attrs": {
        "terrain": ("pref",), "drop": ("pref",), "weight": ("lo",), "traction": ("pref",)}},
    "sr_running_shoes_03": {"verdict": WD, "attrs": {
        "type": ("pref",), "drop": ("pref",), "weight": ("lo",), "durability": ("hi",)}},
    "sr_coffee_makers_01": {"verdict": WD, "attrs": {
        "type": ("pref",), "brew_temp": ("pref",), "capacity": ("pref",), "brew_time": ("lo",), "carafe": ("pref",),
        "pre_infusion": ("pref",), "sca_certified": ("pref",)}},
    "sr_coffee_makers_02": {"verdict": WD, "attrs": {
        "type": ("pref",), "pressure": ("pref",), "grinder": ("pref",), "milk": ("pref",)}},
    "sr_coffee_makers_03": {"verdict": WD, "attrs": {
        "type": ("pref",), "brew_temp": ("pref",), "weight": ("lo",),
        "portable": ("rank", {"yes": 2, "semi": 1}), "pressure": ("hi",)}},
    "sr_earbuds_01": {"verdict": WD, "attrs": {
        "anc": ("pref",),  # -45dB against words with no figure: no order
        "battery": ("hi",), "codec": ("pref",), "ip_rating": ("ip",)}},
    "sr_earbuds_02": {"verdict": WD, "attrs": {
        "anc": ("pref",), "battery": ("hi",), "codec": ("set",), "ip_rating": ("ip",)}},
    "sr_earbuds_03": {"verdict": WD, "attrs": {
        "fit": ("pref",), "battery": ("hi",), "codec": ("set",), "ip_rating": ("pref",)}},  # IPX8 against IP67: no order
    "sr_smartwatches_01": {"verdict": WD, "attrs": {
        "gps": ("rank", {"dual-band 5-system": 2, "multi-band": 2, "L1+L5": 2, "L1": 1, "built-in": 1}),
        "battery": ("hi",),
        "display": ("rank", {'always-on AMOLED 1.39"': 2, "always-on OLED": 2, "AMOLED": 1}),
        "sensors": ("set",)}},
    # dominant since the Dyson's suction in air watts (its maker's own unit, the second reading's finding 1) became "not
    # stated"; before that, pascals against air watts had no order and the table was weight-dependent
    "sr_robot_vacuums_01": {"verdict": DOM, "attrs": {
        "suction": ("hi",),
        "navigation": ("rank", {"LiDAR + 3D AI": 3, "LiDAR 360": 2, "camera + AI": 2, "camera": 1, "bounce": 1}),
        "emptying": ("rank", {"auto + self-wash/dry": 3, "auto (30 bags)": 2, "auto (30 days)": 2, "manual": 1}),
        "runtime": ("hi",)}},
    "sr_portable_speakers_01": {"verdict": WD, "attrs": {
        "waterproof": ("ip",), "battery": ("hi",), "power": ("hi",), "weight": ("lo",)}},
    "sr_keyboards_01": {"verdict": WD, "attrs": {
        "switches": ("pref",), "connectivity": ("pref",), "layout": ("pref",), "features": ("pref",)}},
    "sr_external_ssds_01": {"verdict": WD, "attrs": {
        "capacity": ("hi",), "speed": ("hi",),
        "interface": ("rank", {"USB 3.2 Gen 2x2": 2, "USB 3.2 Gen 2": 1}),
        "durability": ("pref",)}},  # IP68 with a military drop standard against a 3 m drop: no order
    "sr_water_bottles_01": {"verdict": WD, "attrs": {
        "insulation": ("hi",), "material": ("pref",), "capacity": ("hi",), "weight": ("lo",)}},
    "sr_electric_toothbrushes_01": {"verdict": WD, "attrs": {
        "type": ("pref",), "strokes": ("pref",), "battery": ("hi",), "modes": ("hi",),
        "pressure_sensor": ("rank", {"yes": 1, "no": 0}), "display": ("pref",)}},
    "sr_backpacks_01": {"verdict": WD, "attrs": {
        "capacity": ("pref",), "material": ("pref",), "laptop": ("hi",), "weight": ("lo",)}},
    "sr_blenders_01": {"verdict": WD, "attrs": {
        "power": ("hi",), "capacity": ("hi",), "speeds": ("pref",), "blade": ("pref",), "bpa_free": ("pref",)}},
    "sr_wireless_routers_01": {"verdict": DOM, "attrs": {
        "wifi": ("rank", {"WiFi 6E AXE7800 tri-band": 4, "WiFi 6E AXE6600": 3, "WiFi 6E": 2, "WiFi 6 AX5700": 2,
                          "WiFi 6 AX5400": 1}),  # the 6 GHz band, then the rated speed
        "coverage": ("hi",), "devices": ("hi",),
        "ports": ("rank", {"1x 10G + 4x Gigabit + USB 3.0": 4, "1x 5G + 4x Gigabit": 3, "1x 2.5G + 4x Gigabit": 2,
                           "4x Gigabit": 1, "2x Gigabit": 0})}},  # each holds the ports of the ones below it
    "sr_monitors_01": {"verdict": WD, "attrs": {
        "size": ("pref",),
        "resolution": ("rank", {"4K 3840x2160": 2, "QHD 2560x1440": 1}),
        "panel": ("rank", {"Mini-LED IPS": 2, "IPS": 1, "VA": 1}),
        "refresh": ("hi",), "color": ("pref",), "hdr": ("pref",), "stand": ("pref",)}},
    "sr_tablets_01": {"verdict": WD, "attrs": {
        "display": ("pref",), "processor": ("pref",), "storage": ("hi",), "battery": ("hi",), "stylus": ("pref",)}},
    "sr_cameras_01": {"verdict": DOM, "attrs": {
        "sensor": ("hi",),  # megapixels on the same APS-C format
        "af": ("hi", "count"), "video": ("rank", {"4K 60fps": 2, "4K 30fps": 1}), "weight": ("lo",),
        "ibis": ("rank", {"5-axis 6.5 stops": 1, "no": 0})}},
}
