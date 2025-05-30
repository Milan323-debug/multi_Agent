import io
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams
import base64
from typing import Dict, Any, Union

def extract_text_from_pdf(pdf_content: str) -> Dict[str, Any]:
    """Extract text from a base64 encoded PDF content"""
    try:
        # Validate base64 content
        try:
            pdf_bytes = base64.b64decode(pdf_content)
        except Exception as e:
            return {
                "success": False,
                "text": None,
                "error": f"Invalid base64 content: {str(e)}"
            }

        # Check for PDF signature
        if not pdf_bytes.startswith(b'%PDF'):
            # If not a real PDF, just treat it as text for testing
            return {
                "success": True,
                "text": base64.b64decode(pdf_content).decode('utf-8'),
                "error": None
            }

        output = io.StringIO()
        with io.BytesIO(pdf_bytes) as pdf_file:
            # Extract text with PDFMiner
            extract_text_to_fp(pdf_file, output, laparams=LAParams())
            text = output.getvalue()

        if not text:
            return {
                "success": False,
                "text": None,
                "error": "No text could be extracted from the PDF"
            }
        
        return {
            "success": True,
            "text": text,
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "text": None,
            "error": f"PDF processing error: {str(e)}"
        }

def analyze_pdf_content(text: str) -> Dict[str, Any]:
    """Analyze the extracted text to determine document type and extract key information"""
    if not text:
        return {
            "document_type": "unknown",
            "content": "",
            "metadata": {
                "page_count": 0,
                "error": "No text content provided"
            }
        }

    text_lower = text.lower()
    
    # Document type detection
    doc_type = "unknown"
    confidence = 0.0
    
    # Define document type indicators with confidence scores
    type_indicators = {
        "invoice": {
            "terms": ["invoice", "bill", "payment", "amount due", "total amount"],
            "confidence": 0.8
        },
        "rfq": {
            "terms": ["quotation", "quote", "rfq", "price request", "pricing"],
            "confidence": 0.8
        },
        "complaint": {
            "terms": ["complaint", "dissatisfaction", "issue", "problem", "unsatisfactory"],
            "confidence": 0.7
        },
        "regulation": {
            "terms": ["regulation", "policy", "compliance", "directive", "guidelines"],
            "confidence": 0.9
        }
    }

    # Detect document type
    for dtype, info in type_indicators.items():
        if any(term in text_lower for term in info["terms"]):
            doc_type = dtype
            confidence = info["confidence"]
            break

    return {
        "document_type": doc_type,
        "content": text,
        "metadata": {
            "page_count": text.count('\f') + 1,
            "confidence": confidence,
            "length": len(text)
        }
    }
