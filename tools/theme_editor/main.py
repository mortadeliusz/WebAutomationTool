import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
from .utils.theme_loader import ThemeLoader
from .components.theme_editor import ThemeEditor

class ThemeEditorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("CustomTkinter Theme Editor")
        self.geometry("800x600")
        
        self.theme_loader = ThemeLoader()
        
        self._setup_ui()
        
        # Load default theme if exists
        default_theme = os.path.join("config", "testinmg themes.json")
        if os.path.exists(default_theme):
            self._load_theme(default_theme)
    
    def _setup_ui(self):
        """Setup the user interface"""
        # File info frame
        info_frame = ctk.CTkFrame(self, height=40)
        info_frame.pack(fill="x", padx=10, pady=5)
        info_frame.pack_propagate(False)
        
        self.file_label = ctk.CTkLabel(info_frame, text="No file loaded", font=ctk.CTkFont(size=14, weight="bold"))
        self.file_label.pack(side="left", padx=10, pady=10)
        
        # Top frame for buttons
        button_frame = ctk.CTkFrame(self, height=60)
        button_frame.pack(fill="x", padx=10, pady=5)
        button_frame.pack_propagate(False)
        
        # Buttons
        load_btn = ctk.CTkButton(button_frame, text="Load Theme", command=self._load_theme_dialog)
        load_btn.pack(side="left", padx=5, pady=10)
        
        save_btn = ctk.CTkButton(button_frame, text="Save", command=self._save_theme)
        save_btn.pack(side="left", padx=5, pady=10)
        
        save_as_btn = ctk.CTkButton(button_frame, text="Save As", command=self._save_theme_as)
        save_as_btn.pack(side="left", padx=5, pady=10)
        
        # Theme editor
        self.editor = ThemeEditor(self, self.theme_loader)
        self.editor.pack(fill="both", expand=True, padx=10, pady=5)
    
    def _load_theme_dialog(self):
        """Open file dialog to load theme"""
        file_path = filedialog.askopenfilename(
            title="Load Theme File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir="config"
        )
        if file_path:
            self._load_theme(file_path)
    
    def _load_theme(self, file_path):
        """Load theme from file"""
        if self.theme_loader.load_theme(file_path):
            self.editor.load_theme_data()
            filename = os.path.basename(file_path)
            self.title(f"Theme Editor - {filename}")
            self.file_label.configure(text=f"Editing: {filename}")
        else:
            messagebox.showerror("Error", "Failed to load theme file")
    
    def _save_theme(self):
        """Save current theme"""
        if self.theme_loader.save_theme():
            messagebox.showinfo("Success", "Theme saved successfully")
        else:
            messagebox.showerror("Error", "Failed to save theme")
    
    def _save_theme_as(self):
        """Save theme with new filename"""
        file_path = filedialog.asksaveasfilename(
            title="Save Theme As",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir="config"
        )
        if file_path:
            if self.theme_loader.save_theme(file_path):
                filename = os.path.basename(file_path)
                self.title(f"Theme Editor - {filename}")
                self.file_label.configure(text=f"Editing: {filename}")
                messagebox.showinfo("Success", "Theme saved successfully")
            else:
                messagebox.showerror("Error", "Failed to save theme")

def main():
    app = ThemeEditorApp()
    app.mainloop()

if __name__ == "__main__":
    main()