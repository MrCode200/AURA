import atexit
import json
import os
import struct
from typing import Optional
from pathlib import Path

import pvporcupine
import pyaudio
import vosk

import logging

logger = logging.getLogger("aura.log")



class AudioEngine:
    """
    Audio engine for the agent.
    """
    def __init__(self):
        porcupine_model_path = Path(Path(".").resolve().parent, "models/wakeWord", "Hey-Wobble_en_windows_v3_0_0.ppn") # TODO: Choose Multiple Wake Words
        self.porcupine = pvporcupine.create(
            access_key=os.getenv("PYVOICE_API_KEY"),
            keyword_paths=[str(porcupine_model_path.absolute())],
        )

        vosk_model_path = Path(Path(".").resolve().parent, "models/stt", "vosk-model-small-en-us-0.15")
        transcriber_model = vosk.Model(model_path=str(vosk_model_path.absolute()))  # TODO: Model path in config
        self.transcriber = vosk.KaldiRecognizer(transcriber_model, self.porcupine.sample_rate)
        self.transcriber.SetWords(True)

        pa = pyaudio.PyAudio()
        self.audio_stream = pa.open(  # TODO: choose audio channel
            rate=self.porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.porcupine.frame_length,
        )

        atexit.register(self.close)

    def listen_for_wake_word(self) -> Optional[bool]:
        """
        Listens indefinitely for the wake word and returns when it is detected.
        :return: True if the wake word is detected
        """
        self.audio_stream.start_stream()

        while True:
            pcm = self.audio_stream.read(self.porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)

            keyword_index = self.porcupine.process(pcm)
            if keyword_index >= 0:
                self.audio_stream.stop_stream()
                return True

    def transcribe_audio(self) -> dict[str, str | list[dict[str, str | float]]]:
        """
        Uses a vosk Model to transcribes audio indefinitely and returns the transcribed text.
        :return: A dict containing the
            {
                'result': [{'conf': float, 'end': float, 'start': float, 'text': str}],
                'text': str
            }.
        """
        self.audio_stream.start_stream()

        while True:
            data = self.audio_stream.read(4000, exception_on_overflow=False)
            if self.transcriber.AcceptWaveform(data):
                result: dict[str, str | list[dict[str, str | float]]] = json.loads(self.transcriber.Result())
                if result:
                    self.audio_stream.stop_stream()
                    return result

    def close(self):
        """Clean up safely."""
        try:
            if self.audio_stream.is_active():
                self.audio_stream.stop_stream()
            self.audio_stream.close()
            logger.info("Successfully shutdown the Audio Engine.")
        except Exception as e:
            logger.error(f"Audio cleanup error: {e}")
