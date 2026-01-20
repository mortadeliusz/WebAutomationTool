import customtkinter as ctk

class SubscriptionPage(ctk.CTkFrame):
    def __init__(self, parent, navigate_callback=None):
        super().__init__(parent)
        self.navigate_callback = navigate_callback
        
        self.label = ctk.CTkLabel(self, text="Subscription Page Content")
        self.label.pack(pady=20)