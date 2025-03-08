import os
import re
from pathlib import Path

# Directory containing the restaurant HTML files
restaurant_dir = 'build/restaurant'

# Footer HTML to add to each page
footer_html = '''
<footer>
    <div class="container">
        <div class="footer-columns">
            <div class="footer-column">
                <h3>About Us</h3>
                <ul class="footer-list">
                    <li><a href="/">Home</a></li>
                    <li><a href="/sitemap.html">Sitemap</a></li>
                </ul>
            </div>
            <div class="footer-column">
                <h3>Explore</h3>
                <ul class="footer-list">
                    <li><a href="/italian/">Italian Restaurants</a></li>
                    <li><a href="/swiss/">Swiss Restaurants</a></li>
                    <li><a href="/breakfast/">Breakfast Places</a></li>
                </ul>
            </div>
            <div class="footer-column">
                <h3>Areas</h3>
                <ul class="footer-list">
                    <li><a href="/old-town/">Old Town</a></li>
                    <li><a href="/niederdorf/">Niederdorf</a></li>
                    <li><a href="/oerlikon/">Oerlikon</a></li>
                </ul>
            </div>
        </div>
        <div class="footer-sitemap">
            <a href="/sitemap.html">Sitemap</a>
        </div>
    </div>
</footer>
'''

# Function to fix restaurant HTML files
def fix_restaurant_page(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Remove any existing style tag at the end
    content = re.sub(r'<style>.*?</style>\s*</body>', '</body>', content, flags=re.DOTALL)
    content = re.sub(r'</style>\s*</body>', '</body>', content, flags=re.DOTALL)
    
    # Add footer before closing body tag if it doesn't exist
    if '<footer>' not in content:
        content = content.replace('</body>', f'{footer_html}\n</body>')
    
    # Write the fixed content back to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
    
    return True

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