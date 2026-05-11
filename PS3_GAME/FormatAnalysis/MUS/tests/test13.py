import os
import numpy as np
from scipy.io import wavfile

MUS_DIR = os.path.dirname(os.path.abspath(__file__))

def analyze_audio_math():
    print(f"{'Filename':<30} | {'RMS (Vol)':<10} | {'ZCR (Noise)':<12} | {'Sample Snippet (10 samples)'}")
    print("-" * 110)

    # Find all the test WAV files we generated in test12
    test_files = [f for f in os.listdir(MUS_DIR) if f.startswith("perfect_PSX_") and f.endswith(".wav")]

    if not test_files:
        print("No perfect_PSX_*.wav files found. Make sure test12.py ran successfully.")
        return

    for filename in sorted(test_files):
        filepath = os.path.join(MUS_DIR, filename)

        try:
            # Read the WAV file
            sample_rate, data = wavfile.read(filepath)

            # If it's multi-channel, isolate just the first channel (Channel 0) for analysis
            if len(data.shape) > 1:
                channel_data = data[:, 0]
            else:
                channel_data = data

            # Convert to float for safe math calculations
            channel_data = channel_data.astype(np.float64)

            # 1. Calculate RMS (Root Mean Square) -> Represents Average Volume / Energy
            rms = np.sqrt(np.mean(channel_data**2))

            # 2. Calculate Zero-Crossing Rate (ZCR) -> High ZCR = Static/Noise
            # We check how often the signal changes from positive to negative
            zero_crossings = np.sum(np.abs(np.diff(np.sign(channel_data)))) / 2
            zcr = zero_crossings / len(channel_data)

            # 3. Grab a 10-sample snippet from 1 second into the audio
            start_idx = sample_rate * 1  # 1 second in
            snippet = channel_data[start_idx:start_idx+10].astype(int)
            snippet_str = "[" + ", ".join([str(x) for x in snippet]) + "]"

            print(f"{filename:<30} | {rms:<10.2f} | {zcr:<12.4f} | {snippet_str}")

        except Exception as e:
            print(f"{filename:<30} | ERROR: {str(e)}")

if __name__ == "__main__":
    analyze_audio_math()