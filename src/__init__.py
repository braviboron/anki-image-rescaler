"""
Image Rescaler Addon for Anki
Granular image resizing with correct scoping.
"""

from aqt import mw, gui_hooks
from aqt.editor import Editor, EditorWebView
from aqt.qt import QAction, QMimeData, QMenu, QCursor
from aqt.utils import showInfo, tooltip
from anki.hooks import wrap
import re
import platform

DEFAULT_CONFIG = {
    "resize_width": 605,
    "resize_height": 400,
    "auto_resize_on_paste": True,
    "auto_resize_mode": "width",
    "resize_image_mode": "width",
    "resize_field_mode": "width",
    "resize_card_mode": "width",
}


def get_cfg():
    cfg = mw.addonManager.getConfig(__name__) or {}
    return {**DEFAULT_CONFIG, **cfg}


# ── HTML manipulation ──────────────────────────────────────────────────────────

def stamp_img_tag(tag, mode, value):
    tag = re.sub(r'\s+width="[^"]*"', '', tag)
    tag = re.sub(r'\s+height="[^"]*"', '', tag)
    tag = re.sub(r'\s+data-editor-shrink="[^"]*"', '', tag)
    tag = re.sub(r'\s*/?>$', ' data-editor-shrink="false" {}="{}">'.format(mode, value), tag)
    return tag

def revert_img_tag(tag):
    tag = re.sub(r'\s+width="[^"]*"', '', tag)
    tag = re.sub(r'\s+height="[^"]*"', '', tag)
    tag = re.sub(r'\s+data-editor-shrink="[^"]*"', '', tag)
    return tag

def stamp_all_imgs(html, mode, value):
    return re.sub(r'<img\b[^>]*>', lambda m: stamp_img_tag(m.group(0), mode, value), html, flags=re.IGNORECASE)

def revert_all_imgs(html):
    return re.sub(r'<img\b[^>]*>', lambda m: revert_img_tag(m.group(0)), html, flags=re.IGNORECASE)

def stamp_first_img(html, mode, value):
    """Stamp only the first <img> tag found."""
    done = [False]
    def replacer(m):
        if not done[0]:
            done[0] = True
            return stamp_img_tag(m.group(0), mode, value)
        return m.group(0)
    return re.sub(r'<img\b[^>]*>', replacer, html, flags=re.IGNORECASE)

def revert_first_img(html):
    """Revert only the first <img> tag found."""
    done = [False]
    def replacer(m):
        if not done[0]:
            done[0] = True
            return revert_img_tag(m.group(0))
        return m.group(0)
    return re.sub(r'<img\b[^>]*>', replacer, html, flags=re.IGNORECASE)

def stamp_img_by_src(html, src, mode, value):
    """Stamp only the <img> whose src matches."""
    def replacer(m):
        tag = m.group(0)
        src_match = re.search(r'src="([^"]*)"', tag)
        if src_match and (src_match.group(1) == src or src_match.group(1).endswith(src) or src.endswith(src_match.group(1))):
            return stamp_img_tag(tag, mode, value)
        return tag
    return re.sub(r'<img\b[^>]*>', replacer, html, flags=re.IGNORECASE)

def revert_img_by_src(html, src):
    """Revert only the <img> whose src matches."""
    def replacer(m):
        tag = m.group(0)
        src_match = re.search(r'src="([^"]*)"', tag)
        if src_match and (src_match.group(1) == src or src_match.group(1).endswith(src) or src.endswith(src_match.group(1))):
            return revert_img_tag(tag)
        return tag
    return re.sub(r'<img\b[^>]*>', replacer, html, flags=re.IGNORECASE)


# ── JS to get the src of the last right-clicked / cursor-adjacent image ────────

