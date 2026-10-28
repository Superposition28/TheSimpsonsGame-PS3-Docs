# Documentation review — 2026-10-28

The original PS3 EU ALB/LH2/SMB audit is now reflected in the homepage coverage
registry, map dots/tooltips, format summaries, related-format tables and optional
Remake Engine integration. ALB and LH2 are green for validated data reading and
usable individual-dialogue lookup/output. SMB is yellow: record boundaries and
filename lookup are validated, while many playback fields remain unresolved.
Green does not assert complete original runtime behavior. Xbox statuses retain
independent platform evidence.

The live documentation uses current converter paths and operation numbers
(LH2 CSV 8, fonts 9, FMV subtitles 10, SBK 11, SNU 12, MUS 13, video 14).
Pipeline metadata is synchronized with all 21 active manifest operations,
including asset copying, scene-path refresh and isolated variants. Legacy Lua
CSV host fidelity remains separate from the validated standalone Python reader.
Missing evidence-ledger links were replaced with available inline investigations
and reproduction instructions; the removed JSON ledgers were not restored.

Desktop and narrow-width browser review could not be completed in this session:
the native Computer Use pipe was unavailable, no browser surfaces were returned,
and the in-app browser was unavailable. Static HTML structure, links, generated
coverage and manifest consistency were verified.

Earlier dated reviews below describe their snapshots; their old operation IDs,
validation totals and outstanding work are historical, not current support
claims. The current reference and integration checks are the maintenance source.

---

# Documentation migration — 2026-10-19

The site now presents the game and its file formats as an independent reference. The container-origin format tree and USRDIR asset/use tree remain in place. Remake Engine operation metadata and detailed implementation support have dedicated integration pages. The PS3 and Xbox 360 homepages retain Pipeline Format Coverage as the explicit exception, combining research and project progress. Former pipeline URLs and existing navigation destinations are retained.

## Homepage coverage restoration

The older vertical progress list and coloured Documentation Map are again the first two panels on each platform homepage, side by side on wide screens and stacked on narrow screens. The five colours distinguish usable/readable output, partial implementation, analysis only, research TODO and unverified platform support. Counts refer to grouped tracked references, not a percentage of all game data understood. Xbox research and support are assessed independently of PS3 conversion support.

`reference/coverage.json` owns the per-platform progress entries. `tools/render_home.py` refreshes committed static panels, counts and map dots together, and the core checker detects stale output. Source/naming guidance remains below the main panels. The local `old.index.htm` comparison file is preserved unchanged; its obsolete converter paths and unsupported completeness claims were not restored.

The broken map layout came from removing status dots while retaining a ten-pixel grid column. Dots are restored and text-only map links now have a defensive layout rule. Browser discovery again returned no available surface, and opening the in-app browser reported it unavailable; visual verification remains outstanding.

## Reference foundation

- PS3 EU full release BLES00142, APP_VER/VERSION 01.00 is the baseline. The reference records the inspected PARAM.SFO SHA-256, not an unverified whole-disc identity.
- `PS3-EU-Full-audio_reorg-isRenamed` is the canonical extracted namespace. FullFlattened is an alternate and historical view. Both are processed derivatives.
- Source and naming registries live inside the documentation repository and render to committed static HTML using a dependency-free Python helper. Reading and hosting require no build.
- Eight representative Full/FullFlattened file pairs were checked byte-for-byte using SHA-256. Six additional level-pilot pairs were also checked. These checks do not establish equivalence of all 55,998 normalizer-map entries.
- Naming mappings were compared with the current SQLite rename table. Historical naming notes are retained as an attributed snapshot; inferred meanings remain research observations.
- Movie inventory filenames were reconciled to Full through the map. A level page contains qualified canonical path examples. Existing mixed inventories elsewhere are explicitly labeled pending reconciliation.
- AudioMap.yaml remains byte-for-byte unchanged at its existing path and schema. Its research role and consumer contract are documented separately.

## Validation and remaining work

The core checker runs without a parent checkout; `--module-checks` explicitly enables operation-manifest and implementation-path comparisons. The deployment workflow now runs standalone validation before publishing. Generated reference freshness and source/path metadata are part of core validation.

This migration establishes the reference foundation and changes the site focus. It does not complete resource inventories, reconstruct missing original archive/member provenance, identify every release build, or independently validate every retained parser interpretation. Detailed byte layouts and preformatted sample research are preserved. Historical mixed paths need page-by-page reconciliation against the canonical dataset; whole-build identity and unsupported semantic claims remain unresolved. The final depth of the USRDIR documentation tree remains open, with major groups retained and deeper pages added when substantive analysis warrants them.

Browser review was attempted, but the native computer-use helper was unavailable and browser discovery returned no available surfaces. Desktop and narrow-width visual verification remains outstanding.

---

# Documentation review — 2026-10-18 (historical)

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
