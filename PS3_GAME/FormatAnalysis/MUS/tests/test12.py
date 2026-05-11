import os
import subprocess

MUS_DIR = os.path.dirname(os.path.abspath(__file__))
VGMSTREAM_PATH = r"A:\RemakeEngine\Main\Tools\vgmstream-cli\vgmstream-cli.exe"

def test_interleaves():
    clean_path = os.path.join(MUS_DIR, "hub_mus.mus.clean.raw")
    if not os.path.exists(clean_path):
        print("Run test11.py first to generate the clean raw file.")
        return

    print("--- Testing PSX ADPCM Interleave Matrix ---")

    # Test common EA stem configurations
    channels_to_test = [6, 8, 12, 16]

    # We saw the ADPCM frames (2F E0 FF) begin around chunk 6 (0x180)
    offsets_to_test = ["0x180", "0x1A0", "0x1C0"]

    for ch in channels_to_test:
        for off in offsets_to_test:
            txth_path = clean_path + ".txth"
            out_wav = os.path.join(MUS_DIR, f"perfect_PSX_{ch}ch_off{off}.wav")

            with open(txth_path, "w") as f:
                f.write(f"codec = PSX\n")
                f.write(f"channels = {ch}\n")
                f.write(f"sample_rate = 48000\n")  # PS3 standard
                f.write(f"interleave = 0x10\n")    # 16-byte PSX frames
                f.write(f"start_offset = {off}\n")
                f.write(f"num_samples = data_size\n")

            cmd = [VGMSTREAM_PATH, "-o", out_wav, clean_path]
            subprocess.run(cmd, capture_output=True)
            print(f"Generated test: {out_wav}")

    print("\n[+] Tests generated!")
    print("Listen to the 'perfect_PSX...' files.")

if __name__ == "__main__":
    test_interleaves()