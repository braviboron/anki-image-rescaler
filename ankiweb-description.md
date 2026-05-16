# Image Rescaler

Resize images directly in the Anki editor — precisely, and with the right
scope. Most resize add-ons force one size on everything. Image Rescaler lets
you choose *what* you resize and *how*: a single image, every image in a
field, or every image across the whole note — by width or by height — without
ever altering the original media file.

## Features

**Three scopes**

- **Image** — only the image you clicked / right-clicked.
- **Field** — every image in the current field.
- **Card** — every image in every field of the note.

**In the editor**

- Toolbar: a full `Image Resize ▾` menu, plus one-click **Resize Image**,
  **Resize Field**, and **Resize Card** buttons. Left-click applies your
  default; **right-click** any of them for per-scope options (manual size,
  width, height, revert, settings).
- Right-click inside a field: image-resize options are added to the editor's
  context menu.
- **Manual Resize** dialog: type an exact width and/or height, with an
  optional "remember these values" toggle.
- **Auto-resize on paste**: pasted images are sized automatically
  (toggleable; by width or by height).
- **Revert**: strip the add-on's sizing and return any image to its original
  size, at any scope.

**Cross-platform** — Windows, macOS, and Linux. Right-click on the toolbar
buttons is handled natively, so it works on macOS too.

## How it works

Image Rescaler sets the `width`/`height` attributes on the `<img>` tags in
your note — the same mechanism Anki uses when you drag an image's resize
handle. Your original image files are never modified or recompressed, so
nothing in your collection is degraded. **Revert** simply removes those
attributes, which means every change is fully reversible.

## Settings

Open **Tools → Image Rescaler Settings…**, or choose **Settings** from any
toolbar button's right-click menu:

- Default width and height (px)
- Which dimension each button uses (width or height)
- Auto-resize-on-paste: on/off, and by width or height

You can also edit these under **Tools → Add-ons → Image Rescaler → Config**.

## Source, issues & contributions

Open source under the MIT License. Source code, bug reports, and feature
requests are welcome at:

https://github.com/braviboron/anki-image-rescaler
