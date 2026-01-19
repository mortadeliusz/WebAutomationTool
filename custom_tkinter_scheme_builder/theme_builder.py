# theme_builder.py

import customtkinter as ctk
from tkinter import colorchooser, filedialog, messagebox
import json
from typing import Dict, Any

class ColorPickerFrame(ctk.CTkFrame):
    """Frame with color input field and clickable color preview"""
    def __init__(self, parent, label: str, initial_color: str, callback):
        super().__init__(parent)
        self.callback = callback
        self.current_color = initial_color
        
        self.grid_columnconfigure(1, weight=1)
        
        # Label
        if label:
            ctk.CTkLabel(self, text=label, width=120, anchor="w").grid(
                row=0, column=0, padx=5, pady=5, sticky="w"
            )
        
        # Color entry
        self.color_entry = ctk.CTkEntry(self, width=80)
        self.color_entry.insert(0, initial_color)
        self.color_entry.bind("<Return>", self.on_entry_change)
        self.color_entry.bind("<FocusOut>", self.on_entry_change)
        self.color_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Clickable color preview (replaces Pick button)
        self.preview = ctk.CTkButton(
            self, text="", width=40, height=28, fg_color=initial_color,
            hover_color=initial_color, corner_radius=6,
            command=self.pick_color
        )
        self.preview.grid(row=0, column=2, padx=5, pady=5)
    
    def pick_color(self):
        color = colorchooser.askcolor(initialcolor=self.current_color, title=f"Choose Color")
        if color[1]:
            self.set_color(color[1])
    
    def on_entry_change(self, event=None):
        color = self.color_entry.get().strip()
        if color:
            self.set_color(color)
    
    def set_color(self, color: str):
        try:
            self.current_color = color
            self.color_entry.delete(0, "end")
            self.color_entry.insert(0, color)
            self.preview.configure(fg_color=color, hover_color=color)
            self.callback(color)
        except:
            pass
    
    def get_color(self) -> str:
        return self.current_color


class DualColorPickerFrame(ctk.CTkFrame):
    """Frame with Light and Dark mode color pickers side by side"""
    def __init__(self, parent, label: str, light_color: str, dark_color: str, light_callback, dark_callback):
        super().__init__(parent)
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        
        # Label
        ctk.CTkLabel(self, text=label, width=200, anchor="w").grid(
            row=0, column=0, padx=5, pady=5, sticky="w"
        )
        
        # Light mode picker
        light_frame = ctk.CTkFrame(self, fg_color="transparent")
        light_frame.grid(row=0, column=1, padx=2, pady=5, sticky="ew")
        light_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(light_frame, text="☀️", width=20).grid(row=0, column=0, padx=2)
        self.light_entry = ctk.CTkEntry(light_frame, width=70)
        self.light_entry.insert(0, light_color)
        self.light_entry.bind("<Return>", lambda e: self.on_light_change())
        self.light_entry.bind("<FocusOut>", lambda e: self.on_light_change())
        self.light_entry.grid(row=0, column=1, padx=2, sticky="ew")
        
        self.light_preview = ctk.CTkButton(
            light_frame, text="", width=35, height=28, fg_color=light_color,
            hover_color=light_color, corner_radius=6, command=self.pick_light
        )
        self.light_preview.grid(row=0, column=2, padx=2)
        
        # Dark mode picker
        dark_frame = ctk.CTkFrame(self, fg_color="transparent")
        dark_frame.grid(row=0, column=2, padx=2, pady=5, sticky="ew")
        dark_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(dark_frame, text="🌙", width=20).grid(row=0, column=0, padx=2)
        self.dark_entry = ctk.CTkEntry(dark_frame, width=70)
        self.dark_entry.insert(0, dark_color)
        self.dark_entry.bind("<Return>", lambda e: self.on_dark_change())
        self.dark_entry.bind("<FocusOut>", lambda e: self.on_dark_change())
        self.dark_entry.grid(row=0, column=1, padx=2, sticky="ew")
        
        self.dark_preview = ctk.CTkButton(
            dark_frame, text="", width=35, height=28, fg_color=dark_color,
            hover_color=dark_color, corner_radius=6, command=self.pick_dark
        )
        self.dark_preview.grid(row=0, column=2, padx=2)
        
        self.light_callback = light_callback
        self.dark_callback = dark_callback
        self.light_color = light_color
        self.dark_color = dark_color
    
    def pick_light(self):
        color = colorchooser.askcolor(initialcolor=self.light_color, title="Choose Light Mode Color")
        if color[1]:
            self.set_light_color(color[1])
    
    def pick_dark(self):
        color = colorchooser.askcolor(initialcolor=self.dark_color, title="Choose Dark Mode Color")
        if color[1]:
            self.set_dark_color(color[1])
    
    def on_light_change(self):
        color = self.light_entry.get().strip()
        if color:
            self.set_light_color(color)
    
    def on_dark_change(self):
        color = self.dark_entry.get().strip()
        if color:
            self.set_dark_color(color)
    
    def set_light_color(self, color: str):
        try:
            self.light_color = color
            self.light_entry.delete(0, "end")
            self.light_entry.insert(0, color)
            self.light_preview.configure(fg_color=color, hover_color=color)
            self.light_callback(color)
        except:
            pass
    
    def set_dark_color(self, color: str):
        try:
            self.dark_color = color
            self.dark_entry.delete(0, "end")
            self.dark_entry.insert(0, color)
            self.dark_preview.configure(fg_color=color, hover_color=color)
            self.dark_callback(color)
        except:
            pass
    
    def get_colors(self):
        return (self.light_color, self.dark_color)


