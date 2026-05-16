# Anki Image Rescaler

An [Anki](https://apps.ankiweb.net/) add-on for granular, correctly-scoped image
resizing directly in the note editor. Resize a single image, every image in a
field, or every image in the whole note — by width or height, with sensible
defaults and a manual-entry dialog.

## Features

- **Three scopes:** resize the image at the cursor, all images in the current
  field, or all images in the entire note.
- **Toolbar buttons:** `Image Resize ▾` (full menu), plus dedicated
  **Resize Image** / **Resize Field** / **Resize Card** buttons.
  Left-click applies your default; right-click opens per-scope options.
- **Manual Resize dialog:** enter an exact width and/or height, with an
  optional "remember these values" toggle.
- **Auto-resize on paste:** pasted images are resized automatically
  (toggleable).
- **Revert:** strip the addon's sizing back to the image's original size,
  at any scope.
- Works on macOS, Windows, and Linux (right-click on toolbar buttons is
  handled at the Qt level so it works on native macOS toolbars too).

## Repository layout

```
.
├── src/             # the add-on itself (this is what ships)
│   ├── __init__.py  #   all add-on logic
│   ├── config.json  #   default settings
│   ├── config.md    #   settings docs shown in Anki
│   └── manifest.json#   add-on metadata
├── build.sh         # package src/ into dist/*.ankiaddon
├── deploy.sh        # copy src/ into the local Anki addons folder for testing
├── LICENSE
└── README.md
```

## Installation

### From a packaged build

1. Build the add-on: `./build.sh` (produces `dist/anki-image-rescaler.ankiaddon`).
2. In Anki: **Tools → Add-ons → Install from file…** and select the
   `.ankiaddon` file.
3. Restart Anki.

### Manual install

Copy the contents of `src/` (`__init__.py`, `config.json`, `config.md`,
`manifest.json`) into a new folder inside your Anki `addons21` directory,
then restart Anki.

## Configuration

Open **Tools → Image Rescaler Settings…**, use the **Settings** entry in any
toolbar button menu, or edit the config via **Tools → Add-ons → Config**.
All keys are documented in [src/config.md](src/config.md).

## Development

The source of truth is this repository. To test changes in a live Anki
install, deploy the source into Anki's add-on folder:

```sh
./deploy.sh   # copies src/ into the local Anki addons21 folder
```

Then fully restart Anki to reload the add-on.

`meta.json` is intentionally **not** tracked — Anki generates it per install.

## License

Released under the [MIT License](LICENSE).
