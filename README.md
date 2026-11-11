# PIKNOTT SAPPHIRE

A fully cel-shaded monster-catching RPG for Windows, the second game in the PIKNOTT series. Explore the **Sapphire** region — Crystal Vale, Nightpine, Cragspine, Glacier Mere, the Sapphire Caves, Frostcrown and Azure Summit — as a boy in a navy jacket. Choose one of three starter PIKNOTT, sneak through tall grass, throw **PIKCEL balls** to catch wild **PIKNOTT**, and battle them with your team using the same action-order system as PIKNOTT CELESTIKA, with **Normal / Strong / Agile** move styles.

The legendary sapphire dragon **Azurath** sleeps at Azure Summit. Your index is the **SAPPHIRE DOK**.

©2026 EX INC.HYPERION DIGITAL ©2026. Publisher: EX Inc./HYPERION DIGITAL. Version 1.0.0.

## Download
See [Releases](https://github.com/Teobokki/piknott-sapphire/releases/latest):
- `PIKNOTT.SAPPHIRE.Setup.1.0.0.exe`: installer (goes to `%LOCALAPPDATA%\Programs\PIKNOTT SAPPHIRE`, with desktop and Start-menu shortcuts)
- `PIKNOTT.SAPPHIRE.Portable.exe`: a single-file portable build that updates itself
- `PIKNOTT.SAPPHIRE.1.0.0.Windows.x64.zip`: the plain onedir build

Saves go to `%APPDATA%\PIKNOTT SAPPHIRE\save.json`.

## Controls
| Action | Key |
|---|---|
| Move / run / jump | WASD or arrows / Shift / Space |
| Camera | Mouse (third-person follow) |
| Crouch / sneak | C or Ctrl (you're hidden when crouching in tall grass) |
| Aim / throw PIKCEL ball | Hold right mouse / left click |
| Pick ball | 1-3 or the mouse wheel |
| Send out your PIKNOTT (starts a battle) | G |
| Team / SAPPHIRE DOK / region map | Tab / P / M |
| Talk to people, or rest and heal at the camp fire | E |
| Menu | Esc |
| Battle: styles | Z Normal, X Strong, C Agile; 1-4 pick a move |

Gamepad (basic): left stick moves, right stick turns the camera, A jumps, LT aims, RB throws, X sends out your PIKNOTT, B crouches.

## Build
- Engine: Python 3 + Panda3D 1.10, with custom GLSL toon shaders (3-step ramp) and inverted-hull ink outlines
- `python make_assets.py` builds the icon and backdrop from `assets/cover.jpg`, plus the procedural SFX and looping F# minor music
- `./build.sh` builds PyInstaller onedir, Inno Setup, onefile portable and the zip (under Wine)

## Credits
- UI font: Lilita One by Juan Montoreano (SIL Open Font License 1.1)
- Cover art: supplied by EX Inc.
- All models, PIKNOTT designs and sound effects are original. They are made procedurally or in Blender
