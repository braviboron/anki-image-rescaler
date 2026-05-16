# Image Rescaler – Config

These are the addon's default settings. You can change them via
**Tools → Image Rescaler Settings…** inside Anki, through the **Settings**
entry in the toolbar button menus, or by editing this config directly.

| Key | Type | Default | Description |
|---|---|---|---|
| `resize_width` | integer | `605` | Pixel value applied when resizing by **width**. |
| `resize_height` | integer | `400` | Pixel value applied when resizing by **height**. |
| `auto_resize_on_paste` | boolean | `true` | Automatically resize images when they are pasted into a field. |
| `auto_resize_mode` | `"width"` or `"height"` | `"width"` | Which dimension to apply on paste. |
| `resize_image_mode` | `"width"` or `"height"` | `"width"` | Dimension used by a left-click on the **Resize Image** button. |
| `resize_field_mode` | `"width"` or `"height"` | `"width"` | Dimension used by a left-click on the **Resize Field** button. |
| `resize_card_mode` | `"width"` or `"height"` | `"width"` | Dimension used by a left-click on the **Resize Card** button. |

> The addon also stores a `__manual_resize__` key at runtime to remember the
> last values entered in the **Manual Resize** dialog. It is managed
> automatically — you don't need to set it by hand.
