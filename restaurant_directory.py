import csv
import os
import re
from collections import defaultdict
import math

# Define constants
CSV_FILE = 'Outscraper-20250307150536s9c_restaurants.csv'
OUTPUT_DIR = 'restaurant_directory'
SITE_NAME = 'Zurich Restaurant Guide'
SITE_LOGO = 'logo.png'  # Will create this later

# Create output directory structure
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Define areas in Zurich
AREAS = [
    'Old Town', 'Niederdorf', 'Enge', 'Oerlikon', 'Seefeld', 
    'Wiedikon', 'Airport', 'Altstetten', 'Wollishofen', 'Zurich West'
]

# Define restaurant categories
CATEGORIES = [
    'Italian', 'Chinese', 'Japanese', 'Swiss', 'French', 
    'Indian', 'Thai', 'Mexican', 'Vegetarian', 'Seafood'
]

# Create directories for each area
for area in AREAS:
    area_dir = os.path.join(OUTPUT_DIR, area.lower().replace(' ', '-'))
    if not os.path.exists(area_dir):
        os.makedirs(area_dir)

# Function to clean and normalize text
def clean_text(text):
    if not text:
        return ""
    return text.strip()

# Function to determine area based on address
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

# Function to determine category based on restaurant type
def determine_category(restaurant_type, subtypes):
    if not restaurant_type:
        return "Other"
    
    for category in CATEGORIES:
        if category.lower() in restaurant_type.lower() or (subtypes and category.lower() in subtypes.lower()):
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
        rating = row.get('rating', '0')
        reviews = row.get('reviews', '0')
        website = clean_text(row.get('site', ''))
        phone = clean_text(row.get('phone', ''))
        
        # Determine area and category
        area = determine_area(address, postal_code)
        category = determine_category(restaurant_type, subtypes)
        
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
            'phone': phone
        }
        
        # Add to appropriate collections
        restaurants_by_area[area].append(restaurant)
        restaurants_by_area_category[area][category].append(restaurant)

# Sort restaurants by score in descending order
for area in restaurants_by_area:
    restaurants_by_area[area].sort(key=lambda x: float(x['score']), reverse=True)
    
    for category in restaurants_by_area_category[area]:
        restaurants_by_area_category[area][category].sort(key=lambda x: float(x['score']), reverse=True)

# Function to generate HTML for a restaurant listing
def generate_restaurant_html(restaurant):
    rating_stars = '★' * int(float(restaurant['rating'])) + '☆' * (5 - int(float(restaurant['rating'])))
    
    return f"""
    <div class="restaurant-card">
        <h3>{restaurant['name']}</h3>
        <div class="restaurant-details">
            <div class="rating">
                <span class="stars">{rating_stars}</span>
                <span class="rating-value">{restaurant['rating']}</span>
                <span class="reviews">({restaurant['reviews']} reviews)</span>
            </div>
            <div class="type">{restaurant['type']}</div>
            <div class="address">{restaurant['address']}</div>
            <div class="contact">
                {f'<a href="{restaurant["website"]}" target="_blank">Website</a>' if restaurant["website"] else ''}
                {f'<span class="phone">{restaurant["phone"]}</span>' if restaurant["phone"] else ''}
            </div>
        </div>
    </div>
    """

# Function to generate the navigation menu
def generate_menu():
    menu_html = '<nav class="main-menu"><ul>'
    
    # Add home link
    menu_html += '<li><a href="../index.html">Home</a></li>'
    
    # Add area links
    for area in AREAS:
        area_slug = area.lower().replace(' ', '-')
        menu_html += f'<li><a href="../{area_slug}/index.html">{area}</a></li>'
    
    menu_html += '</ul></nav>'
    return menu_html

# Function to generate the header with logo
def generate_header():
    return f"""
    <header>
        <div class="logo">
            <a href="../index.html">
                <img src="../{SITE_LOGO}" alt="{SITE_NAME}">
                <span>{SITE_NAME}</span>
            </a>
        </div>
        {generate_menu()}
    </header>
    """

