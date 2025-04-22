from cat_scraper import scrape_cats
from dog_scraper import scrape_dogs
from database import export_to_excel

def main():
    mode = input("Enter mode (scrape/export): ").strip().lower()
    
    if mode == 'scrape':
        try:
            max_cats = int(input("Enter the number of unique cats to scrape: ").strip())
            max_dogs = int(input("Enter the number of unique dogs to scrape: ").strip())
            start_page = int(input("Enter the starting page number: ").strip())

            # Scrape data
            print("Scraping cats...")
            cat_data = scrape_cats(max_pets=max_cats, start_page=start_page)  # Scrape specified number of unique cats
            print(f"Scraped {len(cat_data)} cats.")

            print("Scraping dogs...")
            dog_data = scrape_dogs(max_pets=max_dogs, start_page=start_page)  # Scrape specified number of unique dogs
            print(f"Scraped {len(dog_data)} dogs.")

            print("Scraping complete.")
        except Exception as e:
            print(f"An error occurred during scraping: {e}")

    elif mode == 'export':
        try:
            # Export data to Excel
            print("Exporting data...")
            export_to_excel()  # Export data from the database to an Excel file
            print("Data exported successfully.")
        except Exception as e:
            print(f"An error occurred during export: {e}")

    else:
        print("Invalid mode. Please enter 'scrape' or 'export'.")

if __name__ == "__main__":
    main()