# 🚗 Hasham Automobile Chatbot

An intelligent customer support assistant built using FastAPI, LangChain, OpenAI, and TinyDB. This chatbot helps customers inquire about vehicles, request services (like oil changes), and log their contact information—all through a natural conversation.

---

## 📁 Project Structure

```
hasham-automobile-chatbot/
│
├── main.py                          # FastAPI entry point
├── app_context.py                   # LLM, tools, memory, agent setup
├── car_Data.json                    # Vehicle data (used by the bot)
├── tools/
│   ├── user_data.py                 # TinyDB logic for user/service data
│   ├── general_inquiry.py          # Tool for car inquiry
│   └── service_based_query.py      # Tool for service logging
├── routes/
│   └── main.py                      # Frontend + chat API endpoints
├── utils/
│   └── session.py                  # Session ID generator
├── data/
│   ├── car_inquiries.json           # Saved car inquiries (TinyDB)
│   ├── service_requests.json        # Saved service requests (TinyDB)
├── templates/
│   └── index.html                   # Frontend chat UI
└── static/
    └── style.css                    # CSS (optional)
```

---

## 🚀 How to Run

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/hasham-automobile-chatbot.git
cd hasham-automobile-chatbot
```

### 2. Set up environment variables

Create a `.env` file in the root folder:

```
OPENAI_API_KEY=your_openai_key
OPENAI_LLM_MODEL=gpt-4
```

> You can also use `gpt-3.5-turbo` if you don't have access to GPT-4.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python main.py
```

Then open your browser at [http://localhost:8000](http://localhost:8000)

---

## 💡 Features

- 🔍 **Vehicle Info Lookup**: Users can ask about cars (e.g., "Tell me about the Honda Civic").
- 🛠️ **Service Logging**: Logs service interests like "oil change" with user details.
- 📝 **User Inquiries**: Collects name, contact, and interest for follow-up.
- 💾 **TinyDB**: Lightweight NoSQL DB for saving inquiries and service logs.
- 🤖 **LangChain Agent**: Uses OpenAI to decide which tool to invoke.
- 🧠 **Session Memory**: Keeps conversation history per session.

---

## ✅ Requirements

- Python 3.9+
- OpenAI API key
- FastAPI
- Uvicorn
- LangChain
- TinyDB
- dotenv

---

## 📌 Notes

- All data is stored locally under the `/data` folder.
- For production deployment, consider replacing TinyDB with a proper database (e.g., PostgreSQL).

---

## 📞 Contact

Hashim | `https://github.com/haashhii`  
© 2025 Hasham Automobile Solutions