import google.generativeai as genai
from app.memory.shared_memory import store_data
import os
from dotenv import load_dotenv
import pathlib
from typing import Dict, Any
import re

# Load environment variables from .env file
env_path = pathlib.Path(__file__).parents[2] / '.env'
load_dotenv(env_path)

# Configure Gemini
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables. Please check your .env file.")
genai.configure(api_key=api_key)

def clean_response(response_text: str) -> str:
    """Remove markdown formatting and extract the dictionary."""
    clean_text = response_text.replace('```json', '').replace('```python', '').replace('```', '').strip()
    return clean_text

def detect_format(content: str) -> str:
    """Detect the format of the input content"""
    # Check for PDF header (base64 encoded)
    if content.startswith(('JVBERi', 'UERGLTEu')):
        return 'PDF'
    
    # Check for email headers
    email_headers = ['From:', 'To:', 'Subject:', 'Date:', 'Message-ID:']
    if any(header in content[:500] for header in email_headers):
        return 'Email'
    
    # Check for JSON structure
    try:
        if content.strip().startswith('{') and content.strip().endswith('}'):
            return 'JSON'
    except:
        pass
    
    return 'Unknown'

def analyze_intent(content: str) -> Dict[str, Any]:
    """Analyze the content to determine specific intent and extract key information"""
    content_lower = content.lower()
    
    # Initialize intent analysis
    intent = {
        "primary_type": "unknown",
        "confidence": 0.0,
        "subtype": None,
        "urgency": "normal",
        "key_entities": []
    }
    
    # RFQ Detection
    rfq_indicators = ['request for quote', 'rfq', 'price inquiry', 'quotation request']
    if any(indicator in content_lower for indicator in rfq_indicators):
        intent["primary_type"] = "RFQ"
        intent["confidence"] = 0.9
        # Extract product mentions
        products = re.findall(r'product[s]?\s+([A-Za-z0-9-]+)', content)
        if products:
            intent["key_entities"].extend(products)
    
    # Invoice Detection
    invoice_indicators = ['invoice', 'bill', 'payment', 'amount due']
    if any(indicator in content_lower for indicator in invoice_indicators):
        intent["primary_type"] = "Invoice"
        intent["confidence"] = 0.9
        # Extract amount mentions
        amounts = re.findall(r'\$?\d+(?:,\d{3})*(?:\.\d{2})?', content)
        if amounts:
            intent["key_entities"].extend(amounts)
    
    # Complaint Detection
    complaint_indicators = ['complaint', 'issue', 'problem', 'dissatisfied', 'unhappy']
    if any(indicator in content_lower for indicator in complaint_indicators):
        intent["primary_type"] = "Complaint"
        intent["confidence"] = 0.8
        # Determine severity
        severe_words = ['urgent', 'immediate', 'serious', 'critical']
        if any(word in content_lower for word in severe_words):
            intent["subtype"] = "severe"
            intent["urgency"] = "high"
    
    # Regulation/Policy Detection
    regulation_indicators = ['regulation', 'policy', 'compliance', 'directive', 'law']
    if any(indicator in content_lower for indicator in regulation_indicators):
        intent["primary_type"] = "Regulation"
        intent["confidence"] = 0.85
        # Try to identify specific regulation types
        policy_types = ['safety', 'environmental', 'financial', 'data protection']
        for policy in policy_types:
            if policy in content_lower:
                intent["subtype"] = policy
    
    return intent

def classify_input(raw_text: str) -> Dict[str, Any]:
    """Classify input content with enhanced metadata"""
    # Detect format
    doc_format = detect_format(raw_text)
    
    # Analyze intent
    intent_analysis = analyze_intent(raw_text)
    
    # Additional metadata
    metadata = {
        "timestamp": "",  # Will be added by shared_memory
        "content_length": len(raw_text),
        "has_attachments": "attachment" in raw_text.lower(),
        "confidence_score": intent_analysis["confidence"]
    }
    
    result = {
        "format": doc_format,
        "intent": intent_analysis["primary_type"],
        "subtype": intent_analysis["subtype"],
        "urgency": intent_analysis["urgency"],
        "key_entities": intent_analysis["key_entities"],
        "metadata": metadata
    }
    
    return result
