# The Simpsons Game (PS3) - Reverse Engineering Documentation

This repository contains documentation for the reverse engineering efforts of *The Simpsons Game* (2007) for the PlayStation 3. This documentation is maintained as a submodule for the main [TheSimpsonsGame-PS3](https://github.com/Superposition28/TheSimpsonsGame-PS3) game module.

## Links
- **Main Project:** [TheSimpsonsGame-PS3](https://github.com/Superposition28/TheSimpsonsGame-PS3)
- **STR Viewer:** [TheSimpsonsGame-PS3-FileViewer](https://github.com/Superposition28/TheSimpsonsGame-PS3-FileViewer)
- **Documentation Repo:** [TheSimpsonsGame-PS3-Docs](https://github.com/Superposition28/TheSimpsonsGame-PS3-Docs)
- **Hosted Docs:** [Online Documentation](https://superposition28.github.io/TheSimpsonsGame-PS3-Docs/)

## Content Structure

- **[Format Analysis](PS3_GAME/FormatAnalysis/index.html)**: Format inventory and links to binary layouts, examples, operation support and evidence limits.
- **[Format Relationships](PS3_GAME/FormatAnalysis/relationships.html)**: Connections between movie timing, localization, fonts, textures, audio, music, geometry and other resource families.
- **[Operation Pipeline](PS3_GAME/FormatAnalysis/pipeline.html)**: All 18 registered operations, their declared dependencies, inputs, outputs and implementation limits.
- **[PARAM.SFO](PS3_GAME/PARAM.SFO.html)**: PS3 EU, US and demo metadata, binary layout and linked TOML snapshots.
- **[PS3_GAME](PS3_GAME/index.html)**: Documentation of the root files found on the game disc.
- **[USRDIR](PS3_GAME/USRDIR/index.html)**: Detailed documentation of the game's data directory, including level-specific archives and assets.
- **Level Docs**: Individual documentation for each game level (L01 through L16, and Hubs), folder structure based on flattened output from the [remake module](https://github.com/Superposition28/TheSimpsonsGame-PS3)
- **[Documentation Guide](docs.html)**: Shared page conventions, navigation and maintenance.
- **[Documentation Review](review.md)**: Audit findings, sample checks and remaining gaps.

## Features

- **Format Independence**: Format analyses are kept separate from game-specific instances to allow for reusable documentation.
- **Game Context**: Each instance of a format in the game files has localized documentation focusing on its specific purpose and role.
- **Responsive Layout**: The documentation uses simple CSS for a clean, readable layout without the need for complex build tools.

## Maintaining the documentation

Open `index.html` directly, or serve this directory with `python -m http.server` for a local preview. All HTML pages share `style/main.css`; format pages use common summary, relationship, operation-support and evidence sections. Existing byte layouts and sample dumps remain on the relevant format pages, with long hex appendices collapsed.

Run `python tools/check_docs.py` with Python 3.11 or later. It requires no third-party packages and checks local links/anchors, page metadata, format coverage sections and reciprocal relationship links. In a game-module checkout, it also compares the documented operation IDs, dependencies, run-all settings and referenced scripts with `operations.toml`.

Conversion support means a code path is registered. It does not establish that every variant is decoded, every sound-bank subsong is exported, or the original runtime behavior is reconstructed. Preserve this distinction when updating coverage labels. The `.ss.LH2` global tables observed in the EU dataset contain internal labels; EN/ES/FR/IT supply the four subtitle output languages.


## License

This documentation is part of the Remake Engine project and is intended for educational and reverse engineering purposes only.
