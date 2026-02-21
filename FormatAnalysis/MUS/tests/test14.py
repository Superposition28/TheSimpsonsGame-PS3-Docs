import os
import struct

MUS_DIR = os.path.dirname(os.path.abspath(__file__))

def demux_mus_stream(filename="hub_mus.mus"):
    filepath = os.path.join(MUS_DIR, filename)
    if not os.path.exists(filepath):
        print(f"File {filename} not found.")
        return

    out_dir = os.path.join(MUS_DIR, f"{filename}_demuxed")
    os.makedirs(out_dir, exist_ok=True)

    with open(filepath, "rb") as f:
        # Read the 16-byte header
        header = f.read(16)
        if len(header) < 16:
            return

        # Unpack as Little Endian based on the Type 1 signature (0F 00 00 00)
        file_id, stream_count, type_a, type_b = struct.unpack('<IIII', header)
        
        print(f"Header ID: {file_id}")
        print(f"Detected Stream/Layer Count: {stream_count}")
        
        # Fallback in case the stream count byte isn't what we expect
        if stream_count == 0 or stream_count > 32:
            print("Warning: Stream count anomalous. Forcing 6 for hub_mus.mus.")
            stream_count = 6
            
        out_files = []
        for i in range(stream_count):
            out_path = os.path.join(out_dir, f"layer_{i}.raw")
            out_files.append(open(out_path, "wb"))

        chunk_idx = 0
        while True:
            chunk = f.read(64)
            if len(chunk) < 64:
                # Write any trailing bytes to the current target
                if len(chunk) > 0:
                    out_files[chunk_idx % stream_count].write(chunk)
                break
            
            # Deal the chunk to its respective stream file
            out_files[chunk_idx % stream_count].write(chunk)
            chunk_idx += 1

        for out_f in out_files:
            out_f.close()

        print(f"Demux complete: {chunk_idx} physical chunks dealt across {stream_count} files.")

if __name__ == "__main__":
    demux_mus_stream("hub_mus.mus")