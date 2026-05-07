from chatbot import Chatbot

bot = Chatbot("knowledge_base.json")
query = "What is your return policy?"
prompt = bot.process_query(query)

print("\n--- TEST PROMPT ---")
print(prompt)
print("--- END TEST ---")
