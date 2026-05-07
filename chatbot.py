import json
import re
import os
from groq import Groq
from dotenv import load_dotenv
from prompt import build_prompt
from Rag import retrieve as rag_retrieve
from config import GROQ_MODEL, MAX_TOKENS, TEMPERATURE

load_dotenv() # Load environment variables from .env

class IntentClassifier:
    def __init__(self):
        self.intent_map = {
            "product_search": ["find", "search", "show", "buy", "looking for", "have", "product", "hair", "extension", "wig", "topper"],
            "service_inquiry": ["service", "custom", "wholesale", "help", "do you offer", "can you"],
            "pricing_query": ["price", "cost", "how much", "expensive", "cheap", "rate"],
            "bulk_order": ["bulk", "wholesale", "large order", "many", "quantity", "discount for", "business"],
            "policy_query": ["return", "refund", "shipping", "delivery", "policy", "privacy", "cancel"],
        }

    def classify(self, text):
        text = text.lower()
        # High priority for lead info
        if re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text): return "lead_email"
        if re.search(r'\b\d{10}\b', text): return "lead_phone"
        
        for intent, keywords in self.intent_map.items():
            if any(keyword in text for keyword in keywords):
                return intent
        return "others"

class EntityExtractor:
    def __init__(self):
        self.product_types = ["hair", "wig", "extension", "topper", "frontal", "closure", "piece"]
        self.categories = ["blonde", "black", "curly", "straight", "wave", "ash", "platinum", "ombre", "brown"]

    def extract(self, text):
        text = text.lower()
        entities = {
            "product_type": None,
            "quantity": None,
            "category": None,
            "location": None,
            "budget": None,
            "email": None,
            "phone": None,
            "name": None
        }

        # Email Extraction
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        if email_match: entities["email"] = email_match.group(0).lower()

        # Phone Extraction - Handles formats: 1234567890, 123-456-7890, (123) 456-7890
        phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
        if phone_match: 
            # Normalize: strip all non-digits
            entities["phone"] = re.sub(r'\D', '', phone_match.group(0))
        
        # Name Extraction (Simple heuristic: if user says 'my name is X' or 'I am X')
        name_match = re.search(r'(?:my name is|i am|this is|call me|name:?)\s+([a-zA-Z]+)', text, re.IGNORECASE)
        if name_match: entities["name"] = name_match.group(1).capitalize()

        for pt in self.product_types:
            if pt in text:
                entities["product_type"] = pt
                break
        
        for cat in self.categories:
            if cat in text:
                entities["category"] = cat
                break

        quant_match = re.search(r'(\d+)', text)
        if quant_match:
            entities["quantity"] = quant_match.group(1)

        budget_match = re.search(r'\$(\d+)', text)
        if budget_match:
            entities["budget"] = budget_match.group(1)

        return entities

class Chatbot:
    def __init__(self, knowledge_base_path, api_key=None):
        # Load Knowledge Base
        # Resolve path relative to script
        if not os.path.isabs(knowledge_base_path):
            base_dir = os.path.dirname(os.path.abspath(__file__))
            knowledge_base_path = os.path.join(base_dir, knowledge_base_path)

        with open(knowledge_base_path, 'r') as f:
            self.knowledge_base = json.load(f)
        self.classifier = IntentClassifier()
        self.extractor = EntityExtractor()
        
        # Initialize Groq Client
        self.api_key = api_key or os.environ.get("groq_api_key")
        if self.api_key:
            self.client = Groq(api_key=self.api_key)
            print(f"Groq Chatbot initialized with model: {GROQ_MODEL}")
        else:
            self.client = None
            print("Warning: No Groq API Key found. Chat features will be disabled.")

        # Lead tracking state
        self.user_state = {
            "name": None,
            "email": None,
            "phone": None,
            "customer_type": "Visitor", # Individual vs Salon
            "interest": None,
            "lead_captured": False
        }

    def process_query(self, query):
        # 1. Detect Intent
        intent = self.classifier.classify(query)
        
        # 2. Extract Entities & Update User State
        entities = self.extractor.extract(query)
        if entities["email"]: self.user_state["email"] = entities["email"]
        if entities["phone"]: self.user_state["phone"] = entities["phone"]
        if entities["name"]: self.user_state["name"] = entities["name"]
        
        # Mark lead as captured if threshold met
        if self.user_state["name"] and (self.user_state["email"] or self.user_state["phone"]):
            self.user_state["lead_captured"] = True
        if entities["product_type"]: self.user_state["interest"] = entities["product_type"]
        
        # Determine customer type if possible
        if "bulk" in query.lower() or "wholesale" in query.lower() or "salon" in query.lower():
            self.user_state["customer_type"] = "Salon Owner / Wholesale"
        
        # 3. Retrieve relevant documents using RAG
        print(f"[DEBUG] Retrieving context for query: '{query}'")
        retrieved_docs = rag_retrieve(query)
        
        # 4. Build the final prompt using prompt.py
        prompt = build_prompt(query, retrieved_docs, self.user_state)
        
        # 5. Call Groq API if available
        if self.client:
            try:
                chat_completion = self.client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a professional AI customer care assistant for Hair Cider. Follow the instructions and brand personality provided in the context strictly. Output text only."
                        },
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    model=GROQ_MODEL,
                    temperature=TEMPERATURE,
                    max_tokens=MAX_TOKENS,
                )
                response_text = chat_completion.choices[0].message.content
                return response_text, retrieved_docs
            except Exception as e:
                return f"Error calling Groq API: {str(e)}", retrieved_docs
        
        return f"Mock response for: {query} (Groq API Key not configured)", retrieved_docs

if __name__ == "__main__":
    bot = Chatbot("knowledge_base.json")
    print("--- Hair Styler Chatbot Engine Started ---")
    print("Type 'exit' to quit.")
    
    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit", "bye"]:
                break
            
            response, context = bot.process_query(user_input)
            
            print("\n--- [SYSTEM] BOT RESPONSE ---")
            print(response)
            print("------------------------------------------\n")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
