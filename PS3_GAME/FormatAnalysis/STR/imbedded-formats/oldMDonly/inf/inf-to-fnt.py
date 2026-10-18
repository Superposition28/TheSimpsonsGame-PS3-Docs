import os
import struct
import glob


def convert_inf_to_fnt(filepath):
    base_name = os.path.splitext(os.path.basename(filepath))[0]
    png_name = f"{base_name}.png"
    fnt_name = f"{base_name}.fnt"

    with open(filepath, "rb") as f:
        data = f.read()

    file_len = len(data)
    if file_len < 0x0434 or data[0:4] != b"FONT":
        print(f"[SKIP] {base_name}: Invalid magic signature or file size.")
        return

    (
        _file_size,
        _version,
        glyph_count,
        glyph_table_offset,
        _flags,
        _max_glyph_width,
        line_height,
        baseline,
        _lookup_table_offset,
        _alignment,
    ) = struct.unpack(">IHHIIIIIII", data[0x04:0x28])

    kerning_count, _, kerning_table_offset, _ = struct.unpack(">HHII", data[0x428:0x434])

    # 1. Parse 24-byte Glyphs at glyph_table_offset (0x0434)
    offset = glyph_table_offset
    glyphs = []

    for _ in range(glyph_count):
        char_id = data[offset]
        w, h, xadv, xoff, yoff, x0_fix, y0_fix, _x1_fix, _y1_fix, _kc, _ki = struct.unpack(
            ">HHHhhHHHHHH", data[offset + 2 : offset + 24]
        )
        glyphs.append(
            {
                "id": char_id,
                "x": x0_fix >> 4,
                "y": y0_fix >> 4,
                "width": w,
                "height": h,
                "xoffset": xoff,
                "yoffset": yoff,
                "xadvance": xadv,
            }
        )
        offset += 24

    # 2. Parse 4-byte Kerning Pairs at kerning_table_offset + 6
    kernings = []
    if kerning_count > 0 and kerning_table_offset > 0:
        k_offset = kerning_table_offset + 6
        while k_offset + 4 <= file_len and len(kernings) < kerning_count:
            c1, c2, pad, amount = struct.unpack(">BBBb", data[k_offset : k_offset + 4])
            if pad == 0 and c1 != 0 and c2 != 0:
                kernings.append({"first": c1, "second": c2, "amount": amount})
            k_offset += 4

    # 3. Write AngelCode .fnt File
    lh = line_height if line_height > 0 else 60
    base = baseline if baseline > 0 else lh
    with open(fnt_name, "w", encoding="utf-8") as fnt:
        fnt.write(
            f'info face="{base_name}" size={lh} bold=0 italic=0 charset="" unicode=1 '
            f"stretchH=100 smooth=1 aa=1 padding=0,0,0,0 spacing=1,1 outline=0\n"
        )
        fnt.write(
            f"common lineHeight={lh} base={base} scaleW=512 scaleH=512 pages=1 packed=0 "
            f"alphaChnl=0 redChnl=0 greenChnl=0 blueChnl=0\n"
        )
        fnt.write(f'page id=0 file="{png_name}"\n')

        fnt.write(f"chars count={len(glyphs)}\n")
        for g in sorted(glyphs, key=lambda item: item["id"]):
            fnt.write(
                f'char id={g["id"]} x={g["x"]} y={g["y"]} width={g["width"]} height={g["height"]} '
                f'xoffset={g["xoffset"]} yoffset={g["yoffset"]} xadvance={g["xadvance"]} page=0 chnl=15\n'
            )

        if kernings:
            fnt.write(f"kernings count={len(kernings)}\n")
            for k in kernings:
                fnt.write(f'kerning first={k["first"]} second={k["second"]} amount={k["amount"]}\n')

    print(f"[SUCCESS] Exported {fnt_name} ({len(glyphs)} characters, {len(kernings)} kerning pairs)")


def main():
    print("Starting EA .inf to .fnt conversion...\n")
    inf_files = glob.glob("*.inf")

    for f in inf_files:
        convert_inf_to_fnt(f)

    print("\nBatch conversion complete. For full asset-tree mapping, use operations/inf_to_fnt.Fonts.py.")


if __name__ == "__main__":
    main()