"""
Subscription Page - Handle trial and subscription management
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QLineEdit, QFrame, QSpacerItem,
                            QSizePolicy)
from PyQt6.QtCore import Qt

class SubscriptionPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup Subscription page UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(30)
        
        # Add vertical spacer to center content
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Main content frame
        content_frame = QFrame()
        content_frame.setFrameStyle(QFrame.Shape.Box)
        content_frame.setStyleSheet("""
            QFrame {
                border: 2px solid #ddd;
                border-radius: 12px;
                background-color: white;
                padding: 40px;
            }
        """)
        content_frame.setMaximumWidth(600)
        content_frame.setMinimumHeight(500)
        
        content_layout = QVBoxLayout(content_frame)
        content_layout.setSpacing(30)
        
        # Title
        title = QLabel("Subscription Required")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #333;")
        content_layout.addWidget(title)
        
        # Trial expired message
        message = QLabel("Your 30-day trial has expired")
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message.setStyleSheet("font-size: 18px; color: #666; margin-bottom: 10px;")
        content_layout.addWidget(message)
        
        # Subtitle
        subtitle = QLabel("Subscribe to continue using your tasks\\nand unlock import/export features")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("font-size: 16px; color: #666; line-height: 1.4;")
        content_layout.addWidget(subtitle)
        
        # Subscribe button
        subscribe_btn = QPushButton("💳 Subscribe for $0.49/month")
        subscribe_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 16px 32px;
                font-size: 18px;
                font-weight: bold;
                border-radius: 8px;
                margin: 20px 0;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        subscribe_btn.clicked.connect(self.subscribe)
        content_layout.addWidget(subscribe_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("color: #ccc; margin: 20px 0;")
        content_layout.addWidget(separator)
        
        # OR text
        or_label = QLabel("OR")
        or_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        or_label.setStyleSheet("font-size: 14px; color: #999; font-weight: bold;")
        content_layout.addWidget(or_label)
        
        # License key section
        license_section = QFrame()
        license_layout = QVBoxLayout(license_section)
        license_layout.setSpacing(15)
        
        license_title = QLabel("Already have a license key?")
        license_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        license_title.setStyleSheet("font-size: 16px; color: #333; margin-top: 20px;")
        license_layout.addWidget(license_title)
        
        # License key input
        self.license_input = QLineEdit()
        self.license_input.setPlaceholderText("Enter your license key...")
        self.license_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                font-size: 14px;
                border: 2px solid #ddd;
                border-radius: 6px;
                background-color: #f9f9f9;
            }
            QLineEdit:focus {
                border-color: #4CAF50;
                background-color: white;
            }
        """)
        license_layout.addWidget(self.license_input)
        
        # Activate button
        activate_btn = QPushButton("🔑 Activate License")
        activate_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 16px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        activate_btn.clicked.connect(self.activate_license)
        license_layout.addWidget(activate_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        content_layout.addWidget(license_section)
        
        # Another separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        separator2.setStyleSheet("color: #ccc; margin: 20px 0;")
        content_layout.addWidget(separator2)
        
        # Lost key section
        lost_key_section = QFrame()
        lost_key_layout = QVBoxLayout(lost_key_section)
        lost_key_layout.setSpacing(15)
        
        lost_key_title = QLabel("Lost your key?")
        lost_key_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lost_key_title.setStyleSheet("font-size: 16px; color: #333;")
        lost_key_layout.addWidget(lost_key_title)
        
        # Email input
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter your email address...")
        self.email_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                font-size: 14px;
                border: 2px solid #ddd;
                border-radius: 6px;
                background-color: #f9f9f9;
            }
            QLineEdit:focus {
                border-color: #FF9800;
                background-color: white;
            }
        """)
        lost_key_layout.addWidget(self.email_input)
        
        # Resend button
        resend_btn = QPushButton("📧 Resend Key")
        resend_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 16px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        resend_btn.clicked.connect(self.resend_key)
        lost_key_layout.addWidget(resend_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        content_layout.addWidget(lost_key_section)
        
        # Center the content frame
        frame_layout = QHBoxLayout()
        frame_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        frame_layout.addWidget(content_frame)
        frame_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        
        layout.addLayout(frame_layout)
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
    
    def subscribe(self):
        """Handle subscription process"""
        # TODO: Implement subscription flow
        print("Opening subscription flow...")
    
    def activate_license(self):
        """Activate license key"""
        license_key = self.license_input.text().strip()
        if license_key:
            # TODO: Implement license validation
            print(f"Activating license: {license_key}")
        else:
            print("Please enter a license key")
    
    def resend_key(self):
        """Resend license key to email"""
        email = self.email_input.text().strip()
        if email:
            # TODO: Implement key resending
            print(f"Resending key to: {email}")
        else:
            print("Please enter your email address")