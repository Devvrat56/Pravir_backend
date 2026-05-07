from flask import Flask, request, jsonify, render_template
from chatbot import Chatbot
import os

app = Flask(__name__, static_folder='.', template_folder='.', static_url_path='')

# Initialize Chatbot
# In a real app, you'd use an LLM API. 
# For this demo, we'll return the generated prompt or a mock response if no API key is provided.
chatbot = Chatbot("knowledge_base.json")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    
    if not message:
        return jsonify({"error": "No message provided"}), 400
    
    # Get the prompt from our RAG system
    prompt = chatbot.process_query(message)
    
    # Since we don't have an LLM API key here, we'll provide a smart mock response
    # based on the retrieved context.
    # In a real scenario, you'd do: response = llm.generate(prompt)
    
    response = "I've received your query about: " + message
    
    # Let's try to extract some information from the prompt to make it look real
    if "Return Policy" in prompt and "return" in message.lower():
        response = "Our return policy allows unopened products to be returned within 14 days for a full refund. Opened products can be exchanged for salon credit within 7 days. Would you like to know anything else?"
    elif "Cancellation Policy" in prompt and "cancel" in message.lower():
        response = "We require at least 24 hours notice for cancellations. Late cancellations or no-shows may incur a 50% service fee. Is there a specific appointment you're looking at?"
    elif "Classic Haircut" in prompt and ("haircut" in message.lower() or "cut" in message.lower()):
        response = "Our Classic Haircut starts at $50 and includes a consultation, wash, and style. It's tailored specifically to your face shape. Shall I help you book an appointment?"
    elif "Keratin" in prompt and "keratin" in message.lower():
        response = "The Keratin Treatment is $250 and is amazing for eliminating frizz. It usually lasts about 4 months. Are you looking to smooth out your hair?"
    else:
        response = "That's a great question! Based on what I know, I can help you with our services like haircuts, blowouts, and color treatments, as well as our product line. Could you tell me a bit more about what you're looking for?"

    return jsonify({
        "response": response,
        "debug_prompt": prompt # Useful for developers to see what RAG retrieved
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
