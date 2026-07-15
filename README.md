# AI-First CRM — HCP Module

An AI-powered Customer Relationship Management system for Healthcare Professional (HCP) interactions, built for pharmaceutical field representatives.

![Tech Stack](https://img.shields.io/badge/React-19-61DAFB?logo=react)
![Tech Stack](https://img.shields.io/badge/Redux-Toolkit-764ABC?logo=redux)
![Tech Stack](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)
![Tech Stack](https://img.shields.io/badge/LangGraph-AI_Agent-FF6B6B)
![Tech Stack](https://img.shields.io/badge/Groq-gemma2--9b--it-F55036)


live hosted link:- https://ai-first-crm-rho.vercel.app/

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    React + Redux Frontend                │
│  ┌───────────┐  ┌────────────────┐  ┌────────────────┐  │
│  │ Dashboard  │  │ Log Interaction│  │  HCP Directory │  │
│  │           │  │ (Form + Chat)  │  │                │  │
│  └───────────┘  └────────────────┘  └────────────────┘  │
└──────────────────────────┬───────────────────────────────┘
                           │ REST API
┌──────────────────────────▼───────────────────────────────┐
│                   FastAPI Backend                         │
│  ┌───────────────────────────────────────────────────┐   │
│  │              LangGraph ReAct Agent                 │   │
│  │  ┌─────────────┐  ┌─────────────────┐            │   │
│  │  │ Groq LLM    │  │  5 Agent Tools  │            │   │
│  │  │ gemma2-9b-it│  │  ├ log_interaction│           │   │
│  │  └─────────────┘  │  ├ edit_interaction│          │   │
│  │                    │  ├ search_hcp     │           │   │
│  │                    │  ├ get_history    │           │   │
│  │                    │  └ suggest_points │           │   │
│  │                    └─────────────────┘            │   │
│  └───────────────────────────────────────────────────┘   │
│                           │                              │
│  ┌────────────────────────▼──────────────────────────┐   │
│  │              SQLite Database                       │   │
│  │  ├ hcps  ├ interactions  ├ products               │   │
│  └───────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────┘
```

## ✨ Features

### Log Interaction Screen (Dual Mode)
- **Structured Form**: Traditional form with HCP selection, interaction type, channel, products, notes, and follow-up fields
- **AI Chat Interface**: Conversational interface powered by LangGraph agent — just describe your interaction in natural language

### 5 LangGraph Agent Tools
1. **`log_interaction`** — Records new HCP interactions with auto-summarization and entity extraction
2. **`edit_interaction`** — Modifies previously logged interactions with validation
3. **`search_hcp`** — Searches the HCP database by name, specialty, territory
4. **`get_interaction_history`** — Retrieves interaction timeline with filters
5. **`suggest_talking_points`** — AI-generated personalized talking points for upcoming meetings

### Additional Features
- 📊 Dashboard with interaction stats and pending follow-ups
- 👨‍⚕️ HCP Directory with search, filter, and profile cards
- 📋 Interaction History with timeline view and expandable details
- 💊 Product Catalog with key messaging
- 🎨 Premium dark theme with glassmorphism effects

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19 + Redux Toolkit + Vite |
| Backend | Python 3.11+ + FastAPI |
| AI Agent | LangGraph (ReAct pattern) |
| LLM | Groq Cloud — `gemma2-9b-it` |
| Database | SQLite (via SQLAlchemy ORM) |
| Font | Google Inter |

## 🚀 How to Run

### Prerequisites
- **Node.js** 18+ and npm
- **Python** 3.11+
- **Groq API Key** — Get one free at [console.groq.com](https://console.groq.com)

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd project
```

### 2. Backend Setup
```bash
# Create and activate virtual environment
cd backend
python -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cd ..
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# Start the backend server
uvicorn backend.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`  
API docs at `http://localhost:8000/docs`

### 3. Frontend Setup
```bash
# In a new terminal
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173`

### 4. Environment Variables
Create a `.env` file in the project root:
```env
GROQ_API_KEY=your_groq_api_key_here
DATABASE_URL=sqlite:///./crm_hcp.db
LLM_MODEL=gemma2-9b-it
```

## 📁 Project Structure

```
project/
├── backend/
│   ├── agent/
│   │   ├── graph.py          # LangGraph StateGraph definition
│   │   ├── state.py          # Agent state TypedDict
│   │   └── tools.py          # 5 LangGraph tools
│   ├── routes/
│   │   ├── agent.py          # Chat endpoint
│   │   ├── hcps.py           # HCP CRUD API
│   │   ├── interactions.py   # Interaction CRUD API
│   │   └── products.py       # Product API
│   ├── config.py             # Environment config
│   ├── database.py           # SQLAlchemy setup
│   ├── main.py               # FastAPI entry point
│   ├── models.py             # ORM models
│   ├── schemas.py            # Pydantic schemas
│   ├── seed_data.py          # Demo data seeder
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard/
│   │   │   ├── HCPDirectory/
│   │   │   ├── InteractionHistory/
│   │   │   ├── LogInteraction/   # ⭐ Core screen (Form + Chat)
│   │   │   ├── Products/
│   │   │   └── Sidebar/
│   │   ├── store/
│   │   │   └── slices/           # Redux slices
│   │   ├── services/api.js       # Axios service
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css             # Design system
│   ├── index.html
│   └── package.json
├── .env.example
├── .gitignore
└── README.md
```

## 🤖 LangGraph Agent Architecture

The agent uses a **ReAct (Reasoning + Acting)** pattern:

1. **User sends message** → Frontend dispatches to `/api/agent/chat`
2. **Agent receives message** → LLM decides which tool to call
3. **Tool executes** → Database operations + data retrieval
4. **Agent responds** → LLM generates human-readable response with insights
5. **Frontend displays** → Shows response + tool execution cards

### Tool Examples via Chat:
- *"Log a meeting with Dr. Chen about CardioGuard XR"* → Triggers `log_interaction`
- *"Update interaction #1 status to completed"* → Triggers `edit_interaction`
- *"Find oncologists in California"* → Triggers `search_hcp`
- *"Show me history with Dr. Rodriguez"* → Triggers `get_interaction_history`
- *"What should I discuss with Dr. Patel?"* → Triggers `suggest_talking_points`

## 📝 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/hcps` | List all HCPs (with search/filter) |
| POST | `/api/hcps` | Create new HCP |
| GET | `/api/interactions` | List interactions (with filters) |
| POST | `/api/interactions` | Create interaction |
| PUT | `/api/interactions/{id}` | Update interaction |
| DELETE | `/api/interactions/{id}` | Delete interaction |
| GET | `/api/products` | List all products |
| POST | `/api/agent/chat` | Chat with AI agent |
| GET | `/api/health` | Health check |

