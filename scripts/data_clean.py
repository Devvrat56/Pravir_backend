import pandas as pd 
import re
from bs4 import BeautifulSoup

df = pd.read_csv("./scraped_data/products_Unknown.csv")

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

for col in df.columns:
    df[col] = df[col].apply(clean_text)

df.drop_duplicates(inplace=True)
df.to_csv("cleaned_text.csv", index=False)
print("Data cleaning complete. Saved to cleaned_text.csv")