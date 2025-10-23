import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
AUDIO_DIR = ROOT / "audio-to-text"
if str(AUDIO_DIR) not in sys.path:
    sys.path.insert(0, str(AUDIO_DIR))

from speech_to_text import AudioToTextRecorder  # type: ignore
from utils.logger import setup_logger
from utils.text_cleaner import clean_text


def on_text(text: str):
    logger = setup_logger()
    logger.info("Transcript: %s", clean_text(text))
    print(text)


def main():
    print("Starting Concode STT... say something.")
    rec = AudioToTextRecorder()
    while True:
        rec.text(on_text)


if __name__ == "__main__":
    main()
