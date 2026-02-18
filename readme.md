# The Simpsons Game (PS3) - Reverse Engineering Documentation

This repository contains documentation for the reverse engineering efforts of *The Simpsons Game* (2007) for the PlayStation 3. This documentation is maintained as a submodule for the main [TheSimpsonsGame-PS3](https://github.com/Superposition28/TheSimpsonsGame-PS3) game module.

## Links
- **Main Project:** [TheSimpsonsGame-PS3](https://github.com/Superposition28/TheSimpsonsGame-PS3)
- **STR Viewer:** [TheSimpsonsGame-PS3-FileViewer](https://github.com/Superposition28/TheSimpsonsGame-PS3-FileViewer)
- **Documentation Repo:** [TheSimpsonsGame-PS3-Docs](https://github.com/Superposition28/TheSimpsonsGame-PS3-Docs)
- **Hosted Docs:** [Online Documentation](https://superposition28.github.io/TheSimpsonsGame-PS3-Docs/)

## Content Structure

- **[Format Analysis](FormatAnalysis/index.html)**: Low-level reverse engineering writeups for various file formats found in the game (e.g., `.STR`, `.dff`, `.rws`, `.txd`, `.LH2`, etc.).
- **[PS3_GAME](PS3_GAME/index.html)**: Documentation of the root files found on the game disc.
- **[USRDIR](PS3_GAME/USRDIR/index.html)**: Detailed documentation of the game's data directory, including level-specific archives and assets.
- **Level Docs**: Individual documentation for each game level (L01 through L16, and Hubs), folder structure based on flattened output from the [remake module](https://github.com/Superposition28/TheSimpsonsGame-PS3)

## Features

- **Format Independence**: Format analyses are kept separate from game-specific instances to allow for reusable documentation.
- **Game Context**: Each instance of a format in the game files has localized documentation focusing on its specific purpose and role.
- **Responsive Layout**: The documentation uses simple CSS for a clean, readable layout without the need for complex build tools.


## License

This documentation is part of the Remake Engine project and is intended for educational and reverse engineering purposes only.
