import json

import pvporcupine
import pyaudio
import vosk
import struct
import time

porcupine = pvporcupine.create(
    access_key="...",
    keyword_paths=[r"./models/wakeWord/Hey-Wobble_en_windows_v3_0_0.ppn"],
)

transcriber_model = vosk.Model(model_path=r"./models/transcriber/vosk-model-small-en-us-0.15")
transcriber = vosk.KaldiRecognizer(transcriber_model, porcupine.sample_rate)
transcriber.SetWords(True)

# mic input device
pa = pyaudio.PyAudio()
audio_stream = pa.open(
    rate=porcupine.sample_rate,
    channels=1,
    format=pyaudio.paInt16,
    input=True,
    frames_per_buffer=porcupine.frame_length,
)

def transcribe_audio() -> str:
    audio_stream.start_stream()
    print("Listening...")

    while True:
        data = audio_stream.read(4000, exception_on_overflow=False)
        if transcriber.AcceptWaveform(data):
            result = json.loads(transcriber.Result())
            if result["text"]:
                return result["text"]

while True:
    pcm = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
    pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

    keyword_index = porcupine.process(pcm)
    if keyword_index >= 0:
        print("Keyword detected!")
        request = transcribe_audio()
        print(request)
        if request == "kill":
            exit()
