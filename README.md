# Anki Image Rescaler

An [Anki](https://apps.ankiweb.net/) add-on that lets you rescale images in the
note editor. Rescaling sets the display size via the `<img>` tag's
width/height attributes, so the original image file is never modified or
recompressed (unlike resizing, which loses quality). Every change is
reversible. It also supports auto-rescale on paste.

AnkiWeb addon link: https://ankiweb.net/shared/info/1258277333

## Features

- **Three scopes for rescaling:** the image you clicked, every image in the
  current field, or every image in every field of the note.
- **Toolbar buttons:** `Image Rescale ▾` (full menu), plus dedicated
  **Rescale Image** / **Rescale Field** / **Rescale Card** buttons.
  Left-click applies your default size; right-click any button for per-scope
  options (manual size, width-only, height-only, revert, settings).
- **Right-click in a field:** image-rescale options are added to the editor's
  context menu.
- **Manual Rescale dialog:** enter an exact width and/or height, with an
  optional "remember these values" toggle.
- **Auto-rescale on paste:** pasted images are sized automatically
  (toggleable; by width or height).
- **Revert:** strip the add-on's sizing and return any image to its original
  display size, at any scope.
- Works on Windows, macOS, and Linux (right-click on toolbar buttons is
  handled at the Qt level so it works on native macOS toolbars too).

## Repository layout

```
.
├── src/             # the add-on itself (this is what ships)
│   ├── __init__.py  #   all add-on logic
│   ├── config.json  #   default settings
│   ├── config.md    #   settings docs shown in Anki
│   └── manifest.json#   add-on metadata
├── build.sh         # package src/ into publications/*.ankiaddon
├── deploy.sh        # copy src/ into the local Anki addons folder for testing
├── LICENSE
└── README.md
```

## Installation

### From AnkiWeb

AnkiWeb addon link: https://ankiweb.net/shared/info/1258277333

In Anki: Tools → Add-ons → Get Add-ons… and enter the code 1258277333.
Anki keeps it updated automatically.

### From a packaged build

1. Build the add-on: `./build.sh` (produces `publications/anki-image-rescaler.ankiaddon`).
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
