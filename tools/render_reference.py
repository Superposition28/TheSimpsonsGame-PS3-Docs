"""Render the small reference registries without third-party dependencies.

Generated HTML is committed, so reading and hosting the site needs no build.
Run with --check to detect stale pages without writing files.
"""

import argparse
from html import escape
import json
from pathlib import Path

try:
    from format_docs import format_html
except ImportError:
    from .format_docs import format_html


ROOT = Path(__file__).resolve().parent.parent


def page(title: str, body: str) -> str:
    """Wrap reference content in the shared standalone document layout."""
    return format_html(f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title><link rel="stylesheet" href="../style/main.css">
</head><body class="doc-page">
<nav class="breadcrumbs" aria-label="Breadcrumb"><a href="../index.html" target="_top">Documentation</a></nav>
<h1>{escape(title)}</h1>{body}</body></html>''')


def table(headers: list[str], rows: list[list[str]]) -> str:
    """Build a scrollable table; cells are already escaped HTML."""
    return ('<div class="table-scroll" role="region" aria-label="Reference table" tabindex="0">'
            '<table><thead><tr>' + ''.join(f'<th scope="col">{escape(h)}</th>' for h in headers)
            + '</tr></thead><tbody>'
            + ''.join('<tr>' + ''.join(f'<td>{cell}</td>' for cell in row) + '</tr>' for row in rows)
            + '</tbody></table></div>')


def code(value: str) -> str:
    """Escape a literal reference value."""
    return f'<code>{escape(value)}</code>'


def generated_pages(root: Path = ROOT) -> dict[Path, str]:
    """Return deterministic reference pages from the committed registries."""
    sources = json.loads((root / 'reference/sources.json').read_text(encoding='utf-8'))
    naming = json.loads((root / 'reference/naming.json').read_text(encoding='utf-8'))
    source_rows = [[code(s['id']), escape(s['role']), code(s['root']), escape(s['scope'])]
                   for s in sources['sources']]
    sample_rows = [[escape(s['family']), code(s['extracted']), code(s['flattened']), code(s['sha256'])]
                   for s in sources['verified_pairs']]
    body = '''<p>The primary reference is the inspected PS3 EU full release. Extracted resources use the non-flattened Full view. Other releases and platforms supplement this baseline; differences must be attributed to their source.</p>
<h2 id="sources">Source identities and roots</h2>
<p>Paths use forward slashes and are relative to the named root, never a contributor's drive. Source identifiers describe the inspected local reference, not every build sold in that region.</p>'''
    body += table(['Source ID', 'Role', 'Root convention', 'Scope'], source_rows)
    body += f'''<h2 id="identity">Baseline release and snapshot</h2>
<p>Title ID: {code(sources['baseline']['title_id'])}; APP_VER: {code(sources['baseline']['app_version'])}; VERSION: {code(sources['baseline']['version'])}. These values come from the inspected PARAM.SFO and the retained <a href="../PS3_GAME/EU.PARAM.SFO.toml">metadata transcription</a>.</p>
<p>PARAM.SFO SHA-256: {code(sources['baseline']['param_sfo_sha256'])}. This fingerprints the metadata file only; no complete disc/build checksum has been established.</p>
<p>Reference snapshot inspected on {escape(sources['snapshot_date'])}. Full and FullFlattened already include base-folder renaming and audio reorganization. FullFlattened additionally collapses paths and can add six-hex filename suffixes. Neither is the original disc tree. Generated exports in either directory are not automatically original game resources.</p>
<h2 id="paths">Path conventions</h2>
<ul><li>{code('ps3-eu-original:PS3_GAME/USRDIR/...')} starts at the directory containing PS3_GAME.</li>
<li>{code('ps3-eu-extracted:A2_Frontend/...')} starts at PS3-EU-Full-audio_reorg-isRenamed.</li>
<li>{code('ps3-eu-flattened:A2_Frontend/...')} starts at PS3-EU-FullFlattened-audio_reorg-isRenamed.</li>
<li>A page or inventory must declare its source and path namespace. Historical mixed inventories are explicitly marked as awaiting path-level reconciliation; they must not be interpreted as canonical paths.</li>
<li>New examples use the canonical extracted namespace. Retained flattened measurements keep their original provenance until checked against Full. Display names and aliases are described in <a href="naming.html">the naming reference</a>.</li></ul>
<h2 id="provenance">Resource provenance and evidence</h2>
<p>Identify important samples by source release, original containing archive, archive member or extraction identifier, canonical extracted path, and optional flattened alias. Record unknown archive membership as unresolved. Do not infer original membership from a renamed folder alone.</p>
<p>The local normalizer map contains {sources['mapping']['entries']:,} rows. Its original_path field is relative to the already reorganized Full dataset, not the original disc. Its new_path field is relative to FullFlattened. The map includes copied resources and generated files; its row count is not a source-file inventory.</p>
<p>Mapping SHA-256: {code(sources['mapping']['sha256'])}. Local map location: {code(sources['mapping']['local_path'])}. The docs do not require this local checkout to render or validate their core structure.</p>
<h2 id="verified-pairs">Verified path pairs</h2>
<p>The following representative pairs existed and had identical SHA-256 values on the snapshot date. This verifies only these pairs, not every mapped resource or archive origin.</p>'''
    body += table(['Family', 'Canonical extracted path', 'Flattened alias', 'SHA-256 of both files'], sample_rows)
    body += '''<h2 id="supplementary">Supplementary observations</h2>
<p>PS3 US, PS3 demo and Xbox 360 observations must state platform, region, release identity when known, and path root. Historical Xbox NTSC inventories retain that label; they are not silently relabeled as the local Xbox EU set. Matching extensions can share a page with labeled variant sections. Xbox-only extensions remain in an xbox subfolder at the corresponding container location.</p>
<h2 id="migration">Historical research and migration</h2>
<p>Existing byte layouts, measurements and sample dumps are retained. Source notices distinguish legacy mixed paths from new canonical references. Unresolved paths, archive membership and whole-build identity remain research tasks, not assumed equivalences. Tool behavior is supporting evidence and must be distinguished from observed original-game behavior.</p>
<p>Machine-readable source: <a href="sources.json">sources.json</a>. Regenerate this page with <code>python tools/render_reference.py</code>; normal reading and hosting require no generation step.</p>'''
    names = f'''<p>This reference distinguishes original source-folder names, readable extracted groups, internal resource codes and game-facing names. The documentation keeps its two trees: container-based format analysis and USRDIR asset/use analysis.</p>
<p>Folder mappings were compared with the module's rename_mappings SQLite table on {escape(naming['snapshot_date'])}. Titles, codes and aliases were transcribed from the existing naming notes; they are research labels, not proof of a runtime lookup or a complete filename rule. Empty codes mean unrecorded, not absent.</p>'''
    names += table(['Original USRDIR folder', 'Extracted group', 'Display name', 'Recorded code', 'Aliases / scope'], [
        [code(row['original']), code(row['extracted']), escape(row['display_name']),
         code(row['code']) if row['code'] else 'Unrecorded', escape('; '.join(row['aliases']) + ' — ' + row['scope'])]
        for row in naming['folders']])
    names += '''<h2 id="audio">Audio prefixes and meanings</h2>
<p>Prefix associations come from the naming notes and AudioMap patterns. They are contextual evidence; they do not establish binary event IDs or a complete event-to-stream resolver. Original folder names and extracted destination names must remain distinguishable.</p>'''
    names += table(['Prefix', 'Recorded association'], [[code(r['prefix']), escape(r['meaning'])] for r in naming['audio_prefixes']])
    names += '''<h2 id="ownership">Ownership and consumers</h2>
<p><a href="naming.json">naming.json</a> owns this documentation snapshot. An attributed <a href="naming-notes.md">historical notes snapshot</a> preserves the original observations and uncertain associations. Original notes remain in the parent checkout at <code>reversing/data/naming.md</code>; executable rename rules remain in <code>config/RenameMap.db</code>. Changes to those sources need an explicit reconciliation, not an automatic overwrite of research conclusions.</p>
<p><a href="../PS3_GAME/USRDIR/A1_Audio/AudioMap.yaml">AudioMap.yaml</a> remains the maintained audio registry at its existing path and schema. Its game associations and rename instructions are documented separately from the <a href="../integrations/remake-engine/index.html#audio-map">Remake Engine consumer contract</a>.</p>
<p>Use <a href="sources.html">source and path conventions</a> for actual file references. Regenerate this page with <code>python tools/render_reference.py</code>.</p>'''
    return {root / 'reference/sources.html': page('Canonical sources and path conventions', body),
            root / 'reference/naming.html': page('Game folders, names and aliases', names)}


def main() -> int:
    """Render or check the committed reference pages."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    stale = []
    for path, content in generated_pages().items():
        if not path.exists() or path.read_bytes() != content.encode('utf-8'):
            stale.append(path.relative_to(ROOT).as_posix())
            if not args.check:
                path.write_text(content, encoding='utf-8', newline='\n')
    print(('Stale' if args.check else 'Rendered') + f' reference pages: {len(stale)}' + (f' ({", ".join(stale)})' if stale else ''))
    return int(args.check and bool(stale))


if __name__ == '__main__':
    raise SystemExit(main())
