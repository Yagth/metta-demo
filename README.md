# 🧠 Relationship Network RAG Chatbot

A Gradio-powered chatbot that answers questions about a relationship network using a **RAG (Retrieval-Augmented Generation)** pipeline.  
It parses natural language queries into structured JSON, searches the network database, and generates a friendly AI answer with supporting source details.

---

## 🚀 Features
- **Natural Language Questions** → Structured JSON queries
- **Graph/Network Search** → Finds matching people and relationships
- **AI Answer Generation** → Concise, friendly, depth-aware responses
- **Sources Panel** → Shows query JSON and match details
- **Interactive Web UI** built with Gradio

---

## 📂 Project Structure

        ├── app.py # Main Gradio app
        ├── src/
        │ ├── text_to_json_parser.py # Converts questions to JSON
        │ ├── json_to_metta_parser.py # Finds matches in the network
        │ └── data.metta
        ├── requirements.txt # Python dependencies
        └── README.md # This file


---

## ⚙️ Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/metta-demo
cd metta-demo
```
2. **Create and activate a virtual environment**
```bash
python3 -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
```
3. **Install dependencies**
```bash 
    pip install -r requirements.txt
```

### Running the App

```bash
    python3 app.py
```

### How to Use
- Type a question in plain English.

Example:

    Who in Alice's network is a nurse?

    - Click Ask.

    - View the AI-generated answer in the right panel.

    - Check the Sources Used box to see:

        The structured JSON query

        Matching people and their search depth

    - Use Clear to reset the chat.

### 📌 Example Questions
- List all people connected to Alice at depth 2.

- Who are Alice's close friends?

- Find doctors in Alice's network.