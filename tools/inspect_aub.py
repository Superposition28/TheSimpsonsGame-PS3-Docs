"""Audit and inspect Audio User Bus (.aub) configuration descriptors.

Standard-library research and inspection tool.
Parses the SSFX global audio bus table, categories, parameters, and master DSP graph.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import struct


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_aub(data: bytes) -> dict:
    """Parse .aub (Audio User Bus / EA Sound Audio Configuration)."""
    if len(data) < 0x80:
        raise ValueError(f"File too small for AUB header ({len(data)} bytes)")

    # Read leading header words
    words = struct.unpack(">10I", data[:40])
    bus_count = words[4]      # e.g. 55 (0x37)
    category_count = words[5] # e.g. 5
    magic = data[0x1C:0x20].decode("ascii", errors="replace")

    if magic != "SSFX":
        raise ValueError(f"Unexpected AUB magic '{magic}' (expected 'SSFX')")

    # Parse 100-byte bus entries starting at 0x80
    buses = []
    start_buses = 0x80
    for i in range(bus_count):
        pos = start_buses + (i * 100)
        if pos + 100 > len(data):
            break
        bus_name = data[pos:pos+64].split(b"\0")[0].decode("ascii", errors="replace").strip()
        cat_name = data[pos+64:pos+96].split(b"\0")[0].decode("ascii", errors="replace").strip()
        param_u32 = struct.unpack(">I", data[pos+96:pos+100])[0]
        param_f32 = struct.unpack(">f", data[pos+96:pos+100])[0]

        buses.append({
            "index": i,
            "offset": f"0x{pos:04X}",
            "bus_name": bus_name,
            "category": cat_name,
            "param_hex": f"0x{param_u32:08X}",
            "param_float": round(param_f32, 4) if abs(param_f32) < 10000 else None,
        })

    # Scan trailing DSP nodes and acoustic zones starting after buses table
    dsp_nodes = []
    cur = start_buses + (bus_count * 100)
    while cur < len(data) - 24:
        name_bytes = data[cur+20:cur+64].split(b"\0")[0]
        if len(name_bytes) >= 3 and all(32 <= b < 127 for b in name_bytes):
            node_name = name_bytes.decode("ascii", errors="replace").strip()
            dsp_nodes.append({
                "offset": f"0x{cur:04X}",
                "name": node_name,
            })
            cur += 64
        else:
            cur += 4

    return {
        "format": "AUB",
        "file_size": len(data),
        "sha256": sha256(data),
        "magic": magic,
        "declared_bus_count": bus_count,
        "declared_category_count": category_count,
        "buses": buses,
        "dsp_nodes_count": len(dsp_nodes),
        "dsp_nodes": dsp_nodes,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect Audio User Bus (.aub) files")
    parser.add_argument("file", type=Path, help="Path to .aub file")
    args = parser.parse_args()

    data = args.file.read_bytes()
    result = parse_aub(data)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

