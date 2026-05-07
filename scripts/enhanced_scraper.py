import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

class PrarviScraper:
    def __init__(self):
        self.base_url = "https://prarvihair.com"
        self.output_dir = "scraped_data"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def save_to_csv(self, data, filename):
        if data:
            df = pd.DataFrame(data)
            path = os.path.join(self.output_dir, filename)
            df.to_csv(path, index=False)
            print(f"Saved {len(data)} items to {path}")
        else:
            print(f"No data to save for {filename}")

    def scrape_products(self):
        print("Scraping products...")
        all_products = []
        page = 1
        while True:
            response = requests.get(f"{self.base_url}/products.json", params={"page": page})
            if response.status_code != 200: break
            products = response.json().get("products", [])
            if not products: break
            for p in products:
                for v in p.get("variants", []):
                    all_products.append({
                        "Title": p.get("title"),
                        "Type": p.get("product_type"),
                        "Vendor": p.get("vendor"),
                        "Price": v.get("price"),
                        "SKU": v.get("sku"),
                        "Handle": p.get("handle")
                    })
            page += 1
            time.sleep(0.5)
        
        # Save by type
        types = set(p["Type"] for p in all_products)
        for t in types:
            type_name = str(t).replace("/", "_").replace(" ", "_") if t else "Unknown"
            type_data = [p for p in all_products if p["Type"] == t]
            self.save_to_csv(type_data, f"products_{type_name}.csv")

    def scrape_page(self, url, title_key):
        print(f"Scraping page: {url}")
        response = requests.get(url)
        if response.status_code != 200: return None
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # This is a generic way to get content, might need adjustment per site
        content = soup.find('div', {'class': 'rte'}) or soup.find('main')
        text = content.get_text(separator='\n', strip=True) if content else ""
        
        return {"URL": url, "Title": title_key, "Content": text}

    def scrape_policies(self):
        print("Scraping policies...")
        policy_urls = {
            "Shipping": f"{self.base_url}/pages/shipping-policy",
            "Return": f"{self.base_url}/pages/return-policy",
            "Privacy": f"{self.base_url}/pages/privacy-policy",
            "Terms": f"{self.base_url}/pages/terms-conditions"
        }
        policies = []
        for name, url in policy_urls.items():
            data = self.scrape_page(url, name)
            if data: policies.append(data)
            time.sleep(0.5)
        self.save_to_csv(policies, "policies.csv")


    def scrape_faqs(self):
        print("Scraping FAQs...")
        data = self.scrape_page(f"{self.base_url}/pages/faqs", "FAQs")
        if data:
            # Try to split by question/answer if possible
            self.save_to_csv([data], "faqs.csv")

    def scrape_services(self):
        print("Scraping services...")
        service_urls = {
            "Wholesale": f"{self.base_url}/pages/wholesale-hair-extensions",
            "Custom Order": f"{self.base_url}/pages/custom-order"
        }
        services = []
        for name, url in service_urls.items():
            data = self.scrape_page(url, name)
            if data: services.append(data)
            time.sleep(0.5)
        self.save_to_csv(services, "services.csv")

    def scrape_blog(self):
        print("Scraping blog...")
        # Shopify blogs usually have .atom or just scrape the list
        blog_url = f"{self.base_url}/blogs/hair-beauty-health.atom"
        response = requests.get(blog_url)
        if response.status_code != 200: 
            # Fallback to HTML if atom fails
            return
        
        soup = BeautifulSoup(response.text, 'xml')
        entries = soup.find_all('entry')
        blog_posts = []
        for entry in entries:
            blog_posts.append({
                "Title": entry.find('title').text,
                "Published": entry.find('published').text,
                "Content": BeautifulSoup(entry.find('content').text, 'html.parser').get_text(separator='\n', strip=True)
            })
        self.save_to_csv(blog_posts, "blog_posts.csv")

    def run_all(self):
        self.scrape_products()
        self.scrape_policies()
        self.scrape_faqs()
        self.scrape_services()
        self.scrape_blog()

if __name__ == "__main__":
    scraper = PrarviScraper()
    scraper.run_all()
