import re

def parse_color(color_str):
    """Convert color string to hex format"""
    if color_str == "transparent":
        return "#00000000"
    
    if color_str.startswith("#"):
        return color_str
    
    # Handle gray colors
    if color_str.startswith("gray"):
        gray_value = int(color_str[4:])
        hex_value = int(gray_value * 2.55)
        return f"#{hex_value:02x}{hex_value:02x}{hex_value:02x}"
    
    return color_str

def is_color_attribute(value):
    """Check if attribute value is a color tuple"""
    return (isinstance(value, list) and 
            len(value) == 2 and 
            all(isinstance(item, str) for item in value))

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    if hex_color.startswith("#"):
        hex_color = hex_color[1:]
    if len(hex_color) == 6:
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return (128, 128, 128)  # Default gray

def rgb_to_hex(rgb):
    """Convert RGB tuple to hex string"""
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"