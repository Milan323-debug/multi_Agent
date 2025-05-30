# 🤖 Multi-Agent Document Processing System

A powerful FastAPI-based system that automatically processes, classifies, and extracts information from multiple document types using AI agents and Redis-backed storage.

## ✨ Features

- 📄 **Multi-Format Support**: Process PDFs, Emails (plain/HTML), and JSON documents
- 🧠 **Intelligent Classification**: AI-powered document type and intent detection
- 💾 **Redis Persistence**: Reliable data storage with metadata tracking
- 🔍 **Smart Extraction**: Automatically extracts key information and embedded JSON
- 🚀 **Modern API**: FastAPI with async support and automatic OpenAPI documentation

## 🛠️ Quick Start

1. **Clone and Install**
```powershell
git clone <your-repo-url>
cd multi_agent_system
pip install -r app/requirements.txt
```

2. **Set Up Environment**
```powershell
# Copy example env file and edit with your values
Copy-Item .env.example .env
# Edit .env with your Google API key and Redis configuration
```

3. **Run the Server**
```powershell
uvicorn app.main:app --reload
```

## 🌐 API Endpoints

### Process Documents
```http
POST /process/
Content-Type: application/json

{
    "id": "doc_id",
    "content": "your_content",
    "content_type": "email|json|pdf_base64",
    "metadata": { "source": "your_source" }
}
```

### Get Document History
```http
GET /document/{id}
```

## 📝 Example Usage

### Process an Email
```json
{
    "id": "email_001",
    "content": "From: user@example.com\nSubject: Quote Request\n\nNeed pricing for 10 units.",
    "content_type": "email"
}
```

### Process a JSON Document
```json
{
    "id": "json_001",
    "content_type": "json",
    "json": {
        "order_id": "ORD123",
        "items": ["item1", "item2"]
    }
}
```

## 🔧 Requirements

- Python 3.8+
- Redis
- Google AI API Key
- FastAPI
- Additional dependencies in `requirements.txt`

## 🔒 Security

- API keys and sensitive data are stored in `.env` (not committed to git)
- Input validation and error handling for all endpoints
- Secure metadata tracking and storage

## 📚 Documentation

Full API documentation available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---
Made with ❤️ using FastAPI, Redis, and Google AI