JS_GET_CURSOR_IMG = """
(function() {
    // 1. Last right-clicked image
    if (window.__imgRescalerLastCtxImg) {
        var src = window.__imgRescalerLastCtxImg.getAttribute('src');
        window.__imgRescalerLastCtxImg = null;
        return src;
    }
    // 2. Image in current selection
    var sel = window.getSelection();
    if (sel && sel.rangeCount > 0) {
        var range = sel.getRangeAt(0);
        var frag = range.cloneContents();
        var imgs = frag.querySelectorAll('img');
        if (imgs.length > 0) return imgs[0].getAttribute('src');
        // Check if cursor is right next to an image
        var node = range.startContainer;
        if (node.nodeType === 1) {
            var img = node.querySelector('img');
            if (img) return img.getAttribute('src');
        }
        if (node.parentElement) {
            var img = node.parentElement.querySelector('img');
            if (img) return img.getAttribute('src');
        }
    }
    return null;
})();
"""

JS_TRACK_CONTEXTMENU = """
(function() {
    if (window.__imgRescalerCtxInit) return;
    window.__imgRescalerCtxInit = true;
    document.addEventListener('contextmenu', function(e) {
        var el = e.target;
        while (el) {
            if (el.tagName === 'IMG') {
                window.__imgRescalerLastCtxImg = el;
                return;
            }
            el = el.parentElement;
        }
        window.__imgRescalerLastCtxImg = null;
    }, true);
})();
"""


# ── Field helpers ──────────────────────────────────────────────────────────────

def get_field_idx(editor):
    field_idx = editor.currentField
    if field_idx is not None:
        return field_idx
    for i, fld in enumerate(editor.note.fields):
        if re.search(r'<img\b', fld, re.IGNORECASE):
            return i
    return None


# ── Single image operations (uses JS to find which image) ─────────────────────

def do_resize(editor, mode, value):
    """Resize the single image at the cursor/right-click position."""
    def got_src(src):
        note = editor.note
        if not note:
            return
        idx = get_field_idx(editor)
        if idx is None:
            showInfo("Click into a field first.")
            return
        html = note.fields[idx]
        if not re.search(r'<img\b', html, re.IGNORECASE):
            showInfo("No images found in this field.")
            return
        if src:
            note.fields[idx] = stamp_img_by_src(html, src, mode, value)
        else:
            # No specific image identified — stamp first one in field
            note.fields[idx] = stamp_first_img(html, mode, value)
        editor.loadNoteKeepingFocus()
        tooltip("Image resized to {}={}px".format(mode, value))
    editor.web.evalWithCallback(JS_GET_CURSOR_IMG, got_src)

def do_revert(editor):
    """Revert the single image at the cursor/right-click position."""
    def got_src(src):
        note = editor.note
        if not note:
            return
        idx = get_field_idx(editor)
        if idx is None:
            showInfo("Click into a field first.")
            return
        html = note.fields[idx]
        if not re.search(r'<img\b', html, re.IGNORECASE):
            showInfo("No images found in this field.")
            return
        if src:
            note.fields[idx] = revert_img_by_src(html, src)
        else:
            note.fields[idx] = revert_first_img(html)
        editor.loadNoteKeepingFocus()
        tooltip("Image reverted to original size.")
    editor.web.evalWithCallback(JS_GET_CURSOR_IMG, got_src)


# ── All-in-field operations ────────────────────────────────────────────────────

def do_resize_all_in_field(editor, mode, value):
    note = editor.note
    if not note:
        return
    idx = get_field_idx(editor)
    if idx is None:
        showInfo("Click into a field first.")
        return
    html = note.fields[idx]
    if not re.search(r'<img\b', html, re.IGNORECASE):
        tooltip("No images found in this field.")
        return
    note.fields[idx] = stamp_all_imgs(html, mode, value)
    editor.loadNoteKeepingFocus()
    tooltip("All images in field resized to {}={}px".format(mode, value))

def do_revert_all_in_field(editor):
    note = editor.note
    if not note:
        return
    idx = get_field_idx(editor)
    if idx is None:
        showInfo("Click into a field first.")
        return
    html = note.fields[idx]
    if not re.search(r'<img\b', html, re.IGNORECASE):
        tooltip("No images found in this field.")
        return
    note.fields[idx] = revert_all_imgs(html)
    editor.loadNoteKeepingFocus()
    tooltip("All images in field reverted.")


