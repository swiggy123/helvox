import tkinter as tk

from helvox.utils.platform import app_font


class RoundedButton(tk.Canvas):
    def __init__(
        self,
        parent,
        text,
        command=None,
        bg_color="#000000",
        fg_color="#FFFFFF",
        width=150,
        height=50,
        corner_radius=20,
        dot=False,
        font=None,
        enabled=True,
        disabled_bg_color="#C8C8C8",
        disabled_fg_color="#6E6E6E",
    ):
        canvas_bg = "#f0f0f0"
        for color_key in ("bg", "background"):
            try:
                canvas_bg = parent.cget(color_key)
                break
            except tk.TclError:
                continue

        tk.Canvas.__init__(
            self,
            parent,
            width=width,
            height=height,
            bg=canvas_bg,
            highlightthickness=0,
        )

        self.command = command
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.corner_radius = corner_radius
        self.text = text
        self.dot = dot
        self.font = font or app_font(10, bold=True)
        self.enabled = enabled
        self.disabled_bg_color = disabled_bg_color
        self.disabled_fg_color = disabled_fg_color

        # Draw the button
        self.draw_button()

        # Bind click event
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Configure>", lambda _: self.draw_button())

    def draw_button(self, hover=False):
        self.delete("all")

        # Slightly lighter color on hover
        if self.enabled:
            current_bg = (
                self._adjust_color(self.bg_color, 30) if hover else self.bg_color
            )
            current_fg = self.fg_color
        else:
            current_bg = self.disabled_bg_color
            current_fg = self.disabled_fg_color

        # Draw rounded rectangle
        width = self.winfo_reqwidth()
        height = self.winfo_reqheight()
        radius = self.corner_radius

        # Create rounded rectangle using polygon
        points = [
            radius,
            0,
            width - radius,
            0,
            width,
            0,
            width,
            radius,
            width,
            height - radius,
            width,
            height,
            width - radius,
            height,
            radius,
            height,
            0,
            height,
            0,
            height - radius,
            0,
            radius,
            0,
            0,
        ]

        self.create_polygon(points, fill=current_bg, smooth=True, outline=current_bg)

        # Draw red dot
        if self.dot:
            dot_x = width // 2 - 20
            dot_y = height // 2
            dot_color = "#8B0000" if self.enabled else "#9A9A9A"
            self.create_oval(
                dot_x - 5,
                dot_y - 5,
                dot_x + 5,
                dot_y + 5,
                fill=dot_color,
                outline=dot_color,
            )

        # Draw text
        text_x = width // 2 + 5 if self.dot else width // 2
        self.create_text(
            text_x,
            height // 2,
            text=self.text,
            fill=current_fg,
            font=self.font,
        )

    def _adjust_color(self, color, amount):
        """Lighten a hex color by amount"""
        color = color.lstrip("#")
        rgb = tuple(int(color[i : i + 2], 16) for i in (0, 2, 4))
        rgb = tuple(min(255, c + amount) for c in rgb)
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

    def _on_click(self, event):
        if self.enabled and self.command:
            self.command()

    def _on_enter(self, event):
        if self.enabled:
            self.draw_button(hover=True)

    def _on_leave(self, event):
        self.draw_button(hover=False)

    def update_button(self, **kwargs):
        """Update button properties and redraw"""
        if "text" in kwargs:
            self.text = kwargs["text"]
        if "bg_color" in kwargs:
            self.bg_color = kwargs["bg_color"]
        if "fg_color" in kwargs:
            self.fg_color = kwargs["fg_color"]
        if "dot" in kwargs:
            self.dot = kwargs["dot"]
        if "font" in kwargs:
            self.font = kwargs["font"]
        if "enabled" in kwargs:
            self.enabled = bool(kwargs["enabled"])
        if "disabled_bg_color" in kwargs:
            self.disabled_bg_color = kwargs["disabled_bg_color"]
        if "disabled_fg_color" in kwargs:
            self.disabled_fg_color = kwargs["disabled_fg_color"]

        # Redraw the button with new settings
        self.draw_button()

    config = update_button
    configure = update_button
