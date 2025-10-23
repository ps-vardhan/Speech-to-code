def parse_command(text: str) -> dict:
    text = text.strip().lower()
    if text.startswith("change loop to "):
        try:
            n = int(text.replace("change loop to ", ""))
            return {"action": "edit_loop", "value": n}
        except ValueError:
            pass
    return {"action": "unknown", "text": text}