# ── All-in-card operations ────────────────────────────────────────────────────

def do_resize_all_in_card(editor, mode, value):
    note = editor.note
    if not note:
        return
    changed = False
    for i, html in enumerate(note.fields):
        if re.search(r'<img\b', html, re.IGNORECASE):
            note.fields[i] = stamp_all_imgs(html, mode, value)
            changed = True
    if changed:
        editor.loadNoteKeepingFocus()
        tooltip("All images in card resized to {}={}px".format(mode, value))
    else:
        tooltip("No images found in any field.")

def do_revert_all_in_card(editor):
    note = editor.note
    if not note:
        return
    changed = False
    for i, html in enumerate(note.fields):
        if re.search(r'<img\b', html, re.IGNORECASE):
            note.fields[i] = revert_all_imgs(html)
            changed = True
    if changed:
        editor.loadNoteKeepingFocus()
        tooltip("All images in card reverted.")
    else:
        tooltip("No images found in any field.")



def _find_editor_for_webview(web_view):
    try:
        from aqt.editcurrent import EditCurrent
        from aqt.addcards import AddCards
        from aqt.browser.browser import Browser
        for widget in mw.app.topLevelWidgets():
            ed = None
            if isinstance(widget, (EditCurrent, AddCards)):
                ed = widget.editor
            elif isinstance(widget, Browser):
                ed = getattr(widget, 'editor', None)
            if ed and ed.web is web_view:
                return ed
    except Exception:
        pass
    return None


# ── Settings dialog ────────────────────────────────────────────────────────────

def _make_parent(editor):
    if platform.system() == "Windows" and editor is not None:
        try:
            return editor.parentWindow
        except Exception:
            pass
    return mw


def open_settings(editor=None):
    from aqt.qt import (
        QDialog, QVBoxLayout, QHBoxLayout, QLabel,
        QSpinBox, QComboBox, QPushButton, QCheckBox, QFrame,
    )
    cfg = get_cfg()
    dlg = QDialog(_make_parent(editor))
    dlg.setWindowTitle("Image Rescaler - Settings")
    dlg.setMinimumWidth(380)
    layout = QVBoxLayout(dlg)

    def section_label(text):
        lbl = QLabel("<b>{}</b>".format(text))
        layout.addWidget(lbl)

    def add_row(label_text, widget):
        row = QHBoxLayout()
        row.addWidget(QLabel(label_text))
        row.addWidget(widget)
        layout.addLayout(row)
        return widget

    def combo(options, current):
        c = QComboBox()
        c.addItems(options)
        c.setCurrentText(current)
        return c

    def spinbox(val):
        s = QSpinBox()
        s.setRange(10, 9999)
        s.setValue(val)
        return s

    def separator():
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

    # ── Dimensions ──
    section_label("Dimensions")
    spin_w = add_row("Default width (px):", spinbox(cfg["resize_width"]))
    spin_h = add_row("Default height (px):", spinbox(cfg["resize_height"]))

    separator()

    # ── Button default actions ──
    section_label("Button default actions (left-click)")
    combo_img_mode  = add_row("'Resize Image' button uses:", combo(["width", "height"], cfg.get("resize_image_mode", "width")))
    combo_fld_mode  = add_row("'Resize Field' button uses:", combo(["width", "height"], cfg.get("resize_field_mode", "width")))
    combo_card_mode = add_row("'Resize Card' button uses:",  combo(["width", "height"], cfg.get("resize_card_mode",  "width")))

    separator()

    # ── Paste ──
    section_label("Paste")
    combo_paste = add_row("Auto-resize on paste by:", combo(["width", "height"], cfg.get("auto_resize_mode", "width")))
    chk = QCheckBox("Auto-resize images on paste")
    chk.setChecked(cfg.get("auto_resize_on_paste", True))
    layout.addWidget(chk)

    separator()

    row_btns = QHBoxLayout()
    btn_save   = QPushButton("Save")
    btn_cancel = QPushButton("Cancel")
    row_btns.addWidget(btn_save)
    row_btns.addWidget(btn_cancel)
    layout.addLayout(row_btns)

    def save():
        # Preserve manual-resize memory key while writing main settings
        raw = mw.addonManager.getConfig(__name__) or {}
        manual_mem = raw.get(_MANUAL_CFG_KEY, {})
        new_cfg = {
            "resize_width":      spin_w.value(),
            "resize_height":     spin_h.value(),
            "auto_resize_mode":  combo_paste.currentText(),
            "auto_resize_on_paste": chk.isChecked(),
            "resize_image_mode": combo_img_mode.currentText(),
            "resize_field_mode": combo_fld_mode.currentText(),
            "resize_card_mode":  combo_card_mode.currentText(),
        }
        if manual_mem:
            new_cfg[_MANUAL_CFG_KEY] = manual_mem
        mw.addonManager.writeConfig(__name__, new_cfg)
        dlg.accept()
        tooltip("Image Rescaler settings saved.")

    btn_save.clicked.connect(save)
    btn_cancel.clicked.connect(dlg.reject)
    dlg.exec()


