"""
Main Window - Primary application window with page navigation
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QStackedWidget, QMenuBar, QStatusBar, QLabel)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction

from .task_execution_page import TaskExecutionPage
from .task_manager_page import TaskManagerPage
from .subscription_page import SubscriptionPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Web Automation Tool")
        self.setGeometry(100, 100, 1200, 800)
        
        self.setup_ui()
        
        # Start on Task Execution page
        self.show_task_execution()
    
    def setup_ui(self):
        """Setup main UI layout"""
        central_widget = QWidget()
        central_widget.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
            }
        """)
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Navigation buttons
        nav_widget = QWidget()
        nav_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-bottom: 2px solid #e0e0e0;
            }
        """)
        nav_layout = QHBoxLayout(nav_widget)
        nav_layout.setContentsMargins(20, 15, 20, 15)
        
        # App title
        app_title = QLabel("🤖 Web Automation Tool")
        app_title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #2c3e50;
            margin-right: 30px;
        """)
        nav_layout.addWidget(app_title)
        
        self.btn_task_execution = QPushButton("🚀 Task Execution")
        self.btn_task_manager = QPushButton("🛠️ Task Manager")
        self.btn_subscription = QPushButton("💳 Subscription")
        
        # Style navigation buttons
        nav_button_style = """
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: 500;
                color: #555;
                border-radius: 6px;
                margin: 0 5px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
                color: #333;
            }
            QPushButton:pressed {
                background-color: #e0e0e0;
            }
        """
        
        for btn in [self.btn_task_execution, self.btn_task_manager, self.btn_subscription]:
            btn.setStyleSheet(nav_button_style)
        
        self.btn_task_execution.clicked.connect(self.show_task_execution)
        self.btn_task_manager.clicked.connect(self.show_task_manager)
        self.btn_subscription.clicked.connect(self.show_subscription)
        
        nav_layout.addWidget(self.btn_task_execution)
        nav_layout.addWidget(self.btn_task_manager)
        nav_layout.addWidget(self.btn_subscription)
        nav_layout.addStretch()
        
        # Page stack
        self.page_stack = QStackedWidget()
        
        # Create pages
        self.task_execution_page = TaskExecutionPage()
        self.task_manager_page = TaskManagerPage()
        self.subscription_page = SubscriptionPage()
        
        # Add pages to stack
        self.page_stack.addWidget(self.task_execution_page)
        self.page_stack.addWidget(self.task_manager_page)
        self.page_stack.addWidget(self.subscription_page)
        
        # Add to layout
        layout.addWidget(nav_widget)
        layout.addWidget(self.page_stack)
    


    def show_task_execution(self):
        """Show Task Execution page"""
        self.page_stack.setCurrentWidget(self.task_execution_page)
        self.update_nav_buttons("execution")
    
    def show_task_manager(self):
        """Show Task Manager page"""
        self.page_stack.setCurrentWidget(self.task_manager_page)
        self.update_nav_buttons("manager")
    
    def show_subscription(self):
        """Show Subscription page"""
        self.page_stack.setCurrentWidget(self.subscription_page)
        self.update_nav_buttons("subscription")
    
    def update_nav_buttons(self, active_page):
        """Update navigation button styles"""
        # Active button style
        active_style = """
            QPushButton {
                background-color: #4CAF50;
                border: none;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: 600;
                color: white;
                border-radius: 6px;
                margin: 0 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """
        
        # Inactive button style
        inactive_style = """
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: 500;
                color: #555;
                border-radius: 6px;
                margin: 0 5px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
                color: #333;
            }
            QPushButton:pressed {
                background-color: #e0e0e0;
            }
        """
        
        # Reset all buttons to inactive
        for btn in [self.btn_task_execution, self.btn_task_manager, self.btn_subscription]:
            btn.setStyleSheet(inactive_style)
        
        # Set active button
        if active_page == "execution":
            self.btn_task_execution.setStyleSheet(active_style)
        elif active_page == "manager":
            self.btn_task_manager.setStyleSheet(active_style)
        elif active_page == "subscription":
            self.btn_subscription.setStyleSheet(active_style)