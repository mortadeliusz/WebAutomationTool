"""
DataTable Component - Pure table widget with theme integration
"""

import customtkinter as ctk
import tkinter.ttk as ttk
import pandas as pd
from typing import Optional
from src.core.theme_manager import get_component_colors


class _TreeviewTable(ctk.CTkBaseClass):
    """Internal TTK Treeview component - pure table widget, no placeholder"""
    
    _theme_applied_for_mode = None  # Class-level theme tracking
    
    def __init__(self, parent, max_rows: int = 10, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Configuration
        self.max_rows = max_rows
        
        # Widgets
        self.tree = None
        self.v_scrollbar = None
        self.h_scrollbar = None
        
        self.setup_ui()
    
    def _set_appearance_mode(self, mode):
        """Called automatically when theme changes"""
        super()._set_appearance_mode(mode)
        
        # Apply theme only once across ALL _TreeviewTable instances
        if _TreeviewTable._theme_applied_for_mode != mode:
            self._apply_class_theme()
            _TreeviewTable._theme_applied_for_mode = mode
    
    def _apply_class_theme(self):
        """Apply theme styling to all _TreeviewTable instances"""
        colors = get_component_colors("DataTable")
        
        # Get colors from JSON (no detection)
        bg = colors.get("background", ["#f0f0f0", "#212121"])
        text = colors.get("text", ["#000000", "#ffffff"])
        selected = colors.get("selected_bg", ["#14375e", "#14375e"])
        header = colors.get("header_bg", ["#1f538d", "#1f538d"])
        header_text = colors.get("header_text", ["#000000", "#ffffff"])
        
        # Resolve tuple colors for current theme
        current_mode = ctk.get_appearance_mode()
        bg_color = bg[1] if current_mode == "Dark" else bg[0]
        text_color = text[1] if current_mode == "Dark" else text[0]
        selected_color = selected[1] if current_mode == "Dark" else selected[0]
        header_color = header[1] if current_mode == "Dark" else header[0]
        header_text_color = header_text[1] if current_mode == "Dark" else header_text[0]
        
        # Apply component-specific TTK styling with default theme foundation
        style = ttk.Style()
        style.theme_use("default")  # Foundation for custom styles
        
        style.configure("DataTable.Treeview",
                       background=bg_color,
                       foreground=text_color,
                       rowheight=25,
                       fieldbackground=bg_color,
                       bordercolor=bg_color,
                       borderwidth=0)
        style.map('DataTable.Treeview', background=[('selected', selected_color)])
        
        style.configure("DataTable.Treeview.Heading",
                       background=header_color,
                       foreground=header_text_color,
                       relief="flat")
        style.map("DataTable.Treeview.Heading",
                  background=[('active', header_color)])
    
    def setup_ui(self):
        """Setup table - always create, no placeholder"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create table immediately
        self._create_table()
    
    def _create_table(self):
        """Create table widgets"""
        # Create treeview with component-specific style
        self.tree = ttk.Treeview(self, style="DataTable.Treeview")
        
        # Create scrollbars
        self.v_scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.h_scrollbar = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)
        
        # Grid table
        self.tree.grid(row=0, column=0, sticky="nsew")
        
        # Bind events
        self.tree.bind('<Configure>', self._update_scrollbars)
        
        # Apply initial theme
        self._apply_class_theme()
    
    def set_data(self, dataframe: Optional[pd.DataFrame]):
        """Set table data - empty DataFrame shows empty table"""
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Handle empty/None data
        if dataframe is None or dataframe.empty:
            self.tree["columns"] = ()
            self.tree["show"] = "tree"  # Show empty tree
            self._update_scrollbars()
            return
        
        # Configure columns
        preview_df = dataframe.head(self.max_rows)
        columns = list(dataframe.columns)
        
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
        
        self._update_scrollbars()
    
    def clear(self):
        """Clear table data - shows empty table"""
        self.set_data(None)
    
    def _update_scrollbars(self, event=None):
        """Show/hide scrollbars based on content size"""
        if self.tree is None:
            return
        self.after(10, self._check_scrollbars)
    
    def _check_scrollbars(self):
        """Check scrollbar necessity and grid them properly"""
        if self.tree is None:
            return
        
        # Vertical scrollbar
        if self.tree.yview() != (0.0, 1.0):
            self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        else:
            self.v_scrollbar.grid_remove()
        
        # Horizontal scrollbar
        if self.tree.xview() != (0.0, 1.0):
            self.h_scrollbar.grid(row=1, column=0, sticky="ew")
        else:
            self.h_scrollbar.grid_remove()


class DataTable(ctk.CTkFrame):
    """Public DataTable component with placeholder support"""
    
    def __init__(self, parent, max_rows: int = 10, placeholder_text: str = "No data to display", **kwargs):
        super().__init__(parent, **kwargs)
        
        # Configuration
        self.placeholder_text = placeholder_text
        
        # Setup grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create components
        self.placeholder_label = ctk.CTkLabel(
            self, 
            text=self.placeholder_text,
            font=ctk.CTkFont(size=14)
        )
        
        self.table = _TreeviewTable(self, max_rows=max_rows)
        
        # Show placeholder initially
        self._show_placeholder()
    
    def set_data(self, dataframe: Optional[pd.DataFrame]):
        """Set table data - shows placeholder if empty, table if data"""
        if dataframe is None or dataframe.empty:
            self._show_placeholder()
        else:
            self._show_table()
            self.table.set_data(dataframe)
    
    def clear(self):
        """Clear table data - shows placeholder"""
        self._show_placeholder()
    
    def _show_placeholder(self):
        """Show placeholder label, hide table"""
        self.table.grid_remove()
        self.placeholder_label.grid(row=0, column=0, sticky="nsew")
    
    def _show_table(self):
        """Show table, hide placeholder"""
        self.placeholder_label.grid_remove()
        self.table.grid(row=0, column=0, sticky="nsew")