# ── Main dropdown menu ─────────────────────────────────────────────────────────

def show_main_menu(editor):
    cfg = get_cfg()
    w = cfg["resize_width"]
    h = cfg["resize_height"]
    menu = QMenu()

    menu.addAction("Image resize settings", lambda: open_settings(editor))
    menu.addSeparator()

    # ── Image ──
    menu.addAction("Resize image (specify size)",
                   lambda: open_manual_resize(editor, scope="image"))
    menu.addAction("Resize image (width = {} px)".format(w),
                   lambda: do_resize(editor, "width", w))
    menu.addAction("Resize image (height = {} px)".format(h),
                   lambda: do_resize(editor, "height", h))
    menu.addAction("Revert image to original size",
                   lambda: do_revert(editor))
    menu.addSeparator()

    # ── Field ──
    menu.addAction("Resize all images in field (specify size)",
                   lambda: open_manual_resize(editor, scope="field"))
    menu.addAction("Resize all images in field (width = {} px)".format(w),
                   lambda: do_resize_all_in_field(editor, "width", w))
    menu.addAction("Resize all images in field (height = {} px)".format(h),
                   lambda: do_resize_all_in_field(editor, "height", h))
    menu.addAction("Revert all images in field to original size",
                   lambda: do_revert_all_in_field(editor))
    menu.addSeparator()

    # ── Card ──
    menu.addAction("Resize all images in card (specify size)",
                   lambda: open_manual_resize(editor, scope="card"))
    menu.addAction("Resize all images in card (width = {} px)".format(w),
                   lambda: do_resize_all_in_card(editor, "width", w))
    menu.addAction("Resize all images in card (height = {} px)".format(h),
                   lambda: do_resize_all_in_card(editor, "height", h))
    menu.addAction("Revert all images in card to original size",
                   lambda: do_revert_all_in_card(editor))

    menu.exec(QCursor.pos())


# ── Manual Resize dialog ───────────────────────────────────────────────────────

_MANUAL_CFG_KEY = "__manual_resize__"

def _get_manual_memory():
    """Load persisted manual-resize values from addon config (isolated key)."""
    raw = mw.addonManager.getConfig(__name__) or {}
    mem = raw.get(_MANUAL_CFG_KEY, {})
    return {"width": mem.get("width", ""), "height": mem.get("height", "")}

def _save_manual_memory(width, height):
    """Persist manual-resize values without touching any other config keys."""
    raw = mw.addonManager.getConfig(__name__) or {}
    raw[_MANUAL_CFG_KEY] = {"width": width, "height": height}
    mw.addonManager.writeConfig(__name__, raw)

def _clear_manual_memory():
    """Clear persisted manual-resize values."""
    raw = mw.addonManager.getConfig(__name__) or {}
    raw.pop(_MANUAL_CFG_KEY, None)
    mw.addonManager.writeConfig(__name__, raw)

