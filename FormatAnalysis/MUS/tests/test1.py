import os
import struct
import binascii

# use current dir of script file
MUS_DIR = os.path.dirname(os.path.abspath(__file__))

# Known signatures from the readme
TYPE_1_SIG = b'\x0F\x00\x00\x00\x78\x01\x32\x00'
TYPE_2_SIG = b'\x0B\x00\x00\x00\x02\x03\x02\x03'

def analyze_mus_headers():
    print(f"{'Filename':<15} | {'File ID':<10} | {'Unk/Size':<10} | {'Type'}")
    print("-" * 55)

    for filename in os.listdir(MUS_DIR):
        if not filename.endswith(".mus"):
            continue

        filepath = os.path.join(MUS_DIR, filename)

        with open(filepath, "rb") as f:
            header = f.read(16)
            if len(header) < 16:
                print(f"{filename:<15} | ERROR: File too small")
                continue

            # Unpack the first two 32-bit integers (Little Endian)
            file_id, unk_var = struct.unpack('<II', header[0:8])

            # Check the signature bytes (0x08 to 0x0F)
            signature = header[8:16]

            mus_type = "Unknown"
            if signature == TYPE_1_SIG:
                mus_type = "Type 1"
            elif signature == TYPE_2_SIG:
                mus_type = "Type 2"
            else:
                mus_type = f"Unknown Sig: {binascii.hexlify(signature).decode()}"

            print(f"{filename:<15} | 0x{file_id:<08X} | {unk_var:<10} | {mus_type}")

if __name__ == "__main__":
    analyze_mus_headers()