import setuptools
import os

# Get the absolute path of requirements.txt
req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")

# Read requirements.txt safely
with open(req_path, "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

# Read README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="speech-to-text",
    version="0.4.0",
    author="Kolja Beigel",
    author_email="kolja.beigel@web.de",
    description="A fast Voice Activity Detection and Transcription System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/KoljaB/RealTimeSTT",
    packages=setuptools.find_packages(include=["speech_to_text", "speech_to_text_server"]),
    python_requires='>=3.6',
    license='MIT',
    install_requires=requirements,
    keywords="real-time, audio, transcription, speech-to-text, voice-activity-detection, VAD, real-time-transcription, ambient-noise-detection, microphone-input, faster_whisper, speech-recognition, voice-assistants, audio-processing, buffered-transcription, pyaudio, ambient-noise-level, voice-deactivity",
    package_data={"speech_to_text": ["warmup_audio.wav"]},
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'stt-server=speech_to_text_server.stt_server:main',
            'stt=speech_to_text_server.stt_cli_client:main',
        ],
    },
)
