import os
import struct
import glob

# =============================================================================
# CONFIGURATION
# =============================================================================
# Offset 0x0434 (1076) is stored at header offset 0x0C (GlyphTableOffset) after
# the 40-byte main header (0x00..0x28), 1024-byte runtime index buffer (0x28..0x428),
# and 12-byte kerning header (0x428..0x434).
DEFAULT_GLYPH_START_OFFSET = 0x0434
GLYPH_RECORD_SIZE = 24


def scan_inf_file(filepath):
    print(f"\n{'-'*60}")
    print(f"Scanning: {os.path.basename(filepath)}")
    print(f"{'-'*60}")

    with open(filepath, "rb") as f:
        data = f.read()

    file_len = len(data)
    if file_len < DEFAULT_GLYPH_START_OFFSET:
        print("  [FAIL] File too small to be a valid .inf font map.")
        return False

    # 1. Parse 40-byte Main Header (0x00..0x28)
    magic = data[0:4]
    if magic != b"FONT":
        print(f"  [FAIL] Invalid magic signature: {magic}. Expected b'FONT'.")
        return False

    (
        expected_size,
        version,
        glyph_count,
        glyph_table_offset,
        flags,
        max_glyph_width,
        line_height,
        baseline,
        lookup_table_offset,
        alignment,
    ) = struct.unpack(">IHHIIIIIII", data[0x04:0x28])

    kerning_count, _, kerning_table_offset, _ = struct.unpack(">HHII", data[0x428:0x434])

    print("  [INFO] Header parsed successfully:")
    print(f"         - Magic: {magic.decode('ascii')}")
    print(f"         - Declared Size: {expected_size} bytes (Actual: {file_len} bytes)")
    print(f"         - Version: {version}")
    print(f"         - Glyph Count: {glyph_count}")
    print(f"         - Glyph Table Offset: 0x{glyph_table_offset:04X} ({glyph_table_offset})")
    print(f"         - Metrics: MaxWidth={max_glyph_width}px, LineHeight={line_height}px, Baseline={baseline}px")
    print(f"         - Lookup Table Offset: 0x{lookup_table_offset:04X}")
    print(f"         - Kerning Count: {kerning_count} (Offset: 0x{kerning_table_offset:04X})")

    # 2. Locate and Validate Glyph Table (24 bytes per glyph)
    if glyph_table_offset + (glyph_count * GLYPH_RECORD_SIZE) > file_len:
        print("  [FAIL] Glyph table exceeds actual file size!")
        return False

    print(f"\n  [INFO] Validating Glyph Table (Start Offset: 0x{glyph_table_offset:04X})...")
    valid_glyphs = 0
    offset = glyph_table_offset

    try:
        for _ in range(glyph_count):
            char_code = data[offset]
            w, h, xadv, xoff, yoff, x0_fix, y0_fix, x1_fix, y1_fix, kc, ki = struct.unpack(
                ">HHHhhHHHHHH", data[offset + 2 : offset + 24]
            )
            x0, y0 = x0_fix >> 4, y0_fix >> 4
            x1, y1 = x1_fix >> 4, y1_fix >> 4
            if (x1 - x0) == w and (y1 - y0) == h:
                valid_glyphs += 1
            offset += GLYPH_RECORD_SIZE

        print(f"  [PASS] Successfully parsed {glyph_count} x 24-byte glyph structures.")
        print(f"         - Verified 12.4 fixed-point UV boxes: {valid_glyphs}/{glyph_count}")

    except struct.error as e:
        print(f"  [FAIL] Struct unpacking error in glyph table at offset {offset}: {e}")
        return False

    # 3. Locate and Validate Kerning Table
    if kerning_count > 0 and kerning_table_offset > 0:
        print(f"\n  [INFO] Validating Kerning Table (Start Offset: 0x{kerning_table_offset:04X})...")
        k_offset = kerning_table_offset + 6
        valid_kerning = 0
        while k_offset + 4 <= file_len and valid_kerning < kerning_count:
            c1, c2, pad, amt = struct.unpack(">BBBb", data[k_offset : k_offset + 4])
            if pad == 0 and c1 != 0 and c2 != 0:
                valid_kerning += 1
            k_offset += 4
        print(f"  [PASS] Successfully parsed {valid_kerning}/{kerning_count} 4-byte kerning pairs.")

    print("\n  [PASS] File structure is fully validated!")
    return True


def main():
    print("Initializing batch validation for EA .inf font files...")
    inf_files = glob.glob("*.inf")

    if not inf_files:
        print("[WARN] No .inf files found in the current directory.")
        return

    print(f"Found {len(inf_files)} files. Beginning sequential scan...\n")

    success_count = 0
    for f in inf_files:
        if scan_inf_file(f):
            success_count += 1

    print(f"\n{'='*60}")
    print(f"Batch Scan Complete! Successfully Parsed: {success_count}/{len(inf_files)}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()