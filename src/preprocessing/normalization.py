import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer, WordNetLemmatizer
from typing import List, Optional

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
except:
    pass

# Initialize tools
stop_words = set(stopwords.words('english'))
stemmer = PorterStemmer()
lemmatizer = WordNetLemmatizer()

# CV-specific stopwords
CV_STOPWORDS = {
    'email', 'phone', 'address', 'linkedin', 'github', 'http', 'https', 'www',
    'com', 'org', 'net', 'cv', 'resume', 'references', 'available', 'upon',
    'request', 'page', 'date', 'year', 'month', 'name', 'section'
}
stop_words.update(CV_STOPWORDS)

def tokenize_text(text: str) -> List[str]:
    """Tokenize text into words"""
    return word_tokenize(text) if text else []

def remove_stopwords(tokens: List[str]) -> List[str]:
    """Remove stopwords from token list"""
    return [token for token in tokens if token.lower() not in stop_words]

def stem_tokens(tokens: List[str]) -> List[str]:
    """Apply stemming to tokens"""
    return [stemmer.stem(token) for token in tokens]

def lemmatize_tokens(tokens: List[str]) -> List[str]:
    """Apply lemmatization to tokens"""
    return [lemmatizer.lemmatize(token) for token in tokens]

def filter_short_tokens(tokens: List[str], min_length: int = 2) -> List[str]:
    """Filter out short tokens"""
    return [token for token in tokens if len(token) >= min_length]

def normalize_text(text: str, use_lemmatization: bool = True) -> str:
    """
    Main normalization function
    
    Args:
        text: Input text to normalize
        use_lemmatization: Use lemmatization instead of stemming (default: True)
    
    Returns:
        Normalized text
    """
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Tokenize
    tokens = tokenize_text(text)
    
    # Remove stopwords
    tokens = remove_stopwords(tokens)
    
    # Filter short tokens
    tokens = filter_short_tokens(tokens)
    
    # Apply stemming or lemmatization
    if use_lemmatization:
        tokens = lemmatize_tokens(tokens)
    else:
        tokens = stem_tokens(tokens)
    
    return " ".join(tokens)

def get_text_statistics(text: str) -> dict:
    """
    Get statistics about the text
    
    Returns:
        Dictionary with text statistics
    """
    if not text:
        return {}
    
    tokens = tokenize_text(text)
    unique_tokens = set(tokens)
    
    return {
        "word_count": len(tokens),
        "unique_word_count": len(unique_tokens),
        "avg_word_length": sum(len(word) for word in tokens) / len(tokens) if tokens else 0,
        "stopword_count": sum(1 for token in tokens if token.lower() in stop_words)
    }

if __name__ == "__main__":
    # Test the normalization functions
    test_text = "I am running quickly through the beautiful gardens"
    normalized = normalize_text(test_text)
    print(f"Original: {test_text}")
    print(f"Normalized: {normalized}")
    print(f"Statistics: {get_text_statistics(test_text)}")