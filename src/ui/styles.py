"""
UI Styles - Centralized design system for consistent components
"""

from PyQt6.QtWidgets import QPushButton, QComboBox, QTableWidget, QLabel
from PyQt6.QtCore import Qt

class Styles:
    """Centralized styling for all UI components"""
    
    # Color palette
    PRIMARY = "#4CAF50"
    PRIMARY_HOVER = "#45a049"
    SECONDARY = "#6c757d"
    SECONDARY_HOVER = "#5a6268"
    DANGER = "#dc3545"
    DANGER_HOVER = "#c82333"
    BORDER = "#dee2e6"
    TEXT_MUTED = "#6c757d"
    BACKGROUND = "#f8f9fa"
    
    @staticmethod
    def primary_button(button: QPushButton):
        """Style primary button"""
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {Styles.PRIMARY};
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 500;
                border-radius: 4px;
                min-height: 20px;
            }}
            QPushButton:hover {{
                background-color: {Styles.PRIMARY_HOVER};
            }}
            QPushButton:pressed {{
                background-color: #3d8b40;
            }}
        """)
    
    @staticmethod
    def secondary_button(button: QPushButton):
        """Style secondary button"""
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {Styles.SECONDARY};
                border: 1px solid {Styles.BORDER};
                padding: 8px 16px;
                font-size: 12px;
                border-radius: 4px;
                min-height: 16px;
            }}
            QPushButton:hover {{
                background-color: {Styles.BACKGROUND};
                color: {Styles.SECONDARY_HOVER};
            }}
        """)
    
    @staticmethod
    def danger_button(button: QPushButton):
        """Style danger button"""
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {Styles.DANGER};
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 500;
                border-radius: 4px;
                min-height: 20px;
            }}
            QPushButton:hover {{
                background-color: {Styles.DANGER_HOVER};
            }}
        """)
    
    @staticmethod
    def standard_dropdown(combo: QComboBox):
        """Style standard dropdown"""
        combo.setStyleSheet(f"""
            QComboBox {{
                padding: 8px 12px;
                border: 1px solid {Styles.BORDER};
                border-radius: 4px;
                font-size: 14px;
                background-color: white;
                min-height: 20px;
            }}
            QComboBox:hover {{
                border-color: {Styles.PRIMARY};
            }}
            QComboBox:focus {{
                border-color: {Styles.PRIMARY};
                outline: none;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                width: 12px;
                height: 12px;
            }}
        """)
    
    @staticmethod
    def data_table(table: QTableWidget):
        """Style data table"""
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setVisible(True)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        table.setStyleSheet(f"""
            QTableWidget {{
                border: 1px solid {Styles.BORDER};
                border-radius: 4px;
                background-color: white;
                gridline-color: {Styles.BORDER};
                font-size: 13px;
            }}
            QTableWidget::item {{
                padding: 8px;
                border: none;
            }}
            QTableWidget::item:selected {{
                background-color: #e3f2fd;
                color: #1976d2;
            }}
            QHeaderView::section {{
                background-color: {Styles.BACKGROUND};
                padding: 10px 8px;
                border: none;
                border-bottom: 1px solid {Styles.BORDER};
                border-right: 1px solid {Styles.BORDER};
                font-weight: 600;
                font-size: 13px;
                color: #333;
            }}
        """)
    
    @staticmethod
    def muted_text(label: QLabel):
        """Style muted text"""
        label.setStyleSheet(f"""
            QLabel {{
                color: {Styles.TEXT_MUTED};
                font-size: 12px;
            }}
        """)
    
    @staticmethod
    def container_frame(frame):
        """Style container frame"""
        frame.setStyleSheet(f"""
            QFrame {{
                border: 1px solid {Styles.BORDER};
                border-radius: 6px;
                background-color: white;
                padding: 15px;
            }}
        """)