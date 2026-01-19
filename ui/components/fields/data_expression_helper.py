"""
Data Expression Helper - Icon button with column selector popup
Enables users to insert {{col('name')}} or {{col(0)}} expressions
"""

import customtkinter as ctk
import tkinter as tk
from typing import Optional, Callable
import pandas as pd


class DataExpressionHelper(ctk.CTkFrame):
    """
    Reusable data expression helper component
    - Icon button (📊)
    - Column selector popup (when data available)
    - Educational popup (when no data)
    - Inserts expressions at cursor position
    """
    
    def __init__(
        self,
        parent,
        target_entry: ctk.CTkEntry,
        data_sample: Optional[pd.DataFrame] = None,
        on_load_data: Optional[Callable] = None
    ):
        """
        Args:
            parent: Parent widget
            target_entry: Text entry to insert expressions into
            data_sample: Optional DataFrame with column data
            on_load_data: Optional callback when user clicks "Load Data Sample"
        """
        super().__init__(parent, fg_color="transparent")
        self.target_entry = target_entry
        self.data_sample = data_sample
        self.on_load_data = on_load_data
        
        # Icon button
        self.icon_btn = ctk.CTkButton(
            self,
            text="📊",
            width=30,
            command=self.on_icon_clicked
        )
        self.icon_btn.pack()
    
    def set_data_sample(self, data_sample: Optional[pd.DataFrame]):
        """Update available columns"""
        self.data_sample = data_sample
    
    def on_icon_clicked(self):
        """Show column selector or educational message"""
        if self.data_sample is None or self.data_sample.empty:
            self.show_educational_popup()
        else:
            self.show_column_selector()
    
    def show_educational_popup(self):
        """Show popup explaining feature + Load Data button"""
        popup = EducationalPopup(self, self.on_load_data)
    
    def show_column_selector(self):
        """Show popup with searchable column list"""
        popup = ColumnSelectorPopup(
            self,
            self.data_sample,
            self.insert_expression
        )
    
    def insert_expression(self, expression: str):
        """Insert expression at cursor position"""
        self.target_entry.insert(tk.INSERT, expression)
        self.target_entry.focus()


class EducationalPopup(ctk.CTkToplevel):
    """Educational popup when no data loaded"""
    
    def __init__(self, parent, on_load_data: Optional[Callable] = None):
        super().__init__(parent)
        self.on_load_data = on_load_data
        
        self.title("Data Expression Helper")
        self.geometry("500x550")
        self.resizable(False, False)
        
        # Center on parent
        self.transient(parent)
        self.grab_set()
        
        # Scrollable content
        content = ctk.CTkScrollableFrame(self)
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title = ctk.CTkLabel(
            content,
            text="📊 Insert Data Columns",
            font=("", 16, "bold")
        )
        title.pack(pady=(0, 15))
        
        # Load data first message (if callback provided)
        if self.on_load_data:
            load_message = ctk.CTkLabel(
                content,
                text="⚠️ Load data sample first to use this feature",
                font=("", 12, "bold"),
                text_color=("orange", "orange")
            )
            load_message.pack(pady=(0, 10))
            
            load_btn = ctk.CTkButton(
                content,
                text="📊 Load Data Sample",
                command=self.on_load_clicked,
                height=40,
                width=200
            )
            load_btn.pack(pady=(0, 20))
            
            # Separator
            separator = ctk.CTkLabel(
                content,
                text="─" * 50,
                text_color="gray"
            )
            separator.pack(pady=(0, 20))
        
        # Explanation
        explanation = ctk.CTkLabel(
            content,
            text="This helper lets you insert column\nreferences from your data:",
            justify="left"
        )
        explanation.pack(pady=(0, 10), anchor="w")
        
        # Examples
        examples = ctk.CTkLabel(
            content,
            text="• {{col('email')}} - by column name\n• {{col(0)}} - by column index",
            justify="left"
        )
        examples.pack(pady=(0, 15), anchor="w")
        
        # Usage example
        usage_title = ctk.CTkLabel(
            content,
            text="Example:",
            font=("", 12, "bold"),
            justify="left"
        )
        usage_title.pack(pady=(0, 5), anchor="w")
        
        usage = ctk.CTkLabel(
            content,
            text='"Hello {{col(\'firstname\')}}"',
            justify="left",
            text_color="gray"
        )
        usage.pack(anchor="w")
        
        usage_result = ctk.CTkLabel(
            content,
            text='becomes "Hello John"',
            justify="left",
            text_color="gray"
        )
        usage_result.pack(pady=(0, 15), anchor="w")
        
        # When to use guidance
        guidance_title = ctk.CTkLabel(
            content,
            text="When to use names vs indexes:",
            font=("", 12, "bold"),
            justify="left"
        )
        guidance_title.pack(pady=(0, 5), anchor="w")
        
        guidance = ctk.CTkLabel(
            content,
            text="• Use names if column names never change\n"
                 "• Use indexes if names might change but\n"
                 "  positions stay the same",
            justify="left"
        )
        guidance.pack(pady=(0, 20), anchor="w")
    
    def on_load_clicked(self):
        """User clicked Load Data Sample"""
        self.destroy()
        if self.on_load_data:
            self.on_load_data()


