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

def transform_to_json(csv_path, json_path):
    # Load the CSV
    df = pd.read_csv(csv_path)

    # Clean all string columns
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].apply(clean_text)

    # Group by Product ID to consolidate variants
    products_json = []
    
    # We use Handle or Product ID as the unique identifier
    grouped = df.groupby(['Product ID', 'Title', 'Handle', 'Vendor', 'Product Type'])

    for (p_id, title, handle, vendor, p_type), group in grouped:
        variants = []
        tags = []
        if pd.notna(group.iloc[0]['Tags']):
            tags = [t.strip() for t in str(group.iloc[0]['Tags']).split(',')]

        for _, row in group.iterrows():
            variants.append({
                "variant_title": row['Variant Title'],
                "price": row['Price'],
                "sku": row['SKU'],
                "available": row['Available']
            })

        # Create a structured description for the AI
        variant_desc = ", ".join([f"{v['variant_title']} at ${v['price']}" for v in variants])
        full_description = f"The {title} is a {p_type} by {vendor}. "
        if tags:
            full_description += f"It is categorized under: {', '.join(tags)}. "
        full_description += f"Available variants include: {variant_desc}."

        product_entry = {
            "instruction": f"Tell me about {title}",
            "context": {
                "product_id": str(p_id),
                "title": title,
                "handle": handle,
                "vendor": vendor,
                "product_type": p_type,
                "tags": tags,
                "image_url": group.iloc[0]['Primary Image'],
                "variants": variants
            },
            "response": full_description
        }
        products_json.append(product_entry)

    # Save to JSON
    with open(json_path, 'w') as f:
        json.dump(products_json, f, indent=4)

    print(f"Successfully transformed {len(products_json)} products into {json_path}")

if __name__ == "__main__":
    transform_to_json("products.csv", "chatbot_training_data.json")
