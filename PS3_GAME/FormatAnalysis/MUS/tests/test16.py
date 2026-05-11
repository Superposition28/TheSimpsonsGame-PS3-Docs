import os
import subprocess

MUS_DIR = os.path.dirname(os.path.abspath(__file__))
DEMUX_DIR = os.path.join(MUS_DIR, "hub_mus.mus_demuxed")
VGMSTREAM_PATH = r"A:\RemakeEngine\Main\Tools\vgmstream-cli\vgmstream-cli.exe"

def clean_and_test_layer(layer_num=0):
    raw_path = os.path.join(DEMUX_DIR, f"layer_{layer_num}.raw")
    clean_path = os.path.join(DEMUX_DIR, f"layer_{layer_num}.clean.raw")

    if not os.path.exists(raw_path):
        print(f"File not found: {raw_path}")
        return

    print(f"--- Cleaning padding from layer_{layer_num}.raw ---")
    
    chunk_count = 0
    padded_chunks = 0
    total_bytes = 0

    with open(raw_path, "rb") as f, open(clean_path, "wb") as out:
        while True:
            chunk = f.read(64)
            if not chunk:
                break
            
            chunk_count += 1
            
            # Check for the 0C 00 00 00 padding marker
            idx = chunk.find(b'\x0C\x00\x00\x00')
            
            if idx != -1:
                # Keep only the valid data before the marker
                valid_data = chunk[:idx]
                out.write(valid_data)
                padded_chunks += 1
                total_bytes += len(valid_data)
            else:
                # Write the whole 64-byte chunk if no marker was found
                out.write(chunk)
                total_bytes += len(chunk)

    print(f"Total chunks processed: {chunk_count}")
    print(f"Padded chunks trimmed: {padded_chunks}")
    print(f"Clean continuous stream saved to: {clean_path} ({total_bytes} bytes)")

    # Test the clean stream with vgmstream
    print(f"\n--- Testing clean stream ---")
    configs = [
        ("EA_XAS", 1, "0x40"),
        ("EA_XAS", 2, "0x40"),
        ("PSX", 1, "0x40"),
        ("PSX", 2, "0x40")
    ]

    for codec, ch, interleave in configs:
        txth_path = clean_path + ".txth"
        out_wav = os.path.join(DEMUX_DIR, f"layer_{layer_num}_clean_{codec}_{ch}ch.wav")

        with open(txth_path, "w") as f:
            f.write(f"codec = {codec}\n")
            f.write(f"channels = {ch}\n")
            f.write(f"sample_rate = 48000\n")
            f.write(f"interleave = {interleave}\n")
            f.write(f"num_samples = data_size\n")

        cmd = [VGMSTREAM_PATH, "-o", out_wav, clean_path]
        try:
            subprocess.run(cmd, capture_output=True, text=True)
            print(f"[+] Generated: {out_wav}")
        except Exception as e:
            print(f"[-] Failed: {e}")

if __name__ == "__main__":
    clean_and_test_layer(0)