import re
from collections import Counter
from typing import List, Tuple


def process_titles(titles: List[str], stop_words: set | None = None) -> Tuple[str, Counter]:
    """Analyze titles and return (combined_text, Counter of word frequencies).

    Pure function: no printing or I/O.
    """
    if not titles:
        return "", Counter()

    if stop_words is None:
        stop_words = set(['the', 'a', 'is', 'in'])

    output_text = '\n'.join(titles)

    text = output_text.lower()
    text = text.replace("’", "'").replace("‘", "'")
    text = text.replace("'", "")
    text = re.sub(r"[\"\#\$%&\(\)\*\+,\./:;<=>?@\[\\\]^_`\{|\}~]", " ", text)

    words = [w for w in text.split() if w and w not in stop_words]

    contraction_map = {
        'whats': 'what',
        'cant': 'can',
        'dont': 'do',
        'doesnt': 'does',
        'isnt': 'is',
    }
    normalized_words = [contraction_map.get(w, w) for w in words]

    freq = Counter(normalized_words)
    # Return the combined text and the full Counter so callers can aggregate
    return output_text, freq
