# Documentation review — 2026-10-18

The HTML documentation was compared with the module's `operations.toml`, the Lua/BMS entry points under `operations/`, the Blender importer, and the engine TXD export entry point. The review covers documentation and structural sample checks; it did not rerun the extraction/conversion pipeline or validate original game runtime behavior.

## Findings and changes

| Finding | Change |
| --- | --- |
| Format pages ranged from empty stubs to detailed specifications and multi-megabyte dumps. | All 47 format pages now state purpose, identification, byte order/text, related formats, operation support and evidence limits. Detailed existing research is retained; long hex appendices are collapsible. |
| Per-page styles, incorrect stylesheet paths and inconsistent table presentation produced different layouts. | Shared CSS, viewport metadata, bounded table scrolling, contents links, breadcrumbs and consistent headings now apply across the live pages. |
| The original local-target audit found 32 broken targets. | Corrected stylesheet paths and model routes; replaced private Source-folder links with descriptive paths. Added titles to iframe routes and removed the unused duplicate PS3 template. |
| INF and TOX pages referred to absent Python entry points. | Corrected them to registered Lua operations 15 and 16. Embedded Python snippets are identified as illustrative rather than runnable module converters. |
| VP6 was described as converting to OGV with vgmstream and its header byte order was assumed. | Documented FFmpeg operation 13 and separately described TOX/LH2 subtitle generation. The current EU SCHl size field is documented as little-endian based on all 172 local headers. |
| SS localization was called Latin American Spanish; all five variant pages repeated the same mixed inventory. | Documented the observed global SS label table and rebuilt five suffix-specific inventories, with 20 files each and actual sizes/header counts. |
| INF corpus totals claimed 1,813 glyphs and nine files with kerning. | Corrected to 1,784 glyphs and eight kerning-enabled files in the current 12-file EU set. Distinguished observed truncated kerning lengths from a hypothesized exporter cause. |
| AUB's page described ALB/CTB/SNU rather than AUB bytes. | Replaced it with an honest inventory/research scope. Moved audio relationships into the shared guide and relevant format pages. |
| Shared directories and similar terms were sometimes presented as verified dependencies. | Added 64 reciprocal format relationships with evidence labels. Numeric ID joins, embedded names, filename pairing and contextual associations are distinguished explicitly. |
| Operation support and research completeness were mixed together. | Added a reference for all 18 active operations, including organization steps and reset. Recorded declared dependencies and practical inputs separately. |

The new relationship guide covers INF/TXD/LH2/TOX/VP6, ALB/CTB/SNU/SMB/SBK/mix metadata, MSB/MUS/SNR/SNS, model textures, character bindings/animation, Havok resources, scenes, navigation, effects and UI resources. It explains common IDs, pointer bases, units, text/glyph encodings, compound suffixes and platform differences without duplicating full binary specifications.

## Sample verification

Read-only checks used `GameFiles/PS3-EU-FullFlattened-audio_reorg-isRenamed`. These results apply to that local dataset, not all releases or platforms.

| Family | Check and result |
| --- | --- |
| INF | All 12 files have FONT magic, declared sizes matching actual lengths, version 6 and bounded 24-byte glyph tables. All 1,784 glyph rectangles match stored width/height after fixed-point conversion. All eight kerning-enabled files satisfy the documented observed `EOF - KerningOffset = DeclaredCount * 3` allocation formula. This does not prove the original exporter implementation. |
| LH2 | All 654 files have 2HCL magic, matching declared sizes, bounded ID/pointer arrays, and in-range NUL-terminated strings. Each language/SS suffix occurs 20 times. Global SS samples contain labels such as `CREDITS_IntEngineers_1`; four language variants contain readable text. |
| TOX | All 77 files satisfy `FileSize = 16 + RecordCount * 16`, totaling 825 records and 398 distinct IDs. Global English text lacks ID `E6A49A45`, the already documented Bart fallback. Every present TOX label tested matches lowercase SDBM. The fallback is converter policy, not recovered source text. |
| VP6 | All 172 local movie headers begin with SCHl. The next four bytes are little-endian sizes: 40 in 73 files and 44 in 99 files. Other chunk fields and cross-platform parity were not inferred from that result. |

`tools/check_docs.py` validates all 76 live HTML pages, local targets/anchors, format coverage, reciprocal links and manifest metadata. Historical `.history` snapshots and retained `oldMDonly` notes are outside the live HTML consistency pass.

## Remaining gaps

- No dedicated registered decoder exists for many audio-control, animation, physics, scene, navigation, effect and interface formats. Their documented roles and unknown fields remain at different levels of confidence.
- Operation 9's binary reader uses `string.byte`, while newer font/subtitle readers use `string.unicode` and document host high-byte behavior. CSV ID/encoding fidelity requires a separate engine-runtime check; successful structural LH2 validation does not test that converter.
- The SBK operation does not request exhaustive subsong enumeration. A WAV per bank does not prove that every embedded sound was exported.
- Model materials remain partial; music conversion does not evaluate MSB transitions; the launch-manifest operation writes a static file rather than discovering converted assets.
- Existing historical cross-platform measurements were preserved as research observations, not freshly verified for every platform or region. Level/hub pages now explain navigation and scope, but still lack individual resource inventories.
- No browser surface was available to the computer-use tools during this session. Visual rendering at desktop and narrow widths remains unverified; static markup, stylesheet references and navigation checks were completed.
