import os
import struct

MUS_DIR = os.path.dirname(os.path.abspath(__file__))

def dump_header(filename="hub_mus.mus"):
    filepath = os.path.join(MUS_DIR, filename)
    if not os.path.exists(filepath):
        print(f"File {filename} not found.")
        return

    with open(filepath, "rb") as f:
        header_base = f.read(16)
        _, track_count = struct.unpack('<II', header_base[0:8])

        routing_data = f.read(track_count * 4)

        print(f"--- Hex Dump of Variable Header for {filename} ---")
        # Print in rows of 16 bytes
        for i in range(0, len(routing_data), 16):
            chunk = routing_data[i:i+16]
            hex_str = " ".join([f"{b:02X}" for b in chunk])
            print(f"Offset 0x{i+16:02X}: {hex_str}")

if __name__ == "__main__":
    dump_header("hub_mus.mus")
    print("\n")
    dump_header("80b_mus.mus")
