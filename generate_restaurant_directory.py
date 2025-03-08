import csv
import os
import re
import math
import random
from collections import defaultdict
import shutil

# Define constants
CSV_FILE = 'Outscraper-20250307150536s9c_restaurants.csv'
OUTPUT_DIR = 'zurich_restaurants'
SITE_NAME = 'Restaurants in Zurich'
SITE_LOGO = 'logo.png'
SITE_FAVICON = 'favicon.ico'

# Define areas in Zurich
AREAS = [
    'Old Town', 'Niederdorf', 'Enge', 'Oerlikon', 'Seefeld', 
    'Wiedikon', 'Airport', 'Altstetten', 'Wollishofen', 'Zurich West'
]

# Define restaurant categories
CATEGORIES = [
    'Italian', 'Chinese', 'Japanese', 'Swiss', 'French', 
    'Indian', 'Thai', 'Mexican', 'Vegetarian', 'Breakfast'
]

# Create output directory structure
if os.path.exists(OUTPUT_DIR):
    shutil.rmtree(OUTPUT_DIR)
os.makedirs(OUTPUT_DIR)

# Create directories for each area
for area in AREAS:
    area_slug = area.lower().replace(' ', '-')
    area_dir = os.path.join(OUTPUT_DIR, area_slug)
    os.makedirs(area_dir)
    
    # Create directories for each category within each area
    for category in CATEGORIES:
        category_slug = category.lower()
        category_dir = os.path.join(area_dir, category_slug)
        os.makedirs(category_dir)

# Create directories for each category at the root level
for category in CATEGORIES:
    category_slug = category.lower()
    category_dir = os.path.join(OUTPUT_DIR, category_slug)
    os.makedirs(category_dir)

# Create directory for individual restaurant pages
restaurant_dir = os.path.join(OUTPUT_DIR, 'restaurant')
os.makedirs(restaurant_dir)

# Function to clean and normalize text
def clean_text(text):
    if not text:
        return ""
    return text.strip()

# Function to determine area based on address and postal code
def determine_area(address, postal_code):
    # This is a simplified mapping - in a real scenario, you'd need more precise mapping
    postal_mapping = {
        '8001': 'Old Town',
        '8002': 'Enge',
        '8003': 'Wiedikon',
        '8004': 'Zurich West',
        '8005': 'Zurich West',
        '8006': 'Niederdorf',
        '8008': 'Seefeld',
        '8037': 'Wiedikon',
        '8050': 'Oerlikon',
        '8055': 'Altstetten',
        '8057': 'Airport',
        '8045': 'Wollishofen'
    }
    
    # Check for keywords in address
    if 'Old Town' in address or 'Altstadt' in address:
        return 'Old Town'
    elif 'Niederdorf' in address:
        return 'Niederdorf'
    elif 'Seefeld' in address:
        return 'Seefeld'
    elif 'Oerlikon' in address:
        return 'Oerlikon'
    elif 'Airport' in address or 'Flughafen' in address:
        return 'Airport'
    
    # Use postal code mapping as fallback
    if postal_code in postal_mapping:
        return postal_mapping[postal_code]
    
    # Default to Old Town if we can't determine
    return 'Old Town'

# Function to determine category based on restaurant type and subtypes
def determine_category(restaurant_type, subtypes, about):
    if not restaurant_type and not subtypes and not about:
        return "Other"
    
    # Check for breakfast category in about field
    if about and 'breakfast' in about.lower():
        return 'Breakfast'
    
    # Check for categories in type and subtypes
    for category in CATEGORIES:
        if (restaurant_type and category.lower() in restaurant_type.lower()) or \
           (subtypes and category.lower() in subtypes.lower()):
            return category
    
    # Default category
    return "Other"

# Function to calculate restaurant score (rating * log(num_reviews + 1))
def calculate_score(rating, reviews):
    if not rating or not reviews:
        return 0
    try:
        rating = float(rating)
        reviews = float(reviews)
        return rating * math.log(reviews + 1)
    except:
        return 0

# Read and process the CSV file
restaurants_by_area = defaultdict(list)
restaurants_by_area_category = defaultdict(lambda: defaultdict(list))

