import os
import subprocess

# Use current dir of script file
MUS_DIR = os.path.dirname(os.path.abspath(__file__))
VGMSTREAM_PATH = r"A:\RemakeEngine\Main\Tools\vgmstream-cli\vgmstream-cli.exe"

def clean_and_test_stream(filename="hub_mus.mus.raw"):
    raw_path = os.path.join(MUS_DIR, filename)
    clean_path = os.path.join(MUS_DIR, filename.replace(".raw", ".clean.raw"))

    if not os.path.exists(raw_path):
        print(f"File not found: {raw_path}")
        return

    print(f"--- Cleaning padding from {filename} ---")
    chunk_count = 0
    padded_chunks = 0
    total_bytes_written = 0

    with open(raw_path, "rb") as f, open(clean_path, "wb") as out:
        while True:
            chunk = f.read(64)
            if not chunk or len(chunk) < 64:
                # write remaining bytes if EOF is reached awkwardly
                if chunk:
                    out.write(chunk)
                break

            chunk_count += 1

            # Find the 0C 00 00 00 marker
            idx = chunk.find(b'\x0C\x00\x00\x00')

            # Strict check: only trim if the marker is found AND all bytes after it are 0x00 padding
            if idx != -1 and all(b == 0 for b in chunk[idx+4:]):
                valid_data = chunk[:idx]
                out.write(valid_data)
                padded_chunks += 1
                total_bytes_written += len(valid_data)
            else:
                out.write(chunk)
                total_bytes_written += len(chunk)

    print(f"Total chunks processed: {chunk_count}")
    print(f"Padded chunks trimmed: {padded_chunks}")
    print(f"Clean continuous stream saved to: {clean_path} ({total_bytes_written} bytes)")

    # 2. Inspect the first 256 bytes of the defragmented stream
    # This will allow us to see the true EA internal headers now that the gaps are removed
    with open(clean_path, "rb") as f:
        head = f.read(256)
        print("\n--- First 256 bytes of CLEAN stream ---")
        for i in range(0, len(head), 16):
            row = head[i:i+16]
            hex_str = " ".join([f"{b:02X}" for b in row])
            ascii_str = "".join([chr(b) if 32 <= b <= 126 else "." for b in row])
            print(f"{i:03X}: {hex_str:<48} | {ascii_str}")

    # 3. Test again with vgmstream on the CLEAN stream
    print("\n--- Testing vgmstream on CLEAN stream ---")

    # We test EA_XAS, PSX ADPCM, and generic interleaved tests
    codecs = [
        ("PSX", 2, "0x40"),
        ("EA_XAS", 2, "0x40"),
        ("EA_XAS", 16, "0x40") # 16 ch from routing table
    ]

    for codec, ch, interleave in codecs:
        txth_path = clean_path + ".txth"
        out_wav = os.path.join(MUS_DIR, f"clean_{codec}_{ch}ch.wav")

        with open(txth_path, "w") as f:
            f.write(f"codec = {codec}\n")
            f.write(f"channels = {ch}\n")
            f.write(f"sample_rate = 44100\n")
            f.write(f"interleave = {interleave}\n")
            f.write(f"num_samples = data_size\n")

        cmd = [VGMSTREAM_PATH, "-o", out_wav, clean_path]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if "failed" not in result.stdout.lower() and "error" not in result.stderr.lower():
            print(f"[+] Decoded {codec} ({ch}ch). Try listening to {out_wav}!")
        else:
            print(f"[-] {codec} rejected.")

if __name__ == "__main__":
    clean_and_test_stream("hub_mus.mus.raw")