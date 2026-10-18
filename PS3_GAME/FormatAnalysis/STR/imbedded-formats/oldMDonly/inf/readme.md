# EA `FONT` v6 (`.inf`) Font Maps & Texture Atlases (`.png`)

## Overview
All 12 `.inf` binary font descriptor files in `GameFiles/PS3-EU-FullFlattened-audio_reorg-isRenamed` live in two font directories (`A2_Characters/simpsonsCharsGlobalStr/assetsShared/fonts/` and `A2_Frontend/frontendStr/assets/shared/fonts/`) and map 1-to-1 to extracted `.png` texture atlases inside their respective archive's `assetsRws/txd/*_txd/` directories.

See the full HTML documentation at [../../inf.html](../../inf.html) and the production converter script at [`operations/inf_to_fnt.Fonts.py`](../../../../../../../operations/inf_to_fnt.Fonts.py).

## Complete `.inf` <-> `.png` Asset Mapping

### 1. `A2_Characters/simpsonsCharsGlobalStr/assetsShared/fonts/`
- `A2_Characters/simpsonsCharsGlobalStr/assetsShared/fonts/buttons_37bb42.inf` (2,896 B, 33 glyphs)
  -> `A2_Characters/simpsonsCharsGlobalStr/assetsRws/txd/simpsons_chars_global_split8_ce6120_txd/buttons.png` (`256x256`)
- `A2_Characters/simpsonsCharsGlobalStr/assetsShared/fonts/DomCasualStd3636_ff9566.inf` (7,531 B, 191 glyphs)
  -> `A2_Characters/simpsonsCharsGlobalStr/assetsRws/txd/simpsons_chars_global_split9_bade57_txd/DomCasualStd3636.png` (`512x256`)
- `A2_Characters/simpsonsCharsGlobalStr/assetsShared/fonts/HighlanderStdBold6060b_1d35c8.inf` (7,921 B, 191 glyphs)
  -> `A2_Characters/simpsonsCharsGlobalStr/assetsRws/txd/simpsons_chars_global_split6_c2ec11_txd/HighlanderStdBold6060b.png` (`1024x512`)
- `A2_Characters/simpsonsCharsGlobalStr/assetsShared/fonts/HighlanderStdMed3636_ca0d81.inf` (7,819 B, 191 glyphs)
  -> `A2_Characters/simpsonsCharsGlobalStr/assetsRws/txd/simpsons_chars_global_split7_6b8b06_txd/HighlanderStdMed3636.png` (`512x512`)
- `A2_Characters/simpsonsCharsGlobalStr/assetsShared/fonts/HighlanderStdNumsBold3636b_85009b.inf` (5,200 B, 95 glyphs)
  -> `A2_Characters/simpsonsCharsGlobalStr/assetsRws/txd/simpsons_chars_global_split8_ce6120_txd/HighlanderStdNumsBold3636b.png` (`128x128`)
- `A2_Characters/simpsonsCharsGlobalStr/assetsShared/fonts/LetterGothicStdBold2424b_c7c53d.inf` (6,688 B, 191 glyphs)
  -> `A2_Characters/simpsonsCharsGlobalStr/assetsRws/txd/simpsons_chars_global_split9_bade57_txd/LetterGothicStdBold2424b.png` (`512x256`)

### 2. `A2_Frontend/frontendStr/assets/shared/fonts/`
- `A2_Frontend/frontendStr/assets/shared/fonts/buttons_fd7e46.inf` (2,896 B, 33 glyphs)
  -> `A2_Frontend/frontendStr/assetsRws/txd/frontend_split16_704679_txd/buttons.png` (`256x256`)
- `A2_Frontend/frontendStr/assets/shared/fonts/DomCasualStd3636_09608f.inf` (7,531 B, 191 glyphs)
  -> `A2_Frontend/frontendStr/assetsRws/txd/frontend_split23_b54bef_txd/DomCasualStd3636.png` (`512x256`)
- `A2_Frontend/frontendStr/assets/shared/fonts/HighlanderStdBold6060b_929fdc.inf` (7,921 B, 191 glyphs)
  -> `A2_Frontend/frontendStr/assetsRws/txd/frontend_split16_704679_txd/HighlanderStdBold6060b.png` (`1024x512`)
- `A2_Frontend/frontendStr/assets/shared/fonts/HighlanderStdMed3636_c14f63.inf` (7,819 B, 191 glyphs)
  -> `A2_Frontend/frontendStr/assetsRws/txd/frontend_split19_127e84_txd/HighlanderStdMed3636.png` (`512x512`)
- `A2_Frontend/frontendStr/assets/shared/fonts/LetterGothicStdBold2424b_4aa417.inf` (6,688 B, 191 glyphs)
  -> `A2_Frontend/frontendStr/assetsRws/txd/frontend_split24_a22477_txd/LetterGothicStdBold2424b.png` (`512x256`)
- `A2_Frontend/frontendStr/assets/shared/fonts/simpsons_font_acdf54.inf` (4,615 B, 95 glyphs)
  -> `A2_Frontend/frontendStr/assetsRws/txd/frontend_split28_426807_txd/simpsons_font.png` (`256x128`)