with open(CSV_FILE, 'r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        name = clean_text(row.get('name', ''))
        if not name:
            continue
            
        address = clean_text(row.get('full_address', ''))
        postal_code = clean_text(row.get('postal_code', ''))
        restaurant_type = clean_text(row.get('type', ''))
        subtypes = clean_text(row.get('subtypes', ''))
        about = clean_text(row.get('about', ''))
        rating = row.get('rating', '0')
        reviews = row.get('reviews', '0')
        website = clean_text(row.get('site', ''))
        phone = clean_text(row.get('phone', ''))
        photo = clean_text(row.get('photo', ''))
        price_range = clean_text(row.get('range', ''))
        
        # Determine area and category
        area = determine_area(address, postal_code)
        category = determine_category(restaurant_type, subtypes, about)
        
        # Calculate score for ranking
        score = calculate_score(rating, reviews)
        
        # Create restaurant object
        restaurant = {
            'name': name,
            'address': address,
            'postal_code': postal_code,
            'type': restaurant_type,
            'category': category,
            'rating': rating,
            'reviews': reviews,
            'score': score,
            'website': website,
            'phone': phone,
            'photo': photo,
            'price_range': price_range
        }
        
        # Add to appropriate collections
        restaurants_by_area[area].append(restaurant)
        restaurants_by_area_category[area][category].append(restaurant)

# Sort restaurants by score in descending order
for area in restaurants_by_area:
    restaurants_by_area[area].sort(key=lambda x: float(x['score']), reverse=True)
    
    for category in restaurants_by_area_category[area]:
        restaurants_by_area_category[area][category].sort(key=lambda x: float(x['score']), reverse=True)

# Create logo SVG
logo_svg = '''<svg width="300" height="60" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#d32323;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#ff6b6b;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="300" height="60" rx="8" fill="url(#grad1)"/>
  <text x="20" y="38" font-family="'Segoe UI', Tahoma, Geneva, Verdana, sans-serif" font-size="22" font-weight="bold" fill="white">Restaurants in Zurich</text>
</svg>'''

with open(os.path.join(OUTPUT_DIR, SITE_LOGO), 'w') as f:
    f.write(logo_svg)

# Create CSS file
css_content = '''
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Montserrat', 'Helvetica Neue', Arial, sans-serif;
}

body {
    background-color: #f8f9fa;
    color: #333;
    line-height: 1.6;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

header {
    background-color: #fff;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    padding: 15px 0;
    position: sticky;
    top: 0;
    z-index: 100;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.logo {
    display: flex;
    align-items: center;
    padding: 0 20px;
}

.logo img {
    height: 40px;
    margin-right: 10px;
}

.logo span {
    font-size: 1.5rem;
    font-weight: bold;
    color: #d32323;
}

.dropdown-menus {
    display: flex;
    margin-right: 20px;
}

.dropdown {
    position: relative;
    margin-left: 15px;
}

.dropdown-button {
    background-color: #d32323;
    color: white;
    padding: 10px 15px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-weight: bold;
}

.dropdown-content {
    display: none;
    position: absolute;
    right: 0;
    background-color: #f9f9f9;
    min-width: 160px;
    box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2);
    z-index: 1;
    max-height: 400px;
    overflow-y: auto;
}

.dropdown-content a {
    color: black;
    padding: 12px 16px;
    text-decoration: none;
    display: block;
    text-align: left;
}

.dropdown-content a:hover {
    background-color: #f1f1f1;
}

.dropdown:hover .dropdown-content {
    display: block;
}

.dropdown:hover .dropdown-button {
    background-color: #b01d1d;
}

.hero {
    background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url('https://images.unsplash.com/photo-1555396273-367ea4eb4db5');
    background-size: cover;
    background-position: center;
    color: white;
    text-align: center;
    padding: 100px 20px;
    margin-bottom: 40px;
}

.hero h1 {
    font-size: 3rem;
    margin-bottom: 20px;
}

.hero p {
    font-size: 1.2rem;
    max-width: 800px;
    margin: 0 auto 30px;
}

.search-bar {
    max-width: 600px;
    margin: 0 auto;
    display: flex;
}

.search-bar input {
    flex: 1;
    padding: 12px;
    border: none;
    border-radius: 4px 0 0 4px;
    font-size: 1rem;
}

.search-bar button {
    background-color: #d32323;
    color: white;
    border: none;
    padding: 12px 20px;
    border-radius: 0 4px 4px 0;
    cursor: pointer;
    font-weight: bold;
}

.page-title {
    margin: 40px 0 20px;
    text-align: center;
}

.category-nav {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    margin: 20px 0 40px;
}

.category-nav a {
    display: inline-block;
    margin: 5px;
    padding: 8px 15px;
    background-color: #fff;
    border-radius: 20px;
    text-decoration: none;
    color: #333;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    transition: all 0.3s;
}

.category-nav a:hover, .category-nav a.active {
    background-color: #d32323;
    color: white;
}

.restaurant-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
    margin-bottom: 40px;
}

.restaurant-card {
    background-color: white;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    transition: transform 0.3s;
    height: 100%;
    display: flex;
    flex-direction: column;
}

.restaurant-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.restaurant-image {
    height: 180px;
    overflow: hidden;
}

.restaurant-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.3s;
}

.restaurant-card:hover .restaurant-image img {
    transform: scale(1.05);
}

.restaurant-card h3 {
    padding: 15px;
    background-color: #f8f9fa;
    border-bottom: 1px solid #eee;
}

.restaurant-details {
    padding: 15px;
    flex-grow: 1;
    display: flex;
    flex-direction: column;
}

.rating {
    margin-bottom: 10px;
    display: flex;
    align-items: center;
}

.stars {
    color: #f8ce0b;
    margin-right: 5px;
}

.rating-value {
    font-weight: bold;
}

.reviews {
    color: #777;
    font-size: 0.9rem;
    margin-left: 5px;
}

.price {
    color: #2a9d38;
    font-weight: bold;
    margin-left: auto;
}

.type, .address {
    margin-bottom: 5px;
    color: #555;
}

.contact {
    margin-top: auto;
    padding-top: 10px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.contact a {
    color: white;
    text-decoration: none;
    background-color: #d32323;
    padding: 8px 15px;
    border-radius: 4px;
    font-weight: bold;
    transition: background-color 0.3s;
}

.contact a:hover {
    background-color: #b01d1d;
}

.phone {
    color: #555;
}

.featured-areas {
    margin: 40px 0;
}

.featured-areas h2 {
    text-align: center;
    margin-bottom: 20px;
}

.area-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 20px;
}

.area-card {
    position: relative;
    height: 200px;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.area-card img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.3s;
}

.area-card:hover img {
    transform: scale(1.05);
}

.area-card .area-name {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background-color: rgba(0,0,0,0.7);
    color: white;
    padding: 10px;
    text-align: center;
    font-weight: bold;
}

.featured-categories {
    margin: 40px 0;
}

.featured-categories h2 {
    text-align: center;
    margin-bottom: 20px;
}

.category-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 20px;
}

.category-card {
    background-color: white;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    text-align: center;
    transition: transform 0.3s;
}

.category-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.category-card img {
    width: 100%;
    height: 150px;
    object-fit: cover;
}

.category-card h3 {
    padding: 15px;
    color: #333;
}

/* Style for cuisine category links */
.category-grid a {
    text-decoration: none;
    color: #333;
}

.category-grid a:hover {
    text-decoration: none;
}

.featured-restaurants {
    margin: 40px 0;
}

.featured-restaurants h2 {
    text-align: center;
    margin-bottom: 20px;
}

.faq-section {
    margin: 40px 0;
    background-color: #fff;
    border-radius: 8px;
    padding: 30px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.faq-section h2 {
    text-align: center;
    margin-bottom: 30px;
}

.faq-item {
    margin-bottom: 20px;
    border-bottom: 1px solid #eee;
    padding-bottom: 20px;
}

.faq-item:last-child {
    border-bottom: none;
    margin-bottom: 0;
    padding-bottom: 0;
}

.faq-question {
    font-weight: bold;
    font-size: 1.2rem;
    margin-bottom: 10px;
    color: #333;
    text-align: center;
}

.faq-answer {
    color: #555;
}

.section-intro {
    margin-bottom: 30px;
    font-size: 1.1rem;
    line-height: 1.6;
    color: #555;
    max-width: 900px;
    margin-left: auto;
    margin-right: auto;
    text-align: center;
}

.section-intro a {
    color: #d32323;
    text-decoration: none;
    font-weight: 600;
    transition: color 0.3s;
}

.section-intro a:hover {
    color: #b01d1d;
    text-decoration: underline;
}

footer {
    background-color: #333;
    color: white;
    padding: 40px 0;
    margin-top: 40px;
}

.footer-columns {
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
}

.footer-column {
    flex: 1;
    min-width: 250px;
    margin-bottom: 20px;
    padding: 0 15px;
}

.footer-column h3 {
    color: #fff;
    margin-bottom: 20px;
    font-size: 1.2rem;
    text-align: center;
}

.footer-list {
    list-style: none;
}

.footer-list li {
    margin-bottom: 10px;
}

.footer-list a {
    color: #ddd;
    text-decoration: none;
    transition: color 0.3s;
}

.footer-list a:hover {
    color: #d32323;
    text-decoration: underline;
}

.footer-sitemap {
    text-align: center;
    margin-top: 20px;
    padding-top: 20px;
    border-top: 1px solid rgba(255,255,255,0.1);
}

.footer-sitemap a {
    color: #ddd;
    text-decoration: none;
    transition: color 0.3s;
    font-size: 0.9rem;
}

.footer-sitemap a:hover {
    color: #d32323;
    text-decoration: underline;
}

@media (max-width: 768px) {
    .hero h1 {
        font-size: 2rem;
    }
    
    .restaurant-list {
        grid-template-columns: 1fr;
    }
    
    .dropdown-menus {
        flex-direction: column;
    }
    
    .dropdown {
        margin-bottom: 10px;
    }
    
    .area-grid, .category-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .footer-columns {
        flex-direction: column;
    }
    
    .footer-column {
        margin-bottom: 30px;
    }
    
    .footer-column:last-child {
        margin-bottom: 0;
    }
}

@media (max-width: 480px) {
    .area-grid, .category-grid {
        grid-template-columns: 1fr;
    }
}

/* Carousel styles */
.carousel {
    position: relative;
    width: 100%;
    height: 400px;
    overflow: hidden;
    margin-bottom: 30px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.carousel-inner {
    display: flex;
    transition: transform 0.5s ease;
    height: 100%;
}

.carousel-item {
    min-width: 100%;
    height: 100%;
}

.carousel-item img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.carousel-control {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    width: 40px;
    height: 40px;
    background-color: rgba(0,0,0,0.5);
    color: white;
    border: none;
    border-radius: 50%;
    font-size: 20px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10;
}

.carousel-control.prev {
    left: 10px;
}

.carousel-control.next {
    right: 10px;
}

.restaurant-detail {
    background-color: white;
    border-radius: 8px;
    padding: 30px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    margin-bottom: 30px;
}

.restaurant-detail h1 {
    margin-bottom: 20px;
    color: #333;
    text-align: center;
}

.restaurant-meta {
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
    margin-bottom: 20px;
    padding-bottom: 20px;
    border-bottom: 1px solid #eee;
}

.restaurant-rating {
    display: flex;
    align-items: center;
}

.restaurant-category {
    background-color: #f8f9fa;
    padding: 5px 10px;
    border-radius: 20px;
    font-size: 0.9rem;
    color: #555;
}

.restaurant-info {
    margin-bottom: 30px;
}

.restaurant-info h2 {
    font-size: 1.5rem;
    margin-bottom: 15px;
    color: #333;
    text-align: left;
}

.restaurant-info p {
    margin-bottom: 10px;
    color: #555;
}

.restaurant-contact {
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
    margin-top: 30px;
}

.restaurant-contact a.website-btn {
    display: inline-block;
    background-color: #d32323;
    color: white;
    padding: 10px 20px;
    border-radius: 4px;
    text-decoration: none;
    font-weight: bold;
    transition: background-color 0.3s;
}

.restaurant-contact a.website-btn:hover {
    background-color: #b01d1d;
}

.restaurant-contact .phone {
    display: flex;
    align-items: center;
}

.similar-restaurants {
    margin-top: 40px;
}

.similar-restaurants h2 {
    text-align: center;
    margin-bottom: 20px;
}
'''

with open(os.path.join(OUTPUT_DIR, 'style.css'), 'w') as f:
    f.write(css_content)

# Function to generate HTML for a restaurant card with proper relative paths
def generate_restaurant_card(restaurant, level=0):
    # Generate star rating
    rating_value = float(restaurant['rating']) if restaurant['rating'] else 0
    full_stars = int(rating_value)
    half_star = rating_value - full_stars >= 0.5
    empty_stars = 5 - full_stars - (1 if half_star else 0)
    
    stars_html = '★' * full_stars
    if half_star:
        stars_html += '½'
    stars_html += '☆' * empty_stars
    
    # Default image if none provided
    image_url = restaurant['photo'] if restaurant['photo'] else 'https://via.placeholder.com/300x180?text=No+Image'
    
    # Price range
    price_html = restaurant['price_range'] if restaurant['price_range'] else ''
    
    # Website button - changed from text link to a button
    website_html = f'<a href="{restaurant["website"]}" target="_blank">Visit Website</a>' if restaurant["website"] else ''
    
    # Create a slug for the restaurant name
    restaurant_slug = re.sub(r'[^a-zA-Z0-9]', '-', restaurant['name'].lower())
    restaurant_slug = re.sub(r'-+', '-', restaurant_slug).strip('-')
    
    # Create proper relative path based on nesting level
    base_path = '../' * level
    
    # For similar restaurants on individual restaurant pages, we need a special case
    if level == 2 and 'restaurant' in os.path.dirname(os.path.dirname(os.getcwd())):
        # If we're in a restaurant page showing similar restaurants
        link_path = f"../restaurant/{restaurant_slug}.html"
    else:
        link_path = f"{base_path}restaurant/{restaurant_slug}.html"
    
    return f'''
    <div class="restaurant-card">
        <div class="restaurant-image">
            <img src="{image_url}" alt="{restaurant['name']}">
        </div>
        <h3><a href="{link_path}">{restaurant['name']}</a></h3>
        <div class="restaurant-details">
            <div class="rating">
                <span class="stars">{stars_html}</span>
                <span class="rating-value">{restaurant['rating']}</span>
                <span class="reviews">({restaurant['reviews']} reviews)</span>
                <span class="price">{price_html}</span>
            </div>
            <div class="type">{restaurant['type']}</div>
            <div class="address">{restaurant['address']}</div>
            <div class="contact">
                {website_html}
                {f'<span class="phone">{restaurant["phone"]}</span>' if restaurant["phone"] else ''}
            </div>
        </div>
    </div>
    '''

# Function to generate navigation menu with dropdowns
def generate_menu(current_area=None, current_category=None, level=0):
    base_path = '../' * level
    
    # Create areas dropdown
    areas_dropdown = f'''
    <div class="dropdown">
        <button class="dropdown-button">Areas ▼</button>
        <div class="dropdown-content">
    '''
    
    for area in AREAS:
        area_slug = area.lower().replace(' ', '-')
        is_current = current_area and current_area.lower() == area.lower()
        
        areas_dropdown += f'<a href="{base_path}{area_slug}/index.html"{" class=\"active\"" if is_current else ""}>{area}</a>\n'
    
    areas_dropdown += '''
        </div>
    </div>
    '''
    
    # Create categories dropdown
    categories_dropdown = f'''
    <div class="dropdown">
        <button class="dropdown-button">Cuisines ▼</button>
        <div class="dropdown-content">
    '''
    
    for category in CATEGORIES:
        category_slug = category.lower()
        categories_dropdown += f'<a href="{base_path}{category_slug}/index.html">{category}</a>\n'
    
    categories_dropdown += '''
        </div>
    </div>
    '''
    
    return f'''
    <div class="dropdown-menus">
        {areas_dropdown}
        {categories_dropdown}
    </div>
    '''

# Function to generate header with logo and dropdown menus
def generate_header(level=0):
    base_path = '../' * level
    
    return f'''
    <header>
        <div class="logo">
            <a href="{base_path}index.html">
                <img src="{base_path}{SITE_LOGO}" alt="{SITE_NAME}">
            </a>
        </div>
        {generate_menu(level=level)}
    </header>
    '''

# Function to generate HTML head section with correct CSS path
def generate_head(title, description, keywords, level=0):
    base_path = '../' * level
    
    return f'''
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="{description}">
        <meta name="keywords" content="{keywords}">
        <title>{title} - {SITE_NAME}</title>
        <link rel="stylesheet" href="{base_path}style.css">
        <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap" rel="stylesheet">
        <link rel="icon" type="image/x-icon" href="{base_path}{SITE_FAVICON}">
    </head>
    '''

# Function to generate footer with three columns of restaurants
def generate_footer():
    # Get top breakfast restaurants
    breakfast_restaurants = []
    for area in restaurants_by_area:
        for restaurant in restaurants_by_area[area]:
            if 'breakfast' in restaurant.get('type', '').lower() or 'breakfast' in restaurant.get('category', '').lower():
                breakfast_restaurants.append(restaurant)
    
    breakfast_restaurants.sort(key=lambda x: float(x['score']), reverse=True)
    breakfast_restaurants = breakfast_restaurants[:5]
    
    # Get top lunch restaurants (using score as proxy)
    lunch_restaurants = []
    for area in restaurants_by_area:
        lunch_restaurants.extend(restaurants_by_area[area])
    
    lunch_restaurants.sort(key=lambda x: float(x['score']), reverse=True)
    lunch_restaurants = lunch_restaurants[6:11]  # Skip the top 6 to get different restaurants
    
    # Get top dinner restaurants (using score as proxy, different set)
    dinner_restaurants = []
    for area in restaurants_by_area:
        dinner_restaurants.extend(restaurants_by_area[area])
    
    dinner_restaurants.sort(key=lambda x: float(x['score']), reverse=True)
    dinner_restaurants = dinner_restaurants[12:17]  # Skip more to get different restaurants
    
    footer_html = '''
    <footer>
        <div class="container">
            <div class="footer-columns">
                <div class="footer-column">
                    <h3>Best Breakfast in Zurich</h3>
                    <ul class="footer-list">
    '''
    
    # Add breakfast restaurants
    for restaurant in breakfast_restaurants:
        footer_html += f'<li><a href="#">{restaurant["name"]}</a></li>\n'
    
    footer_html += '''
                    </ul>
                </div>
                <div class="footer-column">
                    <h3>Best Lunch in Zurich</h3>
                    <ul class="footer-list">
    '''
    
    # Add lunch restaurants
    for restaurant in lunch_restaurants:
        footer_html += f'<li><a href="#">{restaurant["name"]}</a></li>\n'
    
    footer_html += '''
                    </ul>
                </div>
                <div class="footer-column">
                    <h3>Best Dinner in Zurich</h3>
                    <ul class="footer-list">
    '''
    
    # Add dinner restaurants
    for restaurant in dinner_restaurants:
        footer_html += f'<li><a href="#">{restaurant["name"]}</a></li>\n'
    
    footer_html += '''
                    </ul>
                </div>
            </div>
            <div class="footer-sitemap">
                <a href="sitemap.html">Sitemap</a>
            </div>
        </div>
    </footer>
    '''
    
    return footer_html

# Function to generate a carousel with 3 images
def generate_carousel(restaurant):
    # Use the main photo as the first image
    main_image = restaurant['photo'] if restaurant['photo'] else 'https://via.placeholder.com/800x400?text=No+Image'
    
    # Generate 2 more random images related to the restaurant type
    restaurant_type = restaurant['type'].lower() if restaurant['type'] else 'restaurant'
    category = restaurant['category'].lower() if restaurant['category'] else 'food'
    
    # Use Unsplash for additional images
    image2 = f'https://source.unsplash.com/random/800x400/?{restaurant_type}'
    image3 = f'https://source.unsplash.com/random/800x400/?{category},food'
    
    return f'''
    <div class="carousel">
        <div class="carousel-inner">
            <div class="carousel-item">
                <img src="{main_image}" alt="{restaurant['name']}">
            </div>
            <div class="carousel-item">
                <img src="{image2}" alt="{restaurant['name']} {restaurant_type}">
            </div>
            <div class="carousel-item">
                <img src="{image3}" alt="{restaurant['name']} {category}">
            </div>
        </div>
        <button class="carousel-control prev" onclick="moveCarousel(-1)">❮</button>
        <button class="carousel-control next" onclick="moveCarousel(1)">❯</button>
    </div>
    '''

# Function to generate individual restaurant pages
def generate_restaurant_page(restaurant, all_restaurants):
    # Create a slug for the restaurant name
    restaurant_slug = re.sub(r'[^a-zA-Z0-9]', '-', restaurant['name'].lower())
    restaurant_slug = re.sub(r'-+', '-', restaurant_slug).strip('-')
    
    # Generate star rating
    rating_value = float(restaurant['rating']) if restaurant['rating'] else 0
    full_stars = int(rating_value)
    half_star = rating_value - full_stars >= 0.5
    empty_stars = 5 - full_stars - (1 if half_star else 0)
    
    stars_html = '★' * full_stars
    if half_star:
        stars_html += '½'
    stars_html += '☆' * empty_stars
    
    # Price range
    price_html = restaurant['price_range'] if restaurant['price_range'] else ''
    
    # Website button
    website_html = f'<a href="{restaurant["website"]}" target="_blank" class="website-btn">Visit Website</a>' if restaurant["website"] else ''
    
    # Find similar restaurants (same category or area)
    similar_restaurants = []
    for r in all_restaurants:
        if r['name'] != restaurant['name'] and (r['category'] == restaurant['category'] or r['address'].lower().find(restaurant['address'].lower()) != -1):
            similar_restaurants.append(r)
    
    # Shuffle and take up to 3
    random.shuffle(similar_restaurants)
    similar_restaurants = similar_restaurants[:3]
    
    # Generate HTML for similar restaurants with custom card generation
    similar_html = ''
    if similar_restaurants:
        similar_html = '''
        <section class="featured-restaurants">
            <h2>Similar Restaurants You Might Like</h2>
            <div class="restaurant-list">
        '''
        
        # Generate custom cards for similar restaurants with correct paths
        for r in similar_restaurants:
            r_slug = re.sub(r'[^a-zA-Z0-9]', '-', r['name'].lower())
            r_slug = re.sub(r'-+', '-', r_slug).strip('-')
            
            # Generate star rating for this restaurant
            r_rating_value = float(r['rating']) if r['rating'] else 0
            r_full_stars = int(r_rating_value)
            r_half_star = r_rating_value - r_full_stars >= 0.5
            r_empty_stars = 5 - r_full_stars - (1 if r_half_star else 0)
            
            r_stars_html = '★' * r_full_stars
            if r_half_star:
                r_stars_html += '½'
            r_stars_html += '☆' * r_empty_stars
            
            # Default image if none provided
            r_image_url = r['photo'] if r['photo'] else 'https://via.placeholder.com/300x180?text=No+Image'
            
            # Price range
            r_price_html = r['price_range'] if r['price_range'] else ''
            
            # Website button
            r_website_html = f'<a href="{r["website"]}" target="_blank">Visit Website</a>' if r["website"] else ''
            
            # Add card with correct path to the similar restaurant
            similar_html += f'''
            <div class="restaurant-card">
                <div class="restaurant-image">
                    <img src="{r_image_url}" alt="{r['name']}">
                </div>
                <h3><a href="../restaurant/{r_slug}.html">{r['name']}</a></h3>
                <div class="restaurant-details">
                    <div class="rating">
                        <span class="stars">{r_stars_html}</span>
                        <span class="rating-value">{r['rating']}</span>
                        <span class="reviews">({r['reviews']} reviews)</span>
                        <span class="price">{r_price_html}</span>
                    </div>
                    <div class="type">{r['type']}</div>
                    <div class="address">{r['address']}</div>
                    <div class="contact">
                        {r_website_html}
                        {f'<span class="phone">{r["phone"]}</span>' if r["phone"] else ''}
                    </div>
                </div>
            </div>
            '''
        
        similar_html += '''
            </div>
        </section>
        '''
    
    # Main image
    main_image = restaurant['photo'] if restaurant['photo'] else 'https://via.placeholder.com/800x400?text=No+Image'
    
    # Generate area links with correct paths
    area_links = ''
    for area in AREAS:
        area_slug = area.lower().replace(' ', '-')
        area_links += f'<a href="../{area_slug}/index.html">{area}</a>'
    
    # Generate category links with correct paths
    category_links = ''
    for category in CATEGORIES:
        category_slug = category.lower()
        category_links += f'<a href="../{category_slug}/index.html">{category}</a>'
    
    # Generate the restaurant page HTML with inline styles
    page_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Visit {restaurant['name']}, a {restaurant['type']} in Zurich. {restaurant['rating']} stars with {restaurant['reviews']} reviews.">
    <meta name="keywords" content="{restaurant['name']}, {restaurant['type']}, restaurant Zurich, dining Zurich">
    <title>{restaurant['name']} - {SITE_NAME}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Montserrat', 'Helvetica Neue', Arial, sans-serif;
        }}

        body {{
            background-color: #f8f9fa;
            color: #333;
            line-height: 1.6;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}

        header {{
            background-color: #fff;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 15px 0;
            position: sticky;
            top: 0;
            z-index: 100;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .logo {{
            display: flex;
            align-items: center;
            padding: 0 20px;
        }}

        .logo span {{
            font-size: 1.5rem;
            font-weight: bold;
            color: #d32323;
        }}

        .dropdown-menus {{
            display: flex;
            margin-right: 20px;
        }}

        .dropdown {{
            position: relative;
            margin-left: 15px;
        }}

        .dropdown-button {{
            background-color: #d32323;
            color: white;
            padding: 10px 15px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
        }}

        .dropdown-content {{
            display: none;
            position: absolute;
            right: 0;
            background-color: #f9f9f9;
            min-width: 160px;
            box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2);
            z-index: 1;
            max-height: 400px;
            overflow-y: auto;
        }}

        .dropdown-content a {{
            color: black;
            padding: 12px 16px;
            text-decoration: none;
            display: block;
            text-align: left;
        }}

        .dropdown-content a:hover {{
            background-color: #f1f1f1;
        }}

        .dropdown:hover .dropdown-content {{
            display: block;
        }}

        .dropdown:hover .dropdown-button {{
            background-color: #b01d1d;
        }}

        .restaurant-header {{
            position: relative;
            height: 400px;
            overflow: hidden;
            margin-bottom: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .restaurant-header img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}

        .restaurant-header-overlay {{
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            background: linear-gradient(transparent, rgba(0,0,0,0.8));
            padding: 30px 20px 20px;
            color: white;
        }}

        .restaurant-header-overlay h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
        }}

        .restaurant-meta {{
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            margin-bottom: 10px;
        }}

        .stars {{
            color: #f8ce0b;
            margin-right: 5px;
        }}

        .rating-value {{
            font-weight: bold;
            margin-right: 5px;
        }}

        .reviews {{
            color: #ddd;
            font-size: 0.9rem;
            margin-right: 15px;
        }}

        .restaurant-category {{
            background-color: rgba(255,255,255,0.2);
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 0.9rem;
            margin-right: 10px;
        }}

        .restaurant-price {{
            color: #2a9d38;
            font-weight: bold;
        }}

        .restaurant-content {{
            display: flex;
            flex-wrap: wrap;
            gap: 30px;
            margin-bottom: 40px;
        }}

        .restaurant-info {{
            flex: 2;
            min-width: 300px;
            background-color: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .restaurant-info h2 {{
            font-size: 1.5rem;
            margin-bottom: 15px;
            color: #333;
            text-align: left;
        }}

        .restaurant-info p {{
            margin-bottom: 20px;
            color: #555;
        }}

        .restaurant-contact {{
            margin-top: 30px;
        }}

        .website-btn {{
            display: inline-block;
            background-color: #d32323;
            color: white;
            padding: 10px 20px;
            border-radius: 4px;
            text-decoration: none;
            font-weight: bold;
            transition: background-color 0.3s;
        }}

        .website-btn:hover {{
            background-color: #b01d1d;
        }}

        .phone {{
            display: block;
            margin-top: 10px;
            color: #555;
        }}

        .featured-restaurants {{
            margin: 40px 0;
        }}

        .featured-restaurants h2 {{
            text-align: center;
            margin-bottom: 20px;
        }}

        .restaurant-list {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}

        .restaurant-card {{
            background-color: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.3s;
            height: 100%;
            display: flex;
            flex-direction: column;
        }}

        .restaurant-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}

        .restaurant-image {{
            height: 180px;
            overflow: hidden;
        }}

        .restaurant-image img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.3s;
        }}

        .restaurant-card:hover .restaurant-image img {{
            transform: scale(1.05);
        }}

        .restaurant-card h3 {{
            padding: 15px;
            background-color: #f8f9fa;
            border-bottom: 1px solid #eee;
        }}

        .restaurant-card h3 a {{
            color: #333;
            text-decoration: none;
        }}

        .restaurant-details {{
            padding: 15px;
            flex-grow: 1;
            display: flex;
            flex-direction: column;
        }}

        .rating {{
            margin-bottom: 10px;
            display: flex;
            align-items: center;
        }}

        .type, .address {{
            margin-bottom: 5px;
            color: #555;
        }}

        .contact {{
            margin-top: auto;
            padding-top: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .contact a {{
            color: white;
            text-decoration: none;
            background-color: #d32323;
            padding: 8px 15px;
            border-radius: 4px;
            font-weight: bold;
            transition: background-color 0.3s;
        }}

        .contact a:hover {{
            background-color: #b01d1d;
        }}

        footer {{
            background-color: #333;
            color: white;
            padding: 40px 0;
            margin-top: 40px;
        }}

        .footer-columns {{
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
        }}

        .footer-column {{
            flex: 1;
            min-width: 250px;
            margin-bottom: 20px;
            padding: 0 15px;
        }}

        .footer-column h3 {{
            color: #fff;
            margin-bottom: 20px;
            font-size: 1.2rem;
            text-align: center;
        }}

        .footer-list {{
            list-style: none;
        }}

        .footer-list li {{
            margin-bottom: 10px;
        }}

        .footer-list a {{
            color: #ddd;
            text-decoration: none;
            transition: color 0.3s;
        }}

        .footer-list a:hover {{
            color: #d32323;
            text-decoration: underline;
        }}

        @media (max-width: 768px) {{
            .restaurant-header {{
                height: 300px;
            }}
            
            .restaurant-header-overlay h1 {{
                font-size: 1.8rem;
            }}
            
            .restaurant-content {{
                flex-direction: column;
            }}
            
            .restaurant-list {{
                grid-template-columns: 1fr;
            }}
            
            .dropdown-menus {{
                flex-direction: column;
            }}
            
            .dropdown {{
                margin-bottom: 10px;
            }}
        }}
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap" rel="stylesheet">
</head>
<body>
    <header>
        <div class="logo">
            <a href="../index.html" style="text-decoration: none;">
                <span>{SITE_NAME}</span>
            </a>
        </div>
        <div class="dropdown-menus">
            <div class="dropdown">
                <button class="dropdown-button">Areas ▼</button>
                <div class="dropdown-content">
                    <a href="../index.html">Home</a>
                    {area_links}
                </div>
            </div>
            <div class="dropdown">
                <button class="dropdown-button">Cuisines ▼</button>
                <div class="dropdown-content">
                    {category_links}
                </div>
            </div>
        </div>
    </header>
    
    <div class="container">
        <div class="restaurant-header">
            <img src="{main_image}" alt="{restaurant['name']}">
            <div class="restaurant-header-overlay">
                <h1>{restaurant['name']}</h1>
                <div class="restaurant-meta">
                    <span class="stars">{stars_html}</span>
                    <span class="rating-value">{restaurant['rating']}</span>
                    <span class="reviews">({restaurant['reviews']} reviews)</span>
                    <span class="restaurant-category">{restaurant['type']}</span>
                    <span class="restaurant-price">{price_html}</span>
                </div>
            </div>
        </div>
        
        <div class="restaurant-content">
            <div class="restaurant-info">
                <h2>Location</h2>
                <p>{restaurant['address']}</p>
                
                <h2>Contact</h2>
                <div class="restaurant-contact">
                    {website_html}
                    {f'<div class="phone">{restaurant["phone"]}</div>' if restaurant["phone"] else ''}
                </div>
            </div>
        </div>
        
        {similar_html}
    </div>
    
    <footer>
        <div class="container">
            <div class="footer-columns">
                <div class="footer-column">
                    <h3>Best Breakfast in Zurich</h3>
                    <ul class="footer-list">
                        <li><a href="../breakfast/index.html">View All Breakfast Places</a></li>
                    </ul>
                </div>
                <div class="footer-column">
                    <h3>Best Lunch in Zurich</h3>
                    <ul class="footer-list">
                        <li><a href="../index.html">View Top Rated Restaurants</a></li>
                    </ul>
                </div>
                <div class="footer-column">
                    <h3>Best Dinner in Zurich</h3>
                    <ul class="footer-list">
                        <li><a href="../index.html">View Top Rated Restaurants</a></li>
                    </ul>
                </div>
            </div>
            <div class="footer-sitemap">
                <a href="sitemap.html">Sitemap</a>
            </div>
        </div>
    </footer>
</body>
</html>
'''
    
    # Write the HTML to a file
    with open(os.path.join(OUTPUT_DIR, 'restaurant', f"{restaurant_slug}.html"), 'w', encoding='utf-8') as f:
        f.write(page_html)

# Generate homepage
homepage_html = f'''<!DOCTYPE html>
<html lang="en">
{generate_head("Best Restaurants in Zurich", 
               "Find the best restaurants in Zurich, Switzerland. Discover top-rated places for breakfast, lunch, and dinner.",
               "restaurants in Zurich, best breakfast in Zurich, best Italian restaurants in Zurich, best Chinese restaurant in Zurich")}
<body>
    {generate_header()}
    
    <div class="hero">
        <div class="container">
            <h1>Find the Best Restaurants in Zurich</h1>
            <p>Discover top-rated places for breakfast, lunch, and dinner in Zurich, Switzerland.</p>
            <div class="search-bar">
                <input type="text" placeholder="Search for restaurants, cuisines, or areas...">
                <button>Search</button>
            </div>
        </div>
    </div>
    
    <div class="container">
        <section class="featured-categories">
            <h2>Browse by Cuisine</h2>
            <div class="category-grid">
'''

# Add category cards to homepage with fixed images
category_images = {
    'Italian': 'https://images.unsplash.com/photo-1595295333158-4742f28fbd85?ixlib=rb-4.0.3&auto=format&fit=crop&w=1740&q=80',
    'Chinese': 'https://images.unsplash.com/photo-1563245372-f21724e3856d?ixlib=rb-4.0.3&auto=format&fit=crop&w=1742&q=80',
    'Japanese': 'https://images.unsplash.com/photo-1579871494447-9811cf80d66c?ixlib=rb-4.0.3&auto=format&fit=crop&w=1740&q=80',
    'Swiss': 'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?ixlib=rb-4.0.3&auto=format&fit=crop&w=1740&q=80',
    'French': 'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?ixlib=rb-4.0.3&auto=format&fit=crop&w=1740&q=80',
    'Indian': 'https://images.unsplash.com/photo-1505253758473-96b7015fcd40?ixlib=rb-4.0.3&auto=format&fit=crop&w=1740&q=80',
    'Thai': 'https://images.unsplash.com/photo-1559847844-5315695dadae?ixlib=rb-4.0.3&auto=format&fit=crop&w=1740&q=80',
    'Mexican': 'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?ixlib=rb-4.0.3&auto=format&fit=crop&w=1740&q=80',
    'Vegetarian': 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?ixlib=rb-4.0.3&auto=format&fit=crop&w=1740&q=80',
    'Breakfast': 'https://images.unsplash.com/photo-1484723091739-30a097e8f929?ixlib=rb-4.0.3&auto=format&fit=crop&w=1740&q=80'
}

for category in CATEGORIES:
    category_slug = category.lower()
    image_url = category_images.get(category, 'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?ixlib=rb-4.0.3&auto=format&fit=crop&w=1740&q=80')
    
    homepage_html += f'''
                <a href="{category_slug}/index.html" class="category-card">
                    <img src="{image_url}" alt="{category} Food">
                    <h3>{category}</h3>
                </a>
    '''

homepage_html += '''
            </div>
        </section>
        
        <section class="featured-restaurants">
            <h2>Top Rated Restaurants in Zurich</h2>
            <div class="restaurant-list">
'''

# Get top 6 restaurants across all areas
all_restaurants = []
for area in restaurants_by_area:
    all_restaurants.extend(restaurants_by_area[area])

all_restaurants.sort(key=lambda x: float(x['score']), reverse=True)
top_restaurants = all_restaurants[:6]

# Add top restaurant cards to homepage
for restaurant in top_restaurants:
    homepage_html += generate_restaurant_card(restaurant, level=0)

homepage_html += '''
            </div>
        </section>
        
        <section class="featured-restaurants">
            <h2>Best Restaurants in Zurich Old Town</h2>
            <p class="section-intro">
                Zurich's Old Town has some of the best restaurants in the city. You'll find everything from traditional Swiss dishes to international flavors, all in a lively and welcoming atmosphere.
                <a href="old-town/index.html">View all restaurants in Old Town →</a>
            </p>
            <div class="restaurant-list">
'''

# Get top 3 restaurants in Old Town
old_town_restaurants = restaurants_by_area.get('Old Town', [])[:3]

# Add Old Town restaurant cards to homepage
for restaurant in old_town_restaurants:
    homepage_html += generate_restaurant_card(restaurant, level=0)

homepage_html += '''
            </div>
        </section>
        
        <section class="featured-restaurants">
            <h2>Best Restaurants in Zurich Airport</h2>
            <p class="section-intro">
                If you're at Zurich Airport, there are plenty of good places to eat. Whether you want a quick snack or a proper meal, you'll find quality food without having to leave the airport.
                <a href="airport/index.html">View all restaurants at Zurich Airport →</a>
            </p>
            <div class="restaurant-list">
'''

# Get top 3 restaurants in Airport area
airport_restaurants = restaurants_by_area.get('Airport', [])[:3]

# Add Airport restaurant cards to homepage
for restaurant in airport_restaurants:
    homepage_html += generate_restaurant_card(restaurant, level=0)

homepage_html += '''
            </div>
        </section>
        
        <section class="faq-section">
            <h2>Frequently Asked Questions</h2>
            
            <div class="faq-item">
                <div class="faq-question">Are Restaurants in Zurich Expensive?</div>
                <div class="faq-answer">
                    Yes, Zurich is known for being one of the most expensive cities in the world, and dining out is no exception. 
                    However, there are options for every budget. While high-end restaurants can be quite pricey, you can find more 
                    affordable options in university areas, food markets, and ethnic restaurants. Many restaurants also offer 
                    reasonably priced lunch menus (Tagesmenu) on weekdays.
                </div>
            </div>
            
            <div class="faq-item">
                <div class="faq-question">What Are Some Famous Dishes in Zurich?</div>
                <div class="faq-answer">
                    Zurich's most famous dish is Züri-Geschnetzeltes, which consists of sliced veal in a creamy mushroom sauce, 
                    typically served with Rösti (Swiss-style hash browns). Other popular Swiss dishes include fondue (melted cheese 
                    served in a communal pot), raclette (melted cheese served with potatoes), and various types of sausages like 
                    Cervelat and St. Galler Bratwurst.
                </div>
            </div>
            
            <div class="faq-item">
                <div class="faq-question">What Are the Typical Dining Hours in Zurich?</div>
                <div class="faq-answer">
                    Lunch is typically served from 11:30 AM to 2:00 PM, and dinner from 6:30 PM to 10:00 PM. Many kitchens close 
                    relatively early compared to other European cities. It's advisable to check the opening hours of restaurants 
                    in advance, especially on Sundays when many establishments are closed.
                </div>
            </div>
            
            <div class="faq-item">
                <div class="faq-question">Do I Need to Tip at Restaurants in Zurich?</div>
                <div class="faq-answer">
                    Tipping is not as expected in Switzerland as it is in countries like the United States. Service charges are 
                    included in the bill, but it's common to round up the total or add a small tip (5-10%) for good service. 
                    Simply tell the server the total amount you wish to pay when they bring the bill.
                </div>
            </div>
            
            <div class="faq-item">
                <div class="faq-question">What Are the Best Areas for Dining in Zurich?</div>
                <div class="faq-answer">
                    The Old Town (Altstadt) offers many traditional Swiss restaurants and upscale dining options. Niederdorf is 
                    known for its lively atmosphere and diverse cuisine. Zurich West has become a trendy area with innovative 
                    restaurants and food halls. Seefeld offers beautiful lakeside dining options, while the area around 
                    Langstrasse has many ethnic restaurants and casual eateries.
                </div>
            </div>
            
            <div class="faq-item">
                <div class="faq-question">Is It Necessary to Make Reservations at Restaurants in Zurich?</div>
                <div class="faq-answer">
                    For popular restaurants, especially on weekends, it's highly recommended to make reservations in advance. 
                    Many upscale restaurants require reservations, while casual eateries might accept walk-ins. During lunch 
                    hours on weekdays, business restaurants can get very busy, so reservations are advisable even then.
                </div>
            </div>
        </section>
    </div>
    
    ''' + generate_footer() + '''
</body>
</html>
'''

with open(os.path.join(OUTPUT_DIR, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(homepage_html)

# Generate area pages
for area in AREAS:
    area_slug = area.lower().replace(' ', '-')
    area_dir = os.path.join(OUTPUT_DIR, area_slug)
    
    # Get restaurants for this area
    area_restaurants = restaurants_by_area.get(area, [])
    
    # Generate area index page
    area_html = f'''<!DOCTYPE html>
<html lang="en">
{generate_head(f"Best Restaurants in {area}, Zurich", 
               f"Discover the top-rated restaurants in {area}, Zurich. Find places for breakfast, lunch, and dinner.",
               f"restaurants in {area} Zurich, best restaurants {area}, dining {area} Zurich",
               level=1)}
<body>
    {generate_header(level=1)}
    
    <div class="container">
        <h1 class="page-title">Best Restaurants in {area}, Zurich</h1>
        
        <div class="category-nav">
            <a href="index.html" class="active">All</a>
'''

    # Add category links
    for category in CATEGORIES:
        if category in restaurants_by_area_category[area] and restaurants_by_area_category[area][category]:
            category_slug = category.lower()
            area_html += f'<a href="{category_slug}/index.html">{category}</a>\n'

    area_html += '''
        </div>
        
        <div class="restaurant-list">
'''

    # Add restaurant cards
    for restaurant in area_restaurants[:20]:  # Limit to top 20
        area_html += generate_restaurant_card(restaurant, level=1)

    area_html += '''
        </div>
    </div>
    
    ''' + generate_footer() + '''
</body>
</html>
'''

    with open(os.path.join(area_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(area_html)
    
    # Generate category pages for this area
    for category in CATEGORIES:
        if category not in restaurants_by_area_category[area] or not restaurants_by_area_category[area][category]:
            continue
            
        category_slug = category.lower()
        category_dir = os.path.join(area_dir, category_slug)
        
        # Get restaurants for this category in this area
        category_restaurants = restaurants_by_area_category[area][category]
        
        # Generate category page
        category_html = f'''<!DOCTYPE html>
<html lang="en">
{generate_head(f"Best {category} Restaurants in {area}, Zurich", 
               f"Find the best {category} restaurants in {area}, Zurich. Top-rated {category} dining options.",
               f"best {category} restaurants in {area} Zurich, {category} food {area}, {category} dining Zurich",
               level=2)}
<body>
    {generate_header(level=2)}
    
    <div class="container">
        <h1 class="page-title">Best {category} Restaurants in {area}, Zurich</h1>
        
        <div class="category-nav">
            <a href="../index.html">All Restaurants in {area}</a>
'''

        # Add other category links
        for other_category in CATEGORIES:
            if other_category == category or other_category not in restaurants_by_area_category[area] or not restaurants_by_area_category[area][other_category]:
                continue
                
            other_category_slug = other_category.lower()
            category_html += f'<a href="../{other_category_slug}/index.html">{other_category}</a>\n'

        category_html += f'<a href="index.html" class="active">{category}</a>\n'

        category_html += '''
        </div>
        
        <div class="restaurant-list">
'''

        # Add restaurant cards
        for restaurant in category_restaurants[:20]:  # Limit to top 20
            category_html += generate_restaurant_card(restaurant, level=2)

        category_html += '''
        </div>
    </div>
    
    ''' + generate_footer() + '''
</body>
</html>
'''

        with open(os.path.join(category_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(category_html)

# Generate cuisine category pages at the root level
for category in CATEGORIES:
    category_slug = category.lower()
    category_dir = os.path.join(OUTPUT_DIR, category_slug)
    
    # Get all restaurants for this category across all areas
    category_restaurants = []
    for area in restaurants_by_area_category:
        if category in restaurants_by_area_category[area]:
            category_restaurants.extend(restaurants_by_area_category[area][category])
    
    # Sort by score
    category_restaurants.sort(key=lambda x: float(x['score']), reverse=True)
    
    # Generate category page
    category_html = f'''<!DOCTYPE html>
<html lang="en">
{generate_head(f"Best {category} Restaurants in Zurich", 
               f"Find the best {category} restaurants in Zurich. Top-rated {category} dining options across the city.",
               f"best {category} restaurants in Zurich, {category} food Zurich, {category} dining Zurich",
               level=1)}
<body>
    {generate_header(level=1)}
    
    <div class="container">
        <h1 class="page-title">Best {category} Restaurants in Zurich</h1>
        
        <div class="category-nav">
            <a href="index.html" class="active">{category}</a>
'''

    # Add other category links
    for other_category in CATEGORIES:
        if other_category == category:
            continue
            
        other_category_slug = other_category.lower()
        category_html += f'<a href="../{other_category_slug}/index.html">{other_category}</a>\n'

    category_html += '''
        </div>
        
        <p class="section-intro">
'''
    # Add custom description based on the category
    if category == 'Italian':
        category_html += f'''
            Explore the best Italian restaurants across Zurich. From authentic pasta and pizza to innovative Italian cuisine, 
            find the perfect Italian dining experience in the city.
        '''
    elif category == 'Chinese':
        category_html += f'''
            Explore the best Chinese restaurants across Zurich. From traditional Cantonese dishes to spicy Sichuan specialties, 
            find the perfect Chinese dining experience in the city.
        '''
    elif category == 'Japanese':
        category_html += f'''
            Explore the best Japanese restaurants across Zurich. From fresh sushi and sashimi to hearty ramen and tempura, 
            find the perfect Japanese dining experience in the city.
        '''
    elif category == 'Swiss':
        category_html += f'''
            Explore the best Swiss restaurants across Zurich. From traditional fondue and raclette to modern Swiss cuisine, 
            find the perfect Swiss dining experience in the city.
        '''
    elif category == 'French':
        category_html += f'''
            Explore the best French restaurants across Zurich. From classic bistro fare to refined haute cuisine, 
            find the perfect French dining experience in the city.
        '''
    elif category == 'Indian':
        category_html += f'''
            Explore the best Indian restaurants across Zurich. From aromatic curries to tandoori specialties, 
            find the perfect Indian dining experience in the city.
        '''
    elif category == 'Thai':
        category_html += f'''
            Explore the best Thai restaurants across Zurich. From spicy curries to fragrant noodle dishes, 
            find the perfect Thai dining experience in the city.
        '''
    elif category == 'Mexican':
        category_html += f'''
            Explore the best Mexican restaurants across Zurich. From authentic tacos to flavorful enchiladas, 
            find the perfect Mexican dining experience in the city.
        '''
    elif category == 'Vegetarian':
        category_html += f'''
            Explore the best Vegetarian restaurants across Zurich. From creative plant-based dishes to traditional vegetarian cuisine, 
            find the perfect Vegetarian dining experience in the city.
        '''
    elif category == 'Breakfast':
        category_html += f'''
            Explore the best Breakfast spots across Zurich. From hearty morning meals to delightful brunch options, 
            find the perfect Breakfast experience in the city.
        '''
    else:
        category_html += f'''
            Explore the best {category} restaurants across Zurich. From authentic flavors to innovative interpretations, 
            find the perfect {category} dining experience in the city.
        '''
    
    category_html += '''
        </p>
        
        <div class="restaurant-list">
'''

    # Add restaurant cards
    for restaurant in category_restaurants[:20]:  # Limit to top 20
        category_html += generate_restaurant_card(restaurant, level=1)

    category_html += '''
        </div>
    </div>
    
    ''' + generate_footer() + '''
</body>
</html>
'''

    with open(os.path.join(category_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(category_html)

# Process all restaurants and create individual pages
all_restaurants = []
for area in restaurants_by_area:
    all_restaurants.extend(restaurants_by_area[area])

# Create individual restaurant pages
for restaurant in all_restaurants:
    generate_restaurant_page(restaurant, all_restaurants)

# Generate a sitemap page
sitemap_html = f'''<!DOCTYPE html>
<html lang="en">
{generate_head("Sitemap", 
               "Sitemap for Zurich Restaurant Guide. Find all pages and sections of our website.",
               "sitemap, Zurich restaurants, restaurant guide")}
<body>
    {generate_header()}
    
    <div class="container">
        <h1 class="page-title">Sitemap</h1>
        
        <div class="sitemap-section">
            <h2>Main Pages</h2>
            <ul class="sitemap-list">
                <li><a href="index.html">Homepage</a></li>
            </ul>
        </div>
        
        <div class="sitemap-section">
            <h2>Areas</h2>
            <ul class="sitemap-list">
'''

for area in AREAS:
    area_slug = area.lower().replace(' ', '-')
    sitemap_html += f'                <li><a href="{area_slug}/index.html">{area}</a></li>\n'

sitemap_html += '''
            </ul>
        </div>
        
        <div class="sitemap-section">
            <h2>Cuisines</h2>
            <ul class="sitemap-list">
'''

for category in CATEGORIES:
    category_slug = category.lower()
    sitemap_html += f'                <li><a href="{category_slug}/index.html">{category}</a></li>\n'

sitemap_html += '''
            </ul>
        </div>
    </div>
    
    ''' + generate_footer() + '''

    <style>
        .sitemap-section {
            margin-bottom: 40px;
        }
        
        .sitemap-section h2 {
            margin-bottom: 20px;
            color: #333;
            text-align: center;
        }
        
        .sitemap-list {
            list-style: none;
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 10px;
        }
        
        .sitemap-list li {
            padding: 10px;
            background-color: #fff;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }
        
        .sitemap-list li:hover {
            transform: translateY(-3px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        .sitemap-list a {
            color: #333;
            text-decoration: none;
            display: block;
        }
        
        .sitemap-list a:hover {
            color: #d32323;
        }
    </style>
</body>
</html>
'''

with open(os.path.join(OUTPUT_DIR, 'sitemap.html'), 'w', encoding='utf-8') as f:
    f.write(sitemap_html)

print(f"Restaurant directory generated in '{OUTPUT_DIR}' folder.") 