# The Simpsons Game Documentation — Agent Instructions

These instructions apply throughout this documentation repository, including when it is checked out at `reversing/docs` as a Git submodule of the PS3 game module. Check for more specific `AGENTS.md` files in the area being changed.

## Read before making changes

Before making any change here, read:

1. [docs.html](docs.html), the documentation structure, evidence and maintenance guide.
2. [readme.md](readme.md), the repository scope and maintenance entry point.
3. [reference/sources.html](reference/sources.html), the canonical datasets, path roots and provenance conventions.
4. The files being changed and their relevant surrounding references, as described below.

Read additional context according to the change:

- **File paths, names or inventories:** read [reference/naming.html](reference/naming.html), the applicable source/naming JSON registry, and the relevant directory overview. Consult available extraction maps before translating paths between datasets. Historical [naming notes](reference/naming-notes.md) contain uncertain associations and are not a replacement for verified mappings.
- **Format specifications:** read the affected specification, its container/index page, related format pages and [the relationship guide](PS3_GAME/FormatAnalysis/relationships.html). Follow the linked evidence and implementation references needed to substantiate the change.
- **Asset/use analysis:** read the relevant USRDIR page, its parent overview, the associated format specifications and any registry the page describes.
- **Remake Engine behavior or shared data:** read [the integration overview](integrations/remake-engine/index.html), the relevant pipeline/support page and the actual consumer implementation when available. Review [the AudioMap contract](integrations/remake-engine/index.html#audio-map) before changing its registry or consumer.
- **Navigation, layout or maintenance tools:** read [index.html](index.html), the relevant parts of [style/main.css](style/main.css), and the scripts/workflow affected by the change. Read [review.md](review.md) when addressing migration gaps or historical findings.
- **Generated references:** read the owning JSON registry and [tools/render_reference.py](tools/render_reference.py) before editing. Homepage coverage instead uses [reference/coverage.json](reference/coverage.json) and [tools/render_home.py](tools/render_home.py). Change the owning registry or renderer and regenerate its HTML; do not hand-edit generated output.

If required evidence is unavailable, retain the uncertainty and state the limitation. Do not invent resource provenance or silently promote an inference to an observed fact.

## Scope and source conventions

- Keep the game, its formats and resource relationships as the primary subject. Project-specific operation IDs, output conventions and editor behavior belong under `integrations/remake-engine/`.
- The PS3 and Xbox 360 homepages are the explicit exception: retain Pipeline Format Coverage and the coloured Documentation Map as the first main panels. These combine research progress with Remake Engine support. Keep platform statuses separate and preserve the five-colour legend; usable output does not mean complete understanding. Maintain counts, list entries and map colours through the shared coverage registry.
- Use the inspected PS3 EU full release as the baseline. New extracted references use `PS3-EU-Full-audio_reorg-isRenamed`. `PS3-EU-FullFlattened-audio_reorg-isRenamed` is a separately labeled alternate view. Both are processed derivatives.
- Follow the source identifiers and path namespaces in `reference/sources.json`. Label supplementary platforms/releases and preserve the provenance of historical measurements. Do not silently reinterpret legacy mixed paths as canonical paths.
- Separate observed bytes, inferred semantics, inspected tool behavior and original runtime behavior. Conversion support does not establish format completeness.

## Preserve the two documentation trees

- `PS3_GAME/FormatAnalysis/` follows format origin: root-level extensions, then extracted child formats beneath their container. STR-extracted formats remain beneath `STR/imbedded-formats/`.
- Matching extensions use clearly labeled platform/release sections. Xbox-only extensions get their own page in an `xbox` subfolder at the corresponding location.
- `PS3_GAME/USRDIR/` documents resources, inventories and asset/use analysis. Keep its major groups. Add deeper pages when substantive analysis warrants them; use exact relative-path inventories where the documentation tree is shallower than the game tree.
- Cross-link the two trees. Preserve existing routes, anchors, research samples and attribution when reorganizing content.

## Shared data and repository boundaries

`PS3_GAME/USRDIR/A1_Audio/AudioMap.yaml` is research data and an input consumed directly by the parent game module. Preserve its existing path and schema unless the requested work includes a coordinated consumer migration. Keep game associations distinguishable from rename instructions.

This is a separate Git repository. Check its working tree before editing and preserve existing changes. The parent module records a submodule commit separately; editing documentation does not automatically update that reference. Core documentation must remain readable and checkable without the parent checkout or proprietary game files.

## Validation and maintenance

Keep committed static HTML and shared CSS usable without a site build or third-party packages. Run relevant checks from this repository root with Python 3.11+:

```text
python -B tools/check_docs.py
python -B tools/render_reference.py --check
python -B tools/render_home.py --check
```

After changing a source/naming registry or its renderer, run `python -B tools/render_reference.py` before checking. For changed HTML, use `python -B tools/format_docs.py <changed-file-or-directory>` and preserve preformatted research content.

After changing homepage coverage data or its renderer, run `python -B tools/render_home.py`. Preserve both platform panels and the status dots that occupy the first column of each map link.

Run `python -B tools/check_docs.py --module-checks` when changing Remake Engine integration claims in a parent module checkout. These optional checks compare the integration against the module manifest and script paths.

Review affected pages at desktop and narrow widths after presentation changes. Report any verification that could not be completed. Instruction-only Markdown changes need link and diff review; they do not require running game operations or engine builds.
