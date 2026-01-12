import customtkinter as ctk

class TaskExecutionPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.label = ctk.CTkLabel(self, text="Task Execution Page Content")
        self.label.pack(pady=20)