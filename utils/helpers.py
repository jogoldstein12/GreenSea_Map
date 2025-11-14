"""
Helper Functions
Utility functions used throughout the application
"""

import re
from typing import Any, Optional
from datetime import datetime


def fmt_money(value: float, currency: str = "$") -> str:
    """
    Format a number as currency
    
    Args:
        value: Numeric value
        currency: Currency symbol (default: $)
    
    Returns:
        str: Formatted currency string
    """
    try:
        return f"{currency}{value:,.0f}"
    except (TypeError, ValueError):
        return str(value)


def fmt_number(value: float, decimals: int = 0) -> str:
    """
    Format a number with thousand separators
    
    Args:
        value: Numeric value
        decimals: Number of decimal places
    
    Returns:
        str: Formatted number string
    """
    try:
        if decimals == 0:
            return f"{int(value):,}"
        else:
            return f"{value:,.{decimals}f}"
    except (TypeError, ValueError):
        return str(value)


def fmt_percentage(value: float, decimals: int = 1) -> str:
    """
    Format a number as percentage
    
    Args:
        value: Numeric value (0.15 = 15%)
        decimals: Number of decimal places
    
    Returns:
        str: Formatted percentage string
    """
    try:
        return f"{value * 100:.{decimals}f}%"
    except (TypeError, ValueError):
        return str(value)


def sanitize_string(text: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize a string for safe use in HTML/SQL
    
    Args:
        text: Input text
        max_length: Maximum length (optional)
    
    Returns:
        str: Sanitized string
    """
    if not isinstance(text, str):
        text = str(text)
    
    # Remove control characters
    text = re.sub(r'[\x00-\x1F\x7F]', '', text)
    
    # Trim whitespace
    text = text.strip()
    
    # Truncate if needed
    if max_length and len(text) > max_length:
        text = text[:max_length] + "..."
    
    return text


def create_slug(text: str) -> str:
    """
    Create a URL-safe slug from text
    
    Args:
        text: Input text
    
    Returns:
        str: URL-safe slug
    """
    # Convert to lowercase
    slug = text.lower()
    
    # Replace spaces and special chars with underscores
    slug = re.sub(r'[^a-z0-9]+', '_', slug)
    
    # Remove leading/trailing underscores
    slug = slug.strip('_')
    
    # Collapse multiple underscores
    slug = re.sub(r'_+', '_', slug)
    
    return slug


def parse_coordinate(coord: Any) -> Optional[float]:
    """
    Parse a coordinate value (latitude or longitude)
    
    Args:
        coord: Coordinate value (string or number)
    
    Returns:
        float: Parsed coordinate or None if invalid
    """
    try:
        value = float(coord)
        if -180 <= value <= 180:
            return value
        return None
    except (TypeError, ValueError):
        return None


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format a datetime object
    
    Args:
        dt: Datetime object
        format_str: Format string
    
    Returns:
        str: Formatted datetime string
    """
    try:
        return dt.strftime(format_str)
    except (AttributeError, ValueError):
        return str(dt)


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning default if division by zero
    
    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value if division by zero
    
    Returns:
        float: Result or default
    """
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (TypeError, ValueError):
        return default


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length
    
    Args:
        text: Input text
        max_length: Maximum length
        suffix: Suffix to add when truncated
    
    Returns:
        str: Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def extract_zip_code(zip_string: Any) -> Optional[str]:
    """
    Extract and normalize ZIP code
    
    Args:
        zip_string: ZIP code (may include ZIP+4)
    
    Returns:
        str: 5-digit ZIP code or None
    """
    if not zip_string:
        return None
    
    # Convert to string and remove whitespace
    zip_str = str(zip_string).strip()
    
    # Extract first 5 digits
    match = re.match(r'(\d{5})', zip_str)
    if match:
        return match.group(1)
    
    return None


def batch_list(items: list, batch_size: int = 1000):
    """
    Split a list into batches
    
    Args:
        items: List to split
        batch_size: Size of each batch
    
    Yields:
        list: Batch of items
    """
    for i in range(0, len(items), batch_size):
        yield items[i:i + batch_size]

