"""Audit and inspect Character Motion Audio Binding (.rcm_b) tables.

Standard-library research and inspection tool.
Validates the 16-byte header, 0xEFBE magic, sorted event hash keys, speaker IDs, and sound aliases.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import struct


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_rcmb(data: bytes) -> dict:
    """Parse .rcm_b (Character Motion Audio Binding Table)."""
    if len(data) < 16:
        raise ValueError(f"File too small for RCM_B header ({len(data)} bytes)")

    ver, count = struct.unpack(">HH", data[:4])
    hdr_size = struct.unpack(">I", data[4:8])[0]
    magic = struct.unpack(">H", data[8:10])[0]
    total_size = struct.unpack(">I", data[12:16])[0]

    if ver != 1:
        raise ValueError(f"Unexpected RCM_B version {ver} (expected 1)")
    if magic != 0xEFBE:
        raise ValueError(f"Unexpected RCM_B magic 0x{magic:04X} (expected 0xEFBE)")
    if total_size != len(data):
        raise ValueError(f"Header size 0x{total_size:X} != file length 0x{len(data):X}")

    expected_size = 16 + (count * 20)
    if expected_size != len(data):
        raise ValueError(f"Declared size 16 + {count}*20 = {expected_size} != file length {len(data)}")

    # Parse 20-byte records
    records = []
    speaker_id = None
    is_sorted = True
    prev_event = 0

    for i in range(count):
        pos = 16 + (i * 20)
        ev_hash, spk_id, alias1, alias2, alias3 = struct.unpack(">5I", data[pos:pos+20])
        if i == 0:
            speaker_id = spk_id
        if ev_hash < prev_event:
            is_sorted = False
        prev_event = ev_hash

        records.append({
            "index": i,
            "event_hash": f"0x{ev_hash:08X}",
            "speaker_id": f"0x{spk_id:08X}",
            "sound_aliases": [
                f"0x{alias1:08X}",
                f"0x{alias2:08X}",
                f"0x{alias3:08X}",
            ],
        })

    return {
        "format": "RCM_B",
        "file_size": len(data),
        "sha256": sha256(data),
        "version": ver,
        "record_count": count,
        "magic": f"0x{magic:04X}",
        "speaker_id": f"0x{speaker_id:08X}" if speaker_id is not None else None,
        "events_sorted": is_sorted,
        "records": records,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect Character Motion Audio Binding (.rcm_b) files")
    parser.add_argument("file", type=Path, help="Path to .rcm_b file")
    args = parser.parse_args()

    data = args.file.read_bytes()
    result = parse_rcmb(data)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

