import pandas as pd

# Read the CSV file
file_path = 'Outscraper-20250307150536s9c_restaurants.csv'
df = pd.read_csv(file_path)

# Display basic information
print("CSV File Structure:")
print(f"Number of rows: {len(df)}")
print(f"Columns: {df.columns.tolist()}")

# Display first few rows
print("\nFirst 5 rows:")
print(df.head(5).to_string()) 