class ColumnSelectorPopup(ctk.CTkToplevel):
    """Popup for selecting data columns"""
    
    _preferred_mode = "name"  # Class variable for session persistence
    
    def __init__(
        self,
        parent,
        data_sample: pd.DataFrame,
        on_select_callback: Callable[[str], None]
    ):
        super().__init__(parent)
        self.data_sample = data_sample
        self.on_select = on_select_callback
        self.columns = data_sample.columns.tolist()
        self.mode = ColumnSelectorPopup._preferred_mode
        
        self.title("Select Column")
        self.geometry("600x500")
        
        # Center on parent
        self.transient(parent)
        self.grab_set()
        
        # Main container
        container = ctk.CTkFrame(self)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Search box (create but don't pack yet - will pack after explanation)
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self.on_search_changed)
        search_entry = ctk.CTkEntry(
            container,
            placeholder_text="Search columns...",
            textvariable=self.search_var,
            height=35
        )
        
        # Explanation
        explanation = ctk.CTkLabel(
            container,
            text="Use names if column names never change.\n"
                 "Use indexes if names might change but positions stay the same.",
            justify="left",
            text_color="gray"
        )
        explanation.pack(fill="x", pady=(0, 10))
        
        # Search box
        search_entry.pack(fill="x", pady=(0, 10))
        search_entry.focus()
        
        # Scrollable table (headers + data rows)
        self.table_frame = ctk.CTkScrollableFrame(container, fg_color="transparent")
        self.table_frame.pack(fill="both", expand=True)
        
        # Populate table
        self.refresh_table()
        
        # Bind Escape to close
        self.bind("<Escape>", lambda e: self.destroy())
    
    def refresh_table(self, filter_text: str = ""):
        """Refresh table with optional filtering"""
        # Clear existing rows
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        
        # Create header row first
        self.create_header_row()
        
        # Get filtered columns (case-insensitive)
        filtered_columns = [
            (idx, col) for idx, col in enumerate(self.columns)
            if not filter_text or filter_text.lower() in col.lower()
        ]
        
        # Create data rows
        for i, (col_index, col_name) in enumerate(filtered_columns):
            self.create_row(col_name, col_index, i)
    
    def create_header_row(self):
        """Create header row with mode toggle"""
        row = ctk.CTkFrame(self.table_frame, fg_color="transparent")
        row.pack(fill="x", pady=(0, 5))
        
        # Header label (changes based on mode)
        header_text = "Column Name" if self.mode == "name" else "Index (Column Name)"
        header_label = ctk.CTkLabel(
            row,
            text=header_text,
            font=("", 12, "bold")
        )
        header_label.pack(side="left", padx=(6, 0))
        
        # Mode toggle (right side)
        toggle_text = "Switch to Index ⚙" if self.mode == "name" else "Switch to Name ⚙"
        self.mode_label = ctk.CTkLabel(
            row,
            text=toggle_text,
            font=("", 10),
            text_color="gray",
            cursor="hand2"
        )
        self.mode_label.pack(side="right", padx=(10, 6))
        self.mode_label.bind("<Button-1>", self.toggle_mode)
        
        # Hover effect
        self.mode_label.bind("<Enter>", lambda e: self.mode_label.configure(text_color=("blue", "lightblue")))
        self.mode_label.bind("<Leave>", lambda e: self.mode_label.configure(text_color="gray"))
    
    def create_row(self, col_name: str, col_index: int, row_num: int):
        """Create single table row (single column based on mode)"""
        # Row container
        row = ctk.CTkFrame(self.table_frame, fg_color="transparent")
        row.pack(fill="x", pady=2)
        
        # Zebra striping colors
        if row_num % 2 == 0:
            btn_color = ("gray90", "gray17")
            hover_color = ("gray75", "gray30")
        else:
            btn_color = ("gray85", "gray20")
            hover_color = ("gray70", "gray33")
        
        # Button text and command based on mode
        if self.mode == "name":
            btn_text = col_name
            btn_command = lambda: self.select_by_name(col_name)
        else:
            btn_text = f"{col_index} ({col_name})"
            btn_command = lambda: self.select_by_index(col_index)
        
        # Single button (full width)
        btn = ctk.CTkButton(
            row,
            text=btn_text,
            command=btn_command,
            anchor="w",
            fg_color=btn_color,
            hover_color=hover_color,
            corner_radius=6
        )
        btn.pack(fill="x", padx=(0, 0))
    
    def select_by_name(self, col_name: str):
        """User clicked name button"""
        expression = f"{{{{col('{col_name}')}}}}"
        self.on_select(expression)
        self.destroy()
    
    def select_by_index(self, col_index: int):
        """User clicked index button"""
        expression = f"{{{{col({col_index})}}}}"
        self.on_select(expression)
        self.destroy()
    
    def toggle_mode(self, event):
        """Toggle between name and index mode"""
        self.mode = "index" if self.mode == "name" else "name"
        ColumnSelectorPopup._preferred_mode = self.mode  # Save preference
        
        # Update toggle label
        toggle_text = "Switch to Index ⚙" if self.mode == "name" else "Switch to Name ⚙"
        self.mode_label.configure(text=toggle_text)
        
        # Refresh table
        self.refresh_table()
    
    def on_search_changed(self, *args):
        """Search text changed - filter table"""
        filter_text = self.search_var.get()
        self.refresh_table(filter_text)
