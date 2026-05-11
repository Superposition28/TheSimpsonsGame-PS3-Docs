import os
import struct

MUS_DIR = os.path.dirname(os.path.abspath(__file__))

def find_data_start():
    print(f"{'Filename':<15} | {'Header+TOC Size':<15} | {'First Non-Zero Byte Offset':<25}")
    print("-" * 65)

    for filename in sorted(os.listdir(MUS_DIR)):
        if not filename.endswith(".mus"):
            continue

        filepath = os.path.join(MUS_DIR, filename)

        with open(filepath, "rb") as f:
            header = f.read(16)
            if len(header) < 16:
                continue

            _, track_count = struct.unpack('<II', header[0:8])

            # Calculate where the audio data *should* start if the TOC is just an array of 32-bit ints
            estimated_toc_end = 16 + (track_count * 4)

            f.seek(estimated_toc_end)

            # Scan forward to find the first non-zero byte
            # Many games pad the TOC with 00s until the next logical sector (e.g. 2048 bytes)
            padding_count = 0
            while True:
                byte = f.read(1)
                if not byte:
                    break
                if byte != b'\x00':
                    break
                padding_count += 1

            actual_data_start = estimated_toc_end + padding_count

            print(f"{filename:<15} | 0x{estimated_toc_end:<13X} | 0x{actual_data_start:<8X} (padded {padding_count} bytes)")

if __name__ == "__main__":
    find_data_start()