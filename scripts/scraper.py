import requests
import pandas as pd
import time

def scrape_prarvi_hair():
    base_url = "https://prarvihair.com/products.json"
    page = 1
    all_products = []

    print(f"Starting scrape for {base_url}...")

    while True:
        print(f"Fetching page {page}...")
        response = requests.get(base_url, params={"page": page})
        
        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code}")
            break
            
        data = response.json()
        products = data.get("products", [])
        
        if not products:
            print("No more products found.")
            break
            
        for product in products:
            # Basic product info
            product_id = product.get("id")
            title = product.get("title")
            vendor = product.get("vendor")
            product_type = product.get("product_type")
            handle = product.get("handle")
            tags = ", ".join(product.get("tags", []))
            
            # Primary image
            images = product.get("images", [])
            primary_image = images[0].get("src") if images else ""
            
            # Variants info
            for variant in product.get("variants", []):
                variant_data = {
                    "Product ID": product_id,
                    "Title": title,
                    "Variant Title": variant.get("title"),
                    "Vendor": vendor,
                    "Product Type": product_type,
                    "Handle": handle,
                    "Tags": tags,
                    "Price": variant.get("price"),
                    "Compare at Price": variant.get("compare_at_price"),
                    "SKU": variant.get("sku"),
                    "Available": variant.get("available"),
                    "Weight (grams)": variant.get("grams"),
                    "Primary Image": primary_image
                }
                all_products.append(variant_data)
        
        page += 1
        # Be nice to the server
        time.sleep(1)

    if all_products:
        df = pd.DataFrame(all_products)
        output_file = "products.csv"
        df.to_csv(output_file, index=False)
        print(f"Successfully scraped {len(all_products)} product variants.")
        print(f"Data saved to {output_file}")
    else:
        print("No product data collected.")

if __name__ == "__main__":
    scrape_prarvi_hair()
