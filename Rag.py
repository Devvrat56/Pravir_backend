import numpy as np
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utlis import load_json
from config import TOP_K, KNOWLEDGE_BASE_FILE

class RAGEngine:
    def __init__(self):
        print("Initializing Lightweight RAG Engine with TF-IDF...")
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Load KB
        kb_path = os.path.join(self.base_dir, KNOWLEDGE_BASE_FILE)
        self.kb = load_json(kb_path)
        
        # Load products if exists
        try:
            prod_path = os.path.join(self.base_dir, "product.json")
            self.products = load_json(prod_path)
            print(f"Loaded {len(self.products)} products from {prod_path}")
        except:
            self.products = []
            print("Warning: product.json not found.")

        self.tfidf_matrix = None
        self.documents = []
        self._build_index()

    def _prepare_text(self, item):
        """Combine fields into a single string for indexing."""
        if 'title' in item: # Product structure
            name = item.get('title', 'Unknown')
            category = item.get('product_type', 'Hair')
            tags = ", ".join(item.get('tags', []))
            variants = item.get('variants', [])
            prices = [str(v.get('price')) for v in variants if v.get('price')]
            price_range = f"${min(prices)} - ${max(prices)}" if prices else "N/A"
            text = f"Product: {name}. Category: {category}. Tags: {tags}. Price Range: {price_range}."
        else: # Knowledge base structure
            name = item.get('name', 'Unknown')
            category = item.get('category', item.get('type', 'General'))
            description = item.get('description', '')
            price = item.get('price', 'N/A')
            text = f"Name: {name}. Category: {category}. Description: {description}. Price: {price}."
            if 'metadata' in item and 'Content' in item['metadata']:
                text += f" Content: {item['metadata']['Content']}."
        return text

    def _build_index(self):
        print("Building TF-IDF index...")
        all_items = self.kb + self.products
        self.documents = [self._prepare_text(item) for item in all_items]
        
        # Build TF-IDF matrix
        self.tfidf_matrix = self.vectorizer.fit_transform(self.documents)
        self.full_kb = all_items
        print(f"Index built with {len(all_items)} total items.")

    def retrieve(self, query, k=TOP_K):
        # Transform query and calculate cosine similarity
        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        
        # Get top k indices
        top_indices = similarities.argsort()[-k:][::-1]
        
        results = []
        for i in top_indices:
            # Only include if there is some similarity
            if similarities[i] > 0:
                results.append(self.full_kb[i])
        
        # If no results found with TF-IDF, return first k as fallback
        if not results:
            results = self.full_kb[:k]
            
        return results

# Singleton instance
_engine = None

def get_retriever():
    global _engine
    if _engine is None:
        _engine = RAGEngine()
    return _engine

def retrieve(query):
    retriever = get_retriever()
    return retriever.retrieve(query)

if __name__ == "__main__":
    # Quick test
    import sys
    test_query = sys.argv[1] if len(sys.argv) > 1 else "blonde hair extensions"
    print(f"\nTesting retrieval for: '{test_query}'")
    docs = retrieve(test_query)
    print("\nTop Results:")
    for i, doc in enumerate(docs):
        name = doc.get('title') or doc.get('name', 'Unknown')
        category = doc.get('product_type') or doc.get('category', 'General')
        print(f"{i+1}. {name} ({category})")