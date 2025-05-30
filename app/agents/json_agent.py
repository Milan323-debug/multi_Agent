from typing import Dict, Any, List
from datetime import datetime

class SchemaValidator:
    SCHEMAS = {
        "invoice": {
            "required": ["invoice_number", "date", "amount", "customer"],
            "types": {
                "invoice_number": str,
                "date": str,
                "amount": (int, float),
                "customer": dict,
                "items": list,
                "tax": (int, float),
                "total": (int, float)
            }
        },
        "rfq": {
            "required": ["rfq_number", "date", "items"],
            "types": {
                "rfq_number": str,
                "date": str,
                "customer": dict,
                "items": list,
                "deadline": str
            }
        },
        "complaint": {
            "required": ["reference", "customer", "description"],
            "types": {
                "reference": str,
                "customer": dict,
                "description": str,
                "severity": str,
                "category": str
            }
        }
    }

    @staticmethod
    def validate_type(value: Any, expected_type: Any) -> bool:
        if isinstance(expected_type, tuple):
            return any(isinstance(value, t) for t in expected_type)
        return isinstance(value, expected_type)

def parse_json(json_payload: Dict[str, Any]) -> Dict[str, Any]:
    # Initialize response structure
    result = {
        "valid": True,
        "document_type": "unknown",
        "missing_fields": [],
        "type_errors": [],
        "anomalies": [],
        "processed_data": {},
        "metadata": {
            "timestamp": datetime.utcnow().isoformat(),
            "schema_version": "1.0"
        }
    }

    # Detect document type
    if "invoice_number" in json_payload:
        result["document_type"] = "invoice"
    elif "rfq_number" in json_payload:
        result["document_type"] = "rfq"
    elif "complaint" in json_payload or "reference" in json_payload:
        result["document_type"] = "complaint"

    # Validate against schema if document type is known
    if result["document_type"] in SchemaValidator.SCHEMAS:
        schema = SchemaValidator.SCHEMAS[result["document_type"]]
        
        # Check required fields
        for field in schema["required"]:
            if field not in json_payload:
                result["missing_fields"].append(field)
                result["valid"] = False

        # Validate types
        for field, value in json_payload.items():
            if field in schema["types"]:
                expected_type = schema["types"][field]
                if not SchemaValidator.validate_type(value, expected_type):
                    result["type_errors"].append(f"{field}: expected {expected_type}, got {type(value)}")
                    result["valid"] = False

    # Check for anomalies
    if result["document_type"] == "invoice":
        # Verify amounts
        if "items" in json_payload and "total" in json_payload:
            items_total = sum(item.get("amount", 0) for item in json_payload["items"])
            if abs(items_total - json_payload["total"]) > 0.01:  # Allow small float difference
                result["anomalies"].append("Total amount doesn't match sum of items")

    # Store processed data
    result["processed_data"] = json_payload

    return result
