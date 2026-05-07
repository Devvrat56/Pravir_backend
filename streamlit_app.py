import streamlit as st
import time
from chatbot import Chatbot
import os
from dotenv import load_dotenv

load_dotenv()

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Prarvi Hair Styler | AI Assistant",
    page_icon="💇‍♀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background: radial-gradient(circle at top, #1a1a2e 0%, #0f0c29 100%);
        color: #e0e0e0;
    }
    
    /* Header Styling */
    .main-header {
        font-family: 'Playfair Display', serif;
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #fccb90 0%, #d57eeb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2.5rem;
        text-shadow: 0px 10px 20px rgba(0,0,0,0.3);
    }
    
    /* Chat Message Styling */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.03) !important;
        border-radius: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
        margin-bottom: 1.2rem !important;
        padding: 1.5rem !important;
    }
    
    /* User Message Specific */
    [data-testid="stChatMessageUser"] {
        background-color: rgba(213, 126, 235, 0.05) !important;
        border: 1px solid rgba(213, 126, 235, 0.2) !important;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0a0a1a !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    /* Input Field Styling */
    .stTextInput input, .stChatInputContainer textarea {
        background-color: #161625 !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
    }
    
    /* Button Styling */
    .stButton button {
        background: linear-gradient(45deg, #d57eeb 0%, #fccb90 100%) !important;
        color: #000000 !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        border: none !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 15px rgba(213, 126, 235, 0.4) !important;
    }
    
    /* Expander Styling */
    .stExpander {
        background-color: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 15px !important;
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #0f0c29;
    }
    ::-webkit-scrollbar-thumb {
        background: #302b63;
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #d57eeb;
    }
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@400;600&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# --- INITIALIZATION ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chatbot" not in st.session_state:
    st.session_state.chatbot = None

@st.cache_resource
def load_chatbot(api_key=None):
    return Chatbot("knowledge_base.json", api_key=api_key)

# --- MAIN CONTENT HEADER (Render this first!) ---
st.markdown('<h1 class="main-header">Prarvi Hair AI Assistant</h1>', unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    # Use a more reliable icon or local placeholder
    st.markdown("### 💇‍♀️ Prarvi Luxury Salon")
    st.title("Settings")
    
    groq_api_key = st.text_input("Groq API Key (Optional)", type="password", placeholder="Enter your Groq API Key")
    
    if st.session_state.get("chatbot") is None:
        try:
            with st.status("Initializing Groq AI Assistant..."):
                # Use the cached loader
                st.session_state.chatbot = load_chatbot(api_key=groq_api_key)
                if st.session_state.chatbot.client:
                    st.success("Groq Assistant Ready!")
                else:
                    st.error("Failed to initialize Groq client. Check logs or API key.")
        except Exception as e:
            st.error(f"Error: {e}")
            
    # Reference for the rest of the script
    chatbot = st.session_state.chatbot
    
    st.divider()
    st.markdown("""
    ### About Prarvi Hair
    Our AI assistant helps you with:
    - 💇‍♀️ Service Information
    - 🛍️ Product Recommendations
    - 📦 Order & Return Policies
    - 🗓️ Booking Assistance
    """)
    
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# --- MAIN CHAT AREA ---
# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "context" in message and message["role"] == "assistant":
            with st.expander("See retrieved sources"):
                for i, doc in enumerate(message["context"]):
                    if 'title' in doc: # Product
                        st.markdown(f"**{i+1}. {doc.get('title')}**")
                        if doc.get('primary_image'):
                            st.image(doc.get('primary_image'), width=150)
                        
                        # Show stock and weight
                        variants = doc.get('variants', [])
                        in_stock = any(v.get('available', False) for v in variants)
                        stock_text = "✅ In Stock" if in_stock else "❌ Out of Stock"
                        st.write(f"Status: {stock_text}")
                        
                        weights = [v.get('weight_grams', 100) for v in variants]
                        avg_weight = sum(weights)/len(weights) if weights else 100
                        st.write(f"Weight: {avg_weight}g")
                    else: # KB Item
                        st.markdown(f"**{i+1}. {doc.get('name', 'Info')}**")
                        st.write(doc.get('description', 'No description available'))

# Chat Input
if prompt := st.chat_input("How can I help you today?"):
    # User message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Bot response
    with st.chat_message("assistant"):
        if chatbot:
            with st.spinner("Styling your response..."):
                response_text, context = chatbot.process_query(prompt)
                
                # Simulate typing effect
                full_response = ""
                placeholder = st.empty()
                for chunk in response_text.split(" "):
                    full_response += chunk + " "
                    time.sleep(0.05)
                    placeholder.markdown(full_response + "▌")
                placeholder.markdown(full_response)
                
                # Context expander
                with st.expander("See retrieved sources"):
                    for i, doc in enumerate(context):
                        if 'title' in doc: # Product
                            st.markdown(f"**{i+1}. {doc.get('title')}**")
                            if doc.get('primary_image'):
                                st.image(doc.get('primary_image'), width=150)
                            
                            # Show stock and weight
                            variants = doc.get('variants', [])
                            in_stock = any(v.get('available', False) for v in variants)
                            stock_text = "✅ In Stock" if in_stock else "❌ Out of Stock"
                            st.write(f"Status: {stock_text}")
                            
                            weights = [v.get('weight_grams', 100) for v in variants]
                            avg_weight = sum(weights)/len(weights) if weights else 100
                            st.write(f"Weight: {avg_weight}g")
                        else: # KB Item
                            st.markdown(f"**{i+1}. {doc.get('name', 'Info')}**")
                            st.write(doc.get('description', 'No description available'))
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": full_response,
                    "context": context
                })
        else:
            st.error("Chatbot not initialized. Please provide an API Key in the sidebar.")
