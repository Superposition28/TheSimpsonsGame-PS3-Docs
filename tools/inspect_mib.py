"""Audit and inspect Audio Mix Snapshot (.mib) files.

Standard-library research and inspection tool.
Parses the 48-byte header, 44-byte mix bus ducking/gain records,
and 32-byte DSP parameter override records (e.g. helium pitch shifts and robobart filters).
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import struct


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_mib(data: bytes) -> dict:
    """Parse .mib (Audio Mix Snapshot Binary)."""
    if len(data) < 48:
        raise ValueError(f"File too small for MIB header ({len(data)} bytes)")

    bus_count = struct.unpack(">I", data[0x20:0x24])[0]
    dsp_count = struct.unpack(">I", data[0x28:0x2C])[0]
    payload_size = struct.unpack(">I", data[0x2C:0x30])[0]

    expected_size = 48 + (bus_count * 44) + (dsp_count * 32)
    if expected_size != len(data):
        raise ValueError(f"Declared size 48 + {bus_count}*44 + {dsp_count}*32 = {expected_size} != file length {len(data)}")

    # Parse 44-byte mix bus records
    buses = []
    for i in range(bus_count):
        pos = 48 + i * 44
        bus_hash = struct.unpack(">I", data[pos:pos+4])[0]
        floats = [round(struct.unpack(">f", data[pos+j*4:pos+(j+1)*4])[0], 3) for j in range(1, 9)]
        flags, reserved = struct.unpack(">II", data[pos+36:pos+44])

        buses.append({
            "index": i,
            "bus_hash": f"0x{bus_hash:08X}",
            "volume_or_ducking": floats[0],
            "attack_sec": floats[1],
            "release_sec": floats[2],
            "threshold": floats[3],
            "param_pitch": floats[4],
            "param_filter": floats[5],
            "wet_dry": floats[6],
            "reverb_send": floats[7],
            "flags": f"0x{flags:08X}",
        })

    # Parse 32-byte DSP parameter override records
    dsp_records = []
    dsp_start = 48 + (bus_count * 44)
    for i in range(dsp_count):
        pos = dsp_start + i * 32
        bus_hash, reserved, effect_id, param_id, flags = struct.unpack(">5I", data[pos:pos+20])
        val1, val2 = struct.unpack(">2f", data[pos+20:pos+28])
        curve = struct.unpack(">I", data[pos+28:pos+32])[0]

        dsp_records.append({
            "index": i,
            "bus_hash": f"0x{bus_hash:08X}",
            "effect_id": f"0x{effect_id:08X}",
            "parameter_id": f"0x{param_id:08X}",
            "value": round(val1, 3),
            "target_value": round(val2, 3),
            "flags": f"0x{flags:08X}",
            "curve": f"0x{curve:08X}",
        })

    return {
        "format": "MIB",
        "file_size": len(data),
        "sha256": sha256(data),
        "bus_count": bus_count,
        "dsp_override_count": dsp_count,
        "payload_size": payload_size,
        "buses": buses,
        "dsp_overrides": dsp_records,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect Audio Mix Snapshot (.mib) files")
    parser.add_argument("file", type=Path, help="Path to .mib file")
    args = parser.parse_args()

    data = args.file.read_bytes()
    result = parse_mib(data)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

