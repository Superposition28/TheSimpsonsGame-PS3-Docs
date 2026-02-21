import os

# use current dir of script file
MUS_DIR = os.path.dirname(os.path.abspath(__file__))

PADDING_MARKER = b'\x0C\x00\x00\x00'

def analyze_mus_chunks(filename_to_test):
    filepath = os.path.join(MUS_DIR, filename_to_test)

    chunk_count = 0
    padded_chunks = 0

    with open(filepath, "rb") as f:
        # Skip the 16-byte header
        f.seek(16)

        while True:
            chunk = f.read(64)
            if not chunk or len(chunk) < 64:
                break

            chunk_count += 1

            # Check if the padding marker exists anywhere in this 64-byte chunk
            if PADDING_MARKER in chunk:
                padded_chunks += 1

    percent_padded = (padded_chunks / chunk_count) * 100 if chunk_count > 0 else 0
    print(f"File: {filename_to_test}")
    print(f"Total 64-byte chunks: {chunk_count}")
    print(f"Chunks containing padding marker (0C 00 00 00): {padded_chunks} ({percent_padded:.2f}%)")

if __name__ == "__main__":
    # Test on a smaller file first, like hub_mus.mus
    analyze_mus_chunks("hub_mus.mus")