import re
try:
    from .seper_config import BREAK_WORDS, CODE_INTENT_WORDS
except ImportError:
    # Fallback to local import if run directly or misconfigured
    try:
        from seper_config import BREAK_WORDS, CODE_INTENT_WORDS
    except ImportError:
         print("Warning: Could not import constants from seper_config.")
         BREAK_WORDS = []
         CODE_INTENT_WORDS = set()

def process_string(text: str) -> dict:
    """
    Splits the input text string into 'non_code' and 'code' parts.
    
    Priority: Split at the end of the first found BREAK_WORD or start of first CODE_INTENT_WORD.
    
    1. BREAK_WORDS: Phrases like "the code is" -> Split AFTER the phrase.
    2. CODE_INTENT_WORDS: Keywords like "function", "variable" -> Split BEFORE the word.
       (Because these words are usually PART of the code/pseudocode, e.g. "function foo")
    
    Returns:
        dict: {"non_code": str, "code": str}
    """
    
    # 1. Check for Break Words (Split AFTER)
    # These represent transition phrases, usually NOT part of the code itself, but preceding it.
    if BREAK_WORDS:
        # Sort by length desc to match longest phrase first
        sorted_break = sorted(BREAK_WORDS, key=len, reverse=True)
        pattern_str = r"\b(" + "|".join(re.escape(w) for w in sorted_break) + r")\b"
        break_pattern = re.compile(pattern_str, re.IGNORECASE)
        
        match = break_pattern.search(text)
        if match:
            # Found a break word.
            # Split point is the end of the match. 
            split_idx = match.end()
            
            non_code = text[:split_idx]
            code = text[split_idx:]
            
            return {
                "non_code": non_code, 
                "code": code
            }

    # 2. Check for Code Intent Words (Split BEFORE)
    # These represent the START of the code/pseudocode structure.
    if CODE_INTENT_WORDS:
        # Sort by length desc to ensure "create a function" matches before "function"
        sorted_intent = sorted(list(CODE_INTENT_WORDS), key=len, reverse=True)
        # Use simple word boundary check
        pattern_str = r"\b(" + "|".join(re.escape(w) for w in sorted_intent) + r")\b"
        intent_pattern = re.compile(pattern_str, re.IGNORECASE)
        
        match = intent_pattern.search(text)
        if match:
            # Found an intent word (e.g. "function").
            # The code likely STARTS here.
            split_idx = match.start()
            
            non_code = text[:split_idx]
            code = text[split_idx:]
            
            return {
                "non_code": non_code, 
                "code": code
            }

    # 3. Fallback
    return {
        "non_code": "",
        "code": text
    }

    # 3. Fallback
    return {
        "non_code": "",
        "code": text
    }
