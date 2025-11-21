# main.py -- single entrypoint to run the recorder and append transcripts to transcripts.txt
import os
import time
from datetime import datetime

TRANSCRIPT_FILE = "transcripts.txt"

from audio_recorder import AudioToTextRecorder


def append_transcript(text: str, filename: str = TRANSCRIPT_FILE):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {text.strip()}\n"
    with open(filename, "a", encoding="utf-8") as f:
        f.write(line)


def main():
    if not os.path.exists(TRANSCRIPT_FILE):
        open(TRANSCRIPT_FILE, "w", encoding="utf-8").close()

    recorder = AudioToTextRecorder(
        model="tiny",
        device="cpu",
        input_device_index=None,
        sample_rate=16000,
        buffer_size=512,
        post_speech_silence_duration=0.75,
        min_length_of_recording=0.25,
        silero_sensitivity=0.1,
        webrtc_sensitivity=0,
        debug_mode=True,
    )

    try:
        recorder.start()
    except Exception as e:
        print("Failed to start recorder:", e)
        return

    print("Recorder started. Speak into the microphone. Press Ctrl-C to stop.")

    try:
        while True:
            text_result = recorder.text()
            if text_result:
                print("Transcribed:", text_result)
                append_transcript(text_result)
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Stopping...")

    finally:
        recorder.shutdown()
        print("Recorder stopped. Transcripts saved to", TRANSCRIPT_FILE)


if __name__ == "__main__":
    main()
