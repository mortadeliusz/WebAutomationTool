import customtkinter as ctk
from typing import Optional

class MainContent(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.current_page: Optional[ctk.CTkFrame] = None
    
    def show_page(self, page_instance: ctk.CTkFrame) -> None:
        # Hide current page
        if self.current_page:
            self.current_page.pack_forget()
        
        # Show new page with margins
        page_instance.pack(fill="both", expand=True, padx=(0, 5), pady=5)
        self.current_page = page_instance