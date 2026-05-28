import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from platformdirs import user_config_path

from helvox.ui.auto_resize_text import AutoResizingText
from helvox.ui.button import RoundedButton
from helvox.ui.rounded_canvas import RoundedCanvas
from helvox.ui.settings import SettingsDialog
from helvox.utils.platform import app_font, default_recordings_dir
from helvox.utils.recorder import Recorder


class App:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root

        self.recorder = Recorder(
            output_folder=default_recordings_dir(), sample_rate=48000, channels=1
        )

        self.settings_path = (
            user_config_path(appname="helvox", appauthor="noxenum") / "config.ini"
        )
        self.current_id: str | None = None
        self.previous_ids: list[str] = []
        self.current_rating: str | None = None

        self.setup_window()
        self.setup_ui()

        # Show settings dialog on startup
        self.show_settings()

    def setup_window(self) -> None:
        self.root.title("Helvox")
        self.root.geometry("900x700")

        # Set minimum window size
        self.root.minsize(900, 700)

        # Set app icon
        icon_path = Path(__file__).parent / "resources" / "icons" / "app.png"
        if icon_path.exists():
            icon = tk.PhotoImage(file=icon_path)
            self.root.iconphoto(False, icon)

        # Bind configure event
        self.root.bind("<Configure>", self.configure_handler)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_styles(self) -> None:
        """Use a predictable ttk theme so macOS and Windows look/behave alike."""
        style = ttk.Style(self.root)

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("TLabel", font=app_font(10), foreground="#1F1F1F")
        style.configure("TLabelframe.Label", font=app_font(10, bold=True))

    def setup_ui(self) -> None:
        self.setup_styles()

        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nswe")

        # Configure grid weights for responsiveness
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)  # Allow spacing before buttons
        main_frame.columnconfigure(0, weight=1)

        # Settings button at the top
        settings_frame = ttk.Frame(main_frame)
        settings_frame.grid(row=0, column=0, sticky="we", pady=(0, 10))
        settings_frame.columnconfigure(0, weight=1)

        settings_btn = RoundedButton(
            settings_frame,
            text="Settings",
            command=self.show_settings,
            bg_color="#E6E6E6",
            fg_color="#363636",
            width=120,
            height=40,
            corner_radius=20,
            dot=False,
        )
        settings_btn.grid(row=0, column=0, padx=5, sticky="e")

        # Text frame
        text_frame = ttk.LabelFrame(main_frame, text="Text", padding="5")
        text_frame.grid(row=1, column=0, sticky="we", pady=5, padx=5)
        text_frame.columnconfigure(0, weight=1)

        de_text_frame = ttk.Frame(text_frame)
        de_text_frame.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        de_text_frame.columnconfigure(0, weight=1)

        ttk.Label(de_text_frame, text="DE:").grid(row=0, column=0, sticky=tk.W, padx=0)

        self.de_text_var = tk.StringVar(value="")
        de_text_label = tk.Label(
            de_text_frame,
            textvariable=self.de_text_var,
            relief="sunken",
            background="#FFFFFF",
            foreground="#1F1F1F",
            font=app_font(12),
            padx=6,
            pady=5,
            anchor="w",
            justify="left",
        )
        de_text_label.grid(row=1, column=0, sticky="ew")

        # update wraplength dynamically
        de_text_label.bind(
            "<Configure>",
            lambda e: e.widget.configure(wraplength=e.width - 10),
        )

        # CH
        ch_text_frame = ttk.Frame(text_frame)
        ch_text_frame.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        ch_text_frame.columnconfigure(0, weight=1)

        ttk.Label(ch_text_frame, text="CH (Suggestion):").grid(
            row=0, column=0, sticky=tk.W, padx=0
        )

        self.ch_text_var = tk.StringVar(value="")
        ch_text_label = tk.Label(
            ch_text_frame,
            textvariable=self.ch_text_var,
            relief="sunken",
            background="#FFFFFF",
            foreground="#1F1F1F",
            font=app_font(12),
            padx=6,
            pady=5,
            anchor="w",
            justify="left",
        )
        ch_text_label.grid(row=1, column=0, sticky="ew")

        # update wraplength dynamically
        ch_text_label.bind(
            "<Configure>",
            lambda e: e.widget.configure(wraplength=e.width - 10),
        )

        # CH (Editable)
        ch_text_edit_frame = ttk.Frame(text_frame)
        ch_text_edit_frame.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        ch_text_edit_frame.columnconfigure(0, weight=1)

        ttk.Label(ch_text_edit_frame, text="CH (Edit):").grid(
            row=0, column=0, sticky=tk.W, padx=0
        )

        self.ch_text_edit_var = tk.StringVar(value="")
        self.speaker_input = AutoResizingText(
            ch_text_edit_frame,
            textvariable=self.ch_text_edit_var,
            font=app_font(12),
            background="white",
            foreground="#000000",
            wrap="word",
            padx=5,
            pady=5,
            min_height=2,
            max_height=8,
        )
        self.speaker_input.grid(row=1, column=0, padx=(0, 0), pady=8, sticky="ew")

        # Recording frame
        recording_frame = ttk.LabelFrame(main_frame, text="Recording", padding="5")
        recording_frame.grid(row=2, column=0, sticky="we", pady=5, padx=5)

        # Configure recording frame columns - column 2 expands
        recording_frame.columnconfigure(2, weight=1)

        self.level_canvas = tk.Canvas(recording_frame, width=40, height=160, bg="black")
        self.level_canvas.grid(row=0, rowspan=4, column=0, sticky="ns", padx=5, pady=5)

        self.level_text = tk.StringVar(value="Level: 0 dB")
        ttk.Label(recording_frame, textvariable=self.level_text).grid(
            row=4, column=0, sticky=tk.W, padx=5
        )

        self.waveform_canvas_full = RoundedCanvas(
            recording_frame, height=50, bg="black", corner_radius=20
        )
        self.waveform_canvas_full.grid(row=0, column=2, sticky="we", padx=5, pady=5)

        self.play_btn_full = RoundedButton(
            recording_frame,
            text="Preview",
            command=self.recorder.play_audio_data_full_audio,
            bg_color="#10A560",
            fg_color="#FFFFFF",
            width=120,
            height=50,
            corner_radius=20,
        )
        self.play_btn_full.grid(row=0, column=3, padx=5)

        self.duration_text_full = tk.StringVar(value="Full | Duration: 0.0 seconds")
        ttk.Label(recording_frame, textvariable=self.duration_text_full).grid(
            row=1, column=2, sticky=tk.W, padx=5
        )

        self.waveform_canvas_trimmed = RoundedCanvas(
            recording_frame, height=50, bg="black", corner_radius=20
        )
        self.waveform_canvas_trimmed.grid(row=2, column=2, sticky="we", padx=5, pady=5)

        self.play_btn_trimmed = RoundedButton(
            recording_frame,
            text="Preview",
            command=self.recorder.play_audio_data_trimmed_audio,
            bg_color="#10A560",
            fg_color="#FFFFFF",
            width=120,
            height=50,
            corner_radius=20,
        )
        self.play_btn_trimmed.grid(row=2, column=3, padx=5)

        self.duration_text_trimmed = tk.StringVar(
            value="Trimmed | Duration: 0.0 seconds"
        )
        ttk.Label(recording_frame, textvariable=self.duration_text_trimmed).grid(
            row=3, column=2, sticky=tk.W, padx=5
        )

        # Record Button
        self.record_btn = RoundedButton(
            recording_frame,
            text="REC",
            command=self.toggle_recording,
            bg_color="#000000",
            fg_color="#FFFFFF",
            width=120,
            height=40,
            corner_radius=20,
            dot=True,
        )
        self.record_btn.grid(row=4, column=3, padx=5)

        # Spacer
        ttk.Frame(main_frame).grid(row=3, column=0, sticky="nsew")

        # Button frame with separator
        ttk.Separator(main_frame, orient="horizontal").grid(
            row=3, column=0, columnspan=2, sticky="ew", pady=(0, 15)
        )

        # Controls
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=4, column=0, sticky="we", pady=(0, 0))
        control_frame.columnconfigure(0, weight=1)

        # Total duration
        self.duration_text = tk.StringVar(value="Total Duration: 0s")
        ttk.Label(control_frame, textvariable=self.duration_text).grid(
            row=0, column=0, sticky=tk.W, padx=5
        )

        # Previous button
        self.previous_btn = RoundedButton(
            control_frame,
            text="Previous",
            command=self.previous_sample,
            bg_color="#E6E6E6",
            fg_color="#363636",
            width=120,
            height=40,
            corner_radius=20,
            dot=False,
            enabled=False,
        )
        self.previous_btn.grid(row=0, column=1, padx=5, sticky="e")

        # Skip button
        self.skip_btn = RoundedButton(
            control_frame,
            text="Skip",
            command=self.skip,
            bg_color="#E6E6E6",
            fg_color="#363636",
            width=120,
            height=40,
            corner_radius=20,
            dot=False,
        )
        self.skip_btn.grid(row=0, column=2, padx=5, sticky="e")

        # Thumb buttons
        self.thumb_down_btn = RoundedButton(
            control_frame,
            text="Thumb Down",
            command=lambda: self.set_rating("down"),
            bg_color="#E6E6E6",
            fg_color="#363636",
            width=120,
            height=40,
            corner_radius=20,
            dot=False,
        )
        self.thumb_down_btn.grid(row=0, column=3, padx=5, sticky="e")

        self.thumb_up_btn = RoundedButton(
            control_frame,
            text="Thumb Up",
            command=lambda: self.set_rating("up"),
            bg_color="#E6E6E6",
            fg_color="#363636",
            width=120,
            height=40,
            corner_radius=20,
            dot=False,
        )
        self.thumb_up_btn.grid(row=0, column=4, padx=5, sticky="e")

        # Next button at the bottom
        self.save_btn = RoundedButton(
            control_frame,
            text="Save & Next",
            command=self.save,
            bg_color="#3B32B3",
            fg_color="#F5F5F5",
            width=120,
            height=40,
            corner_radius=20,
            dot=False,
        )
        self.save_btn.grid(row=0, column=5, padx=5, sticky="e")

        self.update_skip_button_state()
        self.update_rating_buttons()
        self.update_previous_button_state()

    def show_settings(self) -> None:
        self.recorder.load_settings(self.settings_path)
        dialog = SettingsDialog(self.root, self.recorder)
        result = dialog.show()

        if result:
            # Apply settings
            self.recorder.update_output_folder(result["output_folder"])
            self.recorder.update_selected_device(result["device"])
            self.recorder.speaker_id = result["speaker_id"]
            self.recorder.speaker_dialect = result["speaker_dialect"]
            self.recorder.skip_enabled = bool(result["skip_enabled"])
            self.recorder.input_file = result["input_file"]
            self.recorder.output_file = (
                Path(result["output_folder"]) / result["speaker_id"] / "output.json"
            )
            self.recorder.skipped_file = (
                Path(result["output_folder"]) / result["speaker_id"] / "skipped.txt"
            )

            self.current_id = None
            self.previous_ids = []
            self.current_rating = None

            self.recorder.save_settings(self.settings_path)
            self.recorder.load_data()

            if not self.recorder.input_data:
                messagebox.showwarning(
                    "No Input Data",
                    "No samples loaded. Please verify your JSON file and selected dialect in Settings.",
                    parent=self.root,
                )

        self.start_monitoring()
        self.load_next_sample()

        self.update_duration()
        self.update_skip_button_state()
        self.update_previous_button_state()

    def set_empty_sample_state(self, message: str = "") -> None:
        self.de_text_var.set(message)
        self.ch_text_var.set("")
        self.ch_text_edit_var.set("")
        self.current_rating = None
        self.update_rating_buttons()
        self.update_skip_button_state()
        self.update_previous_button_state()

    def update_skip_button_state(self) -> None:
        feature_enabled = bool(self.recorder.skip_enabled)
        button_enabled = bool(feature_enabled and self.current_id)
        button_text = "Skip" if feature_enabled else "Skip Off"
        self.skip_btn.config(text=button_text, enabled=button_enabled)

    def update_previous_button_state(self) -> None:
        self.previous_btn.config(enabled=bool(self.previous_ids))
        self.save_btn.config(enabled=bool(self.current_id))

    def set_rating(self, rating: str) -> None:
        if rating not in {"up", "down"}:
            self.current_rating = None
        elif self.current_rating == rating:
            self.current_rating = None
        else:
            self.current_rating = rating

        self.update_rating_buttons()

    def update_rating_buttons(self) -> None:
        has_current = bool(self.current_id)
        is_up = self.current_rating == "up"
        is_down = self.current_rating == "down"

        self.thumb_up_btn.config(
            enabled=has_current,
            bg_color="#1E8E3E" if is_up else "#E6E6E6",
            fg_color="#FFFFFF" if is_up else "#363636",
        )
        self.thumb_down_btn.config(
            enabled=has_current,
            bg_color="#B3261E" if is_down else "#E6E6E6",
            fg_color="#FFFFFF" if is_down else "#363636",
        )

    def load_sample_by_id(self, sample_id: str) -> bool:
        sample = self.recorder.get_sample_by_id(sample_id)

        if not sample:
            self.current_id = None
            self.set_empty_sample_state(f"Sample {sample_id} could not be loaded.")
            return False

        text_de = str(sample.get("de", ""))
        if "ch" in sample:
            text_ch = str(sample.get("ch", ""))
        else:
            text_ch = str(sample.get(f"ch_{self.recorder.speaker_dialect.lower()}", ""))

        if not text_de and not text_ch:
            self.current_id = None
            self.set_empty_sample_state(
                f"Sample {sample_id} has no text fields for DE/CH."
            )
            return False

        self.current_id = sample_id
        self.de_text_var.set(text_de)
        self.ch_text_var.set(text_ch)
        self.ch_text_edit_var.set(text_ch)

        rating = sample.get("rating")
        self.current_rating = rating if rating in {"up", "down"} else None
        self.update_rating_buttons()
        self.update_skip_button_state()
        self.update_previous_button_state()
        return True

    def update_duration(self) -> None:
        total_seconds = self.recorder.total_duration
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        milliseconds = int((total_seconds - int(total_seconds)) * 100)

        self.duration_text.set(
            f"Total Duration: {hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:02d}"
        )

    def update_level_meter(self) -> None:
        level = self.recorder.get_current_level()

        # Update level text
        self.level_text.set(f"Level: {level:.1f} dB")

        # Get canvas dimensions
        width = self.level_canvas.winfo_width()
        height = self.level_canvas.winfo_height()

        if height > 1:  # Only draw if canvas is visible
            # Clear canvas
            self.level_canvas.delete("all")

            # Convert dB to normalized value (0-1)
            db_min = -60
            db_max = 0
            normalized = max(0, min(1, (level - db_min) / (db_max - db_min)))

            # Number of segments
            num_segments = 20
            segment_height = height / num_segments
            segment_spacing = 2  # Pixels between segments

            # Draw segments from bottom to top
            for i in range(num_segments):
                segment_normalized = i / num_segments
                segment_y = height - (i + 1) * segment_height

                # Determine if segment should be lit
                is_lit = normalized >= segment_normalized

                # Determine color based on position
                if i >= int(num_segments * 0.9):  # Top 10% red
                    color = "red" if is_lit else "darkred"
                elif i >= int(num_segments * 0.7):  # Next 20% yellow
                    color = "yellow" if is_lit else "darkgoldenrod4"
                else:  # Bottom 70% green
                    color = "green2" if is_lit else "darkgreen"

                # Draw segment
                self.level_canvas.create_rectangle(
                    2,  # Left margin
                    segment_y + segment_spacing / 2,
                    width - 2,  # Right margin
                    segment_y + segment_height - segment_spacing / 2,
                    fill=color,
                    outline="",
                )

            # Draw tick marks and dB labels every 10 dB
            for i in range(0, 7):
                db_value = db_min + (i * 10)
                y_pos = height * (1 - (db_value - db_min) / (db_max - db_min))
                # Tick mark
                self.level_canvas.create_line(0, y_pos, 5, y_pos, fill="gray", width=1)
                # dB label
                self.level_canvas.create_text(
                    width + 15,
                    y_pos,
                    text=f"{db_value}",
                    fill="white",
                    anchor="w",
                    font=("Arial", 7),
                )

        # Schedule next update
        self.root.after(50, self.update_level_meter)

    def start_monitoring(self) -> None:
        if self.recorder.selected_device:
            self.recorder.start_monitoring()
            self.update_level_meter()

    def toggle_recording(self) -> None:
        if not self.recorder.recording:
            started = self.recorder.start_recording()
            if not started:
                messagebox.showerror(
                    "Recording Error",
                    self.recorder.last_error
                    or "Unable to start recording with the selected input device.",
                    parent=self.root,
                )
                return
            self.clear_waveform_canvas()
            self.record_btn.config(
                text="Stop Recording", bg_color="#8B0000", dot=False
            )  # Dark red
        else:
            self.recorder.stop_recording()
            self.record_btn.config(text="REC", bg_color="#000000", dot=True)  # Black
            self.update_waveform()

    def clear_waveform_canvas(self) -> None:
        self.waveform_canvas_full.delete("all")
        self.waveform_canvas_trimmed.delete("all")

        self.waveform_canvas_full.draw_canvas()
        self.waveform_canvas_trimmed.draw_canvas()

    def load_next_sample(self) -> None:
        if self.current_id:
            self.previous_ids.append(self.current_id)

        next_id = self.recorder.get_next_id()
        if next_id is None:
            self.current_id = None
            self.set_empty_sample_state(
                "No open samples available. Please check your input file and settings."
            )
            self.update_previous_button_state()
            self.update_skip_button_state()
            return

        self.load_sample_by_id(next_id)
        self.update_previous_button_state()

    def previous_sample(self) -> None:
        if not self.previous_ids:
            return

        current_id = self.current_id
        if (
            current_id
            and current_id not in self.recorder.output_index
            and current_id not in self.recorder.skipped_ids
        ):
            self.recorder.prepend_open_id(current_id)

        previous_id = self.previous_ids.pop()
        self.recorder.open_ids = [
            open_id for open_id in self.recorder.open_ids if open_id != previous_id
        ]
        self.load_sample_by_id(previous_id)
        self.update_previous_button_state()
        self.update_skip_button_state()

    def update_waveform(self) -> None:
        if self.recorder.full_audio is None or self.recorder.trimmed_audio is None:
            return

        # Update duration text
        duration_full = self.recorder.get_duration_full_audio()
        self.duration_text_full.set(f"Full | Duration: {duration_full:.1f} seconds")

        duration_trimmed = self.recorder.get_duration_trimmed_audio()
        self.duration_text_trimmed.set(
            f"Trimmed | Duration: {duration_trimmed:.1f} seconds"
        )

        # Get waveform data
        waveform_full = self.recorder.get_waveform_full_audio()
        waveform_trimmed = self.recorder.get_waveform_trimmed_audio()

        # Get canvas dimensions
        width = self.waveform_canvas_full.winfo_width()
        height = self.waveform_canvas_full.winfo_height()
        center_y = height // 2

        # Clear canvas
        self.clear_waveform_canvas()

        # Draw vertical bars (full)
        bar_width = max(1, width // len(waveform_full) // 2)
        for i, value in enumerate(waveform_full):
            x = int((i / len(waveform_full)) * width)
            # Scale the value to half the height (since we're drawing from center)
            bar_height = int(value * (height / 2))
            # Draw vertical bar centered at center_y
            if bar_height != 0:  # Only draw if there's a visible amplitude
                self.waveform_canvas_full.create_line(
                    x,
                    center_y - bar_height,
                    x,
                    center_y + bar_height,
                    fill="orange red",
                    width=bar_width,
                    capstyle=tk.ROUND,
                    joinstyle=tk.ROUND,
                )

        # Draw vertical bars (trimmed)
        bar_width = max(1, width // len(waveform_trimmed) // 2)
        for i, value in enumerate(waveform_trimmed):
            x = int((i / len(waveform_trimmed)) * width)
            # Scale the value to half the height (since we're drawing from center)
            bar_height = int(value * (height / 2))
            # Draw vertical bar centered at center_y
            if bar_height != 0:  # Only draw if there's a visible amplitude
                self.waveform_canvas_trimmed.create_line(
                    x,
                    center_y - bar_height,
                    x,
                    center_y + bar_height,
                    fill="orange red",
                    width=bar_width,
                    capstyle=tk.ROUND,
                    joinstyle=tk.ROUND,
                )

    def configure_handler(self, event):
        self.update_waveform()

    def save(self) -> None:
        if not getattr(self, "current_id", None):
            return

        if self.recorder.trimmed_audio is None:
            return

        duration_s = self.recorder.save_audio(self.current_id)
        self.recorder.add_sample(
            id=self.current_id,
            text_de=self.de_text_var.get(),
            text_ch=self.ch_text_edit_var.get(),
            dialect=self.recorder.speaker_dialect,
            audio_path=f"{self.current_id}.flac",
            duration_s=duration_s,
            rating=self.current_rating,
        )

        self.recorder.audio_data = []
        self.recorder.full_audio = None
        self.recorder.trimmed_audio = None

        self.clear_waveform_canvas()

        self.update_duration()
        self.load_next_sample()

    def skip(self):
        if not getattr(self, "current_id", None):
            return

        if not self.recorder.skip_enabled:
            return

        self.recorder.add_skip(self.current_id)
        self.load_next_sample()

    def on_closing(self) -> None:
        self.recorder.stop_monitoring()
        if self.recorder.recording:
            self.recorder.stop_recording()
        self.root.destroy()