def open_manual_resize(editor, scope="image"):
    from aqt.qt import (
        QDialog, QVBoxLayout, QHBoxLayout, QLabel,
        QLineEdit, QPushButton, QCheckBox, QIntValidator,
        Qt,
    )

    if platform.system() == "Windows" and editor is not None:
        try:
            parent = editor.parentWindow
        except Exception:
            parent = mw
    else:
        parent = mw

    dlg = QDialog(parent)
    scope_label = {"image": "Image", "field": "All Images in Field", "card": "All Images in Card"}.get(scope, "Image")
    dlg.setWindowTitle("Manual Resize — {}".format(scope_label))
    dlg.setMinimumWidth(280)
    layout = QVBoxLayout(dlg)

    mem = _get_manual_memory()

    # Width row
    row_w = QHBoxLayout()
    row_w.addWidget(QLabel("Width (px):"))
    edit_w = QLineEdit()
    edit_w.setPlaceholderText("leave blank to skip")
    edit_w.setValidator(QIntValidator(1, 9999))
    if mem["width"]:
        edit_w.setText(mem["width"])
    row_w.addWidget(edit_w)
    layout.addLayout(row_w)

    # Height row
    row_h = QHBoxLayout()
    row_h.addWidget(QLabel("Height (px):"))
    edit_h = QLineEdit()
    edit_h.setPlaceholderText("leave blank to skip")
    edit_h.setValidator(QIntValidator(1, 9999))
    if mem["height"]:
        edit_h.setText(mem["height"])
    row_h.addWidget(edit_h)
    layout.addLayout(row_h)

    # Remember checkbox
    chk_remember = QCheckBox("Remember these values next time")
    chk_remember.setChecked(bool(mem["width"] or mem["height"]))
    layout.addWidget(chk_remember)

    # Buttons
    row_btns = QHBoxLayout()
    btn_apply = QPushButton("Apply")
    btn_apply.setDefault(True)
    btn_cancel = QPushButton("Cancel")
    row_btns.addWidget(btn_apply)
    row_btns.addWidget(btn_cancel)
    layout.addLayout(row_btns)

    def apply():
        w_text = edit_w.text().strip()
        h_text = edit_h.text().strip()

        if not w_text and not h_text:
            tooltip("Enter at least one dimension.")
            return

        # Update memory
        if chk_remember.isChecked():
            _save_manual_memory(w_text, h_text)
        else:
            _clear_manual_memory()

        dlg.accept()

        # Apply to the image at cursor, for each specified dimension
        def apply_dimensions(src):
            note = editor.note
            if not note:
                return
            idx = get_field_idx(editor)
            if idx is None:
                showInfo("Click into a field first.")
                return
            html = note.fields[idx]
            if not re.search(r'<img\b', html, re.IGNORECASE):
                showInfo("No images found in this field.")
                return

            # Apply width first, then height, targeting the same image.
            # We stamp both attributes onto the tag rather than calling
            # stamp_img_tag twice (which would strip each previous one).
            def stamper(m):
                tag = m.group(0)
                # Check src match if we have one
                if src:
                    src_match = re.search(r'src="([^"]*)"', tag)
                    if not src_match:
                        return tag
                    t_src = src_match.group(1)
                    if not (t_src == src or t_src.endswith(src) or src.endswith(t_src)):
                        return tag
                elif getattr(stamper, '_done', False):
                    return tag
                # Strip existing dimensional attrs
                tag = re.sub(r'\s+width="[^"]*"', '', tag)
                tag = re.sub(r'\s+height="[^"]*"', '', tag)
                tag = re.sub(r'\s+data-editor-shrink="[^"]*"', '', tag)
                # Build new attr string
                attrs = ' data-editor-shrink="false"'
                if w_text:
                    attrs += ' width="{}"'.format(w_text)
                if h_text:
                    attrs += ' height="{}"'.format(h_text)
                tag = re.sub(r'\s*/?>$', attrs + '>', tag)
                if not src:
                    stamper._done = True
                return tag

            stamper._done = False
            note.fields[idx] = re.sub(r'<img\b[^>]*>', stamper, html, flags=re.IGNORECASE)
            editor.loadNoteKeepingFocus()
            parts = []
            if w_text:
                parts.append("width={}px".format(w_text))
            if h_text:
                parts.append("height={}px".format(h_text))
            tooltip("Image resized: {}".format(", ".join(parts)))

        def apply_dimensions_bulk(bulk_scope):
            note = editor.note
            if not note:
                return
            def do_stamp(html):
                def stamper(m):
                    tag = m.group(0)
                    tag = re.sub(r'\s+width="[^"]*"', '', tag)
                    tag = re.sub(r'\s+height="[^"]*"', '', tag)
                    tag = re.sub(r'\s+data-editor-shrink="[^"]*"', '', tag)
                    attrs = ' data-editor-shrink="false"'
                    if w_text:
                        attrs += ' width="{}"'.format(w_text)
                    if h_text:
                        attrs += ' height="{}"'.format(h_text)
                    tag = re.sub(r'\s*/?>$', attrs + '>', tag)
                    return tag
                return re.sub(r'<img\b[^>]*>', stamper, html, flags=re.IGNORECASE)
            if bulk_scope == "field":
                idx = get_field_idx(editor)
                if idx is None:
                    showInfo("Click into a field first.")
                    return
                html = note.fields[idx]
                if not re.search(r'<img\b', html, re.IGNORECASE):
                    tooltip("No images found in this field.")
                    return
                note.fields[idx] = do_stamp(html)
            else:
                changed = False
                for i, html in enumerate(note.fields):
                    if re.search(r'<img\b', html, re.IGNORECASE):
                        note.fields[i] = do_stamp(html)
                        changed = True
                if not changed:
                    tooltip("No images found in any field.")
                    return
            editor.loadNoteKeepingFocus()
            parts = []
            if w_text:
                parts.append("width={}px".format(w_text))
            if h_text:
                parts.append("height={}px".format(h_text))
            tooltip("Images resized: {}".format(", ".join(parts)))

        if scope == "image":
            editor.web.evalWithCallback(JS_GET_CURSOR_IMG, apply_dimensions)
        elif scope == "field":
            apply_dimensions_bulk("field")
        else:
            apply_dimensions_bulk("card")

    btn_apply.clicked.connect(apply)
    btn_cancel.clicked.connect(dlg.reject)

    # Focus width field on open
    dlg.show()
    edit_w.setFocus(Qt.FocusReason.OtherFocusReason)
    dlg.exec()


