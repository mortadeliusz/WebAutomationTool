"""
Main Window - Primary application window with page navigation
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QStackedWidget, QMenuBar, QStatusBar)
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
        self.setup_menu()
        self.setup_status_bar()
        
        # Start on Task Execution page
        self.show_task_execution()
    
    def setup_ui(self):
        """Setup main UI layout"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Navigation buttons
        nav_layout = QHBoxLayout()
        
        self.btn_task_execution = QPushButton("Task Execution")
        self.btn_task_manager = QPushButton("Task Manager")
        self.btn_subscription = QPushButton("Subscription")
        
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
        layout.addLayout(nav_layout)
        layout.addWidget(self.page_stack)
    
    def setup_menu(self):
        """Setup menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Settings menu
        settings_menu = menubar.addMenu("Settings")
        
        preferences_action = QAction("Preferences", self)
        settings_menu.addAction(preferences_action)
    
    def setup_status_bar(self):
        """Setup status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def show_task_execution(self):
        """Show Task Execution page"""
        self.page_stack.setCurrentWidget(self.task_execution_page)
        self.update_nav_buttons("execution")
        self.status_bar.showMessage("Task Execution")
    
    def show_task_manager(self):
        """Show Task Manager page"""
        self.page_stack.setCurrentWidget(self.task_manager_page)
        self.update_nav_buttons("manager")
        self.status_bar.showMessage("Task Manager")
    
    def show_subscription(self):
        """Show Subscription page"""
        self.page_stack.setCurrentWidget(self.subscription_page)
        self.update_nav_buttons("subscription")
        self.status_bar.showMessage("Subscription")
    
    def update_nav_buttons(self, active_page):
        """Update navigation button styles"""
        # Reset all buttons
        for btn in [self.btn_task_execution, self.btn_task_manager, self.btn_subscription]:
            btn.setStyleSheet("")
        
        # Highlight active button
        if active_page == "execution":
            self.btn_task_execution.setStyleSheet("background-color: #e3f2fd;")
        elif active_page == "manager":
            self.btn_task_manager.setStyleSheet("background-color: #e3f2fd;")
        elif active_page == "subscription":
            self.btn_subscription.setStyleSheet("background-color: #e3f2fd;")