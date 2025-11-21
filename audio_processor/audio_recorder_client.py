
# audio_recorder_client.py -- simplified client that records locally and returns transcriptions
# This client is provided for completeness; for a single-machine setup you can use AudioToTextRecorder directly.
import threading
import time
import logging
from audio_recorder import AudioToTextRecorder

logger = logging.getLogger("AudioToTextRecorderClient")
if not logger.handlers:
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(h)
logger.setLevel(logging.INFO)

class AudioToTextRecorderClient:
    """
    Thin wrapper to run a local AudioToTextRecorder and expose a similar API.
    Useful when you want to run the recorder as a separate component.
    """
    def __init__(self, **kwargs):
        self.recorder = AudioToTextRecorder(**kwargs)
        self._started = False

    def start(self):
        if not self._started:
            self.recorder.start()
            self._started = True

    def text(self, timeout: float = None):
        return self.recorder.text(timeout=timeout)

    def shutdown(self):
        self.recorder.shutdown()
