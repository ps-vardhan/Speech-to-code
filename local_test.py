from speech_to_text import AudioToTextRecorder

def process_text(text):
    print(f"Transcribed: {text}")

if __name__ == '__main__':
    print("Starting local microphone transcription...")
    print("Speak into your microphone. Press Ctrl+C to stop.")
    
    recorder = AudioToTextRecorder(
        model='tiny',  # Use 'tiny' for faster processing
        language='en',
        spinner=True
    )
    
    try:
        while True:
            recorder.text(process_text)
    except KeyboardInterrupt:
        print("\nStopping transcription...")
        recorder.shutdown()