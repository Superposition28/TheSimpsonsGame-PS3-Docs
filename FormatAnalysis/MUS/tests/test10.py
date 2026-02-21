import os
import subprocess

MUS_DIR = os.path.dirname(os.path.abspath(__file__))
VGMSTREAM_PATH = r"A:\RemakeEngine\Main\Tools\vgmstream-cli\vgmstream-cli.exe"

def create_and_test_txth(filename, codec_name, channels, interleave, sample_rate=48000):
    raw_path = os.path.join(MUS_DIR, filename)
    txth_path = raw_path + ".txth"
    out_path = os.path.join(MUS_DIR, f"{filename}_{codec_name}_{channels}ch.wav")

    # Write the TXTH configuration file
    with open(txth_path, "w") as f:
        f.write(f"codec = {codec_name}\n")
        f.write(f"channels = {channels}\n")
        f.write(f"sample_rate = {sample_rate}\n")
        f.write(f"interleave = {interleave}\n")
        f.write(f"num_samples = data_size\n") # Let vgmstream guess the length

    print(f"\n--- Testing Codec: {codec_name} | Channels: {channels} | Interleave: {interleave} ---")

    cmd = [VGMSTREAM_PATH, "-o", out_path, raw_path]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if "failed" in result.stdout.lower() or "error" in result.stderr.lower():
            print(f"[!] vgmstream rejected {codec_name}.")
        else:
            print(f"[+] SUCCESS! Decoded using {codec_name}.")
            print(f"    Saved to: {out_path}")
    except Exception as e:
        print(f"Error executing vgmstream: {e}")

if __name__ == "__main__":
    # Theory 1: It's PlayStation 3 ADPCM (very common for multi-platform EA games on PS3)
    # We test 2 channels (stereo), with an interleave of 64 bytes (0x40) or 32 bytes (0x20)
    create_and_test_txth("hub_mus.mus.raw", "PSX", channels=2, interleave="0x40")

    # Theory 2: It's EA's proprietary XAS ADPCM codec
    create_and_test_txth("hub_mus.mus.raw", "EA_XAS", channels=2, interleave="0x40")

    # Theory 3: It's EA XAS but multiplexed across all 16 channels we saw in the routing table
    create_and_test_txth("hub_mus.mus.raw", "EA_XAS", channels=16, interleave="0x40")