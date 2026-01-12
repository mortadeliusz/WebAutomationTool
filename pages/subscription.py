import customtkinter as ctk

class SubscriptionPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.label = ctk.CTkLabel(self, text="Subscription Page Content")
        self.label.pack(pady=20)