import logging

class CodeT5Handler:
    def __init__(self, model_path: str | None = None):
        self.model_path = model_path
        logging.getLogger(__name__).info("Initialized CodeT5Handler with model_path=%s", model_path)

    def generate(self, prompt: str) -> str:
        return f"[CodeT5 stub] Generated code for prompt: {prompt[:60]}..."
