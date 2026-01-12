import customtkinter as ctk

class TaskManagementPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.label = ctk.CTkLabel(self, text="Task Management Page Content")
        self.label.pack(pady=20)