# ── Toolbar button right-click menus ──────────────────────────────────────────

def _show_btn_context_menu(editor, scope):
    """Right-click popup for Resize Image / Resize Field / Resize Card buttons."""
    cfg = get_cfg()
    w = cfg["resize_width"]
    h = cfg["resize_height"]
    menu = QMenu()

    if scope == "image":
        menu.addAction("Manual resize", lambda: open_manual_resize(editor, scope="image"))
        menu.addAction("Resize width to {} px".format(w), lambda: do_resize(editor, "width", w))
        menu.addAction("Resize height to {} px".format(h), lambda: do_resize(editor, "height", h))
        menu.addAction("Revert image to original size", lambda: do_revert(editor))
    elif scope == "field":
        menu.addAction("Manual resize", lambda: open_manual_resize(editor, scope="field"))
        menu.addAction("Resize width to {} px".format(w), lambda: do_resize_all_in_field(editor, "width", w))
        menu.addAction("Resize height to {} px".format(h), lambda: do_resize_all_in_field(editor, "height", h))
        menu.addAction("Revert all images in field to original size", lambda: do_revert_all_in_field(editor))
    else:
        menu.addAction("Manual resize", lambda: open_manual_resize(editor, scope="card"))
        menu.addAction("Resize width to {} px".format(w), lambda: do_resize_all_in_card(editor, "width", w))
        menu.addAction("Resize height to {} px".format(h), lambda: do_resize_all_in_card(editor, "height", h))
        menu.addAction("Revert all images in card to original size", lambda: do_revert_all_in_card(editor))

    menu.addSeparator()
    menu.addAction("Settings", lambda: open_settings(editor))
    menu.exec(QCursor.pos())


