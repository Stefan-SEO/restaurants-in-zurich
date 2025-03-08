# Zurich Restaurant Directory Generator

A Python script that processes restaurant data from a CSV file and generates a static HTML website for restaurants in Zurich, Switzerland.

## Features

- **SEO-Optimized**: Pages are structured to rank for keywords like "restaurants in Zurich", "best breakfast in Zurich", etc.
- **Area-based Navigation**: Browse restaurants by different areas of Zurich (Old Town, Niederdorf, Enge, etc.)
- **Cuisine Categories**: Filter restaurants by cuisine type (Italian, Chinese, Japanese, etc.)
- **Responsive Design**: Mobile-friendly layout that works on all devices
- **Rating-based Sorting**: Restaurants are sorted by a score combining rating and number of reviews
- **Image Support**: Displays restaurant photos when available
- **Price Range**: Shows price indicators for each restaurant

## URL Structure

The website follows this URL structure:

- Homepage: `index.html`
- Area pages: `/{area}/index.html` (e.g., `/old-town/index.html`)
- Category pages: `/{area}/{category}-restaurant/index.html` (e.g., `/old-town/italian-restaurant/index.html`)

## How to Use

1. Make sure you have the CSV file `Outscraper-20250307150536s9c_restaurants.csv` in the same directory as the script.

2. Run the Python script:
   ```
   python generate_restaurant_directory.py
   ```

3. The website will be generated in the `zurich_restaurants` folder.

4. Open `zurich_restaurants/index.html` in your web browser to view the site.

5. To deploy to a web server, simply upload the entire `zurich_restaurants` folder to your hosting provider.

## Customization

You can customize the website by modifying the following in the Python script:

- `AREAS`: List of areas in Zurich
- `CATEGORIES`: List of restaurant categories
- CSS styles in the `css_content` variable
- HTML templates in the various generator functions

## Requirements

- Python 3.6 or higher
- No external dependencies required (uses only standard library modules)

## Data Structure

The script expects a CSV file with the following columns:
- `name`: Restaurant name
- `full_address`: Complete address
- `postal_code`: Postal code for area determination
- `type`: Restaurant type/cuisine
- `subtypes`: Additional cuisine types
- `about`: Description of the restaurant
- `rating`: Google rating (0-5)
- `reviews`: Number of reviews
- `site`: Website URL
- `phone`: Contact phone number
- `photo`: URL to restaurant photo
- `range`: Price range indicator

## License

This project is for demonstration purposes only. The restaurant data should be used in accordance with its original licensing terms. 