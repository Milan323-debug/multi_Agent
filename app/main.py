from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Body
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Union
import json
import base64
from bs4 import BeautifulSoup

# Import your agent functions and shared memory utilities
from app.agents.classifier_agent import classify_input
from app.agents.json_agent import parse_json
from app.agents.email_agent import parse_email
from app.agents.pdf_agent import extract_text_from_pdf, analyze_pdf_content
from app.memory.shared_memory import store_data, get_data, get_processing_history

app = FastAPI()

class ProcessRequest(BaseModel):
    id: str
    content: str
    content_type: Optional[str] = Field(None, description="Type of content: 'text', 'email', 'json', or 'pdf_base64'")
    json: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

@app.post("/process/")
async def process_input(
    request: ProcessRequest = Body(...),
):
    try:
        doc_id = request.id
        content_type = request.content_type or "text"
        metadata = request.metadata or {}
        
        # Handle webhook payload with separate JSON field
        if request.json:
            content = json.dumps(request.json)
            content_type = "json"
        else:
            content = request.content

        # Store metadata
        store_data(f"{doc_id}_metadata", metadata, source="client_metadata")

        # Classify the input
        classification = classify_input(content)
        store_data(f"{doc_id}_classification", classification, source="classifier_agent")

        # Process based on the content type
        result = {"status": "processed", "classification": classification}

        if content_type == "pdf_base64":
            pdf_extraction = extract_text_from_pdf(content)
            if not pdf_extraction["success"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"PDF processing failed: {pdf_extraction['error']}"
                )
            
            pdf_analysis = analyze_pdf_content(pdf_extraction["text"])
            store_data(f"{doc_id}_pdf", pdf_analysis, source="pdf_agent")
            result["pdf_analysis"] = pdf_analysis

        elif content_type == "email":
            # Handle HTML content in email
            if "<html" in content.lower():
                soup = BeautifulSoup(content, 'html.parser')
                content = soup.get_text()
                
            email_data = parse_email(content)
            store_data(f"{doc_id}_email", email_data, source="email_agent")
            result["email_analysis"] = email_data
            
            # Check for embedded JSON in email
            try:
                json_start = content.find('{')
                json_end = content.rfind('}')
                if json_start != -1 and json_end != -1:
                    json_str = content[json_start:json_end + 1]
                    json_data = json.loads(json_str)
                    json_analysis = parse_json(json_data)
                    store_data(f"{doc_id}_embedded_json", json_analysis, source="json_agent")
                    result["json_analysis"] = json_analysis
            except json.JSONDecodeError:
                pass  # No valid JSON found in email

        elif content_type == "json":
            try:
                if isinstance(content, str):
                    json_content = json.loads(content)
                else:
                    json_content = content
                json_analysis = parse_json(json_content)
                store_data(f"{doc_id}_json", json_analysis, source="json_agent")
                result["json_analysis"] = json_analysis
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid JSON content")

        return result

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process/file")
async def process_file(
    file: UploadFile = File(...),
    id: str = Form(...)
):
    try:
        content = await file.read()
        if file.content_type == 'application/pdf':
            pdf_base64 = base64.b64encode(content).decode()
            
            # Create a ProcessRequest and use the existing process_input function
            request = ProcessRequest(
                id=id,
                content=pdf_base64,
                content_type="pdf_base64",
                metadata={"filename": file.filename, "content_type": file.content_type}
            )
            
            return await process_input(request)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/document/{id}")
async def get_document(id: str):
    # Get all processing results for the document
    classification = get_data(f"{id}_classification")
    metadata = get_data(f"{id}_metadata")
    processing_history = get_processing_history(id)
    
    if not classification and not metadata:
        raise HTTPException(status_code=404, detail="Document not found")
    
    result = {
        "id": id,
        "classification": classification["data"] if classification else None,
        "metadata": metadata["data"] if metadata else None,
        "processing_history": processing_history
    }
    
    # Add type-specific processing results
    pdf_data = get_data(f"{id}_pdf")
    if pdf_data:
        result["pdf_analysis"] = pdf_data["data"]
    
    email_data = get_data(f"{id}_email")
    if email_data:
        result["email_analysis"] = email_data["data"]
    
    json_data = get_data(f"{id}_json")
    if json_data:
        result["json_analysis"] = json_data["data"]
    
    return result