def _make_scope_click(scope):
    """Return a left-click handler that reads config at call time."""
    def handler(editor):
        cfg = get_cfg()
        w = cfg["resize_width"]
        h = cfg["resize_height"]
        if scope == "image":
            mode = cfg.get("resize_image_mode", "width")
            value = w if mode == "width" else h
            do_resize(editor, mode, value)
        elif scope == "field":
            mode = cfg.get("resize_field_mode", "width")
            value = w if mode == "width" else h
            do_resize_all_in_field(editor, mode, value)
        else:
            mode = cfg.get("resize_card_mode", "width")
            value = w if mode == "width" else h
            do_resize_all_in_card(editor, mode, value)
    return handler


# ── Qt-level right-click on toolbar buttons ────────────────────────────────────

def _attach_right_click(qt_btn, editor, scope):
    """
    Monkey-patch mousePressEvent on the Qt button widget so that a right-click
    (button 2) opens our context menu. This works on all platforms including
    Mac, where Anki's toolbar buttons are native Qt widgets — not HTML elements
    — so JS mousedown/contextmenu events never reach them.
    """
    from aqt.qt import Qt, QMouseEvent
    original = qt_btn.mousePressEvent

    def patched(event):
        if event.button() == Qt.MouseButton.RightButton:
            _show_btn_context_menu(editor, scope)
        else:
            original(event)

    qt_btn.mousePressEvent = patched


# ── Toolbar buttons ────────────────────────────────────────────────────────────

def add_toolbar_button(buttons, editor: Editor):
    # "Image Resize ▾" dropdown
    btn_menu = editor.addButton(
        icon="",
        cmd="resize_images_menu",
        func=lambda ed: show_main_menu(ed),
        tip="Image Resize options",
        label="Image Resize ▾",
    )
    buttons.append(btn_menu)

    # "Resize Image" — left-click per settings; right-click = options menu
    btn_img = editor.addButton(
        icon="",
        cmd="resize_image_btn",
        func=_make_scope_click("image"),
        tip="Resize image (right-click for options)",
        label="Resize Image",
    )
    buttons.append(btn_img)

    # "Resize Field"
    btn_field = editor.addButton(
        icon="",
        cmd="resize_field_btn",
        func=_make_scope_click("field"),
        tip="Resize all images in field (right-click for options)",
        label="Resize Field",
    )
    buttons.append(btn_field)

    # "Resize Card"
    btn_card = editor.addButton(
        icon="",
        cmd="resize_card_btn",
        func=_make_scope_click("card"),
        tip="Resize all images in card (right-click for options)",
        label="Resize Card",
    )
    buttons.append(btn_card)

    # Attach Qt-level right-click handlers.
    # We use a short timer so Qt has finished laying out the toolbar.
    # We search only within the editor's own parent widget tree, and match
    # buttons by a unique objectName we'll set via JS eval on the webview.
    # Since editor.addButton returns HTML in modern Anki, we find QPushButtons
    # by text within the editor's widget hierarchy only.
    def attach_after_layout():
        from aqt.qt import QPushButton
        label_to_scope = {
            "Resize Image": "image",
            "Resize Field": "field",
            "Resize Card":  "card",
        }
        # Find the editor's root Qt widget
        try:
            root = editor.parentWindow
        except Exception:
            root = None
        if root is None:
            # Fallback: search all top-level widgets but only match editor's buttons
            # by checking that the button's window is associated with this editor
            for widget in mw.app.topLevelWidgets():
                for btn in widget.findChildren(QPushButton):
                    if btn.text() in label_to_scope:
                        scope = label_to_scope[btn.text()]
                        if btn.objectName() != "imgrescaler_{}".format(scope):
                            btn.setObjectName("imgrescaler_{}".format(scope))
                            _attach_right_click(btn, editor, scope)
            return
        for btn in root.findChildren(QPushButton):
            if btn.text() in label_to_scope:
                scope = label_to_scope[btn.text()]
                _attach_right_click(btn, editor, scope)

    mw.progress.timer(200, attach_after_layout, False)

    return buttons


