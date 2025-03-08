import os
import re
import shutil
from pathlib import Path

# Source and destination directories
source_dir = 'zurich_restaurants'
build_dir = 'build'

# Create build directory if it doesn't exist
os.makedirs(build_dir, exist_ok=True)

# Function to fix paths in HTML files
def fix_paths_in_file(file_path, dest_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Fix relative paths in the file
    # For CSS files
    content = re.sub(r'href="\.\.\/style\.css"', 'href="/style.css"', content)
    content = re.sub(r'href="style\.css"', 'href="/style.css"', content)
    
    # For images
    content = re.sub(r'src="\.\.\/Restaurants\.png"', 'src="/Restaurants.png"', content)
    content = re.sub(r'src="Restaurants\.png"', 'src="/Restaurants.png"', content)
    content = re.sub(r'href="\.\.\/Favicon\.png"', 'href="/Favicon.png"', content)
    content = re.sub(r'href="Favicon\.png"', 'href="/Favicon.png"', content)
    
    # For links to other pages
    content = re.sub(r'href="\.\.\/index\.html"', 'href="/"', content)
    content = re.sub(r'href="index\.html"', 'href="/"', content)
    
    # Fix area and category links
    content = re.sub(r'href="\.\.\/([^\/]+)\/index\.html"', r'href="/\1/"', content)
    content = re.sub(r'href="([^\/\.]+)\/index\.html"', r'href="/\1/"', content)
    
    # Fix restaurant links
    content = re.sub(r'href="\.\.\/restaurant\/([^"]+)\.html"', r'href="/restaurant/\1"', content)
    content = re.sub(r'href="restaurant\/([^"]+)\.html"', r'href="/restaurant/\1"', content)
    
    with open(dest_path, 'w', encoding='utf-8') as file:
        file.write(content)
    
    return True

# Copy and process all files
def process_all_files():
    html_count = 0
    file_count = 0
    
    for root, dirs, files in os.walk(source_dir):
        # Create corresponding directory in build
        rel_path = os.path.relpath(root, source_dir)
        build_path = os.path.join(build_dir, rel_path) if rel_path != '.' else build_dir
        os.makedirs(build_path, exist_ok=True)
        
        for file in files:
            source_file = os.path.join(root, file)
            dest_file = os.path.join(build_path, file)
            
            if file.endswith('.html'):
                # Process HTML files
                if fix_paths_in_file(source_file, dest_file):
                    html_count += 1
                    print(f"Processed HTML: {source_file} -> {dest_file}")
            else:
                # Copy other files as is
                shutil.copy2(source_file, dest_file)
                file_count += 1
                print(f"Copied file: {source_file} -> {dest_file}")
    
    print(f"\nTotal HTML files processed: {html_count}")
    print(f"Total other files copied: {file_count}")
    print(f"All files prepared for Vercel in the '{build_dir}' directory")

if __name__ == "__main__":
    process_all_files()
    
    # Create a vercel.json file in the build directory
    vercel_config = '''{
  "trailingSlash": true,
  "cleanUrls": true
}'''
    
    with open(os.path.join(build_dir, 'vercel.json'), 'w') as f:
        f.write(vercel_config)
    
    print("Created vercel.json configuration file")
    print("\nDEPLOYMENT INSTRUCTIONS:")
    print("1. Deploy the 'build' directory to Vercel")
    print("2. Make sure to set the root directory to 'build' in your Vercel project settings") 