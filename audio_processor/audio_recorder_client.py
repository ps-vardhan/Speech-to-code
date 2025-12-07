# Client wrapper for audio recorder
# Provides a simplified interface for local recording and transcription
import logging
from audio_recorder import AudioToTextRecorder

logger = logging.getLogger("AudioToTextRecorderClient")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


class AudioToTextRecorderClient:
    """
    Wrapper for AudioToTextRecorder providing a simplified API.
    Useful for running the recorder as a separate component.
    """
    def __init__(self, **kwargs):
        self.recorder = AudioToTextRecorder(**kwargs)
        self._is_running = False

    def start(self):
        """Start the audio recorder."""
        if not self._is_running:
            self.recorder.start()
            self._is_running = True

    def text(self, timeout: float = None):
        """Retrieve transcribed text."""
        return self.recorder.text(timeout=timeout)

    def shutdown(self):
        """Stop the recorder and clean up resources."""
        self.recorder.shutdown()
        self._is_running = False
