"""
Utility functions for the Coffee Agent application.
"""
from typing import Dict, Any


def convert_scalekit_response(response) -> Dict[str, Any]:
    """
    Convert a ScaleKit response object to a Python dictionary.
    
    ScaleKit can return different types of response objects:
    - Objects with __dict__ attribute (standard Python objects)
    - Objects with to_dict() method (custom serializable objects)
    - Other types (fallback to string conversion)
    
    Args:
        response: The response object from ScaleKit API
        
    Returns:
        dict: A dictionary representation of the response
    """
    if hasattr(response, '__dict__'):
        # Standard Python object - convert attributes to dict
        return response.__dict__
    elif hasattr(response, 'to_dict'):
        # Object has a to_dict method - use it
        return response.to_dict()
    else:
        # Fallback: convert to string and wrap in dict
        return {"raw_response": str(response)}
