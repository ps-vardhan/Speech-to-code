from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIO_TO_TEXT_DIR = ROOT / "audio-to-text"
STT_MODULE_PATH = AUDIO_TO_TEXT_DIR / "speech_to_text"

TRIGGER_WORDS = {
    "code": ["code", "coding"],
    "describe": ["describe", "explain"],
    "stop": ["stop", "end"],
}
