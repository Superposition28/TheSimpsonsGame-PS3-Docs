# Simpsons Game `.mus` Audio Format

**File Extension:** `.mus`

**Origin:** The Simpsons Game (PAL PS3 Version), likely a proprietary format from EA Redwood Shores.

**Purpose:** Container archives for Interactive, Segmented, and Layered background music.

**Key Characteristics:**

*   **Proprietary EA Format Container:**
*   **Two Subtypes:** Identified by values in the header:
    *   **Type 1:** Header bytes `0x08-0x0B` = `0F 00 00 00` (15 LE), bytes `0x0C-0x0F` = `78 01 32 00`.
    *   **Type 2:** Header bytes `0x08-0x0B` = `0B 00 00 00` (11 LE), bytes `0x0C-0x0F` = `02 03 02 03`.
*   **Header and Table of Contents (TOC):** Contains a per-file ID, a file details header, and structured TOC entries starting at offset `0x28`. The total number of files/segments inside the archive is read as a single byte at offset `0x04` of the header.
*   **28-Byte Structured TOC Entries:**
    - `0x00` (uint32): HASH (Sound-specific hash identifier)
    - `0x04` (uint16): NUMBER (Segment stream sequence number)
    - `0x06` (uint16): PADDING (Usually always 0)
    - `0x08` (uint32): `SNR_OFFSET_RAW` (Multiply by `0x10` to get real file offset)
    - `0x0C` (uint32): `SNS_OFFSET_RAW` (Multiply by `0x80` to get real file offset)
    - `0x10` (uint32): `SNR_SIZE` (Byte size of segment SNR metadata)
    - `0x14` (uint32): `SNS_SIZE` (Byte size of segment SNS stream audio payload)
    - `0x18` (uint32): PADDING (Usually always 0)
*   **Extraction & Decodability:** Unpacked successfully via `operations/mus.bms` into paired `.snr` and `.sns` segments, which natively decode into `.wav` streams using `vgmstream`.
*   **Segmented Streaming Structure:** The audio clips are split into contiguous short streams (often approx. 2-second segments) intended to be played consecutively to seamlessly assemble the full song.

## Reconstructing Continuous Audio
Because each track is built of numerous ~2-second snippets, playing back a continuous music track requires sequential concatenation. A typical pipeline workflow is:
1. Extract the `.mus` archive with `operations/mus.bms` using QuickBMS to obtain the `.snr` and `.sns` segment pairs.
2. Decode each `.snr` individually to `.wav` files using `vgmstream-cli`.
3. Concatenate/sequence the final `.wav` segments (e.g., `[Name]__000.wav`, `[Name]__001.wav`, ...) within the game engine or build pipeline logic.


