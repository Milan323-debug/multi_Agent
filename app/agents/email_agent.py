import re
from bs4 import BeautifulSoup
import json
from datetime import datetime
import email
from email import policy
from email.parser import BytesParser

def extract_json_from_text(text):
    """Extract JSON content from text if present"""
    try:
        # Look for JSON-like content between curly braces
        json_match = re.search(r'\{.*\}', text)
        if json_match:
            json_str = json_match.group(0)
            return json.loads(json_str)
    except json.JSONDecodeError:
        return None
    return None

def parse_email(email_content, raw=False):
    if raw:
        # Parse raw email content
        msg = BytesParser(policy=policy.default).parsebytes(email_content.encode())
    else:
        # Parse string email content
        msg = email.message_from_string(email_content, policy=policy.default)

    # Extract basic email metadata
    metadata = {
        "subject": msg.get("subject", ""),
        "from": msg.get("from", ""),
        "to": msg.get("to", ""),
        "date": msg.get("date", ""),
        "message_id": msg.get("message-id", ""),
        "in_reply_to": msg.get("in-reply-to", ""),
        "references": msg.get("references", ""),
        "timestamp": datetime.utcnow().isoformat()
    }

    # Initialize body content
    text_content = ""
    html_content = None
    attachments = []

    # Process email parts
    for part in msg.walk():
        content_type = part.get_content_type()
        if content_type == "text/plain":
            text_content += part.get_content()
        elif content_type == "text/html":
            html_content = part.get_content()
            # Convert HTML to text for analysis
            soup = BeautifulSoup(html_content, 'html.parser')
            text_content += soup.get_text()
        elif part.get_filename():  # Handle attachments
            attachments.append({
                "filename": part.get_filename(),
                "content_type": content_type
            })

    # Analyze content for intent
    urgency = "High" if any(word in text_content.lower() for word in ["urgent", "asap", "emergency"]) else "Normal"
    
    # Determine intent based on content
    intent = "General Inquiry"
    if "request for quote" in text_content.lower() or "rfq" in text_content.lower():
        intent = "RFQ"
    elif "complaint" in text_content.lower() or "dissatisfied" in text_content.lower():
        intent = "Complaint"
    elif "invoice" in text_content.lower() or "payment" in text_content.lower():
        intent = "Invoice"

    # Check for embedded JSON
    embedded_json = extract_json_from_text(text_content)

    return {
        "metadata": metadata,
        "content": {
            "text": text_content,
            "html": html_content is not None,
            "attachments": attachments
        },
        "analysis": {
            "intent": intent,
            "urgency": urgency,
            "has_embedded_json": embedded_json is not None
        },
        "embedded_json": embedded_json
    }
