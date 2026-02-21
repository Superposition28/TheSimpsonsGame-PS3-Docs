import os
import struct
import binascii

# Use current dir of script file
MUS_DIR = os.path.dirname(os.path.abspath(__file__))

def analyze_toc():
    print(f"{'Filename':<15} | {'Count':<5} | {'First 5 TOC Entries (Hex / Decimal)'}")
    print("-" * 80)

    for filename in sorted(os.listdir(MUS_DIR)):
        if not filename.endswith(".mus"):
            continue

        filepath = os.path.join(MUS_DIR, filename)

        with open(filepath, "rb") as f:
            header = f.read(16)
            if len(header) < 16:
                continue

            # Extract the Track Count (Unk/Size)
            _, track_count = struct.unpack('<II', header[0:8])

            # Read the assumed TOC array (track_count * 4 bytes)
            # We'll just read enough to show the first 5 entries
            bytes_to_read = min(track_count * 4, 20)
            toc_data = f.read(bytes_to_read)

            # Unpack the TOC data into 32-bit integers
            num_ints = len(toc_data) // 4
            if num_ints > 0:
                unpack_str = '<' + ('I' * num_ints)
                toc_ints = struct.unpack(unpack_str, toc_data)

                # Format for printing
                toc_str = " | ".join([f"0x{x:08X} ({x})" for x in toc_ints])
                print(f"{filename:<15} | {track_count:<5} | {toc_str}")
            else:
                print(f"{filename:<15} | {track_count:<5} | No TOC data extracted")

if __name__ == "__main__":
    analyze_toc()