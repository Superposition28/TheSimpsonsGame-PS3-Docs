import os
import subprocess

MUS_DIR = os.path.dirname(os.path.abspath(__file__))
DEMUX_DIR = os.path.join(MUS_DIR, "hub_mus.mus_demuxed")
# Ensure this matches the path used in your previous test scripts
VGMSTREAM_PATH = r"A:\RemakeEngine\Main\Tools\vgmstream-cli\vgmstream-cli.exe"

def test_demuxed_layers():
    if not os.path.exists(DEMUX_DIR):
        print(f"Directory not found: {DEMUX_DIR}")
        return

    # We will just test the first layer to find the correct codec
    target_file = os.path.join(DEMUX_DIR, "layer_0.raw")
    if not os.path.exists(target_file):
        print(f"File not found: {target_file}")
        return

    print(f"--- Testing Codecs on {target_file} ---")

    # Testing EA-XAS and PSX ADPCM in both Mono and Stereo
    configs = [
        ("EA_XAS", 1, "0x40"),
        ("EA_XAS", 2, "0x40"),
        ("PSX", 1, "0x40"),
        ("PSX", 2, "0x40")
    ]

    for codec, ch, interleave in configs:
        txth_path = target_file + ".txth"
        out_wav = os.path.join(DEMUX_DIR, f"layer_0_test_{codec}_{ch}ch.wav")

        with open(txth_path, "w") as f:
            f.write(f"codec = {codec}\n")
            f.write(f"channels = {ch}\n")
            f.write(f"sample_rate = 48000\n")
            f.write(f"interleave = {interleave}\n")
            f.write(f"num_samples = data_size\n")

        cmd = [VGMSTREAM_PATH, "-o", out_wav, target_file]

        try:
            subprocess.run(cmd, capture_output=True, text=True)
            print(f"[+] Generated test: {out_wav}")
        except Exception as e:
            print(f"[-] Failed to run vgmstream: {e}")

    print("\n[!] Extraction finished. Check the DEMUX_DIR for the WAV files.")

if __name__ == "__main__":
    test_demuxed_layers()