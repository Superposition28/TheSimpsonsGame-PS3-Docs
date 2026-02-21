import os
import struct

MUS_DIR = os.path.dirname(os.path.abspath(__file__))

def extract_raw_audio(filename="hub_mus.mus"):
    filepath = os.path.join(MUS_DIR, filename)
    if not os.path.exists(filepath):
        print(f"File {filename} not found.")
        return

    outpath = os.path.join(MUS_DIR, filename + ".raw")

    with open(filepath, "rb") as f, open(outpath, "wb") as out:
        header_base = f.read(16)
        if len(header_base) < 16:
            return

        _, word_count = struct.unpack('<II', header_base[0:8])

        # Skip the variable header to reach the 64-byte chunks
        f.seek(16 + (word_count * 4))

        chunk_count = 0
        written_chunks = 0

        while True:
            chunk = f.read(64)
            if len(chunk) < 64:
                break

            chunk_count += 1

            # Filter out chunks that are purely empty padding
            # (either entirely null, or just the 0C padding marker and nulls)
            if chunk == b'\x00' * 64:
                continue
            if chunk == (b'\x0C\x00\x00\x00' + (b'\x00' * 60)):
                continue

            # If it has actual data, write it to the raw file
            out.write(chunk)
            written_chunks += 1

    print(f"Extraction complete for {filename}.")
    print(f"Total chunks scanned: {chunk_count}")
    print(f"Active audio chunks extracted: {written_chunks}")
    print(f"Raw data saved to: {outpath}")

if __name__ == "__main__":
    extract_raw_audio("hub_mus.mus")
    extract_raw_audio("gts_mus.mus")