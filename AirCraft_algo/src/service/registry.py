"""
API Registry Pattern - Dynamic API handler registration.
"""
from typing import Dict, Any, Callable


class APIRegistry:
    """
    Registry for API handlers.
    Allows dynamic registration of APIs by name.
    """
    _handlers: Dict[str, Callable] = {}
    
    @classmethod
    def register(cls, api_name: str):
        """Decorator to register an API handler."""
        def decorator(handler_class):
            cls._handlers[api_name] = handler_class
            return handler_class
        return decorator
    
    @classmethod
    def get(cls, api_name: str):
        """Get a handler by API name."""
        return cls._handlers.get(api_name)
    
    @classmethod
    def list_apis(cls) -> list:
        """List all registered API names."""
        return list(cls._handlers.keys())


class BaseAPIHandler:
    """Base class for API handlers."""
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the input data and return result."""
        raise NotImplementedError


def get_api_handler(api_name: str) -> BaseAPIHandler:
    """
    Get an API handler instance by name.
    
    Raises:
        ValueError: If API not found
    """
    handler_class = APIRegistry.get(api_name)
    if handler_class is None:
        raise ValueError(f"API '{api_name}' not registered. Available: {APIRegistry.list_apis()}")
    return handler_class()
