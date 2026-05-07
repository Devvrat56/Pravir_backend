import faiss
import numpy as np
import os
from sentence_transformers import SentenceTransformer
from utlis import load_json
from config import TOP_K, EMBEDDING_MODEL, KNOWLEDGE_BASE_FILE

class RAGEngine:
    def __init__(self):
        print(f"Initializing RAG Engine with model: {EMBEDDING_MODEL}...")
        self.model = SentenceTransformer(EMBEDDING_MODEL)
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

        self.index = None
        self.documents = []
        self._build_index()

    def _prepare_text(self, item):
        """Combine fields into a single string for embedding."""
        if 'title' in item: # Product structure
            name = item.get('title', 'Unknown')
            category = item.get('product_type', 'Hair')
            tags = ", ".join(item.get('tags', []))
            
            # Extract detailed variant info for automation
            variants = item.get('variants', [])
            prices = [str(v.get('price')) for v in variants if v.get('price')]
            price_range = f"${min(prices)} - ${max(prices)}" if prices else "N/A"
            
            # Stock check
            in_stock = any(v.get('available', False) for v in variants)
            stock_status = "In Stock" if in_stock else "Out of Stock"
            
            # Shipping data (average weight)
            weights = [v.get('weight_grams', 0) for v in variants if v.get('weight_grams')]
            avg_weight = f"{sum(weights)/len(weights):.1f}g" if weights else "100g"
            
            text = f"Product: {name}. Category: {category}. Tags: {tags}. Price Range: {price_range}. Stock Status: {stock_status}. Weight: {avg_weight}."
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
        print("Building FAISS index...")
        # Combine both data sources
        all_items = self.kb + self.products
        self.documents = [self._prepare_text(item) for item in all_items]
        
        embeddings = self.model.encode(self.documents, show_progress_bar=True)
        embeddings = np.array(embeddings).astype('float32')
        
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings)
        print(f"Index built with {len(all_items)} total items.")
        
        # Store combined KB for retrieval lookup
        self.full_kb = all_items

    def retrieve(self, query, k=TOP_K):
        query_embedding = self.model.encode([query])
        query_embedding = np.array(query_embedding).astype('float32')
        
        distances, indices = self.index.search(query_embedding, k)
        
        results = []
        for i in indices[0]:
            if i != -1:
                results.append(self.full_kb[i])
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