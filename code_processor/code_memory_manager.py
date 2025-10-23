from dataclasses import dataclass
from typing import Dict

@dataclass
class CodeBlock:
    path: str
    content: str

class CodeMemoryManager:
    def __init__(self):
        self.blocks: Dict[str, CodeBlock] = {}

    def update(self, path: str, content: str):
        self.blocks[path] = CodeBlock(path, content)

    def get(self, path: str) -> str | None:
        block = self.blocks.get(path)
        return block.content if block else None
