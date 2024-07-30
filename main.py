import pyaudio
import wave
import numpy as np

RATE = 16000
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1

SILENCE_THRESHOLD = 300
SILENCE_FRAMES_THRESHOLD = 30
ENERGY_HISTORY_LEN = 50

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("Listening...")

recording = False
audio_buffer = []
energy_history = []

while True:
    audio_data = stream.read(CHUNK, exception_on_overflow=False)

    audio_array = np.frombuffer(audio_data, dtype=np.int16)

    rms = np.sqrt(np.mean(np.square(audio_array)))

    energy_history.append(rms)

    energy_history = energy_history[-ENERGY_HISTORY_LEN:]

    moving_avg_energy = sum(energy_history) / len(energy_history)

    if moving_avg_energy < SILENCE_THRESHOLD:
        if recording:
            silence_frames += 1

            if silence_frames >= SILENCE_FRAMES_THRESHOLD:
                break
        continue

    silence_frames = 0

    if not recording:
        recording = True

    audio_buffer.append(audio_data)

full_audio = b''.join(audio_buffer)

output_file = "output.wav"

with wave.open(output_file, 'wb') as wf:
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(full_audio)

print("Speech saved to", output_file)

stream.stop_stream()
stream.close()
p.terminate()
