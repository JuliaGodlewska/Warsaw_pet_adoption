import pandas as pd

# Save data to Excel
def save_to_excel(pets_data, filename="pets_data.xlsx"):
    # Check if there's data to save
    if not pets_data:
        print("No data to save.")
        return

    # Convert the list of dictionaries to a pandas DataFrame
    df = pd.DataFrame(pets_data)

    # Save to Excel
    try:
        df.to_excel(filename, index=False)  # index=False to avoid adding an extra index column
        print(f"Data successfully saved to {filename}")
    except Exception as e:
        print(f"Error saving to Excel: {e}")
        
# Function to save data to CSV
def save_to_csv(pets_data, filename="pets_data.csv"):
    # Check if there's data to save
    if not pets_data:
        print("No data to save.")
        return

    # Convert the list of dictionaries to a pandas DataFrame
    df = pd.DataFrame(pets_data)

    # Save to CSV
    try:
        df.to_csv(filename, index=False)  # index=False to avoid adding an extra index column
        print(f"Data successfully saved to {filename}")
    except Exception as e:
        print(f"Error saving to CSV: {e}")
