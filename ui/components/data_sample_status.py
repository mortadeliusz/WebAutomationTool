"""
Data Sample Status Indicator - Shows data sample load status with actions
Reusable component for displaying and managing data sample state
"""

import customtkinter as ctk
from typing import Callable
from src.app_services import get_workflow_data_sample, clear_workflow_data_sample


class DataSampleStatus(ctk.CTkFrame):
    """Status indicator for loaded data sample with load/clear/replace actions"""
    
    def __init__(self, parent, on_load: Callable, on_change: Callable):
        """
        Args:
            parent: Parent widget
            on_load: Callback when user clicks load/replace
            on_change: Callback when data state changes (for refresh)
        """
        super().__init__(parent, fg_color="transparent")
        self.on_load = on_load
        self.on_change = on_change
        self.setup_ui()
        self.refresh()
    
    def setup_ui(self):
        """Setup status UI container"""
        self.status_frame = ctk.CTkFrame(self)
        self.status_frame.pack(fill="x")
    
    def refresh(self):
        """Refresh status display based on current data state"""
        # Clear existing widgets
        for widget in self.status_frame.winfo_children():
            widget.destroy()
        
        data_sample = get_workflow_data_sample()
        
        if data_sample is None:
            self._show_no_data_state()
        else:
            self._show_data_loaded_state(data_sample)
    
    def _show_no_data_state(self):
        """Show UI when no data is loaded"""
        icon = ctk.CTkLabel(self.status_frame, text="⚠️", font=("", 14))
        icon.pack(side="left", padx=(5, 5))
        
        label = ctk.CTkLabel(self.status_frame, text="No sample data loaded")
        label.pack(side="left", padx=(0, 10))
        
        load_btn = ctk.CTkButton(
            self.status_frame,
            text="Load Data Sample",
            command=self.on_load,
            width=130
        )
        load_btn.pack(side="left", padx=(0, 5))
    
    def _show_data_loaded_state(self, data_sample):
        """Show UI when data is loaded"""
        icon = ctk.CTkLabel(self.status_frame, text="✅", font=("", 14))
        icon.pack(side="left", padx=(5, 5))
        
        rows = len(data_sample)
        label = ctk.CTkLabel(self.status_frame, text=f"Data sample ({rows} rows)")
        label.pack(side="left", padx=(0, 10))
        
        clear_btn = ctk.CTkButton(
            self.status_frame,
            text="✕",
            command=self.clear_data,
            width=30,
            fg_color="darkred",
            hover_color="red"
        )
        clear_btn.pack(side="left", padx=(0, 5))
        
        replace_btn = ctk.CTkButton(
            self.status_frame,
            text="Replace",
            command=self.on_load,
            width=80
        )
        replace_btn.pack(side="left", padx=(0, 5))
    
    def clear_data(self):
        """Clear data sample and trigger refresh"""
        clear_workflow_data_sample()
        self.on_change()
