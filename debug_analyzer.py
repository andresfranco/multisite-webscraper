import sys
sys.path.insert(0, '.')
from webscraper_core.analyzer import process_titles

titles = ["What's new?", "It's great!", "Don't stop."]
text, counter = process_titles(titles)
print('Text:', repr(text))
print('Counter:', counter)
print('Words in counter:', list(counter.keys()))
