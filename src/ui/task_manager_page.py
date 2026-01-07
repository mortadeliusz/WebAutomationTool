"""
Task Manager Page - Manage and create automation tasks
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTableWidget, QTableWidgetItem,
                            QFrame, QLineEdit, QTextEdit, QSplitter,
                            QHeaderView, QComboBox, QMessageBox, QListWidget,
                            QListWidgetItem, QCheckBox, QDialog, QRadioButton,
                            QInputDialog, QScrollArea)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.task_storage import TaskStorage
from core.task_manager_worker import TaskManagerWorkerThread



class TaskManagerPage(QWidget):
    def __init__(self):
        super().__init__()
        self.builder_visible = False
        self.task_storage = TaskStorage()
        self.current_task = None
        self.current_actions = []
        self.worker_thread = None  # Persistent worker thread
        self.editing_action_index = -1  # Track if editing existing action
        self.setup_ui()
        self.refresh_task_list()  # Load tasks on startup
    
    def setup_ui(self):
        """Setup Task Manager page UI"""
        # Create scroll area for entire page
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Create main content widget
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(20)
        
        # Page title
        title = QLabel("Task Manager")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Toolbar
        toolbar = self.create_toolbar()
        layout.addWidget(toolbar)
        
        # Main content area with splitter
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Task list (top section)
        self.task_list_widget = self.create_task_list()
        self.splitter.addWidget(self.task_list_widget)
        
        # Task builder (bottom section - initially hidden)
        self.task_builder_widget = self.create_task_builder()
        self.task_builder_widget.setVisible(False)
        self.splitter.addWidget(self.task_builder_widget)
        
        # Set initial splitter sizes (100% to task list)
        self.splitter.setSizes([800, 0])
        
        layout.addWidget(self.splitter)
        
        # Set content widget to scroll area
        scroll.setWidget(content_widget)
        
        # Set scroll area as main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
    
    def create_toolbar(self):
        """Create toolbar with action buttons"""
        toolbar = QFrame()
        toolbar.setFrameStyle(QFrame.Shape.Box)
        toolbar.setStyleSheet("QFrame { border: 1px solid #ddd; border-radius: 6px; padding: 10px; }")
        
        layout = QHBoxLayout(toolbar)
        
        # Action buttons
        self.new_task_btn = QPushButton("➕ New Task")
        self.new_task_btn.clicked.connect(self.create_new_task)
        
        self.import_btn = QPushButton("📥 Import")
        self.export_btn = QPushButton("📤 Export")
        
        layout.addWidget(self.new_task_btn)
        layout.addWidget(self.import_btn)
        layout.addWidget(self.export_btn)
        
        # Search
        layout.addStretch()
        layout.addWidget(QLabel("🔍 Search:"))
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search tasks...")
        self.search_input.setMaximumWidth(200)
        layout.addWidget(self.search_input)
        
        return toolbar
    
    def create_task_list(self):
        """Create task list table"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.Box)
        frame.setStyleSheet("QFrame { border: 1px solid #ddd; border-radius: 6px; padding: 10px; }")
        
        layout = QVBoxLayout(frame)
        
        # Table
        self.task_table = QTableWidget()
        self.task_table.setColumnCount(4)
        self.task_table.setHorizontalHeaderLabels(["Task Name", "Description", "Modified", "Actions"])
        
        # Configure table
        header = self.task_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        # Single click to edit task
        self.task_table.itemClicked.connect(self.on_task_clicked)
        
        # Add sample data
        # self.populate_sample_tasks()  # Removed - using real tasks from storage
        
        layout.addWidget(self.task_table)
        
        return frame
    
    def create_task_builder(self):
        """Create task builder section"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.Box)
        frame.setStyleSheet("QFrame { border: 1px solid #ddd; border-radius: 6px; padding: 10px; }")
        
        layout = QVBoxLayout(frame)
        
        # Builder header
        header_layout = QHBoxLayout()
        
        self.builder_title = QLabel("Editing: New Task")
        self.builder_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(self.builder_title)
        
        header_layout.addStretch()
        
        close_btn = QPushButton("✖️ Close")
        close_btn.clicked.connect(self.close_builder)
        header_layout.addWidget(close_btn)
        
        layout.addLayout(header_layout)
        
        # Task details
        details_layout = QVBoxLayout()
        
        # Task name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Task Name:"))
        self.task_name_input = QLineEdit()
        self.task_name_input.setPlaceholderText("Enter task name...")
        name_layout.addWidget(self.task_name_input)
        details_layout.addLayout(name_layout)
        
        # Description
        desc_layout = QHBoxLayout()
        desc_layout.addWidget(QLabel("Description:"))
        self.task_desc_input = QLineEdit()
        self.task_desc_input.setPlaceholderText("Enter task description...")
        desc_layout.addWidget(self.task_desc_input)
        details_layout.addLayout(desc_layout)
        
        layout.addLayout(details_layout)
        
        # Uses data checkbox
        self.uses_data_checkbox = QCheckBox("This task does not use data (single execution)")
        layout.addWidget(self.uses_data_checkbox)
        
        # Setup section (placeholder)
        setup_frame = QFrame()
        setup_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        setup_frame.setStyleSheet("background-color: #f5f5f5; border-radius: 4px; padding: 10px;")
        
        setup_layout = QVBoxLayout(setup_frame)
        
        # Browser and URL setup
        browser_layout = QHBoxLayout()
        browser_layout.addWidget(QLabel("Browser:"))
        
        self.browser_combo = QComboBox()
        self.browser_combo.addItem("Chrome")
        self.browser_combo.addItem("Edge")
        browser_layout.addWidget(self.browser_combo)
        
        browser_layout.addWidget(QLabel("URL:"))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com")
        browser_layout.addWidget(self.url_input)
        
        setup_layout.addLayout(browser_layout)        
        layout.addWidget(setup_frame)
        
        # Actions section (placeholder)
        actions_frame = QFrame()
        actions_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        actions_frame.setStyleSheet("background-color: #f5f5f5; border-radius: 4px; padding: 10px;")
        
        actions_layout = QVBoxLayout(actions_frame)
        actions_layout.addWidget(QLabel("Actions:"))
        
        # Actions list
        self.actions_list = QListWidget()
        self.actions_list.setMaximumHeight(150)
        self.actions_list.itemClicked.connect(self.edit_action_item)  # Single click to edit
        actions_layout.addWidget(self.actions_list)
        
        # Action buttons
        action_buttons_layout = QHBoxLayout()
        
        add_action_btn = QPushButton("➕ Add Action")
        add_action_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
        """)
        add_action_btn.clicked.connect(self.show_action_form)
        
        delete_action_btn = QPushButton("🗑️ Delete Selected")
        delete_action_btn.clicked.connect(self.delete_selected_action)
        
        action_buttons_layout.addWidget(add_action_btn)
        action_buttons_layout.addWidget(delete_action_btn)
        action_buttons_layout.addStretch()
        
        actions_layout.addLayout(action_buttons_layout)
        
        # Action creation form (initially hidden)
        self.action_form = self.create_action_form()
        self.action_form.setVisible(False)
        actions_layout.addWidget(self.action_form)
        
        layout.addWidget(actions_frame)
        
        # Save/Cancel buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_btn = QPushButton("💾 Save Task")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
        """)
        save_btn.clicked.connect(self.save_task)
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.clicked.connect(self.close_builder)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        return frame
    
    def create_action_form(self):
        """Create action creation form"""
        form_frame = QFrame()
        form_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        form_frame.setStyleSheet("background-color: #e8f4fd; border-radius: 4px; padding: 10px; border: 2px solid #2196F3;")
        
        layout = QVBoxLayout(form_frame)
        
        # Form title
        title = QLabel("Add Action")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #2196F3;")
        layout.addWidget(title)
        
        # Action type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Action Type:"))
        
        self.action_type_combo = QComboBox()
        self.action_type_combo.addItems(["Set Value", "Click", "Navigate", "Wait"])
        self.action_type_combo.currentTextChanged.connect(self.on_action_type_changed)
        type_layout.addWidget(self.action_type_combo)
        type_layout.addStretch()
        layout.addLayout(type_layout)
        
        # Target element
        element_layout = QHBoxLayout()
        element_layout.addWidget(QLabel("Target Element:"))
        
        self.target_element_input = QLineEdit()
        self.target_element_input.setPlaceholderText("XPath selector will appear here...")
        element_layout.addWidget(self.target_element_input)
        
        self.pick_element_btn = QPushButton("🎯")
        self.pick_element_btn.setMaximumSize(30, 30)
        self.pick_element_btn.setStyleSheet("background-color: #2196F3; color: white; border: none; border-radius: 4px;")
        self.pick_element_btn.clicked.connect(self.pick_element_for_form)
        element_layout.addWidget(self.pick_element_btn)
        
        layout.addLayout(element_layout)
        
        # Value field
        value_layout = QHBoxLayout()
        self.value_label = QLabel("Value:")
        value_layout.addWidget(self.value_label)
        
        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText("Enter value...")
        value_layout.addWidget(self.value_input)
        value_layout.addStretch()
        layout.addLayout(value_layout)
        
        # Description
        desc_layout = QHBoxLayout()
        desc_layout.addWidget(QLabel("Description:"))
        
        self.action_desc_input = QLineEdit()
        self.action_desc_input.setPlaceholderText("Optional description...")
        desc_layout.addWidget(self.action_desc_input)
        layout.addLayout(desc_layout)
        
        # Form buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.add_action_btn = QPushButton("Add Action")
        self.add_action_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 6px 12px; border: none; border-radius: 4px;")
        self.add_action_btn.clicked.connect(self.add_action_from_form)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.hide_action_form)
        
        button_layout.addWidget(self.add_action_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        return form_frame
    
    def populate_sample_tasks(self):
        """Add sample tasks to the table"""
        sample_tasks = [
            ("Contact Form Entry", "Enters contact information into web form", "2 days ago"),
            ("Product Upload", "Bulk product upload to e-commerce site", "1 week ago"),
            ("Survey Responses", "Submit survey responses automatically", "3 days ago")
        ]
        
        self.task_table.setRowCount(len(sample_tasks))
        
        for row, (name, desc, modified) in enumerate(sample_tasks):
            self.task_table.setItem(row, 0, QTableWidgetItem(name))
            self.task_table.setItem(row, 1, QTableWidgetItem(desc))
            self.task_table.setItem(row, 2, QTableWidgetItem(modified))
            
            # Action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setMaximumSize(30, 30)
            edit_btn.clicked.connect(lambda checked, r=row: self.edit_task(r))
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setMaximumSize(30, 30)
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.addStretch()
            
            self.task_table.setCellWidget(row, 3, actions_widget)
    
    def create_new_task(self):
        """Create a new task"""
        self.clear_all_task_fields()  # Clear everything first
        self.show_builder("New Task")
    
    def clear_all_task_fields(self):
        """Clear all task creation fields"""
        self.task_name_input.clear()
        self.task_desc_input.clear()
        self.url_input.clear()
        self.browser_combo.setCurrentIndex(0)
        self.uses_data_checkbox.setChecked(False)
        self.current_actions.clear()
        self.actions_list.clear()
        self.clear_action_form()
        self.action_form.setVisible(False)  # Always hide action form for new tasks
        self.editing_action_index = -1
    
    def edit_task(self, row):
        """Edit existing task (legacy method - now handled by on_task_clicked)"""
        # This method is kept for compatibility but functionality moved to on_task_clicked
        pass
    
    def show_builder(self, task_name):
        """Show task builder section"""
        self.builder_visible = True
        self.task_builder_widget.setVisible(True)
        self.builder_title.setText(f"Editing: {task_name}")
        
        # Adjust splitter sizes (20% list, 80% builder)
        self.splitter.setSizes([160, 640])
    
    def close_builder(self):
        """Close task builder section"""
        self.builder_visible = False
        self.task_builder_widget.setVisible(False)
        
        # Adjust splitter sizes (100% list)
        self.splitter.setSizes([800, 0])
    
    def save_task(self):
        """Save current task"""
        task_name = self.task_name_input.text().strip()
        task_desc = self.task_desc_input.text().strip()
        browser = self.browser_combo.currentText().lower()
        url = self.url_input.text().strip()
        uses_data = not self.uses_data_checkbox.isChecked()  # Checkbox is "does NOT use data"
        
        if not task_name:
            QMessageBox.warning(self, "Warning", "Please enter a task name")
            return
        
        if not url:
            QMessageBox.warning(self, "Warning", "Please enter a URL")
            return
        
        # Create task
        task = self.task_storage.create_task_template(task_name, task_desc, browser, url, uses_data)
        task['actions'] = self.current_actions.copy()
        
        # Save task
        if self.task_storage.save_task(task):
            QMessageBox.information(self, "Success", f"Task '{task_name}' saved successfully!")
            self.close_builder()
            self.refresh_task_list()  # Refresh the list to show new task
            self.current_actions.clear()  # Clear actions for next task
        else:
            QMessageBox.critical(self, "Error", "Failed to save task")
    
    def pick_element(self):
        """Pick element functionality for real task building"""
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Warning", "Please enter a URL first")
            return
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            self.url_input.setText(url)
        
        # Disable button during picking
        sender = self.sender()
        sender.setEnabled(False)
        sender.setText("Picking...")
        
        # Run element picker in separate thread
        browser_type = 'chrome' if 'Chrome' in self.browser_combo.currentText() else 'edge'
        self.picker_thread = ElementPickerThread(browser_type, url)
        self.picker_thread.result_ready.connect(self.on_element_picked)
        self.picker_thread.error_occurred.connect(self.on_picker_error)
        self.picker_thread.finished.connect(lambda: self.reset_picker_button(sender))
        self.picker_thread.start()
    
    def on_element_picked(self, result):
        """Handle element picker results - add to task actions"""
        if result['selector']:
            # Show action type selection dialog
            from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QRadioButton, QLineEdit
            
            dialog = QDialog(self)
            dialog.setWindowTitle("Create Action")
            dialog.setModal(True)
            
            layout = QVBoxLayout(dialog)
            
            # Show selected element info
            info_label = QLabel(f"Selected element: {result['selector'][:50]}...")
            layout.addWidget(info_label)
            
            # Action type selection
            layout.addWidget(QLabel("Choose action type:"))
            
            click_radio = QRadioButton("Click this element")
            click_radio.setChecked(True)
            layout.addWidget(click_radio)
            
            set_value_radio = QRadioButton("Set value in this element")
            layout.addWidget(set_value_radio)
            
            # Value input for set_value
            value_label = QLabel("Value (for set_value):")
            value_input = QLineEdit()
            value_input.setPlaceholderText("Enter static value...")
            layout.addWidget(value_label)
            layout.addWidget(value_input)
            
            # Buttons
            button_layout = QHBoxLayout()
            ok_btn = QPushButton("Add Action")
            cancel_btn = QPushButton("Cancel")
            
            ok_btn.clicked.connect(dialog.accept)
            cancel_btn.clicked.connect(dialog.reject)
            
            button_layout.addWidget(ok_btn)
            button_layout.addWidget(cancel_btn)
            layout.addLayout(button_layout)
            
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # Create action based on selection
                if click_radio.isChecked():
                    action = {
                        'type': 'click',
                        'selector': result['selector'],
                        'description': f"Click element ({result['reliability']} reliability)"
                    }
                else:
                    action = {
                        'type': 'set_value',
                        'selector': result['selector'],
                        'value': value_input.text(),
                        'description': f"Set value '{value_input.text()}' ({result['reliability']} reliability)"
                    }
                
                self.add_action_to_list(action)
        else:
            QMessageBox.warning(self, "Warning", "No element was selected")
    
    def on_picker_error(self, error_msg):
        """Handle element picker errors"""
        QMessageBox.critical(self, "Error", f"Element picker failed: {error_msg}")
    
    def reset_picker_button(self, button):
        """Reset element picker button state"""
        button.setEnabled(True)
        button.setText("🎯 Pick Element")
    
    def add_action_to_list(self, action):
        """Add action to the actions list"""
        self.current_actions.append(action)
        
        # Add to UI list
        item_text = f"{len(self.current_actions)}. {action['description']}"
        self.actions_list.addItem(item_text)
    
    def add_navigate_action(self):
        """Add navigate action"""
        url, ok = QInputDialog.getText(self, "Navigate Action", "Enter URL:")
        if ok and url:
            action = {
                'type': 'navigate',
                'url': url,
                'description': f"Navigate to {url}"
            }
            self.add_action_to_list(action)
    
    def add_wait_action(self):
        """Add wait action"""
        duration, ok = QInputDialog.getDouble(self, "Wait Action", "Wait duration (seconds):", 1.0, 0.1, 60.0, 1)
        if ok:
            action = {
                'type': 'wait',
                'duration': duration,
                'description': f"Wait {duration} seconds"
            }
            self.add_action_to_list(action)
    
    def refresh_task_list(self):
        """Refresh the task list from storage"""
        tasks = self.task_storage.list_tasks()
        
        # Clear current table
        self.task_table.setRowCount(0)
        
        # Add tasks from storage
        self.task_table.setRowCount(len(tasks))
        
        for row, task in enumerate(tasks):
            self.task_table.setItem(row, 0, QTableWidgetItem(task['name']))
            self.task_table.setItem(row, 1, QTableWidgetItem(task['description']))
            self.task_table.setItem(row, 2, QTableWidgetItem(task.get('modified_at', 'Unknown')))
            
            # Action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setMaximumSize(30, 30)
            delete_btn.clicked.connect(lambda checked, r=row: self.delete_task_from_storage(tasks[r]['name']))
            
            actions_layout.addWidget(delete_btn)
            actions_layout.addStretch()
            
            self.task_table.setCellWidget(row, 3, actions_widget)
    
    def show_action_form(self):
        """Show action creation form"""
        if self.editing_action_index == -1:
            self.clear_action_form()  # Only clear if creating new action
            self.add_action_btn.setText("Add Action")
        else:
            self.add_action_btn.setText("Update Action")
        
        self.action_form.setVisible(True)
        self.on_action_type_changed()  # Update form fields based on action type
    
    def hide_action_form(self):
        """Hide action creation form"""
        self.action_form.setVisible(False)
        self.clear_action_form()
        self.editing_action_index = -1  # Reset editing state
    
    def clear_action_form(self):
        """Clear action form fields"""
        self.target_element_input.clear()
        self.value_input.clear()
        self.action_desc_input.clear()
        self.action_type_combo.setCurrentIndex(0)
    
    def on_action_type_changed(self):
        """Handle action type change - show/hide relevant fields"""
        action_type = self.action_type_combo.currentText()
        
        if action_type == "Navigate":
            # Navigate: hide target element, show value as URL
            self.target_element_input.setVisible(False)
            self.pick_element_btn.setVisible(False)
            self.value_label.setText("URL:")
            self.value_input.setPlaceholderText("https://example.com")
            self.value_input.setVisible(True)
            
        elif action_type == "Wait":
            # Wait: hide target element, show value as duration
            self.target_element_input.setVisible(False)
            self.pick_element_btn.setVisible(False)
            self.value_label.setText("Duration (seconds):")
            self.value_input.setPlaceholderText("1.0")
            self.value_input.setVisible(True)
            
        elif action_type == "Click":
            # Click: show target element, hide value
            self.target_element_input.setVisible(True)
            self.pick_element_btn.setVisible(True)
            self.value_label.setText("Value:")
            self.value_input.setVisible(False)
            
        else:  # Set Value
            # Set Value: show both target element and value
            self.target_element_input.setVisible(True)
            self.pick_element_btn.setVisible(True)
            self.value_label.setText("Value:")
            self.value_input.setPlaceholderText("Enter value to set...")
            self.value_input.setVisible(True)
    
    def pick_element_for_form(self):
        """Pick element to populate form field"""
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Warning", "Please enter a URL first")
            return
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            self.url_input.setText(url)
        
        if not self.worker_thread:
            QMessageBox.critical(self, "Error", "Task Manager worker not available")
            return
        
        # Disable button during picking
        self.pick_element_btn.setEnabled(False)
        self.pick_element_btn.setText("...")
        
        # Check if browser exists, launch only if needed
        if not self.worker_thread.is_browser_running():
            self.worker_thread.launch_browser('chrome')
        
        # Navigate and pick
        self.worker_thread.navigate_to(url)
    
    def on_element_picked_for_form(self, result):
        """Handle element picker result for form"""
        if result['selector']:
            # Populate the target element field
            self.target_element_input.setText(result['selector'])
            
            # Auto-generate description if empty
            if not self.action_desc_input.text():
                action_type = self.action_type_combo.currentText()
                reliability = result['reliability']
                self.action_desc_input.setText(f"{action_type} element ({reliability} reliability)")
        else:
            QMessageBox.warning(self, "Warning", "No element was selected")
        
        self.reset_form_picker_button()
    
    def reset_form_picker_button(self):
        """Reset form picker button"""
        self.pick_element_btn.setEnabled(True)
        self.pick_element_btn.setText("🎯")
    
    def add_action_from_form(self):
        """Add action from form to actions list"""
        action_type = self.action_type_combo.currentText().lower().replace(' ', '_')
        target_element = self.target_element_input.text().strip()
        value = self.value_input.text().strip()
        description = self.action_desc_input.text().strip()
        
        # Validation
        if action_type in ['click', 'set_value'] and not target_element:
            QMessageBox.warning(self, "Warning", "Please select a target element")
            return
        
        if action_type in ['navigate', 'wait', 'set_value'] and not value:
            QMessageBox.warning(self, "Warning", "Please enter a value")
            return
        
        # Create action
        action = {'type': action_type}
        
        if target_element:
            action['selector'] = target_element
        
        if value:
            if action_type == 'navigate':
                action['url'] = value
            elif action_type == 'wait':
                try:
                    action['duration'] = float(value)
                except ValueError:
                    QMessageBox.warning(self, "Warning", "Duration must be a number")
                    return
            else:
                action['value'] = value
        
        if description:
            action['description'] = description
        else:
            # Auto-generate description
            if action_type == 'navigate':
                action['description'] = f"Navigate to {value}"
            elif action_type == 'wait':
                action['description'] = f"Wait {value} seconds"
            elif action_type == 'click':
                action['description'] = f"Click element"
            else:
                action['description'] = f"Set value '{value}'"
        
        # Add or update action
        if self.editing_action_index >= 0:
            # Update existing action
            self.current_actions[self.editing_action_index] = action
            self.refresh_actions_list()
        else:
            # Add new action
            self.add_action_to_list(action)
        
        # Hide form
        self.hide_action_form()
    
    def edit_task_from_storage(self, task_name):
        """Edit task loaded from storage"""
        task = self.task_storage.load_task(task_name)
        if task:
            self.show_builder(task_name)
            self.task_name_input.setText(task['name'])
            self.task_desc_input.setText(task.get('description', ''))
            self.url_input.setText(task.get('setup', {}).get('url', ''))
            
            # Load browser selection
            browser = task.get('setup', {}).get('browser', 'chrome')
            if browser == 'chrome':
                self.browser_combo.setCurrentText('Chrome')
            elif browser == 'edge':
                self.browser_combo.setCurrentText('Edge')
            
            # Load actions
            self.current_actions = task.get('actions', [])
            self.actions_list.clear()
            for i, action in enumerate(self.current_actions):
                item_text = f"{i+1}. {action.get('description', action['type'])}"
                self.actions_list.addItem(item_text)
            
            # Ensure action form is hidden and no action is selected
            self.action_form.setVisible(False)
            self.actions_list.clearSelection()
            self.editing_action_index = -1
    
    def on_task_clicked(self, item):
        """Handle task table click - edit task"""
        if item.column() < 3:  # Don't trigger on action buttons column
            row = item.row()
            task_name = self.task_table.item(row, 0).text()
            self.edit_task_from_storage(task_name)
    
    def delete_task_from_storage(self, task_name):
        """Delete task from storage"""
        reply = QMessageBox.question(self, "Delete Task", 
                                   f"Are you sure you want to delete '{task_name}'?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.task_storage.delete_task(task_name):
                QMessageBox.information(self, "Success", f"Task '{task_name}' deleted successfully!")
                self.refresh_task_list()
            else:
                QMessageBox.critical(self, "Error", "Failed to delete task")
    
    def showEvent(self, event):
        """Handle page becoming active - start worker thread"""
        super().showEvent(event)
        if not self.worker_thread:
            print("🔧 Starting Task Manager worker thread...")
            self.worker_thread = TaskManagerWorkerThread()
            
            # Connect signals
            self.worker_thread.browser_ready.connect(self.on_browser_ready)
            self.worker_thread.navigation_complete.connect(self.on_navigation_complete)
            self.worker_thread.element_picked.connect(self.on_element_picked_for_form)
            self.worker_thread.error_occurred.connect(self.on_worker_error)
            
            # Start the persistent thread
            self.worker_thread.start()
    
    def hideEvent(self, event):
        """Handle page becoming inactive - stop worker thread"""
        super().hideEvent(event)
        if self.worker_thread:
            print("🧹 Stopping Task Manager worker thread...")
            self.worker_thread.stop_worker()
            self.worker_thread.wait(5000)  # Wait up to 5 seconds
            self.worker_thread.deleteLater()
            self.worker_thread = None
    
    def on_browser_ready(self, success):
        """Handle browser launch result"""
        if success:
            print("✅ Task Manager browser ready")
        else:
            QMessageBox.critical(self, "Error", "Failed to launch browser")
            self.reset_form_picker_button()
    
    def on_navigation_complete(self, success):
        """Handle navigation result"""
        if success:
            print("✅ Navigation complete, starting element picker...")
            self.worker_thread.pick_element()
        else:
            QMessageBox.critical(self, "Error", "Failed to navigate to URL")
            self.reset_form_picker_button()
    
    def on_worker_error(self, error_msg):
        """Handle worker thread errors"""
        print(f"❌ Worker error: {error_msg}")
        QMessageBox.critical(self, "Error", f"Task Manager error: {error_msg}")
        self.reset_form_picker_button()
    
    def delete_selected_action(self):
        """Delete selected action from list"""
        current_row = self.actions_list.currentRow()
        if current_row >= 0:
            # Remove from actions list
            del self.current_actions[current_row]
            
            # Remove from UI
            self.actions_list.takeItem(current_row)
            
            # Renumber remaining actions
            self.refresh_actions_list()
    
    def edit_action_item(self, item):
        """Edit action on double-click"""
        current_row = self.actions_list.currentRow()
        if current_row >= 0:
            action = self.current_actions[current_row]
            
            # Populate form with action data
            self.action_type_combo.setCurrentText(action['type'].replace('_', ' ').title())
            
            if 'selector' in action:
                self.target_element_input.setText(action['selector'])
            
            if 'value' in action:
                self.value_input.setText(str(action['value']))
            elif 'url' in action:
                self.value_input.setText(action['url'])
            elif 'duration' in action:
                self.value_input.setText(str(action['duration']))
            
            if 'description' in action:
                self.action_desc_input.setText(action['description'])
            
            # Show form and mark as editing
            self.editing_action_index = current_row
            self.show_action_form()
    
    def refresh_actions_list(self):
        """Refresh the actions list display"""
        self.actions_list.clear()
        for i, action in enumerate(self.current_actions):
            item_text = f"{i+1}. {action.get('description', action['type'])}"
            self.actions_list.addItem(item_text)