# Image Rescaler – Config

These are the addon's default settings. You can change them via
**Tools → Image Rescaler Settings…** inside Anki, through the **Settings**
entry in the toolbar button menus, or by editing this config directly.

| Key | Type | Default | Description |
|---|---|---|---|
| `scale_width` | integer | `605` | Pixel value applied when rescaling by **width**. |
| `scale_height` | integer | `400` | Pixel value applied when rescaling by **height**. |
| `auto_scale_on_paste` | boolean | `true` | Automatically rescale images when they are pasted into a field. |
| `auto_scale_mode` | `"width"` or `"height"` | `"width"` | Which dimension to apply on paste. |
| `scale_image_mode` | `"width"` or `"height"` | `"width"` | Dimension used by a left-click on the **Rescale Image** button. |
| `scale_field_mode` | `"width"` or `"height"` | `"width"` | Dimension used by a left-click on the **Rescale Field** button. |
| `scale_card_mode` | `"width"` or `"height"` | `"width"` | Dimension used by a left-click on the **Rescale Card** button. |

> The addon also stores a `__manual_scale__` key at runtime to remember the
> last values entered in the **Manual Rescale** dialog. It is managed
> automatically — you don't need to set it by hand.
>
> Settings saved by older versions (`resize_*` / `__manual_resize__`) are
> migrated automatically, so updating won't lose your preferences.
