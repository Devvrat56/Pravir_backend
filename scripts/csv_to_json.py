import pandas as pd
import json
import re
from bs4 import BeautifulSoup

def clean_text(text):
    if pd.isna(text):
        return ""
    if isinstance(text, str):
        # Remove HTML tags
        text = BeautifulSoup(text, "html.parser").get_text()
        # Replace multiple whitespaces with a single space
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    return text

def convert_to_structured_json(csv_path, json_path):
    # Load the CSV
    df = pd.read_csv(csv_path)

    # Clean all string columns
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].apply(clean_text)

    # Group by Product ID to consolidate variants
    products_list = []
    
    # Grouping by the main product attributes
    grouped = df.groupby(['Product ID', 'Title', 'Handle', 'Vendor', 'Product Type'])

    for (p_id, title, handle, vendor, p_type), group in grouped:
        variants = []
        tags = []
        if pd.notna(group.iloc[0]['Tags']):
            tags = [t.strip() for t in str(group.iloc[0]['Tags']).split(',')]

        for _, row in group.iterrows():
            variants.append({
                "variant_title": row['Variant Title'],
                "price": float(row['Price']) if pd.notna(row['Price']) else 0.0,
                "compare_at_price": float(row['Compare at Price']) if pd.notna(row['Compare at Price']) else None,
                "sku": row['SKU'] if pd.notna(row['SKU']) else None,
                "available": str(row['Available']).lower() == 'true',
                "weight_grams": float(row['Weight (grams)']) if pd.notna(row['Weight (grams)']) else 0.0
            })

        product_entry = {
            "product_id": str(p_id),
            "title": title,
            "handle": handle,
            "vendor": vendor,
            "product_type": p_type,
            "tags": tags,
            "primary_image": group.iloc[0]['Primary Image'],
            "variants": variants
        }
        products_list.append(product_entry)

    # Save to JSON
    with open(json_path, 'w') as f:
        json.dump(products_list, f, indent=4)

    print(f"Successfully created structured JSON with {len(products_list)} products in {json_path}")

if __name__ == "__main__":
    convert_to_structured_json("products.csv", "product.json")
