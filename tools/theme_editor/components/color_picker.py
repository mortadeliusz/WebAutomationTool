import tkinter as tk
from tkinter import colorchooser
import customtkinter as ctk
from ..utils.color_utils import parse_color, hex_to_rgb, rgb_to_hex

class ColorSquare(ctk.CTkFrame):
    def __init__(self, parent, color, callback, **kwargs):
        super().__init__(parent, width=40, height=40, **kwargs)
        self.color = color
        self.callback = callback
        
        self.configure(fg_color=self._get_display_color())
        self.bind("<Button-1>", self._on_click)
        
        # Make frame clickable
        for child in self.winfo_children():
            child.bind("<Button-1>", self._on_click)
    
    def _get_display_color(self):
        """Convert color string to displayable color"""
        try:
            parsed = parse_color(self.color)
            if parsed == "#00000000":  # transparent
                return "gray80"
            return parsed
        except:
            return "gray80"
    
    def _on_click(self, event):
        """Handle color square click"""
        current_color = self._get_display_color()
        if current_color == "gray80":
            current_color = "#808080"
        
        # Convert to RGB for color chooser
        try:
            rgb = hex_to_rgb(current_color)
            # Pass RGB tuple directly (integers 0-255)
            color_tuple = rgb
        except:
            color_tuple = (128, 128, 128)
        
        # Open color chooser
        result = colorchooser.askcolor(color=color_tuple, title="Choose Color")
        if result[1]:  # If user didn't cancel
            new_color = result[1]
            self.update_color(new_color)
            if self.callback:
                self.callback(new_color)
    
    def update_color(self, new_color):
        """Update the color square display"""
        self.color = new_color
        self.configure(fg_color=self._get_display_color())