# ── Context menu tracker + suppressor ─────────────────────────────────────────

JS_SETUP = """
(function() {
    if (window.__imgRescalerSetup) return;
    window.__imgRescalerSetup = true;

    // Track which image was right-clicked
    document.addEventListener('contextmenu', function(e) {
        var el = e.target;
        window.__imgRescalerLastCtxImg = null;
        while (el) {
            if (el.tagName === 'IMG') {
                window.__imgRescalerLastCtxImg = el;
                break;
            }
            el = el.parentElement;
        }
    }, true);

    // Suppress the browser context menu on all toolbar buttons.
    // Right-click menus on our scope buttons are handled at the Qt level
    // via mousePressEvent monkey-patching (works on Mac and all platforms).
    document.addEventListener('contextmenu', function(e) {
        var el = e.target;
        while (el) {
            if (el.tagName === 'BUTTON' || (el.tagName === 'INPUT' && el.type === 'button')) {
                e.preventDefault();
                e.stopPropagation();
                return;
            }
            el = el.parentElement;
        }
    }, true);
})();
"""

def inject_js(editor):
    editor.web.eval(JS_SETUP)


# ── Right-click context menu (field content only, no toolbar) ─────────────────

def on_editor_context_menu(web_view, menu):
    editor = _find_editor_for_webview(web_view)
    if editor is None:
        return
    if web_view is not editor.web:
        return

    # Normal right-click on note field content — append image resize items
    cfg = get_cfg()
    w = cfg["resize_width"]
    h = cfg["resize_height"]
    menu.addSeparator()
    menu.addAction("Resize image (specify size)",
                   lambda: open_manual_resize(editor, scope="image"))
    menu.addAction("Resize image (width = {} px)".format(w),
                   lambda: do_resize(editor, "width", w))
    menu.addAction("Resize image (height = {} px)".format(h),
                   lambda: do_resize(editor, "height", h))
    menu.addAction("Revert image to original size",
                   lambda: do_revert(editor))


# ── Paste intercept ───────────────────────────────────────────────────────────

def _processMime_around(self, mime, extended=False, drop_event=False, _old=None):
    cfg = get_cfg()
    if not cfg.get("auto_resize_on_paste"):
        return _old(self, mime, extended, drop_event)
    if mime.hasHtml() and re.search(r'<img\b', mime.html(), re.IGNORECASE):
        mode = cfg["auto_resize_mode"]
        value = cfg["resize_width"] if mode == "width" else cfg["resize_height"]
        stamped_html = stamp_all_imgs(mime.html(), mode, value)
        new_mime = QMimeData()
        new_mime.setHtml(stamped_html)
        if mime.hasText():
            new_mime.setText(mime.text())
        if mime.hasUrls():
            new_mime.setUrls(mime.urls())
        if mime.hasImage():
            new_mime.setImageData(mime.imageData())
        return _old(self, new_mime, extended, drop_event)
    return _old(self, mime, extended, drop_event)


# ── Tools menu ─────────────────────────────────────────────────────────────────

def add_menu_item():
    action = QAction("Image Rescaler Settings", mw)
    action.triggered.connect(lambda: open_settings())
    mw.form.menuTools.addAction(action)


def setup():
    EditorWebView._processMime = wrap(EditorWebView._processMime, _processMime_around, 'around')


gui_hooks.editor_did_init_buttons.append(add_toolbar_button)
gui_hooks.editor_did_load_note.append(inject_js)
gui_hooks.editor_will_show_context_menu.append(on_editor_context_menu)
gui_hooks.main_window_did_init.append(add_menu_item)
setup()
