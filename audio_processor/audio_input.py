
# audio_input.py  -- improved audio input helper
from colorama import init, Fore, Style
from scipy.signal import butter, filtfilt, resample_poly
import pyaudio
import logging
import numpy as np

DESIRED_RATE = 16000
CHUNK_SIZE = 1024
AUDIO_FORMAT = pyaudio.paInt16
CHANNELS = 1

class AudioInput:
    def __init__(
            self,
            input_device_index: int = None,
            debug_mode: bool = False,
            target_samplerate: int = DESIRED_RATE,
            chunk_size: int = CHUNK_SIZE,
            audio_format: int = AUDIO_FORMAT,
            channels: int = CHANNELS,
            resample_to_target: bool = True,
        ):

        self.input_device_index = input_device_index
        self.debug_mode = debug_mode
        self.audio_interface = None
        self.stream = None
        self.device_sample_rate = None
        self.target_samplerate = target_samplerate
        self.chunk_size = chunk_size
        self.audio_format = audio_format
        self.channels = channels
        self.resample_to_target = resample_to_target
        self._logger = logging.getLogger("AudioInput")
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s:%(name)s: %(message)s'))
            self._logger.addHandler(handler)
        self._logger.setLevel(logging.INFO if not debug_mode else logging.DEBUG)

    def get_supported_sample_rates(self, device_index):
        standard_rates = [8000, 9600, 11025, 12000, 16000, 22050, 24000, 32000, 44100, 48000]
        supported_rates = []
        try:
            device_info = self.audio_interface.get_device_info_by_index(device_index)
            max_input_channels = int(device_info.get('maxInputChannels', 0))
            for rate in standard_rates:
                try:
                    if self.audio_interface.is_format_supported(
                        rate,
                        input_device=device_index,
                        input_channels=max_input_channels,
                        input_format=self.audio_format,
                    ):
                        supported_rates.append(rate)
                except ValueError:
                    continue
                except Exception:
                    continue
        except Exception as e:
            self._logger.debug(f"get_supported_sample_rates failed: {e}")
        return supported_rates

    def _get_best_sample_rate(self, actual_device_index, desired_rate):
        try:
            device_info = self.audio_interface.get_device_info_by_index(actual_device_index)
            supported_rates = self.get_supported_sample_rates(actual_device_index)
            if not supported_rates:
                default_rate = int(device_info.get('defaultSampleRate', 44100))
                return default_rate
            if desired_rate in supported_rates:
                return desired_rate
            lower = [r for r in supported_rates if r <= desired_rate]
            if lower:
                return max(lower)
            higher = [r for r in supported_rates if r > desired_rate]
            if higher:
                return min(higher)
            return supported_rates[0]
        except Exception as e:
            self._logger.warning(f"Error determining sample rate: {e}")
            return 44100

    def list_devices(self):
        try:
            init()
            self.audio_interface = pyaudio.PyAudio()
            device_count = self.audio_interface.get_device_count()

            print("Available audio input devices:")
            for i in range(device_count):
                device_info = self.audio_interface.get_device_info_by_index(i)
                device_name = device_info.get('name')
                max_input_channels = device_info.get('maxInputChannels', 0)

                if max_input_channels > 0:
                    supported_rates = self.get_supported_sample_rates(i)
                    print(f"{Fore.LIGHTGREEN_EX}Device {Style.RESET_ALL}{i}{Fore.LIGHTGREEN_EX}: {device_name}{Style.RESET_ALL}")
                    if supported_rates:
                        rates_formatted = ", ".join([f"{Fore.CYAN}{rate}{Style.RESET_ALL}" for rate in supported_rates])
                        print(f"  {Fore.YELLOW}Supported sample rates: {rates_formatted}{Style.RESET_ALL}")
                    else:
                        print(f"  {Fore.YELLOW}Supported sample rates: Unknown{Style.RESET_ALL}")

        except Exception as e:
            print(f"Error listing devices: {e}")
        finally:
            if self.audio_interface:
                self.audio_interface.terminate()
                self.audio_interface = None

    def setup(self):
        try:
            self.audio_interface = pyaudio.PyAudio()
            if self.debug_mode:
                self._logger.debug(f"Input device index: {self.input_device_index}")

            try:
                if self.input_device_index is None:
                    default_info = self.audio_interface.get_default_input_device_info()
                    actual_device_index = int(default_info['index'])
                else:
                    actual_device_index = int(self.input_device_index)
            except Exception:
                actual_device_index = None
                for i in range(self.audio_interface.get_device_count()):
                    info = self.audio_interface.get_device_info_by_index(i)
                    if int(info.get('maxInputChannels', 0)) > 0:
                        actual_device_index = i
                        break
                if actual_device_index is None:
                    raise RuntimeError("No input-capable device found")

            self.input_device_index = actual_device_index
            self.device_sample_rate = self._get_best_sample_rate(actual_device_index, self.target_samplerate)

            if self.debug_mode:
                self._logger.debug(f"Opening device {self.input_device_index} with rate {self.device_sample_rate}")

            self.stream = self.audio_interface.open(
                format=self.audio_format,
                channels=self.channels,
                rate=self.device_sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                input_device_index=self.input_device_index,
            )
            if self.debug_mode:
                self._logger.debug(f"Audio recording initialized successfully at {self.device_sample_rate} Hz")
            return True

        except Exception as e:
            print(f"Error initializing audio recording: {e}")
            if self.audio_interface:
                try:
                    self.audio_interface.terminate()
                except Exception:
                    pass
                self.audio_interface = None
            return False

    def lowpass_filter(self, signal_arr, cutoff_freq, sample_rate):
        nyquist_rate = sample_rate / 2.0
        normal_cutoff = cutoff_freq / nyquist_rate
        b, a = butter(5, normal_cutoff, btype='low', analog=False)
        filtered_signal = filtfilt(b, a, signal_arr)
        return filtered_signal

    def resample_audio(self, pcm_data, target_sample_rate, original_sample_rate):
        if target_sample_rate < original_sample_rate:
            pcm_filtered = self.lowpass_filter(pcm_data, target_sample_rate / 2, original_sample_rate)
            resampled = resample_poly(pcm_filtered, target_sample_rate, original_sample_rate)
        else:
            resampled = resample_poly(pcm_data, target_sample_rate, original_sample_rate)
        return resampled

    def read_chunk(self):
        try:
            data = self.stream.read(self.chunk_size, exception_on_overflow=False)
            return data
        except IOError as e:
            self._logger.warning(f"Audio read overflow: {e}")
            return (b'\x00' * self.chunk_size * 2)
        except Exception as e:
            self._logger.error(f"Unhandled error reading audio chunk: {e}")
            raise

    def cleanup(self):
        try:
            if self.stream:
                try:
                    self.stream.stop_stream()
                except Exception:
                    pass
                try:
                    self.stream.close()
                except Exception:
                    pass
                self.stream = None
            if self.audio_interface:
                try:
                    self.audio_interface.terminate()
                except Exception:
                    pass
                self.audio_interface = None
        except Exception as e:
            print(f"Error cleaning up audio resources: {e}")
