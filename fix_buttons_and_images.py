import os
import re
from pathlib import Path

# Directory containing the restaurant HTML files
restaurant_dir = 'build/restaurant'

# CSS for buttons and centered images
button_css = '''
<style>
    .restaurant-actions {
        display: flex;
        gap: 15px;
        margin: 25px 0;
    }
    
    .cta-button {
        display: inline-block;
        padding: 12px 25px;
        border-radius: 5px;
        text-decoration: none;
        font-weight: 600;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .cta-button:first-child {
        background-color: #e74c3c;
        color: white;
    }
    
    .cta-button:first-child:hover {
        background-color: #c0392b;
    }
    
    .phone-button {
        background-color: #27ae60;
        color: white;
    }
    
    .phone-button:hover {
        background-color: #1f7a2a;
    }

    .restaurant-image-container {
        width: 100%;
        height: 400px;
        overflow: hidden;
        margin: 0 auto 30px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        display: flex;
        justify-content: center;
        align-items: center;
    }
    
    .restaurant-main-image {
        max-width: 100%;
        max-height: 100%;
        object-fit: contain;
    }
</style>
'''

# Function to fix restaurant HTML files
def fix_restaurant_page(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Check if the page has restaurant actions (buttons)
    if '<div class="restaurant-actions">' in content and '</head>' in content:
        # Add button CSS to the head section
        content = content.replace('</head>', f'{button_css}\n</head>')
        
        # Fix the phone button class if it doesn't have the phone-button class
        content = re.sub(
            r'<a href="tel:([^"]+)" class="cta-button"([^>]*)>',
            r'<a href="tel:\1" class="cta-button phone-button"\2>',
            content
        )
        
        # Write the fixed content back to the file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        
        return True
    
    return False

# Process all restaurant HTML files
def process_all_files():
    count = 0
    for root, dirs, files in os.walk(restaurant_dir):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                if fix_restaurant_page(file_path):
                    count += 1
                    print(f"Fixed file: {file_path}")
    
    print(f"\nTotal files fixed: {count}")

if __name__ == "__main__":
    process_all_files() 