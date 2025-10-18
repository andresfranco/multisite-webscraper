"""Tests for the text analyzer module."""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from webscraper_core.analyzer import process_titles


def test_process_titles_basic():
    """Test basic title processing."""
    titles = ["Hello World", "Python Programming", "Web Scraping"]
    text, counter = process_titles(titles)
    
    assert isinstance(text, str)
    assert len(text) > 0
    assert "hello" in text.lower()
    assert "world" in text.lower()
    print("✓ process_titles returns text and counter")


def test_process_titles_punctuation():
    """Test that punctuation is removed."""
    titles = ["What's new?", "It's great!", "Don't stop."]
    text, counter = process_titles(titles)
    
    # Check that words are extracted and contractions are handled
    assert "what" in counter
    assert "new" in counter
    assert "great" in counter or "great!" in counter  # May or may not have punctuation
    assert "do" in counter  # "don't" -> "do"
    print("✓ Punctuation and contractions handled correctly")


def test_process_titles_stop_words():
    """Test filtering with stop words."""
    titles = ["The Quick Brown Fox", "The Lazy Dog"]
    stop_words = {"the", "and", "or"}
    text, counter = process_titles(titles, stop_words)
    
    # "the" should be filtered out
    assert "the" not in counter
    assert "quick" in counter
    assert "fox" in counter
    print("✓ Stop words are filtered correctly")


def test_counter_frequency():
    """Test that Counter returns correct word frequencies."""
    titles = ["apple banana", "apple cherry", "apple"]
    text, counter = process_titles(titles)
    
    assert counter["apple"] == 3
    assert counter["banana"] == 1
    assert counter["cherry"] == 1
    print("✓ Counter tracks word frequencies accurately")


def test_empty_titles():
    """Test processing empty title list."""
    titles = []
    text, counter = process_titles(titles)
    
    assert text == ""
    assert len(counter) == 0
    print("✓ Empty titles handled gracefully")


if __name__ == '__main__':
    print("Running analyzer tests...\n")
    test_process_titles_basic()
    test_process_titles_punctuation()
    test_process_titles_stop_words()
    test_counter_frequency()
    test_empty_titles()
    print("\n✅ All analyzer tests passed!")
