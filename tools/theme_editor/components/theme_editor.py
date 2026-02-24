import customtkinter as ctk
from ..utils.color_utils import is_color_attribute
from .color_picker import ColorSquare

class ThemeEditor(ctk.CTkScrollableFrame):
    def __init__(self, parent, theme_loader, **kwargs):
        super().__init__(parent, **kwargs)
        self.theme_loader = theme_loader
        self.color_squares = {}
        
    def load_theme_data(self):
        """Load and display theme data"""
        # Clear existing widgets
        for widget in self.winfo_children():
            widget.destroy()
        self.color_squares.clear()
        
        theme_data = self.theme_loader.get_theme_data()
        
        row = 0
        for widget_class, attributes in theme_data.items():
            # Skip non-visual sections
            if widget_class in ["CTkFont"]:
                continue
                
            # Widget class header
            header = ctk.CTkLabel(self, text=widget_class, font=ctk.CTkFont(size=16, weight="bold"))
            header.grid(row=row, column=0, columnspan=4, sticky="w", padx=10, pady=(10, 5))
            row += 1
            
            # Process attributes
            for attr_name, attr_value in attributes.items():
                if is_color_attribute(attr_value):
                    self._create_color_row(widget_class, attr_name, attr_value, row)
                    row += 1
                elif isinstance(attr_value, dict):
                    # Handle nested attributes (like CTkFont)
                    for sub_attr, sub_value in attr_value.items():
                        if is_color_attribute(sub_value):
                            full_attr = f"{attr_name}.{sub_attr}"
                            self._create_color_row(widget_class, full_attr, sub_value, row)
                            row += 1
    
    def _create_color_row(self, widget_class, attr_name, color_tuple, row):
        """Create a row with color attribute controls"""
        # Attribute label
        label = ctk.CTkLabel(self, text=attr_name, width=150)
        label.grid(row=row, column=0, sticky="w", padx=10, pady=2)
        
        # Light mode color
        light_square = ColorSquare(
            self, 
            color_tuple[0],
            lambda new_color, wc=widget_class, attr=attr_name, idx=0: self._on_color_change(wc, attr, idx, new_color)
        )
        light_square.grid(row=row, column=1, padx=5, pady=2)
        
        light_entry = ctk.CTkEntry(self, width=100)
        light_entry.insert(0, color_tuple[0])
        light_entry.bind("<Return>", lambda e, wc=widget_class, attr=attr_name, idx=0, entry=light_entry, square=light_square: self._on_entry_change(wc, attr, idx, entry, square))
        light_entry.bind("<FocusOut>", lambda e, wc=widget_class, attr=attr_name, idx=0, entry=light_entry, square=light_square: self._on_entry_change(wc, attr, idx, entry, square))
        light_entry.grid(row=row, column=2, sticky="w", padx=5, pady=2)
        
        # Dark mode color
        dark_square = ColorSquare(
            self,
            color_tuple[1],
            lambda new_color, wc=widget_class, attr=attr_name, idx=1: self._on_color_change(wc, attr, idx, new_color)
        )
        dark_square.grid(row=row, column=3, padx=5, pady=2)
        
        dark_entry = ctk.CTkEntry(self, width=100)
        dark_entry.insert(0, color_tuple[1])
        dark_entry.bind("<Return>", lambda e, wc=widget_class, attr=attr_name, idx=1, entry=dark_entry, square=dark_square: self._on_entry_change(wc, attr, idx, entry, square))
        dark_entry.bind("<FocusOut>", lambda e, wc=widget_class, attr=attr_name, idx=1, entry=dark_entry, square=dark_square: self._on_entry_change(wc, attr, idx, entry, square))
        dark_entry.grid(row=row, column=4, sticky="w", padx=5, pady=2)
        
        # Store references
        key = f"{widget_class}.{attr_name}"
        self.color_squares[key] = {
            'light': {'square': light_square, 'entry': light_entry},
            'dark': {'square': dark_square, 'entry': dark_entry}
        }
    
    def _on_color_change(self, widget_class, attr_name, index, new_color):
        """Handle color change from color picker"""
        # Handle nested attributes
        if '.' in attr_name:
            parts = attr_name.split('.')
            # For now, just handle simple nested case
            attr_name = parts[0]
        
        self.theme_loader.update_color(widget_class, attr_name, index, new_color)
        
        # Update entry field
        key = f"{widget_class}.{attr_name}"
        if key in self.color_squares:
            mode = 'light' if index == 0 else 'dark'
            entry = self.color_squares[key][mode]['entry']
            entry.delete(0, 'end')
            entry.insert(0, new_color)
    
    def _on_entry_change(self, widget_class, attr_name, index, entry, square):
        """Handle color change from entry field"""
        new_color = entry.get().strip()
        if new_color:
            # Handle nested attributes
            if '.' in attr_name:
                parts = attr_name.split('.')
                attr_name = parts[0]
            
            self.theme_loader.update_color(widget_class, attr_name, index, new_color)
            square.update_color(new_color)