import re

FILLERS = ["um", "uh", "like", "you know"]

def clean_text(text: str) -> str:
    t = text.strip()
    for f in FILLERS:
        t = re.sub(rf"\b{re.escape(f)}\b", "", t, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", t).strip()
