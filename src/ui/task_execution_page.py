"""
Task Execution Page - Landing page for running automation tasks
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QComboBox, QPushButton, QTableWidget, QProgressBar,
                            QFrame, QTextEdit, QMessageBox)
from PyQt6.QtCore import Qt
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.task_storage import TaskStorage
from core.task_execution_thread import TaskExecutionThread

class TaskExecutionPage(QWidget):
    def __init__(self):
        super().__init__()
        self.task_storage = TaskStorage()
        self.execution_thread = None
        self.setup_ui()
        self.refresh_tasks()  # Load tasks on startup
    
    def setup_ui(self):
        """Setup Task Execution page UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Page title
        title = QLabel("Task Execution")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Task selection
        task_section = self.create_task_selection()
        layout.addWidget(task_section)
        
        # Data loading section
        data_section = self.create_data_section()
        layout.addWidget(data_section)
        
        # Execute/Cancel button
        execute_layout = QHBoxLayout()
        execute_layout.addStretch()
        
        self.execute_btn = QPushButton("🚀 Execute Task")
        self.execute_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.execute_btn.clicked.connect(self.execute_task)
        
        self.cancel_btn = QPushButton("❌ Cancel")
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        self.cancel_btn.clicked.connect(self.cancel_execution)
        self.cancel_btn.setVisible(False)
        
        execute_layout.addWidget(self.execute_btn)
        execute_layout.addWidget(self.cancel_btn)
        execute_layout.addStretch()
        layout.addLayout(execute_layout)
        
        # Progress section
        progress_section = self.create_progress_section()
        layout.addWidget(progress_section)
        
        layout.addStretch()
    
    def create_task_selection(self):
        """Create task selection section"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.Box)
        frame.setStyleSheet("QFrame { border: 1px solid #ddd; border-radius: 6px; padding: 10px; }")
        
        layout = QVBoxLayout(frame)
        
        # Task selection
        task_layout = QHBoxLayout()
        task_layout.addWidget(QLabel("Select Task:"))
        
        self.task_combo = QComboBox()
        self.task_combo.addItem("No tasks available")
        self.task_combo.setMinimumWidth(300)
        task_layout.addWidget(self.task_combo)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_tasks)
        task_layout.addWidget(refresh_btn)
        
        task_layout.addStretch()
        layout.addLayout(task_layout)
        
        return frame
    
    def create_data_section(self):
        """Create data loading section"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.Box)
        frame.setStyleSheet("QFrame { border: 1px solid #ddd; border-radius: 6px; padding: 10px; }")
        
        layout = QVBoxLayout(frame)
        
        # Data loading label
        layout.addWidget(QLabel("Load Data:"))
        
        # Data loading area (placeholder)
        data_area = QFrame()
        data_area.setFrameStyle(QFrame.Shape.StyledPanel)
        data_area.setStyleSheet("""
            QFrame {
                border: 2px dashed #ccc;
                border-radius: 6px;
                background-color: #f9f9f9;
                min-height: 100px;
            }
        """)
        
        data_layout = QVBoxLayout(data_area)
        data_layout.addStretch()
        
        load_btn = QPushButton("📁 Load Data")
        load_btn.setStyleSheet("border: none; background: none; font-size: 14px;")
        data_layout.addWidget(load_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        help_text = QLabel("Drag & drop files here or Ctrl+V to paste")
        help_text.setStyleSheet("color: #666; font-size: 12px;")
        help_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        data_layout.addWidget(help_text)
        
        data_layout.addStretch()
        
        layout.addWidget(data_area)
        
        # Data preview (placeholder)
        self.data_preview = QTableWidget(0, 0)
        self.data_preview.setMaximumHeight(200)
        self.data_preview.hide()  # Hidden until data is loaded
        layout.addWidget(self.data_preview)
        
        return frame
    
    def create_progress_section(self):
        """Create progress tracking section"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.Box)
        frame.setStyleSheet("QFrame { border: 1px solid #ddd; border-radius: 6px; padding: 10px; }")
        
        layout = QVBoxLayout(frame)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status text
        self.status_label = QLabel("")
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)
        
        return frame
    
    def refresh_tasks(self):
        """Refresh available tasks"""
        tasks = self.task_storage.list_tasks()
        
        self.task_combo.clear()
        
        if tasks:
            for task in tasks:
                self.task_combo.addItem(task['name'])
        else:
            self.task_combo.addItem("No tasks available")
    
    def execute_task(self):
        """Execute selected task in worker thread"""
        task_name = self.task_combo.currentText()
        if task_name == "No tasks available":
            QMessageBox.warning(self, "Warning", "No task selected")
            return
        
        # Load task
        task = self.task_storage.load_task(task_name)
        if not task:
            QMessageBox.critical(self, "Error", f"Failed to load task '{task_name}'")
            return
        
        # Start execution in worker thread
        self.execution_thread = TaskExecutionThread(task)
        self.execution_thread.progress_update.connect(self.on_progress_update)
        self.execution_thread.action_completed.connect(self.on_action_completed)
        self.execution_thread.execution_finished.connect(self.on_execution_finished)
        
        # Update UI for execution state
        self.execute_btn.setVisible(False)
        self.cancel_btn.setVisible(True)
        self.progress_bar.setVisible(True)
        self.status_label.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Starting execution...")
        
        # Start execution
        self.execution_thread.start()
    
    def cancel_execution(self):
        """Cancel running execution"""
        if self.execution_thread and self.execution_thread.isRunning():
            self.execution_thread.stop_execution()
            self.status_label.setText("Cancelling execution...")
    
    def on_progress_update(self, current: int, total: int, message: str):
        """Handle progress updates from execution thread"""
        if total > 0:
            progress = int((current / total) * 100)
            self.progress_bar.setValue(progress)
        self.status_label.setText(message)
    
    def on_action_completed(self, action_index: int, success: bool, error_message: str):
        """Handle individual action completion"""
        status = "✅" if success else "❌"
        message = f"{status} Action {action_index + 1} {'completed' if success else 'failed'}"
        if error_message:
            message += f": {error_message}"
        print(message)  # For now, just print - could add to a log widget
    
    def on_execution_finished(self, result: dict):
        """Handle execution completion"""
        # Update UI back to ready state
        self.execute_btn.setVisible(True)
        self.cancel_btn.setVisible(False)
        self.progress_bar.setVisible(False)
        self.status_label.setVisible(False)
        
        # Show result
        if result['success']:
            QMessageBox.information(self, "Success", result['message'])
        else:
            error_details = "\n".join(result['errors']) if result['errors'] else "Unknown error"
            QMessageBox.critical(self, "Execution Failed", f"{result['message']}\n\nDetails:\n{error_details}")
        
        # Cleanup thread
        if self.execution_thread:
            self.execution_thread.deleteLater()
            self.execution_thread = None
    
    def hideEvent(self, event):
        """Handle page becoming inactive - cleanup any running execution"""
        super().hideEvent(event)
        if self.execution_thread and self.execution_thread.isRunning():
            print("🧹 Stopping execution due to page change...")
            self.execution_thread.stop_execution()
            self.execution_thread.wait(3000)  # Wait up to 3 seconds for cleanup
            if self.execution_thread:
                self.execution_thread.deleteLater()
                self.execution_thread = None