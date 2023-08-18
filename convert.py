from typing import cast
import numpy as np
from scipy.io import wavfile
import pickle

from conversion_config import Config

# Parameters for audio generation

with open("left.pickle", "rb") as f:
    audio_signal_left = pickle.load(f)
with open("right.pickle", "rb") as f:
    audio_signal_right = pickle.load(f)
with open("config.pickle", "rb") as f:
    config = cast(Config, pickle.load(f))

# Combine the audio signals for stereo output
stereo_audio_signal = np.column_stack((audio_signal_left, audio_signal_right))

# Export the stereo audio to a WAV file
output_filename = "curve_animation_stereo_audio.wav"
wavfile.write(output_filename, config.sampling_rate, stereo_audio_signal.astype(np.float32))
