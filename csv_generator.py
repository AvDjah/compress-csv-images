import csv
import random

# Function to generate random product names
def generate_product_name():
    adjectives = ['Elegant', 'Durable', 'Compact', 'Innovative', 'Eco-friendly']
    nouns = ['Laptop', 'Smartphone', 'Tablet', 'Headphones', 'Smartwatch']
    return f"{random.choice(adjectives)} {random.choice(nouns)}"

# Function to generate random image URLs
def generate_image_urls():
    base_url = "https://example.com/images/"
    return ','.join([f"{base_url}{random.randint(1000, 9999)}.jpg" for _ in range(random.randint(1, 3))])

# Generate the CSV file
def generate_csv(filename, num_rows):
    with open(filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        
        # Write the header
        csvwriter.writerow(["Sno.", "Product Name", "Input Image Urls"])
        
        # Write the data rows
        for i in range(1, num_rows + 1):
            csvwriter.writerow([
                i,
                generate_product_name(),
                generate_image_urls()
            ])

# Generate a CSV file with 10 rows
generate_csv('products.csv', 10)

print("CSV file 'products.csv' has been generated successfully.")