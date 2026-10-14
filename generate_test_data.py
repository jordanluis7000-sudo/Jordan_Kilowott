import pandas as pd
import numpy as np

# Intentionally messy supplier data:
# - Uses non-standard headers (item_code, Title, dept, mfg, size, wt, fabric, shade, safety, cost)
# - Missing critical data (cost, wt) on certain rows to trigger UI compliance errors
data = [
    {
        "item_code": "SKU-9921",
        "Title": "Industrial Ergonomic Task Chair",
        "dept": "Office Furniture",
        "mfg": "SteelWorks",
        "size": "65 x 65 x 110 cm",
        "wt": "14.5 kg",
        "fabric": "Mesh & Reinforced Nylon",
        "shade": "Matte Black",
        "safety": "BIFMA, ISO-9001",
        "cost": 249.99
    },
    {
        "item_code": "SKU-4402",
        "Title": "HydroShield Waterproof Keyboard",
        "dept": "Peripherals",
        "mfg": "KeyForge",
        "size": "44 x 13 x 3.5 cm",
        "wt": "850 g",
        "fabric": "ABS Plastic, Silicone Gaskets",
        "shade": "Gunmetal Grey",
        "safety": "IP68, CE, FCC",
        "cost": 79.50
    },
    {
        "item_code": "SKU-1189",
        "Title": "Precision Digital Vernier Caliper",
        "dept": "Measurement Tools",
        "mfg": "ApexMeasure",
        "size": "25 x 8 x 2 cm",
        "wt": "220 g",
        "fabric": "Hardened Stainless Steel",
        "shade": "Silver / Black",
        "safety": "NIST Traceable, DIN 862",
        "cost": 45.00
    },
    {
        "item_code": "SKU-5099",
        "Title": "UltraView 27-inch 4K Monitor",
        "dept": "Displays",
        "mfg": "VisionTech",
        "size": "61 x 20 x 45 cm",
        "wt": "5.2 kg",
        "fabric": "Aluminum & Recycled Plastic",
        "shade": "Space Gray",
        "safety": "Energy Star, RoHS",
        "cost": None  # Missing to trigger "Base Price" Syndication Blocked error
    },
    {
        "item_code": "SKU-7734",
        "Title": "Vertical Ergonomic Mouse",
        "dept": "Peripherals",
        "mfg": "KeyForge",
        "size": "12 x 8 x 7 cm",
        "wt": "",  # Missing to trigger "Weight" Syndication Blocked error
        "fabric": "Textured Rubber, ABS",
        "shade": "Charcoal",
        "safety": "CE, FCC",
        "cost": 29.99
    },
    {
        "item_code": "SKU-2044",
        "Title": "Dual Motor Standing Desk",
        "dept": "Office Furniture",
        "mfg": "SteelWorks",
        "size": "150 x 75 x 70-120 cm",
        "wt": "35 kg",
        "fabric": "Bamboo Top, Steel Frame",
        "shade": "Natural Wood / White",
        "safety": "UL, BIFMA",
        "cost": 499.00
    },
    {
        "item_code": "SKU-8810",
        "Title": "AeroNoise Cancelling Headphones",
        "dept": "Audio",
        "mfg": "SonicBoom",
        "size": "18 x 15 x 8 cm",
        "wt": "",    # Missing to trigger error
        "fabric": "Vegan Leather, Memory Foam",
        "shade": "Midnight Blue",
        "safety": "FCC, CE",
        "cost": ""   # Missing to trigger double error!
    },
    {
        "item_code": "SKU-3120",
        "Title": "ProConnect 10-in-1 USB-C Hub",
        "dept": "Accessories",
        "mfg": "TechLink",
        "size": "15 x 5 x 1.5 cm",
        "wt": "150 g",
        "fabric": "Anodized Aluminum",
        "shade": "Silver",
        "safety": "RoHS, CE",
        "cost": 59.99
    },
    {
        "item_code": "SKU-6652",
        "Title": "Foldable Aluminum Laptop Stand",
        "dept": "Accessories",
        "mfg": "TechLink",
        "size": "24 x 23 x 0.4 cm",
        "wt": "450 g",
        "fabric": "Aircraft Grade Aluminum",
        "shade": "Matte Silver",
        "safety": "", # Missing safety certs (lowers data health score)
        "cost": 34.50
    },
    {
        "item_code": "SKU-9901",
        "Title": "Lumina True Wireless Earbuds",
        "dept": "Audio",
        "mfg": "SonicBoom",
        "size": "6 x 4 x 2.5 cm (Case)",
        "wt": "45 g",
        "fabric": "Polycarbonate",
        "shade": "Gloss White",
        "safety": "IPX5, CE",
        "cost": 89.00
    }
]

df = pd.DataFrame(data)
df.to_excel("messy_supplier_data.xlsx", index=False)
print(f"Saved messy_supplier_data.xlsx with {len(df)} records!")