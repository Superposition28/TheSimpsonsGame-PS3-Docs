import os
import struct

MUS_DIR = os.path.dirname(os.path.abspath(__file__))

def inspect_chunks(filename="hub_mus.mus", num_chunks=10):
    filepath = os.path.join(MUS_DIR, filename)
    if not os.path.exists(filepath):
        return

    with open(filepath, "rb") as f:
        header_base = f.read(16)
        _, track_count = struct.unpack('<II', header_base[0:8])

        # Skip the variable routing header
        f.seek(16 + (track_count * 4))

        print(f"--- First {num_chunks} Chunks of {filename} ---")
        for i in range(num_chunks):
            chunk = f.read(64)
            if len(chunk) < 64:
                break

            # Print the first 16 bytes of the chunk to see the block header
            hex_str = " ".join([f"{b:02X}" for b in chunk[:16]])

            # Check if it ends in our padding marker
            is_padded = b'\x0C\x00\x00\x00' in chunk
            pad_str = "[PADDED]" if is_padded else ""

            print(f"Chunk {i:02d}: {hex_str} ... {pad_str}")

if __name__ == "__main__":
    inspect_chunks("hub_mus.mus", 15)
