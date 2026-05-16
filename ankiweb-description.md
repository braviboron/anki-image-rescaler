# Image Rescaler

An Anki add-on that lets you rescale images in the editor. Rescaling sets the
display size via the `<img>` tag's width/height attributes, so the original
image file is never modified or recompressed (unlike resizing, which loses
quality). Every change is reversible.

It also supports auto-rescale on paste, so pasted images get sized
automatically.

## Features

**Three scopes for rescaling:**

- **Image** — affects only the image you clicked.
- **Field** — affects every image in the current field.
- **Card** — affects every image in every field of the note.

**In the editor:**

- Toolbar buttons for **Rescale Image**, **Rescale Field**, and **Rescale
  Card**, plus a full **Image Rescale** dropdown menu.
- Left-click applies your default size. Right-click any button for per-scope
  options (manual size, width-only, height-only, revert, settings).
- Right-click inside a field adds image-rescale options to the editor's
  context menu.
- **Manual Rescale** dialog lets you type an exact width and/or height, with
  an optional 'remember these values' toggle.
- Auto-rescale on paste (toggleable, by width or height).
- **Revert** strips the add-on's sizing and returns any image to its original
  display size, at any scope.

Works on Windows, macOS, and Linux. Right-click on toolbar buttons is handled
natively, so it works on macOS too.

## Settings

Open via **Tools → Image Rescaler Settings**, or pick **Settings** from any
toolbar button's right-click menu:

- Default width and height (px)
- Which dimension each button uses (width or height)
- Auto-rescale on paste: on/off, by width or height

You can also edit these under **Tools → Add-ons → Image Rescaler → Config**.

## Source

MIT License. Source, bugs, and feature requests:

https://github.com/braviboron/anki-image-rescaler
