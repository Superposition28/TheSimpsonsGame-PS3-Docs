import os
import struct
import glob

# Standard offset for EA font glyph tables
GLYPH_START_OFFSET = 120 

def convert_inf_to_fnt(filepath):
    base_name = os.path.splitext(os.path.basename(filepath))[0]
    png_name = f"{base_name}.png"
    fnt_name = f"{base_name}.fnt"
    
    with open(filepath, 'rb') as f:
        data = f.read()

    file_len = len(data)
    if file_len < 16 or data[0:4] != b'FONT':
        print(f"[SKIP] {base_name}: Invalid magic signature.")
        return

    # Extract Glyph Count
    glyph_count = struct.unpack('>H', data[10:12])[0]
    
    # 1. Parse Glyphs
    offset = GLYPH_START_OFFSET
    glyphs = []
    
    for _ in range(glyph_count):
        # Unpack 20 bytes
        # H(X), H(Y), I(Pad), B(Char), B(Pad), H(W), H(H), H(Xadv), h(Xoff), h(Yoff)
        g_data = struct.unpack('>HHIBBHHHhh', data[offset:offset+20])
        
        # If it's a standard font, the Char code is at index 3. 
        # (For UI button icons, this ID might map to a high Unicode value in Godot)
        char_id = g_data[3] 
        
        glyph_dict = {
            'id': char_id,
            'x': g_data[0],
            'y': g_data[1],
            'width': g_data[5],
            'height': g_data[6],
            'xoffset': g_data[8],
            'yoffset': g_data[9],
            'xadvance': g_data[7]
        }
        glyphs.append(glyph_dict)
        offset += 20

    # 2. Parse Kerning
    remaining_bytes = file_len - offset
    kerning_count = remaining_bytes // 4
    kernings = []
    
    for _ in range(kerning_count):
        # Char1(B), Char2(B), Pad(B), Amount(b - signed)
        k_data = struct.unpack('>BBBb', data[offset:offset+4])
        
        # Only log valid kerning pairs (ignoring trailing 00 00 00 00 padding)
        if k_data[0] != 0 and k_data[1] != 0:
            kernings.append({
                'first': k_data[0],
                'second': k_data[1],
                'amount': k_data[3]
            })
        offset += 4

    # 3. Write AngelCode .fnt File
    with open(fnt_name, 'w', encoding='utf-8') as fnt:
        # BMFont Header
        fnt.write(f'info face="{base_name}" size=60 bold=0 italic=0 charset="" unicode=1 stretchH=100 smooth=1 aa=1 padding=0,0,0,0 spacing=1,1 outline=0\n')
        fnt.write(f'common lineHeight=60 base=48 scaleW=2048 scaleH=2048 pages=1 packed=0 alphaChnl=0 redChnl=0 greenChnl=0 blueChnl=0\n')
        fnt.write(f'page id=0 file="{png_name}"\n')
        
        # Glyphs
        fnt.write(f'chars count={len(glyphs)}\n')
        for g in glyphs:
            fnt.write(f'char id={g["id"]} x={g["x"]} y={g["y"]} width={g["width"]} height={g["height"]} xoffset={g["xoffset"]} yoffset={g["yoffset"]} xadvance={g["xadvance"]} page=0 chnl=15\n')
            
        # Kernings
        if kernings:
            fnt.write(f'kernings count={len(kernings)}\n')
            for k in kernings:
                fnt.write(f'kerning first={k["first"]} second={k["second"]} amount={k["amount"]}\n')

    print(f"[SUCCESS] Exported {fnt_name} ({len(glyphs)} characters, {len(kernings)} kerning pairs)")

def main():
    print("Starting EA .inf to .fnt conversion...\n")
    inf_files = glob.glob("*.inf")
    
    for f in inf_files:
        convert_inf_to_fnt(f)
        
    print("\nBatch conversion complete. You can now import the .fnt and .png files into Godot 4.")

if __name__ == '__main__':
    main()