# Function to generate HTML head section
def generate_head(title, description, keywords):
    return f"""
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="{description}">
        <meta name="keywords" content="{keywords}">
        <title>{title} - {SITE_NAME}</title>
        <link rel="stylesheet" href="../styles.css">
    </head>
    """

# Generate CSS file
css_content = """
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Helvetica Neue', Arial, sans-serif;
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

.main-menu {
    background-color: #d32323;
    padding: 10px 0;
}

.main-menu ul {
    display: flex;
    list-style: none;
    justify-content: center;
    flex-wrap: wrap;
}

.main-menu li {
    margin: 0 15px;
}

.main-menu a {
    color: white;
    text-decoration: none;
    font-weight: bold;
    padding: 5px 10px;
    border-radius: 4px;
    transition: background-color 0.3s;
}

.main-menu a:hover {
    background-color: rgba(255,255,255,0.2);
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

.category-nav a:hover {
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
}

.restaurant-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.restaurant-card h3 {
    padding: 15px;
    background-color: #f8f9fa;
    border-bottom: 1px solid #eee;
}

.restaurant-details {
    padding: 15px;
}

.rating {
    margin-bottom: 10px;
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
}

.type, .address {
    margin-bottom: 5px;
    color: #555;
}

.contact {
    margin-top: 10px;
    display: flex;
    justify-content: space-between;
}

.contact a {
    color: #d32323;
    text-decoration: none;
}

.contact a:hover {
    text-decoration: underline;
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
}

footer {
    background-color: #333;
    color: white;
    text-align: center;
    padding: 20px;
    margin-top: 40px;
}

footer p {
    margin-bottom: 10px;
}

footer a {
    color: #d32323;
    text-decoration: none;
}

footer a:hover {
    text-decoration: underline;
}

@media (max-width: 768px) {
    .hero h1 {
        font-size: 2rem;
    }
    
    .restaurant-list {
        grid-template-columns: 1fr;
    }
    
    .main-menu ul {
        flex-direction: column;
        align-items: center;
    }
    
    .main-menu li {
        margin: 5px 0;
    }
}
"""

with open(os.path.join(OUTPUT_DIR, 'styles.css'), 'w', encoding='utf-8') as f:
    f.write(css_content)

# Generate a simple logo placeholder
logo_html = """
<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
    <rect width="200" height="200" fill="#d32323"/>
    <text x="50%" y="50%" font-family="Arial" font-size="24" fill="white" text-anchor="middle" dominant-baseline="middle">ZRG</text>
</svg>
"""

with open(os.path.join(OUTPUT_DIR, SITE_LOGO), 'w', encoding='utf-8') as f:
    f.write(logo_html)

# Generate homepage
homepage_html = f"""<!DOCTYPE html>
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
        <section class="featured-areas">
            <h2>Explore Zurich by Area</h2>
            <div class="area-grid">
"""

# Add area cards to homepage
for area in AREAS:
    area_slug = area.lower().replace(' ', '-')
    homepage_html += f"""
                <a href="{area_slug}/index.html" class="area-card">
                    <img src="https://source.unsplash.com/random/300x200/?zurich,{area_slug}" alt="{area}">
                    <div class="area-name">{area}</div>
                </a>
    """

homepage_html += """
            </div>
        </section>
        
        <section class="featured-categories">
            <h2>Browse by Cuisine</h2>
            <div class="category-grid">
"""

# Add category cards to homepage
for category in CATEGORIES:
    category_slug = category.lower()
    homepage_html += f"""
                <div class="category-card">
                    <img src="https://source.unsplash.com/random/300x200/?{category_slug},food" alt="{category} Food">
                    <h3>{category}</h3>
                </div>
    """

