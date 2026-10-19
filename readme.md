# The Simpsons Game — file formats and game-data reference

An independent technical reference for *The Simpsons Game* (2007): binary formats, original file organization, extracted resources, asset relationships, and observed use. The inspected PS3 EU full release is the baseline. Other PS3 releases, the demo and Xbox 360 research are explicitly scoped additions.

The PS3 and Xbox 360 homepages retain Pipeline Format Coverage and coloured documentation maps. This is the explicit exception to project independence: the progress overview combines research knowledge with Remake Engine support, while keeping platform-specific limitations visible.

## Start here

- [Canonical sources and path conventions](reference/sources.html): release identity, extracted roots, verified path pairs and evidence limits.
- [Naming reference](reference/naming.html): original folders, extracted groups, display names and resource codes.
- [Format analysis](PS3_GAME/FormatAnalysis/index.html): root formats and their extracted child formats.
- [Game files and asset use](PS3_GAME/USRDIR/index.html): inventories, levels, characters, media and resource associations.
- [Format relationships](PS3_GAME/FormatAnalysis/relationships.html): joins and shared data conventions.
- [Documentation guide](docs.html): scope, structure, evidence and contribution conventions.
- [Remake Engine integration](integrations/remake-engine/index.html): optional project-specific operations and output conventions.

## Sources and structure

Original paths are rooted at the directory containing `PS3_GAME`. New extracted references use `PS3-EU-Full-audio_reorg-isRenamed`. `PS3-EU-FullFlattened-audio_reorg-isRenamed` remains an alternate view and the provenance of retained historical research. Both are processed datasets, not untouched disc trees. Legacy mixed inventories are labeled until reconciled; never silently reinterpret their paths.

The format tree follows container origin: root-level extensions, then STR-extracted formats beneath STR. Matching platform variants share labeled sections; Xbox-only extensions live in an `xbox` subfolder at the corresponding location. The USRDIR tree follows major game-resource groups for asset/use analysis. Deeper folders are added when substantive analysis warrants them; exact resource paths belong in inventories even when the documentation tree is shallower.

## Reading and maintaining

Open `index.html` directly or serve this directory with `python -m http.server`. Published pages are committed static HTML using shared CSS. No JavaScript framework, package installation or site build is required.

Python 3.11+ maintenance commands, with no third-party dependencies:

```text
python -B tools/check_docs.py
python -B tools/render_reference.py --check
python -B tools/render_home.py --check
python -B tools/check_docs.py --module-checks
```

The first command validates the standalone documentation. The last explicitly opts into checks against a parent module checkout. After editing source/naming JSON registries, run `python -B tools/render_reference.py`. Homepage coverage uses `reference/coverage.json`; run `python -B tools/render_home.py` to refresh its counts, lists and map colours. Commit the rendered HTML. These are authoring helpers, not a reader or hosting requirement.

`AudioMap.yaml` remains at its established path and now uses V2, with a JSON Schema alongside it. Remake Engine's consumer was migrated together with the registry. Game associations and consumer output conventions are documented separately. Preserve research attribution and distinguish observed bytes, inferred meanings, source-inspected tool behavior and original runtime behavior.

The documentation is maintained in [TheSimpsonsGame-PS3-Docs](https://github.com/Superposition28/TheSimpsonsGame-PS3-Docs) and can also be checked out as a module submodule. [Remake Engine's game module](https://github.com/Superposition28/TheSimpsonsGame-PS3) and the [file viewer](https://github.com/Superposition28/TheSimpsonsGame-PS3-FileViewer) are related implementations.

Existing attribution and historical research are retained. This scope change does not introduce a new license grant.
