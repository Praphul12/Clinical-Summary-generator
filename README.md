# 🩺 Clinical Summary Generator

AI-powered clinical documentation system that generates comprehensive patient summaries from structured clinical data.

## Features

- Generate clinical summaries from patient data using LLM
- FastAPI backend for LLM operations
- Streamlit web interface
- Export summaries in Markdown/TXT/JSON formats

## Installation
```bash
# Clone repository
git clone <repository-url>
cd patient_summary_generator

# Install dependencies
pip install -r requirements.txt
```

**Get OpenRouter API Key:**
1. Visit https://openrouter.ai/
2. Sign up and get your API key
3. Create `.env` file in project root:
```env
OPEN_ROUTER_API_KEY=your_api_key_here
```

## Usage

**Start FastAPI backend:**
```bash
uvicorn api:app --reload
```

**Start Streamlit frontend:**
```bash
streamlit run main.py
```

Access the app at `http://localhost:8501`

## API Endpoint

**POST** `/generate-summary`
```bash
curl -X POST http://localhost:8000/generate-summary \
  -H "Content-Type: application/json" \
  -d '{
    "clinical_facts": [
      {
        "statement": "Patient has hypertension",
        "source": "admission",
        "date": "2024-01-15"
      }
    ]
  }'
```

## Project Structure
```
├── api.py              # FastAPI backend
├── main.py             # Streamlit frontend
├── llm_client.py       # LLM integration
├── summarizers.py      # Data processors
└── data/               # CSV files
```

## Requirements

- Python 3.8+
- OpenRouter API key
- CSV data files (diagnoses, medications, vitals, wounds, notes, oasis)

## License

MIT