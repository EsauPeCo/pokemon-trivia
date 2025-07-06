# Pokemon Trivia App

A full-stack trivia application that generates Pokemon-based questions using AI.

## Tech Stack

- **Frontend**: React + TypeScript + Vite
- **Backend**: Python Flask
- **Database**: //
- **AI**: Gemini

## Project Structure

```
pokemon-trivia/
├── backend/
│   ├── .venv/              # Python virtual environment
│   ├── app.py              # Flask application
│   ├── requirements.txt    # Python dependencies
│   └── .env               # Environment variables
├── frontend/
│   ├── src/               # React components
│   ├── package.json       # Node dependencies
│   └── vite.config.ts     # Vite configuration
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- Gemini API key

### Backend Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt

```

Create `.env` file:

```
OPENAI_API_KEY=your_openai_key_here
FLASK_ENV=development

```

### Frontend Setup

```bash
cd frontend
pnpm install
pnpm run dev
```

## Development

**Backend**: http://localhost:5000
**Frontend**: http://localhost:5173

### Running Both Services

```bash
# Terminal 1 - Backend
cd backend
.venv\Scripts\activate
python app.py

# Terminal 2 - Frontend
cd frontend
pnpm run dev
```

### Test Connection

```bash
curl http://localhost:5000/api/health
```

## Features (Planned)

- [ ] Pokedex like collection
- [ ] Random Pokemon selection
- [ ] AI-generated trivia questions
- [ ] Score tracking
