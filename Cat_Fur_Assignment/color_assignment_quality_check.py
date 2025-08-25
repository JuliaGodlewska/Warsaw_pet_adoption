import pandas as pd
from PIL import Image, ImageTk
import requests
from io import BytesIO
import tkinter as tk

csv_path = r"D:\College_Stuff\Praca_licencjacka\cats_analysis.csv"
df = pd.read_csv(csv_path)

for col in ['color', 'pattern']:
    if col not in df.columns:
        df[col] = None

class CatCorrector:
    def __init__(self, root):
        self.root = root
        self.root.title("Kitty Corrector")
        
        self.info_label = tk.Label(root)
        self.info_label.pack(pady=5)
        
        self.panel = tk.Label(root)
        self.panel.pack(pady=10)
        
        self.input_frame = tk.Frame(root)
        self.input_frame.pack(pady=10)
        
        tk.Label(self.input_frame, text="Base color (e.g., black, orange):").grid(row=0, column=0, sticky='w')
        self.color_entry = tk.Entry(self.input_frame, width=30)
        self.color_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(self.input_frame, text="Pattern (e.g., tabby, solid):").grid(row=1, column=0, sticky='w')
        self.pattern_entry = tk.Entry(self.input_frame, width=30)
        self.pattern_entry.grid(row=1, column=1, padx=5, pady=5)
        
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(pady=10)
        
        self.prev_btn = tk.Button(self.button_frame, text="Previous Cat", command=self.previous_cat)
        self.prev_btn.grid(row=0, column=0, padx=5)
        
        self.next_btn = tk.Button(self.button_frame, text="Next Cat", command=self.next_cat)
        self.next_btn.grid(row=0, column=1, padx=5)
        
        self.save_btn = tk.Button(self.button_frame, text="Save & Next", command=self.save_and_next)
        self.save_btn.grid(row=0, column=2, padx=5)
        
        self.skip_no_photo_var = tk.BooleanVar(value=True)
        self.skip_checkbox = tk.Checkbutton(root, text="Skip 'no photo' entries", 
                                           variable=self.skip_no_photo_var)
        self.skip_checkbox.pack(pady=5)
        
        self.color_entry.bind('<Return>', lambda e: self.pattern_entry.focus())
        self.pattern_entry.bind('<Return>', lambda e: self.save_and_next())
        
        self.current_index = 0
        self.loaded_indices = [] 
        
    def save_current_values(self):
        """Save current values to dataframe"""
        if 0 <= self.current_index < len(df):
            new_color = self.color_entry.get().strip()
            new_pattern = self.pattern_entry.get().strip()
            
            df.at[self.current_index, 'color'] = new_color if new_color else None
            df.at[self.current_index, 'pattern'] = new_pattern if new_pattern else None
            
            df.to_csv(csv_path, index=False)
            print(f"Saved row {self.current_index}: color='{new_color}', pattern='{new_pattern}'")
    
    def should_skip(self, index):
        if index < 0 or index >= len(df):
            return True
            
        row = df.iloc[index]
        
        # Skip if color is "no photo" and we're skipping those
        if (self.skip_no_photo_var.get() and 
            pd.notna(row.get('color')) and 
            str(row['color']).lower() == 'no photo'):
            return True
        
        if pd.isna(row.get('image_url')) or row['image_url'] == '':
            return True
            
        return False
    
    def find_next_valid_index(self, start_index, direction=1):
        index = start_index + direction
        while 0 <= index < len(df):
            if not self.should_skip(index):
                return index
            index += direction
        return None
    
    def find_previous_valid_index(self, start_index):
        index = start_index - 1
        while index >= 0:
            if not self.should_skip(index):
                return index
            index -= 1
        return None
    
    def next_cat(self):
        next_index = self.find_next_valid_index(self.current_index, 1)
        if next_index is not None:
            self.current_index = next_index
            self.load_cat()
        else:
            print("\nNo more cats available!")
            self.info_label.config(text="No more cats available!")
    
    def previous_cat(self):
        prev_index = self.find_previous_valid_index(self.current_index)
        if prev_index is not None:
            self.current_index = prev_index
            self.load_cat()
        else:
            print("\nNo previous cats available!")
            self.info_label.config(text="No previous cats available!")
    
    def save_and_next(self):
        self.save_current_values()
        self.next_cat()
    
    def load_cat(self):
        if self.current_index < 0 or self.current_index >= len(df):
            print("Index out of bounds")
            return
            
        row = df.iloc[self.current_index]
        
        self.info_label.config(text=f"Cat {self.current_index + 1}/{len(df)} - Row {self.current_index}")
        
        print(f"\n--- Kitty row {self.current_index}/{len(df)} ---")
        print(f"URL: {row['image_url']}")
        print(f"Current color: {row.get('color', 'Not set')}")
        print(f"Current pattern: {row.get('pattern', 'Not set')}")
        
        try:
            response = requests.get(row['image_url'], timeout=10)
            response.raise_for_status()
            img_data = BytesIO(response.content)
            img = Image.open(img_data)
            img.thumbnail((800, 800))
            
            img_tk = ImageTk.PhotoImage(img)
            self.panel.config(image=img_tk)
            self.panel.image = img_tk
            
            self.color_entry.delete(0, tk.END)
            if pd.notna(row.get('color')):
                self.color_entry.insert(0, str(row['color']))
            
            self.pattern_entry.delete(0, tk.END)
            if pd.notna(row.get('pattern')):
                self.pattern_entry.insert(0, str(row['pattern']))
            
            self.color_entry.focus_set()
            self.color_entry.icursor(tk.END)
            
            if self.current_index not in self.loaded_indices:
                self.loaded_indices.append(self.current_index)
                
        except Exception as e:
            print(f"Error loading image {row['image_url']}: {e}")
            self.next_cat()

root = tk.Tk()
app = CatCorrector(root)

initial_index = 3150
while initial_index < len(df) and app.should_skip(initial_index):
    initial_index += 1

if initial_index < len(df):
    app.current_index = initial_index
    app.load_cat()
else:
    print("No valid cats found in the dataset!")
    app.info_label.config(text="No valid cats found in the dataset!")

root.mainloop()