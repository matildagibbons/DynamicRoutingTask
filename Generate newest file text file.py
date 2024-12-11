import tkinter as tk
from tkinter import filedialog
import os
import pandas as pd

# Function to open a file dialog and get the file path
def choose_file():
    root = tk.Tk()
    root.withdraw()  # Don't need the root window, just the dialog
    file_path = filedialog.askopenfilename(title="Select a Behavior File", 
                                           filetypes=[("HDF5 Files", "*.hdf5"), ("All Files", "*.*")])
    return file_path

# Automatically select the newest file in a directory
def choose_newest_file(directory):
    files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.hdf5')]  # Adjust for file type
    if files:
        newest_file = max(files, key=os.path.getctime)  # Get the most recently created file
        return newest_file
    else:
        print("No files found.")
        return None

# Get the path of the newest file from a specific directory
directory = 'C:\\Users\\teenspirit\\Desktop\\Behavior\\Tilda\\Behavior data\\Data\\MG021'  # Replace with your directory
newest_file = choose_newest_file(directory)
with open('newest_file.txt', 'w') as file:
    file.write(newest_file)

print(f"The newest file path has been written to 'newest_file.txt'.")

