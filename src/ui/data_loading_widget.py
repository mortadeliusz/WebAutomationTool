"""
Data Loading Widget - UI component for loading data from various sources
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTableWidget, QTableWidgetItem,
                            QFileDialog, QMessageBox, QFrame, QTextEdit,
                            QComboBox, QDialog, QDialogButtonBox, QMenu)
from PyQt6.QtCore import Qt, pyqtSignal, QMimeData
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QKeySequence, QAction
import pandas as pd
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.data_loader import DataLoader
from ui.styles import Styles

class DataLoadingWidget(QWidget):
    """Widget for loading data from files, drag-drop, or paste"""
    
    data_loaded = pyqtSignal(pd.DataFrame)  # Emitted when data is successfully loaded
    
    def __init__(self):
        super().__init__()
        self.data_loader = DataLoader()
        self.current_data = None
        self.setup_ui()
        self.setAcceptDrops(True)
    
    def setup_ui(self):
        """Setup the data loading UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Single container
        self.data_container = QFrame()
        self.data_container.setFrameStyle(QFrame.Shape.StyledPanel)
        layout.addWidget(self.data_container)
        
        # Container layout
        self.container_layout = QVBoxLayout(self.data_container)
        self.container_layout.setContentsMargins(15, 15, 15, 15)
        
        # Setup states
        self.setup_loading_state()
        self.setup_data_state()
        self.show_loading_state()
    
    def setup_loading_state(self):
        """Setup widgets for loading state"""
        self.loading_widget = QWidget()
        loading_layout = QVBoxLayout(self.loading_widget)
        loading_layout.addStretch()
        
        self.load_btn = QPushButton("Load Data")
        Styles.primary_button(self.load_btn)
        self.load_btn.clicked.connect(self.load_file)
        loading_layout.addWidget(self.load_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        loading_layout.addStretch()
        self.container_layout.addWidget(self.loading_widget)
        
        # Setup interactions
        self.data_container.setAcceptDrops(True)
        self.data_container.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.data_container.customContextMenuRequested.connect(self.show_context_menu)
    
    def setup_data_state(self):
        """Setup widgets for data display state"""
        self.data_widget = QWidget()
        data_layout = QVBoxLayout(self.data_widget)
        
        # Info and clear button
        top_layout = QHBoxLayout()
        self.info_label = QLabel("")
        Styles.muted_text(self.info_label)
        top_layout.addWidget(self.info_label)
        top_layout.addStretch()
        
        self.clear_btn = QPushButton("Clear")
        Styles.secondary_button(self.clear_btn)
        self.clear_btn.clicked.connect(self.clear_data)
        top_layout.addWidget(self.clear_btn)
        
        data_layout.addLayout(top_layout)
        
        # Table
        self.preview_table = QTableWidget(0, 0)
        Styles.data_table(self.preview_table)
        data_layout.addWidget(self.preview_table)
        
        self.container_layout.addWidget(self.data_widget)
        self.data_widget.hide()
    def show_loading_state(self):
        """Show loading state"""
        self.loading_widget.show()
        self.data_widget.hide()
    
    def show_data_state(self):
        """Show data state"""
        self.loading_widget.hide()
        self.data_widget.show()
    
    def show_context_menu(self, position):
        """Show context menu for paste option"""
        menu = QMenu(self)
        
        paste_action = QAction("Paste Data", self)
        paste_action.triggered.connect(self.paste_data)
        menu.addAction(paste_action)
        
        menu.exec(self.data_container.mapToGlobal(position))
    
    def paste_data(self):
        """Paste data from clipboard"""
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if text:
            self.load_data_from_text(text)
    
    def load_file(self):
        """Open file dialog to load data"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Data File",
            "",
            "Data Files (*.csv *.xlsx *.json *.yaml *.yml);;All Files (*)"
        )
        
        if file_path:
            self.load_data_from_file(file_path)
    
    def load_data_from_file(self, file_path: str):
        """Load data from file path"""
        try:
            df = self.data_loader.load_from_file(file_path)
            self.set_data(df)
            
        except Exception as e:
            QMessageBox.critical(self, "Error Loading File", str(e))
    
    def load_data_from_text(self, text: str):
        """Load data from text content"""
        if not text.strip():
            return
        
        # Show format selection dialog if ambiguous
        format_hint = self.detect_format_hint(text)
        
        try:
            df = self.data_loader.load_from_text(text, format_hint)
            self.set_data(df)
            
        except Exception as e:
            # Try with format dialog
            format_hint = self.show_format_dialog(text)
            if format_hint:
                try:
                    df = self.data_loader.load_from_text(text, format_hint)
                    self.set_data(df)
                except Exception as e2:
                    QMessageBox.critical(self, "Error Parsing Data", str(e2))
    
    def detect_format_hint(self, text: str) -> str:
        """Try to detect data format from text content"""
        text = text.strip()
        
        if text.startswith('{') or text.startswith('['):
            return 'json'
        elif text.startswith('---') or ':' in text.split('\n')[0]:
            return 'yaml'
        else:
            return 'csv'
    
    def show_format_dialog(self, text: str) -> str:
        """Show dialog to select data format"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Data Format")
        dialog.setModal(True)
        
        layout = QVBoxLayout(dialog)
        
        layout.addWidget(QLabel("Could not auto-detect format. Please select:"))
        
        format_combo = QComboBox()
        format_combo.addItems(["CSV", "JSON", "YAML"])
        layout.addWidget(format_combo)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return format_combo.currentText().lower()
        
        return None
    
    def set_data(self, df: pd.DataFrame):
        """Set the loaded data and update UI"""
        self.current_data = df
        
        # Update info label
        preview = self.data_loader.get_preview(df)
        info_text = f"📊 {preview['total_rows']} rows, {preview['total_columns']} columns loaded"
        if preview['total_rows'] > preview['preview_rows']:
            info_text += f" (showing first {preview['preview_rows']})"
        
        self.info_label.setText(info_text)
        
        # Update preview table
        self.update_preview_table(preview)
        
        # Switch to data state
        self.show_data_state()
        
        # Emit signal
        self.data_loaded.emit(df)
    
    def update_preview_table(self, preview: dict):
        """Update the preview table with data"""
        data = preview['data']
        columns = preview['columns']
        
        self.preview_table.setRowCount(len(data))
        self.preview_table.setColumnCount(len(columns))
        self.preview_table.setHorizontalHeaderLabels(columns)
        
        for row_idx, row_data in enumerate(data):
            for col_idx, col_name in enumerate(columns):
                value = row_data.get(col_name, "")
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.preview_table.setItem(row_idx, col_idx, item)
        
        # Size table to content
        self.preview_table.resizeColumnsToContents()
        self.preview_table.resizeRowsToContents()
    
    def clear_data(self):
        """Clear loaded data"""
        self.current_data = None
        self.data_loader.current_data = None
        self.data_loader.current_columns = []
        
        # Clear table
        self.preview_table.setRowCount(0)
        self.preview_table.setColumnCount(0)
        
        # Switch back to loading state
        self.show_loading_state()
    
    def get_data(self) -> pd.DataFrame:
        """Get the currently loaded data"""
        return self.current_data
    
    def get_columns(self) -> list:
        """Get list of column names"""
        return self.data_loader.get_columns()
    
    # Drag and drop support
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter events"""
        if event.mimeData().hasUrls() or event.mimeData().hasText():
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop events"""
        mime_data = event.mimeData()
        
        if mime_data.hasUrls():
            urls = mime_data.urls()
            if urls:
                file_path = urls[0].toLocalFile()
                self.load_data_from_file(file_path)
        elif mime_data.hasText():
            text = mime_data.text()
            self.load_data_from_text(text)
        
        event.acceptProposedAction()
    
    # Keyboard shortcuts
    def keyPressEvent(self, event):
        """Handle keyboard events"""
        if event.matches(QKeySequence.StandardKey.Paste):
            from PyQt6.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            text = clipboard.text()
            if text:
                self.load_data_from_text(text)
        else:
            super().keyPressEvent(event)e
        self.show_loading_state()
    
    def get_data(self) -> pd.DataFrame:
        """Get the currently loaded data"""
        return self.current_data
    
    def get_columns(self) -> list:
        """Get list of column names"""
        return self.data_loader.get_columns()
    
    # Drag and drop support
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter events"""
        if event.mimeData().hasUrls() or event.mimeData().hasText():
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop events"""
        mime_data = event.mimeData()
        
        if mime_data.hasUrls():
            urls = mime_data.urls()
            if urls:
                file_path = urls[0].toLocalFile()
                self.load_data_from_file(file_path)
        elif mime_data.hasText():
            text = mime_data.text()
            self.load_data_from_text(text)
        
        event.acceptProposedAction()
    
    # Keyboard shortcuts
    def keyPressEvent(self, event):
        """Handle keyboard events"""
        if event.matches(QKeySequence.StandardKey.Paste):
            from PyQt6.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            text = clipboard.text()
            if text:
                self.load_data_from_text(text)
        else:
            super().keyPressEvent(event)