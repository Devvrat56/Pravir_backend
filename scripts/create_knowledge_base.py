import pandas as pd
import re
from bs4 import BeautifulSoup
import json
import os

# ---------- CLEAN FUNCTION ----------
def clean_text(text):
    if pd.isna(text):
        return ""
    text = BeautifulSoup(str(text), "html.parser").get_text()
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# ---------- GENERIC TRANSFORM ----------
def transform_dataframe(df, data_type):
    records = []

    for _, row in df.iterrows():
        row = row.fillna("")

        record = {
            "type": data_type,
            "name": "",
            "category": "",
            "description": "",
            "price": "",
            "source": "",
            "metadata": {}
        }

        # Try mapping intelligently
        for col in df.columns:
            value = clean_text(row[col])

            col_lower = col.lower()

            if "name" in col_lower or "title" in col_lower:
                record["name"] = value

            elif "desc" in col_lower:
                record["description"] += " " + value

            elif "price" in col_lower:
                record["price"] = value

            elif "category" in col_lower:
                record["category"] = value

            elif "url" in col_lower:
                record["source"] = value

            else:
                record["metadata"][col] = value

        # fallback if name missing
        if not record["name"]:
            record["name"] = record["description"][:50]

        records.append(record)

    return records

# ---------- LOAD FILES ----------
# Note: Paths updated to 'scraped_data/' to match the local directory structure
files = {
    "scraped_data/products_Topper.csv": "product",
    "scraped_data/products_Unknown.csv": "product",
    "scraped_data/services.csv": "service",
    "scraped_data/policies.csv": "policy"
}

all_records = []

for file, dtype in files.items():
    if not os.path.exists(file):
        print(f"⚠️ Warning: File not found: {file}")
        continue
        
    print(f"Processing {file}...")
    df = pd.read_csv(file)
    
    # Handling deprecated applymap in newer pandas versions
    if hasattr(df, 'map'):
        df = df.map(clean_text)
    else:
        df = df.applymap(clean_text)
    
    transformed = transform_dataframe(df, dtype)
    all_records.extend(transformed)

# ---------- SAVE JSON ----------
with open("knowledge_base.json", "w", encoding="utf-8") as f:
    json.dump(all_records, f, indent=2, ensure_ascii=False)

print("✅ JSON created successfully")
