import os
import struct

MUS_DIR = os.path.dirname(os.path.abspath(__file__))

def parse_cues():
    print(f"{'Filename':<15} | {'Cues Found':<10} | {'First 2 Cues (ID: Start-End)'}")
    print("-" * 75)

    for filename in sorted(os.listdir(MUS_DIR)):
        if not filename.endswith(".mus"):
            continue

        filepath = os.path.join(MUS_DIR, filename)
        with open(filepath, "rb") as f:
            header_base = f.read(16)
            if len(header_base) < 16:
                continue

            # Extract the Total Header Size in Words
            _, word_count = struct.unpack('<II', header_base[0:8])
            header_data = f.read(word_count * 4)

            cues = []
            i = 0

            # Scan through the header to find the 28-byte Cue structs
            while i <= len(header_data) - 28:
                # Check for the constant signature at offset +16
                if header_data[i+16:i+20] == b'\x00\x00\x00\x08':
                    cue_id = header_data[i+8:i+12].hex().upper()
                    start_off = header_data[i+12:i+16].hex().upper()
                    end_off = header_data[i+20:i+24].hex().upper()

                    cues.append(f"[{cue_id}: {start_off}-{end_off}]")
                    i += 28 # Jump to the next cue block
                else:
                    i += 4 # Step forward by 1 word

            display_cues = ", ".join(cues[:2])
            if len(cues) > 2:
                display_cues += " ..."

            print(f"{filename:<15} | {len(cues):<10} | {display_cues}")

if __name__ == "__main__":
    parse_cues()