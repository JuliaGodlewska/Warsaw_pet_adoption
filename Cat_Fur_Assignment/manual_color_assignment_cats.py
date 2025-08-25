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

class CatLabeler:
    def __init__(self, root):
        self.root = root
        self.root.title("Kitty Viewer")
        
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
        
        self.submit_btn = tk.Button(root, text="Next Cat", command=self.next_cat)
        self.submit_btn.pack(pady=10)
        
        self.color_entry.bind('<Return>', lambda e: self.pattern_entry.focus())
        self.pattern_entry.bind('<Return>', lambda e: self.next_cat())
        
        self.current_index = 0
        
    def next_cat(self):
        if self.current_index < len(df):
            new_color = self.color_entry.get()
            new_pattern = self.pattern_entry.get()
            
            if new_color:
                df.at[self.current_index, 'color'] = new_color
            if new_pattern:
                df.at[self.current_index, 'pattern'] = new_pattern
            
            df.to_csv(csv_path, index=False)
            print(f"Saved row {self.current_index}: color='{new_color}', pattern='{new_pattern}'")
        
        self.current_index += 1
        self.load_next_cat()
    
    def load_next_cat(self):
        while self.current_index < len(df):
            row = df.iloc[self.current_index]
            
            if pd.isna(row.get('image_url')) or row['image_url'] == '':
                self.current_index += 1
                continue
                
            if pd.notna(row.get('color')) and pd.notna(row.get('pattern')):
                print(f"Skipping row {self.current_index} (already labeled)")
                self.current_index += 1
                continue
                
            print(f"\n--- Kitty row {self.current_index}/{len(df)} ---")
            print(f"URL: {row['image_url']}")
            
            try:
                response = requests.get(row['image_url'], timeout=10)
                img_data = BytesIO(response.content)
                img = Image.open(img_data)
                img.thumbnail((800, 800))
                
                img_tk = ImageTk.PhotoImage(img)
                self.panel.config(image=img_tk)
                self.panel.image = img_tk
                
                self.color_entry.delete(0, tk.END)
                if pd.notna(row.get('color')):
                    self.color_entry.insert(0, row['color'])
                
                self.pattern_entry.delete(0, tk.END)
                if pd.notna(row.get('pattern')):
                    self.pattern_entry.insert(0, row['pattern'])
                
                self.color_entry.focus_set()
                self.color_entry.icursor(tk.END)
                
                return
                
            except Exception as e:
                print(f"Error loading image {row['image_url']}: {e}")
                self.current_index += 1
        
        print("\nAll kitties done!")
        self.root.destroy()

root = tk.Tk()
app = CatLabeler(root)

app.load_next_cat()

root.mainloop()