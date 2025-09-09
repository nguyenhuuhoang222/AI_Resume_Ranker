import re
import unicodedata
from typing import Optional

def remove_special_characters(text: str) -> str:
    """Remove special characters, keep letters, spaces, and basic punctuation"""
    if not text:
        return ""
    # Keep letters, spaces, and basic punctuation (. , - &)
    text = re.sub(r'[^a-zA-Z\s\.\,\-\&]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()

def remove_emails(text: str) -> str:
    """Remove email addresses from text"""
    return re.sub(r'\S+@\S+', '', text)

def remove_urls(text: str) -> str:
    """Remove URLs from text"""
    return re.sub(r'http\S+', '', text)

def remove_phone_numbers(text: str) -> str:
    """Remove phone numbers from text"""
    return re.sub(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', '', text)

def normalize_unicode(text: str) -> str:
    """Normalize unicode characters (remove accents)"""
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')

def clean_text(text: str, remove_digits: bool = False) -> str:
    """
    Main cleaning function that applies all cleaning steps
    
    Args:
        text: Input text to clean
        remove_digits: Whether to remove digits (default: False)
    
    Returns:
        Cleaned text
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Apply cleaning steps in sequence
    text = normalize_unicode(text)
    text = remove_emails(text)
    text = remove_urls(text)
    text = remove_phone_numbers(text)
    
    if remove_digits:
        text = re.sub(r'\d+', '', text)
    
    text = remove_special_characters(text)
    
    return text

if __name__ == "__main__":
    # Test the cleaning functions
    test_text = "John Doe email: john.doe@email.com https://linkedin.com 123-456-7890"
    cleaned = clean_text(test_text)
    print(f"Original: {test_text}")
    print(f"Cleaned: {cleaned}")