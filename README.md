# Social Media Content & Script Idea Generator

**A Generative AI application to automate and elevate social media strategy.**
Built with Streamlit, FastAPI, Retrieval-Augmented Generation (RAG), ChromaDB, and Groq.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688)
![Streamlit](https://img.shields.io/badge/Streamlit-1.36.0-FF4B4B)
![ChromaDB](https://img.shields.io/badge/ChromaDB-0.5.3-orange)
![Groq](https://img.shields.io/badge/Groq-LLM-red)

## Overview

The **Social  & Script Idea Generator** is an AI-assisted content creation tool. It eliminates writer's block by instantly producing highly engaging, platform-specific content ideas, captions, video scripts, and call-to-action statements based on user preferences.

Rather than relying on basic text generation, this application uses **Retrieval-Augmented Generation (RAG)**. It retrieves social media best practices from a local knowledge base, converts the context and the user's prompt into embeddings, searches ChromaDB for relevant strategies, and supplies the retrieved context to a Large Language Model to prepare a tailored response.

The application supports a complete content creation workflow: users can select a platform, define their target audience, choose a specific tone, and generate the exact type of content they need in seconds.

## Key Features

*   **Multi-Platform Support:** Generates tailored content for Instagram, YouTube, YouTube Shorts, LinkedIn, and X (Twitter).
*   **Versatile Content Types:** Choose from Content Ideas, Captions + Hashtags, Full Video Scripts, Opening Hooks, and CTAs.
*   **Semantic Search (RAG):** Retrieves passages from a curated `knowledge.txt` file based on meaning, not just exact keywords.
*   **Tone Customization:** Adapts the writing style (Professional, Casual, Humorous, Inspirational, Educational) to match the brand voice.
*   **Ultra-Fast Generation:** Leverages the Groq API (`openai/gpt-oss-20b` model) for rapid inference and low latency.
*   **Downloadable Output:** Results can be instantly downloaded as a Markdown (`.md`) file.

## Technology Stack

| Layer | Technology | Role |
| :--- | :--- | :--- |
| **Frontend** | Streamlit | Web application and user interface |
| **Backend** | Python, FastAPI, Uvicorn | API and application services |
| **LLM Provider** | Groq API (`openai/gpt-oss-20b`) | Fast content generation |
| **RAG Pipeline** | ChromaDB | Vector storage and semantic retrieval |
| **Embeddings** | Sentence-Transformers (`all-MiniLM-L6-v2`) | Generates text embeddings |
| **Validation** | Pydantic | Request and response data validation |
| **Environment** | python-dotenv | Secure API key management |

## System Architecture

### RAG & Generation Workflow

1. **Document Ingestion (Initialization):**
   * The `knowledge.txt` file is loaded, chunked, and converted into vector embeddings.
   * ChromaDB stores these vectors persistently in the `chroma_db` directory.
2. **Query and Retrieval:**
   * The user submits a prompt from the Streamlit frontend.
   * FastAPI embeds the query and uses ChromaDB to retrieve the most semantically similar passages from the knowledge base.
3. **Prompt Engineering & Generation:**
   * The backend constructs a structured prompt injecting the retrieved context and user inputs (Topic, Audience, Tone).
   * The prompt is sent to the Groq API for generation.
   * The generated content is returned to Streamlit and rendered for the user.

## Repository Structure

```text
social-media-genai/
│
├── app/
│   ├── frontend/
│   │   └── streamlit_app.py     # Streamlit UI and API requests
│   │
│   ├── backend/
│   │   ├── main.py              # FastAPI app entry point and CORS setup
│   │   ├── schemas.py           # Pydantic validation models
│   │   └── routes/
│   │       └── content.py       # API endpoints, prompt logic, and RAG integration
│   │
│   ├── services/
│   │   ├── llm_service.py       # Groq API integration and error handling
│   │   ├── rag_service.py       # ChromaDB setup, ingestion, and retrieval
│   │   └── prompt_service.py    # (Optional) Modular prompt templates
│   │
│   └── data/
│       └── knowledge.txt        # Source knowledge base for RAG
│
├── chroma_db/                   # Persistent ChromaDB vector database
├── .env                         # Local environment variables (Git ignored)
├── .gitignore
├── requirements.txt
└── README.md
```

## Getting Started

### Prerequisites
* Python 3.10 or newer
* Git
* A free **Groq API Key** (Get one at [console.groq.com](https://console.groq.com))

### 1. Clone the Repository
```bash
git clone https://github.com/kavya-26331/social-media-genai.git
cd social-media-genai
```

### 2. Set Up Environment Variables
Create a `.env` file in the root directory:
```env
GROQ_API_KEY=gsk_5S84BJR7x2OtugoIRkAwWGdyb3FY........
```

### 3. Backend Setup & Run
Open a terminal and run:
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate
# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI backend
uvicorn app.backend.main:app --reload
```
*Backend runs at: `http://127.0.0.1:8000`*
*Interactive API docs: `http://127.0.0.1:8000/docs`*

### 4. Frontend Setup & Run
Open a **second terminal** (keep the backend running), activate the virtual environment, and run:
```bash
streamlit run app/frontend/streamlit_app.py
```
*Frontend will open automatically at `http://localhost:8501`*

##  API Reference

The FastAPI application mounts its routes under the `/content` prefix.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Returns backend health status. |
| `POST` | `/content/generate` | Validates request, retrieves RAG context, and generates AI content. |

##  Known Limitations
* Output depends on the quality of the LLM and the prompts provided. 
* The current RAG database only retrieves from the local `knowledge.txt`. 
* LLM generation may occasionally hit rate limits depending on your Groq account tier.

## License
This project is licensed under the MIT License.
