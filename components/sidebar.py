import customtkinter as ctk
from pages.task_execution import TaskExecutionPage
from pages.task_management import TaskManagementPage
from pages.subscription import SubscriptionPage
from pages.test_page import TestPage
from pages.browser_test import BrowserTestPage
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from components.main_content import MainContent

class Sidebar(ctk.CTkFrame):
    def __init__(self, parent, main_content: 'MainContent'):
        super().__init__(parent)
        self.main_content = main_content
        
        # Create page instances
        self.task_execution_page: TaskExecutionPage = TaskExecutionPage(main_content)
        self.task_management_page: TaskManagementPage = TaskManagementPage(main_content)
        self.subscription_page: SubscriptionPage = SubscriptionPage(main_content)
        self.test_page: TestPage = TestPage(main_content)
        self.browser_test_page: BrowserTestPage = BrowserTestPage(main_content)
        
        self.create_menu()
        
        # Show default page
        self.main_content.show_page(self.task_execution_page)
    
    def create_menu(self) -> None:
        self.btn_task_execution = ctk.CTkButton(self, text="Task Execution", command=lambda: self.main_content.show_page(self.task_execution_page))
        self.btn_task_execution.pack(pady=10, padx=10)
        
        self.btn_task_management = ctk.CTkButton(self, text="Task Management", command=lambda: self.main_content.show_page(self.task_management_page))
        self.btn_task_management.pack(pady=10, padx=10)
        
        self.btn_subscription = ctk.CTkButton(self, text="Subscription", command=lambda: self.main_content.show_page(self.subscription_page))
        self.btn_subscription.pack(pady=10, padx=10)
        
        # Test page button
        self.btn_test = ctk.CTkButton(self, text="Test Page", command=lambda: self.main_content.show_page(self.test_page))
        self.btn_test.pack(pady=10, padx=10)
        
        # Browser test button
        self.btn_browser_test = ctk.CTkButton(self, text="Browser Test", command=lambda: self.main_content.show_page(self.browser_test_page))
        self.btn_browser_test.pack(pady=10, padx=10)