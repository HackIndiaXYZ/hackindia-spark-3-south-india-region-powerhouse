"""
Connection utilities for handling Windows 10054 errors
"""

import time
import functools
from typing import Callable, Any

def retry_on_connection_error(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Decorator to retry functions that may fail with Windows connection errors
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each retry
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):  # +1 for initial attempt
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    error_str = str(e).lower()
                    
                    # Check if it's a connection error we should retry
                    is_connection_error = any(keyword in error_str for keyword in [
                        "10054", "forcibly closed", "connection", "timeout", 
                        "network", "socket", "reset", "aborted"
                    ])
                    
                    if not is_connection_error or attempt == max_retries:
                        # Not a connection error or max retries reached
                        raise e
                    
                    print(f"⚠️ Connection error on attempt {attempt + 1}/{max_retries + 1}: {e}")
                    print(f"   Retrying in {current_delay:.1f} seconds...")
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            # This should never be reached, but just in case
            raise last_exception
        
        return wrapper
    return decorator

def is_windows_connection_error(error: Exception) -> bool:
    """
    Check if an error is a Windows connection error (10054)
    
    Args:
        error: The exception to check
        
    Returns:
        True if it's a Windows connection error
    """
    error_str = str(error).lower()
    return any(keyword in error_str for keyword in [
        "10054", "forcibly closed", "connection reset", 
        "existing connection was forcibly closed"
    ])

def format_connection_error_message(error: Exception) -> dict:
    """
    Format a connection error into a user-friendly message
    
    Args:
        error: The connection error
        
    Returns:
        Dictionary with error details
    """
    if is_windows_connection_error(error):
        return {
            "error": "Connection interrupted",
            "details": "Windows connection error (10054). This is common and usually temporary.",
            "suggestions": [
                "Try again in a few moments",
                "Check your internet connection",
                "Consider using a VPN if the problem persists"
            ],
            "retry": True,
            "error_code": "WIN_CONNECTION_10054"
        }
    else:
        return {
            "error": "Connection failed",
            "details": str(error),
            "suggestions": ["Check your internet connection", "Try again later"],
            "retry": True,
            "error_code": "GENERAL_CONNECTION_ERROR"
        }