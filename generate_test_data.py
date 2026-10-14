import pandas as pd

# Intentionally messy supplier data: inconsistent column headers and empty fields
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
        "part_number": "SKU-4402",
        "item_name": "HydroShield Waterproof Keyboard",
        "group": "Peripherals",
        "make": "KeyForge",
        "measurement": "44 x 13 x 3.5 cm",
        "net_weight": "850 g",
        "composition": "ABS Plastic, Silicone Gaskets",
        "finish": "Gunmetal Grey",
        "standards": "IP68, CE, FCC",
        "retail_price": 79.50
    },
    {
        "id": "SKU-1189",
        "name": "Precision Digital Vernier Caliper",
        "class": "Measurement Tools",
        "vendor": "ApexMeasure",
        "dims": "25 x 8 x 2 cm",
        "wt": "220 g",
        "material": "Hardened Stainless Steel",
        "color": "Silver / Black",
        "certifications": "NIST Traceable, DIN 862",
        "msrp": 45.00
    }
]

df = pd.DataFrame(data)
df.to_excel("messy_supplier_data.xlsx", index=False)
print("Saved messy_supplier_data.xlsx")