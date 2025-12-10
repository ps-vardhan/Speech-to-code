# Main entry point for audio recording and transcription
import os
import time
from datetime import datetime
from audio_recorder import AudioToTextRecorder
from transcript_manager import TranscriptManager

TRANSCRIPT_FILE = r"d:\PseudoCode\output\transcript\audio.log"


def save_session_transcript(transcripts: list, filename: str = TRANSCRIPT_FILE):
    if not transcripts:
        return
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(filename, "a", encoding="utf-8") as file:
        file.write(f"\n--- Session {timestamp} ---\n")
        for i, text in enumerate(transcripts, 1):
            file.write(f"{i}. {text.strip()}\n")
        file.write("---------------------------\n")


def main():
    """Initialize and run the audio transcription recorder."""
    if not os.path.exists(TRANSCRIPT_FILE):
        with open(TRANSCRIPT_FILE, "w", encoding="utf-8") as file:
            pass
    
    # Configure recorder with fixed interval
    recorder = AudioToTextRecorder(
        model="tiny",
        device="cpu",
        input_device_index=None,
        sample_rate=16000,
        buffer_size=512,
        post_speech_silence_duration=0.75,
        min_length_of_recording=0.25,
        silero_sensitivity=0.6,
        webrtc_sensitivity=0,
        debug_mode=True,
    )

    session_transcripts = []
    transcript_manager = TranscriptManager()
    session_start_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    print(f"Session started at: {session_start_time}")

    try:
        recorder.start()
    except Exception as error:
        print(f"Failed to start recorder: {error}")
        return

    print("Recorder started. Listening for speech... Press Ctrl-C to stop.")

    try:
        while True:
            transcribed_text = recorder.text()
            if transcribed_text:
                print(f"Transcribed: {transcribed_text}")
                session_transcripts.append(transcribed_text)
                transcript_manager.save_transcript(transcribed_text, session_start_time)
            
    except KeyboardInterrupt:
        print("Stopping recorder...")

    finally:
        recorder.shutdown()
        save_session_transcript(session_transcripts)
        print(f"Recorder stopped. Session transcripts saved to {TRANSCRIPT_FILE}")


if __name__ == "__main__":
    main()
