import os
import struct
import glob

# =============================================================================
# CONFIGURATION
# =============================================================================
# Based on the hex dump, the header is padded before the first glyph begins.
# Offset 120 (0x78) is the standard baseline for this specific EA font format.
GLYPH_START_OFFSET = 120

def scan_inf_file(filepath):
    print(f"\n{'-'*50}")
    print(f"Scanning: {os.path.basename(filepath)}")
    print(f"{'-'*50}")

    with open(filepath, 'rb') as f:
        data = f.read()

    file_len = len(data)
    if file_len < 16:
        print("  [FAIL] File too small to be a valid .inf font map.")
        return False

    # 1. Parse Header
    magic = data[0:4]
    if magic != b'FONT':
        print(f"  [FAIL] Invalid magic signature: {magic}. Expected b'FONT'.")
        return False

    # Unpack Bytes 4-15: Size(u32), Version(u16), GlyphCount(u16), Unknown(u32)
    expected_size = struct.unpack('>I', data[4:8])[0]
    version = struct.unpack('>H', data[8:10])[0]
    glyph_count = struct.unpack('>H', data[10:12])[0]
    header_unk = struct.unpack('>I', data[12:16])[0]

    print(f"  [INFO] Header parsed successfully:")
    print(f"         - Magic: {magic.decode('ascii')}")
    print(f"         - Declared Size: {expected_size} bytes (Actual: {file_len} bytes)")
    print(f"         - Version: {version}")
    print(f"         - Glyph Count: {glyph_count}")
    print(f"         - Header Bytes 12-15: {header_unk} (Hex: 0x{header_unk:08X})")

    # 2. Locate and Validate Glyph Table
    if GLYPH_START_OFFSET + (glyph_count * 20) > file_len:
        print(f"  [FAIL] Glyph table exceeds actual file size! Check GLYPH_START_OFFSET.")
        return False

    print(f"\n  [INFO] Validating Glyph Table (Start Offset: {GLYPH_START_OFFSET})...")
    valid_glyphs = 0
    offset = GLYPH_START_OFFSET

    try:
        for _ in range(glyph_count):
            # Unpack 20 bytes: X(u16), Y(u16), Pad(u32), Char(u8), Pad(u8), W(u16), H(u16), Xadv(u16), Xoff(s16), Yoff(s16)
            g_data = struct.unpack('>HHIBBHHHhh', data[offset:offset+20])
            char_code = g_data[3]

            if char_code > 0:
                valid_glyphs += 1

            offset += 20

        print(f"  [PASS] Successfully parsed {glyph_count} x 20-byte glyph structures.")
        print(f"         - Valid mapped characters found: {valid_glyphs}/{glyph_count}")

    except struct.error as e:
        print(f"  [FAIL] Struct unpacking error in glyph table at offset {offset}: {e}")
        return False

    # 3. Locate and Validate Kerning Table
    # The kerning table starts immediately after the last glyph struct.
    kerning_start = offset
    remaining_bytes = file_len - kerning_start

    print(f"\n  [INFO] Validating Kerning Table (Start Offset: {kerning_start})...")

    if remaining_bytes % 4 != 0:
        print(f"  [WARN] Remaining bytes ({remaining_bytes}) is not perfectly divisible by 4.")
        print(f"         This may indicate trailing footer padding or an offset shift.")

    # Calculate how many 4-byte kerning pairs fit in the remaining file space
    kerning_count = remaining_bytes // 4
    print(f"  [INFO] Estimated Kerning Pairs: {kerning_count}")

    valid_kerning = 0
    try:
        for _ in range(kerning_count):
            # Unpack 4 bytes: Char1(u8), Char2(u8), Pad(u8), Amount(s8)
            # 'b' is used for the signed 8-bit integer at the end (kerning amount)
            k_data = struct.unpack('>BBBb', data[offset:offset+4])
            offset += 4
            valid_kerning += 1

        print(f"  [PASS] Successfully parsed {valid_kerning} x 4-byte kerning structures.")

    except struct.error as e:
        print(f"  [FAIL] Struct unpacking error in kerning table at offset {offset}: {e}")
        return False

    print("\n  [PASS] File structure is fully contiguous and successfully mapped!")
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

    print(f"\n{'='*50}")
    print(f"Batch Scan Complete! Successfully Parsed: {success_count}/{len(inf_files)}")
    print(f"{'='*50}")

if __name__ == '__main__':
    main()