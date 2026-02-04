import customtkinter as ctk


class Accordion(ctk.CTkFrame):
    """Generic collapsible accordion component with clickable label header"""
    
    def __init__(self, parent, title: str, expanded: bool = True, anchor: str = "w"):
        super().__init__(parent)
        self.title = title
        self.is_expanded = expanded
        self.anchor = anchor
        self.setup_ui()
    
    def setup_ui(self):
        """Setup accordion UI with clickable header and content frame"""
        # Clickable header label
        self.header_label = ctk.CTkLabel(
            self,
            text=self.get_header_text(),
            font=ctk.CTkFont(size=14, weight="bold"),
            cursor="hand2",
            anchor=self.anchor
        )
        self.header_label.pack(fill="x", padx=10, pady=10)
        self.header_label.bind("<Button-1>", lambda e: self.toggle())
        
        # Hover effects
        self.header_label.bind("<Enter>", self.on_hover_enter)
        self.header_label.bind("<Leave>", self.on_hover_leave)
        
        # Content frame (exposed as property)
        self.content_frame = ctk.CTkFrame(self)
        if self.is_expanded:
            self.content_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
    
    def get_header_text(self) -> str:
        """Get header text with dynamic icon"""
        icon = "▼" if self.is_expanded else "▶"
        return f"{icon} {self.title}"
    
    def toggle(self):
        """Toggle expanded/collapsed state"""
        self.is_expanded = not self.is_expanded
        self.header_label.configure(text=self.get_header_text())
        
        if self.is_expanded:
            self.content_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        else:
            self.content_frame.pack_forget()
    
    def on_hover_enter(self, event):
        """Hover enter effect"""
        self.header_label.configure(text_color=("blue", "lightblue"))
    
    def on_hover_leave(self, event):
        """Hover leave effect"""
        self.header_label.configure(text_color=("black", "white"))