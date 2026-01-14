"""
DataTable Component - Reusable table widget for displaying pandas DataFrames
"""

import customtkinter as ctk
import tkinter.ttk as ttk
import pandas as pd
from typing import Optional


class DataTable(ctk.CTkFrame):
    def __init__(self, parent, dataframe: Optional[pd.DataFrame] = None, max_rows: int = 10, 
                 placeholder_text: str = "No data to display", show_placeholder: bool = True):
        super().__init__(parent)
        self.max_rows = max_rows
        self.placeholder_text = placeholder_text
        self.show_placeholder = show_placeholder
        self.tree = None
        self.v_scrollbar = None
        self.h_scrollbar = None
        self.setup_ui()
        if dataframe is not None:
            self.set_data(dataframe)
    
    def setup_ui(self):
        """Setup the table UI - only create placeholder initially"""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create placeholder label
        self.placeholder_label = ctk.CTkLabel(
            self, 
            text=self.placeholder_text,
            font=ctk.CTkFont(size=14)
        )
        
        # Start in empty state
        self._show_empty_state()
    
    def _create_table(self):
        """Create treeview and scrollbars when needed"""
        if self.tree is not None:
            return  # Already created
        
        # Create treeview
        self.tree = ttk.Treeview(self)
        
        # Create scrollbars
        self.v_scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.h_scrollbar = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)
        
        # Apply styling
        self.apply_styling()
        
        # Bind events
        self.tree.bind('<Configure>', self.update_scrollbars)
        self.tree.bind('<<TreeviewSelect>>', self.update_scrollbars)
    
    def _destroy_table(self):
        """Destroy treeview and scrollbars when switching to empty state"""
        if self.tree is not None:
            self.tree.destroy()
            self.tree = None
        if self.v_scrollbar is not None:
            self.v_scrollbar.destroy()
            self.v_scrollbar = None
        if self.h_scrollbar is not None:
            self.h_scrollbar.destroy()
            self.h_scrollbar = None
    
    def apply_styling(self):
        """Apply theme-adaptive styling to the table"""
        if self.tree is None:
            return
        
        # Get resolved colors from actual CustomTkinter widgets
        dummy_frame = ctk.CTkFrame(self)
        dummy_label = ctk.CTkLabel(self)
        dummy_button = ctk.CTkButton(self)
        
        bg_color = dummy_frame.cget("fg_color")
        text_color = dummy_label.cget("text_color")
        accent_color = dummy_button.cget("fg_color")
        
        # Clean up dummy widgets
        dummy_frame.destroy()
        dummy_label.destroy()
        dummy_button.destroy()
        
        # Consistent color formula: (85% bg + 15% text) + 15% accent
        base_mix = self.mix_colors(bg_color, text_color, 0.15)  # 85% bg + 15% text
        interactive_color = self.mix_colors(base_mix, accent_color, 0.15)  # + 15% accent
        
        # Scrollbar hover color: (70% bg + 30% text) + 35% accent
        hover_base = self.mix_colors(bg_color, text_color, 0.30)  # 70% bg + 30% text
        scrollbar_hover = self.mix_colors(hover_base, accent_color, 0.35)  # + 35% accent
        
        # Apply styling
        style = ttk.Style()
        style.theme_use("default")
        
        style.configure("Treeview",
                       background=self.mix_colors(bg_color, text_color, 0.0),
                       foreground=self.mix_colors(text_color, bg_color, 0.0),
                       rowheight=25,
                       fieldbackground=self.mix_colors(bg_color, text_color, 0.0),
                       bordercolor=self.mix_colors(bg_color, text_color, 0.0),
                       borderwidth=0)
        style.map('Treeview', background=[('selected', interactive_color)])
        
        style.configure("Treeview.Heading",
                       background=interactive_color,
                       foreground="white",
                       relief="flat",
                       font=('', 10, 'normal'))
        style.map("Treeview.Heading",
                 background=[('active', interactive_color)])
        
        # Style scrollbars with hover effect
        style.configure('Vertical.TScrollbar',
                       background=interactive_color,
                       troughcolor=self.mix_colors(bg_color, text_color, 0.0),
                       borderwidth=0,
                       arrowcolor=self.mix_colors(text_color, bg_color, 0.0))
        style.map('Vertical.TScrollbar',
                 background=[('active', scrollbar_hover)])
        
        style.configure('Horizontal.TScrollbar',
                       background=interactive_color,
                       troughcolor=self.mix_colors(bg_color, text_color, 0.0),
                       borderwidth=0,
                       arrowcolor=self.mix_colors(text_color, bg_color, 0.0))
        style.map('Horizontal.TScrollbar',
                 background=[('active', scrollbar_hover)])
    
    def mix_colors(self, base_color, mix_color, mix_ratio: float) -> str:
        """Mix base color with accent color at given ratio"""
        def to_hex(color):
            if isinstance(color, str) and color.startswith('#'):
                return color
            elif isinstance(color, (tuple, list)) and len(color) >= 2:
                # Handle [light, dark] theme arrays
                is_dark = ctk.get_appearance_mode() == "Dark"
                selected_color = color[1] if is_dark else color[0]
                
                # Convert named colors to hex
                if isinstance(selected_color, str):
                    if selected_color.startswith('#'):
                        return selected_color
                    else:
                        # Common named color mappings
                        color_map = {
                            'gray10': '#1a1a1a', 'gray13': '#212121', 'gray16': '#292929',
                            'gray20': '#333333', 'gray84': '#d6d6d6', 'gray90': '#e6e6e6',
                            'gray95': '#f2f2f2', 'transparent': '#212121'
                        }
                        return color_map.get(selected_color, '#212121')
                return '#212121'
            elif isinstance(color, (tuple, list)) and len(color) >= 3:
                # RGB tuple
                r, g, b = color[:3]
                return f"#{int(r):02x}{int(g):02x}{int(b):02x}"
            else:
                return "#212121"  # Fallback
        
        base_hex = to_hex(base_color)
        mix_hex = to_hex(mix_color)
        
        # Convert hex to RGB
        base_rgb = tuple(int(base_hex[i:i+2], 16) for i in (1, 3, 5))
        mix_rgb = tuple(int(mix_hex[i:i+2], 16) for i in (1, 3, 5))
        
        # Blend colors
        result_rgb = tuple(
            int(base * (1 - mix_ratio) + mix * mix_ratio)
            for base, mix in zip(base_rgb, mix_rgb)
        )
        
        return f"#{result_rgb[0]:02x}{result_rgb[1]:02x}{result_rgb[2]:02x}"
    
    def set_data(self, dataframe: pd.DataFrame):
        """Set table data from pandas DataFrame"""
        if dataframe is None or dataframe.empty:
            self._show_empty_state()
            return
        
        # Create table if needed
        self._create_table()
        
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Show table, hide placeholder
        self._show_table_state()
        
        # Get preview data (limited rows)
        preview_df = dataframe.head(self.max_rows)
        columns = list(dataframe.columns)
        
        # Configure columns
        self.tree["columns"] = columns
        self.tree["show"] = "headings"
        
        # Set column headings and widths
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, minwidth=80)
        
        # Insert data rows
        for _, row in preview_df.iterrows():
            values = [str(row[col]) if pd.notna(row[col]) else "" for col in columns]
            self.tree.insert("", "end", values=values)
        
        # Add truncation info if needed
        if len(dataframe) > self.max_rows:
            remaining = len(dataframe) - self.max_rows
            truncate_values = [f"... and {remaining} more rows"] + [""] * (len(columns) - 1)
            self.tree.insert("", "end", values=truncate_values)
        
        # Update scrollbar visibility
        self.update_scrollbars()
    
    def clear(self):
        """Clear all table data"""
        self._show_empty_state()
    
    def _show_empty_state(self):
        """Show placeholder message, destroy table"""
        self._destroy_table()
        if self.show_placeholder:
            self.placeholder_label.grid(row=0, column=0, sticky="nsew")
        else:
            self.placeholder_label.grid_remove()
    
    def _show_table_state(self):
        """Show table, hide placeholder"""
        self.placeholder_label.grid_remove()
        self.tree.grid(row=0, column=0, sticky="nsew")
    
    def update_scrollbars(self, event=None):
        """Show/hide scrollbars based on content size"""
        if self.tree is None:
            return
        self.after(10, self._check_scrollbars)
    
    def _check_scrollbars(self):
        """Check if scrollbars are needed and show/hide accordingly"""
        if self.tree is None:
            return
        
        # Check vertical scrollbar
        if self.tree.yview() != (0.0, 1.0):
            self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        else:
            self.v_scrollbar.grid_remove()
        
        # Check horizontal scrollbar
        if self.tree.xview() != (0.0, 1.0):
            self.h_scrollbar.grid(row=1, column=0, sticky="ew")
        else:
            self.h_scrollbar.grid_remove()