class ThemeBuilder(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("CustomTkinter Theme Builder")
        self.geometry("1400x900")
        
        # Default dark-blue theme colors
        self.theme_colors = {
            "color": {
                "window_bg_color": ["#EBEBEC", "#212121"],
                "frame_low": ["gray92", "gray14"],
                "frame_high": ["gray86", "gray19"]
            },
            "CTkButton": {
                "fg_color": ["#3B8ED0", "#1F6AA5"],
                "hover_color": ["#36719F", "#144870"],
                "border_color": ["#3E454A", "#949A9F"],
                "text_color": ["#DCE4EE", "#DCE4EE"]
            },
            "CTkLabel": {
                "text_color": ["#DCE4EE", "#DCE4EE"]
            },
            "CTkEntry": {
                "fg_color": ["#F9F9FA", "#343638"],
                "border_color": ["#979DA2", "#565B5E"],
                "text_color": ["gray10", "#DCE4EE"],
                "placeholder_text_color": ["gray52", "gray62"]
            },
            "CTkCheckBox": {
                "fg_color": ["#3B8ED0", "#1F6AA5"],
                "border_color": ["#979DA2", "#565B5E"],
                "hover_color": ["#36719F", "#144870"],
                "checkmark_color": ["#DCE4EE", "gray90"],
                "text_color": ["gray10", "#DCE4EE"]
            },
            "CTkSwitch": {
                "fg_color": ["#939BA2", "#4A4D50"],
                "progress_color": ["#3B8ED0", "#1F6AA5"],
                "button_color": ["gray36", "#D5D9DE"],
                "button_hover_color": ["gray20", "gray100"],
                "text_color": ["gray10", "#DCE4EE"]
            },
            "CTkRadioButton": {
                "fg_color": ["#3B8ED0", "#1F6AA5"],
                "border_color": ["#979DA2", "#565B5E"],
                "hover_color": ["#36719F", "#144870"],
                "text_color": ["gray10", "#DCE4EE"]
            },
            "CTkProgressBar": {
                "fg_color": ["#939BA2", "#4A4D50"],
                "progress_color": ["#3B8ED0", "#1F6AA5"],
                "border_color": ["gray", "gray"]
            },
            "CTkSlider": {
                "fg_color": ["#939BA2", "#4A4D50"],
                "progress_color": ["#3B8ED0", "#1F6AA5"],
                "button_color": ["#3B8ED0", "#1F6AA5"],
                "button_hover_color": ["#36719F", "#144870"]
            },
            "CTkScrollbar": {
                "fg_color": ["gray80", "gray20"],
                "button_color": ["gray55", "gray41"],
                "button_hover_color": ["gray40", "gray53"]
            },
            "CTkSegmentedButton": {
                "fg_color": ["#979DA2", "#565B5E"],
                "selected_color": ["#3B8ED0", "#1F6AA5"],
                "selected_hover_color": ["#36719F", "#144870"],
                "unselected_color": ["#979DA2", "#565B5E"],
                "unselected_hover_color": ["gray70", "gray41"],
                "text_color": ["#DCE4EE", "#DCE4EE"],
                "text_color_disabled": ["gray74", "gray60"]
            },
            "CTkTextbox": {
                "fg_color": ["#F9F9FA", "#343638"],
                "border_color": ["#979DA2", "#565B5E"],
                "text_color": ["gray10", "#DCE4EE"],
                "scrollbar_button_color": ["gray55", "gray41"],
                "scrollbar_button_hover_color": ["gray40", "gray53"]
            },
            "CTkScrollableFrame": {
                "label_fg_color": ["gray78", "gray23"]
            },
            "CTkFrame": {
                "fg_color": ["gray90", "gray13"],
                "border_color": ["gray65", "gray28"]
            },
            "CTkComboBox": {
                "fg_color": ["#F9F9FA", "#343638"],
                "border_color": ["#979DA2", "#565B5E"],
                "button_color": ["#979DA2", "#565B5E"],
                "button_hover_color": ["#6E7174", "#7A848D"],
                "text_color": ["gray10", "#DCE4EE"]
            },
            "CTkOptionMenu": {
                "fg_color": ["#3B8ED0", "#1F6AA5"],
                "button_color": ["#36719F", "#144870"],
                "button_hover_color": ["#325882", "#0C3A5E"],
                "text_color": ["#DCE4EE", "#DCE4EE"]
            },
            "CTkTabview": {
                "fg_color": ["gray90", "gray13"],
                "border_color": ["gray65", "gray28"],
                "segmented_button_fg_color": ["gray80", "gray20"],
                "segmented_button_selected_color": ["gray70", "gray30"],
                "segmented_button_selected_hover_color": ["gray65", "gray35"],
                "segmented_button_unselected_color": ["gray80", "gray20"],
                "segmented_button_unselected_hover_color": ["gray75", "gray25"],
                "text_color": ["gray10", "#DCE4EE"],
                "text_color_disabled": ["gray60", "gray45"]
            }
        }
        
        self.setup_ui()
    
    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Left panel - Color controls
        left_panel = ctk.CTkScrollableFrame(self, width=650)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        left_panel.grid_columnconfigure(0, weight=1)
        
        # Title
        ctk.CTkLabel(
            left_panel, text="Theme Color Editor", 
            font=ctk.CTkFont(size=20, weight="bold")
        ).grid(row=0, column=0, pady=10)
        
        # Quick Theme Generator Section
        quick_frame = ctk.CTkFrame(left_panel, fg_color=("gray85", "gray15"))
        quick_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        quick_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            quick_frame, text="⚡ Quick Theme Generator",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, pady=(10, 5), padx=10, sticky="w")
        
        # Master color pickers - two columns
        quick_frame.grid_columnconfigure(0, weight=1)
        quick_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(quick_frame, text="Light Mode", font=ctk.CTkFont(weight="bold")).grid(
            row=1, column=0, padx=5, pady=2
        )
        ctk.CTkLabel(quick_frame, text="Dark Mode", font=ctk.CTkFont(weight="bold")).grid(
            row=1, column=1, padx=5, pady=2
        )
        
        # Primary color
        ctk.CTkLabel(quick_frame, text="Primary:", anchor="w").grid(row=2, column=0, columnspan=2, padx=10, pady=(5,2), sticky="w")
        self.master_primary_light = ColorPickerFrame(
            quick_frame, "", "#3B8ED0", lambda c: None
        )
        self.master_primary_light.grid(row=3, column=0, sticky="ew", padx=5, pady=2)
        self.master_primary_dark = ColorPickerFrame(
            quick_frame, "", "#1F6AA5", lambda c: None
        )
        self.master_primary_dark.grid(row=3, column=1, sticky="ew", padx=5, pady=2)
        
        # Background color
        ctk.CTkLabel(quick_frame, text="Background:", anchor="w").grid(row=4, column=0, columnspan=2, padx=10, pady=(5,2), sticky="w")
        self.master_background_light = ColorPickerFrame(
            quick_frame, "", "#EBEBEC", lambda c: None
        )
        self.master_background_light.grid(row=5, column=0, sticky="ew", padx=5, pady=2)
        self.master_background_dark = ColorPickerFrame(
            quick_frame, "", "#2B2B2B", lambda c: None
        )
        self.master_background_dark.grid(row=5, column=1, sticky="ew", padx=5, pady=2)
        
        # Text color
        ctk.CTkLabel(quick_frame, text="Text:", anchor="w").grid(row=6, column=0, columnspan=2, padx=10, pady=(5,2), sticky="w")
        self.master_text_light = ColorPickerFrame(
            quick_frame, "", "#000000", lambda c: None
        )
        self.master_text_light.grid(row=7, column=0, sticky="ew", padx=5, pady=2)
        self.master_text_dark = ColorPickerFrame(
            quick_frame, "", "#DCE4EE", lambda c: None
        )
        self.master_text_dark.grid(row=7, column=1, sticky="ew", padx=5, pady=2)
        
        ctk.CTkButton(
            quick_frame, text="Generate Theme",
            command=self.generate_theme_from_master,
            height=35
        ).grid(row=8, column=0, columnspan=2, pady=10, padx=10, sticky="ew")
        
        # Font note
        ctk.CTkLabel(
            quick_frame,
            text="ℹ️ Fonts: Use ctk.set_default_font() in your app code",
            font=ctk.CTkFont(size=9),
            text_color="gray"
        ).grid(row=9, column=0, columnspan=2, padx=10, pady=(0,5))
        
        # Separator
        ctk.CTkLabel(
            left_panel, text="Manual Color Overrides:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=2, column=0, pady=(15, 5), padx=10, sticky="w")
        
        # Info note
        info_label = ctk.CTkLabel(
            left_panel, 
            text="ℹ️ Note: 'color' section (window/frame backgrounds) only applies when\nloading theme at app startup with set_default_color_theme()",
            font=ctk.CTkFont(size=10),
            text_color="gray",
            justify="left"
        )
        info_label.grid(row=3, column=0, pady=(0, 10), padx=10, sticky="w")
        
        # Create color pickers for each widget type
        self.color_pickers = {}
        row = 4
        
        for widget_name, colors in self.theme_colors.items():
            # Widget section header
            ctk.CTkLabel(
                left_panel, text=widget_name,
                font=ctk.CTkFont(size=14, weight="bold")
            ).grid(row=row, column=0, sticky="w", padx=10, pady=(15, 5))
            row += 1
            
            self.color_pickers[widget_name] = {}
            
            for color_key, color_value in colors.items():
                if isinstance(color_value, list):
                    # Dual picker (Light and Dark side by side)
                    dual_picker = DualColorPickerFrame(
                        left_panel,
                        f"  {color_key}:",
                        color_value[0],
                        color_value[1],
                        lambda c, w=widget_name, k=color_key: self.on_color_change(w, k, c, 0),
                        lambda c, w=widget_name, k=color_key: self.on_color_change(w, k, c, 1)
                    )
                    dual_picker.grid(row=row, column=0, sticky="ew", padx=10, pady=2)
                    self.color_pickers[widget_name][color_key] = dual_picker
                    row += 1
                else:
                    # Single color (no light/dark variants)
                    picker = ColorPickerFrame(
                        left_panel,
                        f"  {color_key}:",
                        color_value,
                        lambda c, w=widget_name, k=color_key: self.on_color_change(w, k, c, 0)
                    )
                    picker.grid(row=row, column=0, sticky="ew", padx=10, pady=2)
                    self.color_pickers[widget_name][color_key] = picker
                    row += 1
        
        # Right panel - Widget preview
        right_panel = ctk.CTkScrollableFrame(self)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        right_panel.grid_columnconfigure(0, weight=1)
        
        # Preview title
        ctk.CTkLabel(
            right_panel, text="Widget Preview",
            font=ctk.CTkFont(size=20, weight="bold")
        ).grid(row=0, column=0, pady=10)
        
        # Create preview widgets
        self.preview_widgets = {}
        self.create_preview_widgets(right_panel)
        
        # Bottom panel - Actions
        bottom_panel = ctk.CTkFrame(self)
        bottom_panel.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))
        
        ctk.CTkButton(
            bottom_panel, text="Save Theme JSON",
            command=self.save_theme, height=40
        ).pack(side="left", padx=10, pady=10)
        
        ctk.CTkButton(
            bottom_panel, text="Load Theme JSON",
            command=self.load_theme, height=40
        ).pack(side="left", padx=10, pady=10)
        
        ctk.CTkButton(
            bottom_panel, text="Reset to Default",
            command=self.reset_theme, height=40
        ).pack(side="left", padx=10, pady=10)
        
        # Dark/Light mode toggle
        self.theme_switch = ctk.CTkSwitch(
            bottom_panel,
            text="Dark Mode",
            command=self.toggle_appearance_mode
        )
        self.theme_switch.pack(side="right", padx=10, pady=10)
        self.theme_switch.select()  # Start in dark mode
    
    def create_preview_widgets(self, parent):
        row = 1
        
        # Buttons
        frame = ctk.CTkFrame(parent)
        frame.grid(row=row, column=0, sticky="ew", padx=10, pady=5)
        ctk.CTkLabel(frame, text="Buttons:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
        btn1 = ctk.CTkButton(frame, text="Normal Button")
        btn1.pack(padx=10, pady=5)
        btn2 = ctk.CTkButton(frame, text="Hover Me", state="normal")
        btn2.pack(padx=10, pady=5)
        self.preview_widgets["CTkButton"] = [btn1, btn2]
        row += 1
        
        # Entry
        frame = ctk.CTkFrame(parent)
        frame.grid(row=row, column=0, sticky="ew", padx=10, pady=5)
        ctk.CTkLabel(frame, text="Entry:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
        entry = ctk.CTkEntry(frame, placeholder_text="Enter text here...")
        entry.pack(padx=10, pady=5, fill="x")
        self.preview_widgets["CTkEntry"] = [entry]
        row += 1
        
        # CheckBox
        frame = ctk.CTkFrame(parent)
        frame.grid(row=row, column=0, sticky="ew", padx=10, pady=5)
        ctk.CTkLabel(frame, text="CheckBox:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
        cb1 = ctk.CTkCheckBox(frame, text="Option 1")
        cb1.pack(padx=10, pady=5, anchor="w")
        cb2 = ctk.CTkCheckBox(frame, text="Option 2 (checked)")
        cb2.select()
        cb2.pack(padx=10, pady=5, anchor="w")
        self.preview_widgets["CTkCheckBox"] = [cb1, cb2]
        row += 1
        
        # Switch
        frame = ctk.CTkFrame(parent)
        frame.grid(row=row, column=0, sticky="ew", padx=10, pady=5)
        ctk.CTkLabel(frame, text="Switch:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
        sw1 = ctk.CTkSwitch(frame, text="Toggle Off")
        sw1.pack(padx=10, pady=5, anchor="w")
        sw2 = ctk.CTkSwitch(frame, text="Toggle On")
        sw2.select()
        sw2.pack(padx=10, pady=5, anchor="w")
        self.preview_widgets["CTkSwitch"] = [sw1, sw2]
        row += 1
        
        # RadioButton
        frame = ctk.CTkFrame(parent)
        frame.grid(row=row, column=0, sticky="ew", padx=10, pady=5)
        ctk.CTkLabel(frame, text="RadioButton:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
        rb1 = ctk.CTkRadioButton(frame, text="Choice 1")
        rb1.pack(padx=10, pady=5, anchor="w")
        rb2 = ctk.CTkRadioButton(frame, text="Choice 2")
        rb2.pack(padx=10, pady=5, anchor="w")
        self.preview_widgets["CTkRadioButton"] = [rb1, rb2]
        row += 1
        
        # ProgressBar
        frame = ctk.CTkFrame(parent)
        frame.grid(row=row, column=0, sticky="ew", padx=10, pady=5)
        ctk.CTkLabel(frame, text="ProgressBar:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
        pb = ctk.CTkProgressBar(frame)
        pb.set(0.7)
        pb.pack(padx=10, pady=5, fill="x")
        self.preview_widgets["CTkProgressBar"] = [pb]
        row += 1
        
        # Slider
        frame = ctk.CTkFrame(parent)
        frame.grid(row=row, column=0, sticky="ew", padx=10, pady=5)
        ctk.CTkLabel(frame, text="Slider:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
        slider = ctk.CTkSlider(frame)
        slider.set(0.5)
        slider.pack(padx=10, pady=5, fill="x")
        self.preview_widgets["CTkSlider"] = [slider]
        row += 1
        
        # ComboBox
        frame = ctk.CTkFrame(parent)
        frame.grid(row=row, column=0, sticky="ew", padx=10, pady=5)
        ctk.CTkLabel(frame, text="ComboBox:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
        combo = ctk.CTkComboBox(frame, values=["Option 1", "Option 2", "Option 3"])
        combo.pack(padx=10, pady=5, fill="x")
        self.preview_widgets["CTkComboBox"] = [combo]
        row += 1
        
        # OptionMenu
        frame = ctk.CTkFrame(parent)
        frame.grid(row=row, column=0, sticky="ew", padx=10, pady=5)
        ctk.CTkLabel(frame, text="OptionMenu:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
        option = ctk.CTkOptionMenu(frame, values=["Choice A", "Choice B", "Choice C"])
        option.pack(padx=10, pady=5, fill="x")
        self.preview_widgets["CTkOptionMenu"] = [option]
        row += 1
        
        # Textbox
        frame = ctk.CTkFrame(parent)
        frame.grid(row=row, column=0, sticky="ew", padx=10, pady=5)
        ctk.CTkLabel(frame, text="Textbox:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
        textbox = ctk.CTkTextbox(frame, height=80)
        textbox.insert("1.0", "This is a textbox widget.\nYou can type multiple lines here.")
        textbox.pack(padx=10, pady=5, fill="both")
        self.preview_widgets["CTkTextbox"] = [textbox]
        row += 1
        
        # SegmentedButton
        frame = ctk.CTkFrame(parent)
        frame.grid(row=row, column=0, sticky="ew", padx=10, pady=5)
        ctk.CTkLabel(frame, text="SegmentedButton:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
        seg = ctk.CTkSegmentedButton(frame, values=["Tab 1", "Tab 2", "Tab 3"])
        seg.set("Tab 1")
        seg.pack(padx=10, pady=5, fill="x")
        self.preview_widgets["CTkSegmentedButton"] = [seg]
        row += 1
    
    def on_color_change(self, widget_name: str, color_key: str, color: str, mode_index: int = 1):
        """Update theme color and refresh preview widgets"""
        # Update theme data
        if isinstance(self.theme_colors[widget_name][color_key], list):
            self.theme_colors[widget_name][color_key][mode_index] = color
        else:
            self.theme_colors[widget_name][color_key] = color
        
        # Update preview widgets (only for non-color section)
        if widget_name != "color" and widget_name in self.preview_widgets:
            for widget in self.preview_widgets[widget_name]:
                try:
                    widget.configure(**{color_key: color})
                except:
                    pass
        
        # Try to update main window background if it's window_bg_color
        if widget_name == "color" and color_key == "window_bg_color":
            try:
                self.configure(fg_color=color)
            except:
                pass
    
    def save_theme(self):
        """Export theme as JSON file"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save Theme"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(self.theme_colors, f, indent=2)
                messagebox.showinfo("Success", f"Theme saved to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save theme:\n{str(e)}")
    
    def load_theme(self):
        """Load theme from JSON file"""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Load Theme"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    loaded_theme = json.load(f)
                
                # Update theme colors
                self.theme_colors.update(loaded_theme)
                
                # Update all color pickers
                for widget_name, colors in loaded_theme.items():
                    if widget_name in self.color_pickers:
                        for color_key, color_value in colors.items():
                            if color_key in self.color_pickers[widget_name]:
                                picker = self.color_pickers[widget_name][color_key]
                                if isinstance(color_value, list) and hasattr(picker, 'set_light_color'):
                                    # DualColorPickerFrame
                                    picker.set_light_color(color_value[0])
                                    picker.set_dark_color(color_value[1])
                                else:
                                    # Single ColorPickerFrame
                                    color = color_value if not isinstance(color_value, list) else color_value[0]
                                    picker.set_color(color)
                
                messagebox.showinfo("Success", "Theme loaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load theme:\n{str(e)}")
    
    def rgb_to_hls(self, r: int, g: int, b: int):
        """Convert RGB to HLS"""
        r, g, b = r/255.0, g/255.0, b/255.0
        max_c = max(r, g, b)
        min_c = min(r, g, b)
        l = (max_c + min_c) / 2.0
        
        if max_c == min_c:
            h = s = 0.0
        else:
            diff = max_c - min_c
            s = diff / (2.0 - max_c - min_c) if l > 0.5 else diff / (max_c + min_c)
            
            if max_c == r:
                h = (g - b) / diff + (6.0 if g < b else 0.0)
            elif max_c == g:
                h = (b - r) / diff + 2.0
            else:
                h = (r - g) / diff + 4.0
            h /= 6.0
        
        return h, l, s
    
    def hls_to_rgb(self, h: float, l: float, s: float):
        """Convert HLS to RGB"""
        def hue_to_rgb(p, q, t):
            if t < 0: t += 1
            if t > 1: t -= 1
            if t < 1/6: return p + (q - p) * 6 * t
            if t < 1/2: return q
            if t < 2/3: return p + (q - p) * (2/3 - t) * 6
            return p
        
        if s == 0:
            r = g = b = l
        else:
            q = l * (1 + s) if l < 0.5 else l + s - l * s
            p = 2 * l - q
            r = hue_to_rgb(p, q, h + 1/3)
            g = hue_to_rgb(p, q, h)
            b = hue_to_rgb(p, q, h - 1/3)
        
        return int(r * 255), int(g * 255), int(b * 255)
    
    def adjust_color(self, hex_color: str, lightness_factor: float) -> str:
        """Adjust color lightness while preserving hue. factor > 1 lightens, < 1 darkens"""
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        
        h, l, s = self.rgb_to_hls(r, g, b)
        l = max(0.0, min(1.0, l * lightness_factor))
        
        r, g, b = self.hls_to_rgb(h, l, s)
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def generate_theme_from_master(self):
        """Generate all widget colors from master colors"""
        # Get master colors
        primary_light = self.master_primary_light.get_color()
        primary_dark = self.master_primary_dark.get_color()
        bg_light = self.master_background_light.get_color()
        bg_dark = self.master_background_dark.get_color()
        text_light = self.master_text_light.get_color()
        text_dark = self.master_text_dark.get_color()
        
        # Derive all color variations from the 3 master colors
        hover_light = self.adjust_color(primary_light, 0.85)
        hover_dark = self.adjust_color(primary_dark, 0.65)
        border_light = self.adjust_color(bg_light, 0.75)
        border_dark = self.adjust_color(bg_dark, 2.5)
        input_bg_light = self.adjust_color(bg_light, 0.97)
        input_bg_dark = self.adjust_color(bg_dark, 1.6)
        neutral_light = self.adjust_color(bg_light, 0.80)
        neutral_dark = self.adjust_color(bg_dark, 2.2)
        neutral_hover_light = self.adjust_color(neutral_light, 0.85)
        neutral_hover_dark = self.adjust_color(neutral_dark, 1.3)
        disabled_text_light = self.adjust_color(text_light, 1.8)
        disabled_text_dark = self.adjust_color(text_dark, 0.7)
        
        # Generate mappings for ALL widgets and ALL their attributes
        mappings = {}
        for widget_name, widget_colors in self.theme_colors.items():
            mappings[widget_name] = {}
            for color_key in widget_colors.keys():
                # Intelligently map each attribute based on its name
                if "text_color" in color_key:
                    if "disabled" in color_key:
                        mappings[widget_name][color_key] = [disabled_text_light, disabled_text_dark]
                    elif "placeholder" in color_key:
                        mappings[widget_name][color_key] = [disabled_text_light, disabled_text_dark]
                    else:
                        mappings[widget_name][color_key] = [text_light, text_dark]
                
                elif "window_bg" in color_key:
                    mappings[widget_name][color_key] = [bg_light, bg_dark]
                
                elif "frame_low" in color_key:
                    mappings[widget_name][color_key] = [self.adjust_color(bg_light, 0.98), self.adjust_color(bg_dark, 1.05)]
                
                elif "frame_high" in color_key:
                    mappings[widget_name][color_key] = [self.adjust_color(bg_light, 0.96), self.adjust_color(bg_dark, 1.1)]
                
                elif "fg_color" in color_key:
                    # Background colors for widgets
                    if "entry" in widget_name.lower() or "textbox" in widget_name.lower() or "combobox" in widget_name.lower():
                        mappings[widget_name][color_key] = [input_bg_light, input_bg_dark]
                    elif "button" in widget_name.lower() or "optionmenu" in widget_name.lower():
                        mappings[widget_name][color_key] = [primary_light, primary_dark]
                    elif "switch" in widget_name.lower() or "progressbar" in widget_name.lower() or "slider" in widget_name.lower() or "scrollbar" in widget_name.lower():
                        mappings[widget_name][color_key] = [neutral_light, neutral_dark]
                    elif "segmented" in widget_name.lower():
                        mappings[widget_name][color_key] = [neutral_light, neutral_dark]
                    else:
                        mappings[widget_name][color_key] = [bg_light, bg_dark]
                
                elif "border" in color_key:
                    mappings[widget_name][color_key] = [border_light, border_dark]
                
                elif "progress" in color_key or ("selected" in color_key and "unselected" not in color_key):
                    if "hover" in color_key:
                        mappings[widget_name][color_key] = [hover_light, hover_dark]
                    else:
                        mappings[widget_name][color_key] = [primary_light, primary_dark]
                
                elif "hover" in color_key:
                    if "unselected" in color_key or "button" in color_key:
                        mappings[widget_name][color_key] = [neutral_hover_light, neutral_hover_dark]
                    else:
                        mappings[widget_name][color_key] = [hover_light, hover_dark]
                
                elif "button" in color_key:
                    if "scrollbar" in color_key:
                        mappings[widget_name][color_key] = [neutral_light, neutral_dark]
                    else:
                        mappings[widget_name][color_key] = [hover_light, hover_dark]
                
                elif "unselected" in color_key or "checkmark" in color_key:
                    mappings[widget_name][color_key] = [neutral_light, neutral_dark]
                
                elif "label" in color_key:
                    mappings[widget_name][color_key] = [self.adjust_color(bg_light, 0.95), self.adjust_color(bg_dark, 1.08)]
                
                elif "segmented" in color_key:
                    if "selected" in color_key:
                        if "hover" in color_key:
                            mappings[widget_name][color_key] = [self.adjust_color(bg_light, 0.8), self.adjust_color(bg_dark, 1.2)]
                        else:
                            mappings[widget_name][color_key] = [self.adjust_color(bg_light, 0.85), self.adjust_color(bg_dark, 1.15)]
                    else:
                        if "hover" in color_key:
                            mappings[widget_name][color_key] = [self.adjust_color(bg_light, 0.88), self.adjust_color(bg_dark, 1.13)]
                        else:
                            mappings[widget_name][color_key] = [self.adjust_color(bg_light, 0.9), self.adjust_color(bg_dark, 1.1)]
                
                else:
                    # Default fallback - use neutral colors
                    mappings[widget_name][color_key] = [neutral_light, neutral_dark]
        
        # Update theme colors and color pickers
        for widget_name, colors in mappings.items():
            if widget_name in self.theme_colors:
                for color_key, color_value in colors.items():
                    if color_key in self.theme_colors[widget_name]:
                        # Update theme data
                        if isinstance(self.theme_colors[widget_name][color_key], list):
                            self.theme_colors[widget_name][color_key] = color_value
                        else:
                            self.theme_colors[widget_name][color_key] = color_value
                        
                        # Update color picker
                        if widget_name in self.color_pickers and color_key in self.color_pickers[widget_name]:
                            picker = self.color_pickers[widget_name][color_key]
                            if isinstance(color_value, list) and hasattr(picker, 'set_light_color'):
                                # DualColorPickerFrame
                                picker.set_light_color(color_value[0])
                                picker.set_dark_color(color_value[1])
                            else:
                                # Single ColorPickerFrame
                                picker.set_color(color_value)
        
        messagebox.showinfo("Success", "Theme generated! You can now fine-tune individual colors below.")
    
    def toggle_appearance_mode(self):
        """Toggle between dark and light appearance mode"""
        if self.theme_switch.get():
            ctk.set_appearance_mode("dark")
            self.theme_switch.configure(text="Dark Mode")
        else:
            ctk.set_appearance_mode("light")
            self.theme_switch.configure(text="Light Mode")
    
    def reset_theme(self):
        """Reset to default dark-blue theme"""
        if messagebox.askyesno("Confirm Reset", "Reset all colors to default dark-blue theme?"):
            # Just close and reopen the app
            messagebox.showinfo("Reset", "Please restart the application to reset to defaults.")


if __name__ == "__main__":
    app = ThemeBuilder()
    app.mainloop()
