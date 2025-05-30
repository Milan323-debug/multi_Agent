import redis
import json
from datetime import datetime
from typing import Dict, Any, Optional

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def store_data(key: str, data: Dict[str, Any], source: Optional[str] = None) -> None:
    # Add metadata
    metadata = {
        "timestamp": datetime.utcnow().isoformat(),
        "source": source or "unknown",
        "version": "1.0"
    }
    
    # Combine data with metadata
    stored_data = {
        "data": data,
        "metadata": metadata
    }
    
    r.set(key, json.dumps(stored_data))

def get_data(key: str) -> Optional[Dict[str, Any]]:
    value = r.get(key)
    return json.loads(value) if value else None

def update_data(key: str, update_fields: Dict[str, Any], source: Optional[str] = None) -> None:
    existing = get_data(key)
    if existing and "data" in existing:
        # Update only the data portion
        existing["data"].update(update_fields)
        # Update metadata
        existing["metadata"]["timestamp"] = datetime.utcnow().isoformat()
        existing["metadata"]["source"] = source or existing["metadata"].get("source", "unknown")
        store_data(key, existing["data"], source)
    else:
        # If no existing data, create new entry
        store_data(key, update_fields, source)

def get_processing_history(key: str) -> list:
    """Get the processing history of a document by its key"""
    data = get_data(key)
    if data and "metadata" in data:
        return [data["metadata"]]
    return []
