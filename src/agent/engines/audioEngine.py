import atexit
import json
import logging
import os
import struct
from functools import partial
from typing import Optional

import pvporcupine
import pyaudio
import sounddevice as sd
import soundfile as sf
import torch
import vosk
from TTS.api import TTS

from config import settings

logger = logging.getLogger("aura.log")

device = "cuda" if torch.cuda.is_available() else "cpu"


class AudioEngine:
    """
    Audio engine for the agent.
    """

    def __init__(self, wait_for_audio_end: bool = True):
        self.wait_for_audio_end = wait_for_audio_end

        logger.debug("Loading Porcupine Model")
        porcupine_model_path = settings.root_path.joinpath("models/wakeWord",
                                                           settings.hot_word_model)  # TODO: Choose Multiple Wake Words and from config
        self.porcupine = pvporcupine.create(
            access_key=os.getenv("PYVOICE_API_KEY"),
            keyword_paths=[str(porcupine_model_path.absolute())],
        )

        logger.debug("Connecting to Audio Stream (Channel: 1)")
        pa = pyaudio.PyAudio()
        self.audio_stream = pa.open(  # TODO: choose audio channel
            rate=self.porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.porcupine.frame_length,
        )

        logger.debug("Loading Vosk Model")
        vosk_model_path = settings.root_path.joinpath("models/stt", settings.stt_model)
        transcriber_model = vosk.Model(model_path=str(vosk_model_path.absolute()))  # TODO: Model path in config
        self.transcriber = vosk.KaldiRecognizer(transcriber_model, self.porcupine.sample_rate)
        self.transcriber.SetWords(True)

        logger.debug("Loading TTS Model")
        self.premade_audio_path = settings.root_path.joinpath(
            f"models/tts/{settings.tts_model.replace('/', '-')}/premade_audio")
        self.tts = TTS(settings.tts_model).to(device)  # TODO: Choose Model in config
        config = {}
        if self.tts.speakers is not None:
            config["speaker"] = settings.tts_speaker
        if self.tts.languages is not None:
            config["language"] = settings.tts_language
        self.tts_partial = partial(self.tts.tts, **config)
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

    def speech_to_text(self) -> dict[str, str | list[dict[str, str | float]]]:
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

    def text_to_speech(self, text: str) -> None:
        """
        Uses TTS models to convert text to speech.
        :param text: The text to convert to speech.
        """
        if self.wait_for_audio_end:
            try:
                stream = sd.get_stream()
                if stream is not None and stream.active:
                    sd.wait()
            except RuntimeError as e:
                if str(e) == 'play()/rec()/playrec() was not called yet':
                    pass
                else:
                    raise

        audio_array = self.tts_partial(text=text)  # TODO: Speaker and language from config
        sd.play(audio_array, samplerate=22050)

    def play_audio(self, premade_audio_name: str):
        """
        Plays an audio from models/tts/<model_name.replace('/', '-')>/<premade_audio_name>
        :param premade_audio_name: The name of the audio file to play. Must contain the file extension.
        """
        if self.wait_for_audio_end:
            try:
                stream = sd.get_stream()
                if stream is not None and stream.active:
                    sd.wait()
            except RuntimeError as e:
                if str(e) == 'play()/rec()/playrec() was not called yet':
                    pass
                else:
                    raise

        audio_path = self.premade_audio_path.joinpath(premade_audio_name)
        data, samplerate = sf.read(str(audio_path), dtype='float32')
        sd.play(data, samplerate)

    def close(self):
        """Clean up safely."""
        try:
            if self.audio_stream.is_active():
                self.audio_stream.stop_stream()
            self.audio_stream.close()
            logger.info("Successfully shutdown the Audio Engine.")
        except Exception as e:
            logger.error(f"Audio cleanup error: {e}")
