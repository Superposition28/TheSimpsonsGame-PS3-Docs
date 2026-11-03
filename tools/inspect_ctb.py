"""Audit and inspect Audio Control Table (.ctb) files.

Standard-library research and inspection tool.
Parses the version 6 header, 44-byte cue records, event cue names, 3D parameters,
and sound alias ID tables linking to .alb sound banks.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import struct


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_ctb(data: bytes) -> dict:
    """Parse .ctb (Audio Control Table)."""
    if len(data) < 0x38:
        raise ValueError(f"File too small for CTB header ({len(data)} bytes)")

    version, subtype = struct.unpack(">HH", data[:4])
    if version != 6:
        raise ValueError(f"Unexpected CTB version {version} (expected 6)")

    cue_count = struct.unpack(">H", data[0x10:0x12])[0]
    asset_hash = struct.unpack(">I", data[0x18:0x1C])[0]
    default_gain = struct.unpack(">f", data[0x1C:0x20])[0]

    cues = []
    for i in range(cue_count):
        pos = 0x38 + i * 44
        if pos + 12 > len(data):
            raise ValueError(f"Cue record {i} offset 0x{pos:X} exceeds file size 0x{len(data):X}")

        tag, sub, c1, alias_count = data[pos], data[pos+1], data[pos+2], data[pos+3]
        str_off = struct.unpack(">I", data[pos+4:pos+8])[0]
        id_off = struct.unpack(">I", data[pos+8:pos+12])[0]

        if str_off >= len(data):
            raise ValueError(f"Cue {i} string offset 0x{str_off:X} out of bounds")
        if id_off >= len(data):
            raise ValueError(f"Cue {i} ID offset 0x{id_off:X} out of bounds")

        end = data.find(b"\0", str_off)
        name = data[str_off:end].decode("ascii", errors="replace") if end != -1 else ""

        # Extract 3D parameters if within record bounds
        target_hash = 0
        floats = []
        if pos + 40 <= len(data) and (i < cue_count - 1 or pos + 40 <= id_off):
            target_hash = struct.unpack(">I", data[pos+12:pos+16])[0]
            floats = list(struct.unpack(">6f", data[pos+16:pos+40]))

        # Read Sound Alias IDs
        aliases = []
        for a_idx in range(alias_count):
            a_pos = id_off + a_idx * 4
            if a_pos + 4 <= len(data):
                a_id = struct.unpack(">I", data[a_pos:a_pos+4])[0]
                aliases.append(f"0x{a_id:08X}")

        tag_char = chr(tag) if 32 <= tag < 127 else f"\\x{tag:02X}"
        cues.append({
            "index": i,
            "tag": f"0x{tag:02X} ('{tag_char}')",
            "subtype": sub,
            "weight": c1,
            "alias_count": alias_count,
            "event_name": name,
            "string_offset": f"0x{str_off:04X}",
            "alias_offset": f"0x{id_off:04X}",
            "target_hash": f"0x{target_hash:08X}",
            "volume": round(floats[0], 2) if floats else 1.0,
            "pitch_or_pan": round(floats[1], 2) if len(floats) > 1 else 0.0,
            "min_distance": round(floats[2], 2) if len(floats) > 2 else 0.0,
            "max_distance": round(floats[3], 2) if len(floats) > 3 else 0.0,
            "aliases": aliases,
        })

    return {
        "format": "CTB",
        "file_size": len(data),
        "sha256": sha256(data),
        "version": version,
        "cue_count": cue_count,
        "asset_hash": f"0x{asset_hash:08X}",
        "default_gain": round(default_gain, 2),
        "cues": cues,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect Audio Control Table (.ctb) files")
    parser.add_argument("file", type=Path, help="Path to .ctb file")
    args = parser.parse_args()

    data = args.file.read_bytes()
    result = parse_ctb(data)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

