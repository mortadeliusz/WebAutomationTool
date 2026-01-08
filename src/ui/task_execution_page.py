"""
Task Execution Page - Landing page for running automation tasks
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QComboBox, QPushButton, QTableWidget, QProgressBar,
                            QFrame, QTextEdit, QMessageBox)
from PyQt6.QtCore import Qt
import sys
import os
import pandas as pd

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.task_storage import TaskStorage
from core.task_execution_thread import TaskExecutionThread
from core.template_evaluator import TemplateEvaluator
from ui.data_loading_widget import DataLoadingWidget
from ui.styles import Styles

class TaskExecutionPage(QWidget):
    def __init__(self):
        super().__init__()
        self.task_storage = TaskStorage()
        self.template_evaluator = TemplateEvaluator()
        self.execution_thread = None
        self.current_data = None
        self.setup_ui()
        self.refresh_tasks()  # Load tasks on startup
    
    def setup_ui(self):
        """Setup Task Execution page UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Task selection
        task_section = self.create_task_selection()
        layout.addWidget(task_section)
        
        # Data loading section
        data_section = self.create_data_section()
        layout.addWidget(data_section)
        
        # Execute/Cancel button
        execute_layout = QHBoxLayout()
        execute_layout.addStretch()
        
        self.execute_btn = QPushButton("Execute Task")
        Styles.primary_button(self.execute_btn)
        self.execute_btn.clicked.connect(self.execute_task)
        
        self.cancel_btn = QPushButton("Cancel")
        Styles.danger_button(self.cancel_btn)
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
        frame.setStyleSheet("""
            QFrame { 
                border: 1px solid #ddd; 
                border-radius: 8px; 
                padding: 10px;
                background-color: white;
            }
        """)
        
        layout = QVBoxLayout(frame)
        
        # Task selection - no redundant title
        task_layout = QHBoxLayout()
        
        task_label = QLabel("Task:")
        task_label.setStyleSheet("font-size: 14px; color: #555; min-width: 60px;")
        task_layout.addWidget(task_label)
        
        self.task_combo = QComboBox()
        self.task_combo.addItem("No tasks available")
        self.task_combo.setMinimumWidth(350)
        Styles.standard_dropdown(self.task_combo)
        task_layout.addWidget(self.task_combo)
        
        refresh_btn = QPushButton("Refresh")
        Styles.secondary_button(refresh_btn)
        refresh_btn.clicked.connect(self.refresh_tasks)
        task_layout.addWidget(refresh_btn)
        
        task_layout.addStretch()
        layout.addLayout(task_layout)
        
        return frame
    
    def create_data_section(self):
        """Create data loading section"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.Box)
        frame.setStyleSheet("""
            QFrame { 
                border: 1px solid #ddd; 
                border-radius: 8px; 
                padding: 15px;
                background-color: white;
            }
        """)
        
        layout = QVBoxLayout(frame)
        
        # Data loading widget - no title needed
        self.data_widget = DataLoadingWidget()
        self.data_widget.data_loaded.connect(self.on_data_loaded)
        layout.addWidget(self.data_widget)
        
        return frame
    
    def create_progress_section(self):
        """Create progress tracking section"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.Box)
        frame.setStyleSheet("""
            QFrame { 
                border: 1px solid #ddd; 
                border-radius: 8px; 
                padding: 10px;
                background-color: white;
            }
        """)
        
        layout = QVBoxLayout(frame)
        
        # Progress bar - no redundant title
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ddd;
                border-radius: 8px;
                text-align: center;
                font-size: 14px;
                font-weight: bold;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 6px;
            }
        """)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status text
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("""
            font-size: 14px; 
            color: #555; 
            margin-top: 8px;
            padding: 8px;
            background-color: #f8f9fa;
            border-radius: 4px;
        """)
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
    
    def on_data_loaded(self, df: pd.DataFrame):
        """Handle data being loaded"""
        self.current_data = df
        print(f"📊 Data loaded: {len(df)} rows, {len(df.columns)} columns")
        
        # Validate current task if one is selected
        self.validate_current_task()
    
    def validate_current_task(self):
        """Validate current task against loaded data"""
        task_name = self.task_combo.currentText()
        if task_name == "No tasks available" or not self.current_data is not None:
            return
        
        task = self.task_storage.load_task(task_name)
        if not task:
            return
        
        # Validate templates
        validation = self.template_evaluator.validate_task_templates(task, self.current_data)
        
        if not validation['valid']:
            missing = ", ".join(validation['missing_columns'])
            QMessageBox.warning(
                self, 
                "Template Validation", 
                f"Task requires columns that are not in the data:\n{missing}\n\nAvailable columns: {', '.join(validation['available_columns'])}"
            )
    
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
        
        # Check if task needs data
        needs_data = self.task_needs_data(task)
        
        if needs_data and self.current_data is None:
            QMessageBox.warning(self, "Warning", "This task requires data. Please load data first.")
            return
        
        # Validate templates if data is provided
        if self.current_data is not None:
            validation = self.template_evaluator.validate_task_templates(task, self.current_data)
            if not validation['valid']:
                missing = ", ".join(validation['missing_columns'])
                QMessageBox.critical(
                    self, 
                    "Template Validation Failed", 
                    f"Task requires columns that are not in the data:\n{missing}\n\nAvailable columns: {', '.join(validation['available_columns'])}"
                )
                return
        
        # Start execution in worker thread
        self.execution_thread = TaskExecutionThread(task, self.current_data)
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
    
    def task_needs_data(self, task: dict) -> bool:
        """Check if task contains any template expressions that require data"""
        required_columns = self.template_evaluator.extract_required_columns(task)
        return len(required_columns) > 0
    
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