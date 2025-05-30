from fastapi.testclient import TestClient
import base64
import json
from app.main import app

client = TestClient(app)

def test_process_pdf():
    # Create a simple PDF-like content for testing
    sample_pdf_content = "This is an invoice for $500. Payment is due by June 1st, 2025."
    pdf_base64 = base64.b64encode(sample_pdf_content.encode()).decode()
    
    response = client.post(
        "/process/",
        json={
            "id": "test_pdf_1",
            "content": pdf_base64,
            "content_type": "pdf_base64",
            "metadata": {
                "source": "test",
                "filename": "test_invoice.pdf"
            }
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "pdf_analysis" in data
    assert data["pdf_analysis"]["document_type"] == "invoice"

def test_process_email_with_json():
    email_content = """
    From: test@example.com
    Subject: RFQ with JSON Attachment
    
    Please find the attached JSON quote request:
    
    {
        "order_id": "RFQ-123",
        "items": [
            {
                "product": "Widget-A",
                "quantity": 100
            }
        ]
    }
    """
    
    response = client.post(
        "/process/",
        json={
            "id": "test_email_1",
            "content": email_content,
            "content_type": "email",
            "metadata": {
                "source": "test"
            }
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "email_analysis" in data
    assert "embedded_json" in data["email_analysis"]
    assert data["classification"]["intent"] == "RFQ"

def test_process_complex_json():
    json_content = {
        "customer": "Acme Corp",
        "order_id": "PO-789",
        "items": [
            {
                "product_id": "WIDGET-A",
                "quantity": 50,
                "unit_price": 99.99
            }
        ],
        "total_amount": 4999.50
    }
    
    response = client.post(
        "/process/",
        json={
            "id": "test_json_1",
            "content": json.dumps(json_content),
            "content_type": "json",
            "metadata": {
                "source": "test"
            }
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "json_analysis" in data
    assert "missing_fields" in data["json_analysis"]

def test_document_history():
    # First process a document
    doc_id = "test_history_1"
    email_content = """
    From: customer@example.com
    Subject: Urgent Issue
    
    We have a serious problem with our recent order.
    This needs immediate attention.
    """
    
    # Process the document
    response = client.post(
        "/process/",
        json={
            "id": doc_id,
            "content": email_content,
            "content_type": "email",
            "metadata": {"priority": "high"}
        }
    )
    
    assert response.status_code == 200
    
    # Get document history
    history_response = client.get(f"/document/{doc_id}")
    assert history_response.status_code == 200
    history_data = history_response.json()
    
    # Verify history contains all processing steps
    assert "classification" in history_data
    assert "metadata" in history_data
    assert "processing_history" in history_data
    assert history_data["classification"]["intent"] == "Complaint"
    assert history_data["classification"]["urgency"] == "high"
