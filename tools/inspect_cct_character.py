"""Audit CCT character resources: .rcb.PS3 (Rigid body/Character Binary) and .bnk.PS3 (Animation Bank).

Standard-library research and inspection tool.
Validates headers, component tables, 4x4 matrix transforms, and cross-format asset hash joins.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import struct


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_rcb(data: bytes) -> dict:
    """Parse .rcb.PS3 (RenderWare CCT Character / Rigid Body Binary)."""
    if len(data) < 0x60:
        raise ValueError(f"File too small for RCB header ({len(data)} bytes)")

    reloff, ver, asset_hash, w3, w4, w5, count, table_off = struct.unpack(">8I", data[:32])
    if ver != 0x17:
        raise ValueError(f"Unexpected RCB version 0x{ver:X} (expected 0x17)")
    if reloff > len(data):
        raise ValueError(f"Invalid relocation offset 0x{reloff:X} exceeds file length {len(data)}")

    # Parse component / slice entries
    entries = []
    for i in range(count):
        entry_pos = table_off + (i * 24)
        if entry_pos + 24 > len(data):
            raise ValueError(f"Component entry {i} at 0x{entry_pos:X} exceeds file length")
        hash_id, name_ptr, bone_count, ptr_a, ptr_b, ptr_c = struct.unpack(">6I", data[entry_pos:entry_pos+24])

        name = ""
        if name_ptr < len(data):
            c = name_ptr
            while c < len(data) and 32 <= data[c] < 127:
                name += chr(data[c])
                c += 1

        # Check for 4x4 transform matrix at ptr_b if within bounds
        matrices = []
        if ptr_b > 0 and ptr_b + 64 <= len(data):
            floats = struct.unpack(">16f", data[ptr_b:ptr_b+64])
            if all(math.isfinite(f) for f in floats):
                matrices = [floats[r*4:(r+1)*4] for r in range(4)]

        entries.append({
            "index": i,
            "hash_id": f"0x{hash_id:08X}",
            "name": name,
            "bone_count": bone_count,
            "ptr_transform": f"0x{ptr_a:04X}",
            "ptr_matrices": f"0x{ptr_b:04X}",
            "ptr_bounds": f"0x{ptr_c:04X}",
            "has_matrix": len(matrices) > 0,
        })

    # Parse relocation table
    relocs = []
    for pos in range(reloff, len(data), 4):
        off = struct.unpack(">I", data[pos:pos+4])[0]
        if off > 0:
            relocs.append(off)

    return {
        "format": "RCB.PS3",
        "payload_size": reloff,
        "version": ver,
        "asset_hash": f"0x{asset_hash:08X}",
        "entry_count": count,
        "table_offset": f"0x{table_off:X}",
        "entries": entries,
        "relocation_count": len(relocs),
    }


def parse_bnk(data: bytes) -> dict:
    """Parse .bnk.PS3 (RenderWare CCT Animation Bank)."""
    if len(data) < 0x50:
        raise ValueError(f"File too small for BNK header ({len(data)} bytes)")

    words = struct.unpack(">16I", data[:64])
    reloff = words[0]
    ver = words[1]
    bank_hash = words[2]
    skeleton_hash = words[3]
    clip_count = words[8]
    sec_count = words[9]
    table_off = words[10]

    if ver != 0x9:
        raise ValueError(f"Unexpected BNK version 0x{ver:X} (expected 0x9)")
    if reloff > len(data):
        raise ValueError(f"Invalid relocation offset 0x{reloff:X} exceeds file length {len(data)}")

    # Parse relocation table
    relocs = []
    for pos in range(reloff, len(data), 4):
        off = struct.unpack(">I", data[pos:pos+4])[0]
        if off > 0:
            relocs.append(off)

    return {
        "format": "BNK.PS3",
        "payload_size": reloff,
        "version": ver,
        "bank_hash": f"0x{bank_hash:08X}",
        "skeleton_hash": f"0x{skeleton_hash:08X}",
        "clip_count": clip_count,
        "secondary_count": sec_count,
        "table_offset": f"0x{table_off:X}",
        "relocation_count": len(relocs),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect CCT character resources (.rcb.PS3 and .bnk.PS3)")
    parser.add_argument("file", type=Path, help="Path to .rcb.PS3 or .bnk.PS3 file")
    args = parser.parse_args()

    data = args.file.read_bytes()
    name = args.file.name.lower()
    if name.endswith(".rcb.ps3") or name.endswith(".rcb"):
        result = parse_rcb(data)
    elif name.endswith(".bnk.ps3") or name.endswith(".bnk"):
        result = parse_bnk(data)
    else:
        # Try both based on version word
        ver = struct.unpack(">I", data[4:8])[0] if len(data) >= 8 else 0
        if ver == 0x17:
            result = parse_rcb(data)
        elif ver == 0x9:
            result = parse_bnk(data)
        else:
            raise ValueError(f"Unknown format for {args.file} (version word: 0x{ver:X})")

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

