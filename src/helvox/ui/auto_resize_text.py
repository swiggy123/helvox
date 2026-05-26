import tkinter as tk


class AutoResizingText(tk.Text):
    """A Text widget that auto-resizes and syncs with a StringVar."""

    def __init__(
        self, master, textvariable=None, min_height=1, max_height=10, **kwargs
    ):
        super().__init__(master, **kwargs)
        self.textvariable = textvariable
        self.min_height = min_height
        self.max_height = max_height

        # Initialize from StringVar
        if textvariable is not None:
            self.insert("1.0", textvariable.get())
            textvariable.trace_add("write", self._update_from_var)

        # Bind events for updating
        self.bind("<<Modified>>", self._on_text_change)
        self.bind("<Configure>", lambda e: self._resize_height())

    def _on_text_change(self, event=None):
        """When text changes, update the StringVar and resize height."""
        self.edit_modified(False)
        text = self.get("1.0", "end-1c")

        if self.textvariable is not None:
            # Prevent recursive updates
            if self.textvariable.get() != text:
                self.textvariable.set(text)

        self._resize_height()

    def _update_from_var(self, *args):
        if not self.textvariable:
            return

        current_text = self.get("1.0", "end-1c")
        new_text = self.textvariable.get()
        if current_text != new_text:
            self.delete("1.0", "end")
            self.insert("1.0", new_text)
            self._resize_height()

    def _resize_height(self):
        height_raw = self.tk.call(
            (self._w, "count", "-update", "-displaylines", "1.0", "end")
        )

        try:
            height = int(height_raw)
        except (TypeError, ValueError):
            # Tk can occasionally return a Tcl object/string depending on platform.
            parts = str(height_raw).split()
            height = int(parts[0]) if parts else self.min_height

        self.configure(height=min(max(height, self.min_height), self.max_height))
