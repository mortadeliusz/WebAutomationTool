"""
Test page for DataExpressionHelper component
Tests both scenarios: with data and without data
"""

import customtkinter as ctk
import pandas as pd
from ui.components.fields.data_expression_helper import DataExpressionHelper


class DataExpressionHelperTestPage(ctk.CTkFrame):
    """Test page for data expression helper"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup test UI"""
        # Title
        title = ctk.CTkLabel(
            self,
            text="Data Expression Helper Test",
            font=("", 20, "bold")
        )
        title.pack(pady=20)
        
        # Test 1: Without data
        section1 = ctk.CTkFrame(self)
        section1.pack(fill="x", padx=20, pady=10)
        
        label1 = ctk.CTkLabel(
            section1,
            text="Test 1: No Data Loaded (should show educational popup)",
            font=("", 14, "bold")
        )
        label1.pack(pady=10, anchor="w")
        
        input_frame1 = ctk.CTkFrame(section1, fg_color="transparent")
        input_frame1.pack(fill="x", pady=10)
        
        self.entry1 = ctk.CTkEntry(
            input_frame1,
            placeholder_text="Click 📊 to test without data..."
        )
        self.entry1.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.helper1 = DataExpressionHelper(
            input_frame1,
            target_entry=self.entry1,
            data_sample=None,
            on_load_data=self.simulate_load_data
        )
        self.helper1.pack(side="left")
        
        # Test 2: With data
        section2 = ctk.CTkFrame(self)
        section2.pack(fill="x", padx=20, pady=10)
        
        label2 = ctk.CTkLabel(
            section2,
            text="Test 2: Data Loaded (should show column selector)",
            font=("", 14, "bold")
        )
        label2.pack(pady=10, anchor="w")
        
        input_frame2 = ctk.CTkFrame(section2, fg_color="transparent")
        input_frame2.pack(fill="x", pady=10)
        
        self.entry2 = ctk.CTkEntry(
            input_frame2,
            placeholder_text="Click 📊 to test with data..."
        )
        self.entry2.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        # Create sample data
        sample_data = pd.DataFrame({
            'email': ['test@example.com', 'user@test.com'],
            'firstname': ['John', 'Jane'],
            'lastname': ['Doe', 'Smith'],
            'phone': ['555-1234', '555-5678'],
            'address': ['123 Main St', '456 Oak Ave'],
            'city': ['New York', 'Los Angeles'],
            'state': ['NY', 'CA'],
            'zipcode': ['10001', '90001']
        })
        
        self.helper2 = DataExpressionHelper(
            input_frame2,
            target_entry=self.entry2,
            data_sample=sample_data
        )
        self.helper2.pack(side="left")
        
        # Test 3: Multiple insertions (test cursor position)
        section3 = ctk.CTkFrame(self)
        section3.pack(fill="x", padx=20, pady=10)
        
        label3 = ctk.CTkLabel(
            section3,
            text="Test 3: Multiple Insertions (test cursor position)",
            font=("", 14, "bold")
        )
        label3.pack(pady=10, anchor="w")
        
        hint3 = ctk.CTkLabel(
            section3,
            text='Try: Type "Hello ", click 📊 select firstname, type " ", click 📊 select lastname',
            text_color="gray"
        )
        hint3.pack(pady=(0, 10), anchor="w")
        
        input_frame3 = ctk.CTkFrame(section3, fg_color="transparent")
        input_frame3.pack(fill="x", pady=10)
        
        self.entry3 = ctk.CTkEntry(
            input_frame3,
            placeholder_text="Test hybrid expressions..."
        )
        self.entry3.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.helper3 = DataExpressionHelper(
            input_frame3,
            target_entry=self.entry3,
            data_sample=sample_data
        )
        self.helper3.pack(side="left")
        
        # Test 4: Search filtering
        section4 = ctk.CTkFrame(self)
        section4.pack(fill="x", padx=20, pady=10)
        
        label4 = ctk.CTkLabel(
            section4,
            text="Test 4: Search Filtering (type 'mail' in search)",
            font=("", 14, "bold")
        )
        label4.pack(pady=10, anchor="w")
        
        input_frame4 = ctk.CTkFrame(section4, fg_color="transparent")
        input_frame4.pack(fill="x", pady=10)
        
        self.entry4 = ctk.CTkEntry(
            input_frame4,
            placeholder_text="Test search filtering..."
        )
        self.entry4.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.helper4 = DataExpressionHelper(
            input_frame4,
            target_entry=self.entry4,
            data_sample=sample_data
        )
        self.helper4.pack(side="left")
        
        # Instructions
        instructions = ctk.CTkLabel(
            self,
            text="Test Instructions:\n"
                 "1. Test 1: Click 📊 - should show educational popup\n"
                 "2. Test 2: Click 📊 - should show column selector with 8 columns\n"
                 "3. Test 3: Build hybrid expression like 'Hello {{col('firstname')}} {{col('lastname')}}'\n"
                 "4. Test 4: Click 📊, type 'mail' in search - should filter to 'email' only\n"
                 "5. Verify zebra striping and hover effects in column selector\n"
                 "6. Verify clicking name inserts {{col('name')}} and index inserts {{col(0)}}",
            justify="left",
            text_color="gray"
        )
        instructions.pack(pady=20, padx=20, anchor="w")
    
    def simulate_load_data(self):
        """Simulate loading data (for educational popup test)"""
        print("Load Data Sample clicked - in real app, this would open file dialog")
        # In real implementation, this would trigger file dialog in WorkflowEditorView