homepage_html += """
            </div>
        </section>
    </div>
    
    <footer>
        <div class="container">
            <p>&copy; 2023 Zurich Restaurant Guide. All rights reserved.</p>
            <p>Data sourced from public reviews and restaurant information.</p>
        </div>
    </footer>
</body>
</html>
"""

with open(os.path.join(OUTPUT_DIR, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(homepage_html)

# Generate area pages
for area in AREAS:
    area_slug = area.lower().replace(' ', '-')
    area_dir = os.path.join(OUTPUT_DIR, area_slug)
    
    # Get restaurants for this area
    area_restaurants = restaurants_by_area.get(area, [])
    
    # Generate area index page
    area_html = f"""<!DOCTYPE html>
<html lang="en">
{generate_head(f"Best Restaurants in {area}, Zurich", 
               f"Discover the top-rated restaurants in {area}, Zurich. Find places for breakfast, lunch, and dinner.",
               f"restaurants in {area} Zurich, best restaurants {area}, dining {area} Zurich")}
<body>
    {generate_header()}
    
    <div class="container">
        <h1 class="page-title">Best Restaurants in {area}, Zurich</h1>
        
        <div class="category-nav">
            <a href="index.html">All</a>
"""

    # Add category links
    for category in CATEGORIES:
        category_slug = category.lower().replace(' ', '-')
        if category in restaurants_by_area_category[area]:
            area_html += f'<a href="{category_slug}-restaurant/index.html">{category}</a>\n'

    area_html += """
        </div>
        
        <div class="restaurant-list">
"""

    # Add restaurant cards
    for restaurant in area_restaurants[:20]:  # Limit to top 20
        area_html += generate_restaurant_html(restaurant)

    area_html += """
        </div>
    </div>
    
    <footer>
        <div class="container">
            <p>&copy; 2023 Zurich Restaurant Guide. All rights reserved.</p>
            <p>Data sourced from public reviews and restaurant information.</p>
        </div>
    </footer>
</body>
</html>
"""

    with open(os.path.join(area_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(area_html)
    
    # Generate category pages for this area
    for category in CATEGORIES:
        if category not in restaurants_by_area_category[area]:
            continue
            
        category_slug = category.lower().replace(' ', '-')
        category_dir = os.path.join(area_dir, f"{category_slug}-restaurant")
        
        if not os.path.exists(category_dir):
            os.makedirs(category_dir)
        
        # Get restaurants for this category in this area
        category_restaurants = restaurants_by_area_category[area][category]
        
        # Generate category page
        category_html = f"""<!DOCTYPE html>
<html lang="en">
{generate_head(f"Best {category} Restaurants in {area}, Zurich", 
               f"Find the best {category} restaurants in {area}, Zurich. Top-rated {category} dining options.",
               f"best {category} restaurants in {area} Zurich, {category} food {area}, {category} dining Zurich")}
<body>
    {generate_header()}
    
    <div class="container">
        <h1 class="page-title">Best {category} Restaurants in {area}, Zurich</h1>
        
        <div class="category-nav">
            <a href="../index.html">All Restaurants in {area}</a>
"""

        # Add other category links
        for other_category in CATEGORIES:
            if other_category == category or other_category not in restaurants_by_area_category[area]:
                continue
                
            other_category_slug = other_category.lower().replace(' ', '-')
            category_html += f'<a href="../{other_category_slug}-restaurant/index.html">{other_category}</a>\n'

        category_html += """
        </div>
        
        <div class="restaurant-list">
"""

        # Add restaurant cards
        for restaurant in category_restaurants[:20]:  # Limit to top 20
            category_html += generate_restaurant_html(restaurant)

        category_html += """
        </div>
    </div>
    
    <footer>
        <div class="container">
            <p>&copy; 2023 Zurich Restaurant Guide. All rights reserved.</p>
            <p>Data sourced from public reviews and restaurant information.</p>
        </div>
    </footer>
</body>
</html>
"""

        with open(os.path.join(category_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(category_html)

print(f"Restaurant directory generated in '{OUTPUT_DIR}' folder.") 