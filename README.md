# Pravir Hair Styler - Backend

This repository contains the backend code for the Pravir Hair Styler / Hair Cider AI Assistant.

## Features
- **FastAPI API**: High-performance API for chat interactions.
- **RAG Engine**: Retrieval-Augmented Generation using FAISS and Sentence Transformers.
- **Lead Capture**: Automated lead information extraction (Name, Email, Phone).
- **Product Knowledge Base**: Structured data retrieval for hair extensions, wigs, and toppers.

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**:
   Create a `.env` file with your Groq API key:
   ```env
   groq_api_key=your_api_key_here
   ```

3. **Run the API**:
   ```bash
   python main.py
   ```

## Structure
- `main.py`: FastAPI entry point.
- `chatbot.py`: Core chatbot logic and entity extraction.
- `Rag.py`: Retrieval engine.
- `prompt.py`: System prompts and response rules.
- `data/`: Knowledge base and training data.
- `scripts/`: Data cleaning and scraper scripts.
