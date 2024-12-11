import tkinter as tk
from tkinter import messagebox
import os
import glob
import subprocess

def get_newest_file(mouse_name):
    # Set the directory path based on the mouse name
    directory = f'C:/Users/teenspirit/Desktop/Behavior/Tilda/Behavior data/Data/{mouse_name}'  # Adjust your directory path accordingly
    
    # Use glob to search for .hdf5 files in the specified directory
    hdf5_files = glob.glob(os.path.join(directory, "*.hdf5"))
    
    if not hdf5_files:
        return None  # No .hdf5 files found
    
    # Get the most recent file based on modification time
    newest_file = max(hdf5_files, key=os.path.getmtime)
    text_file_path = 'newest_file.txt'
    with open(text_file_path, 'w') as file:
        file.write(newest_file)
    
    # Return the path of the newest file (also saved in the text file)
    return newest_file

def save_mouse_name_to_file(mouse_name):
    file_path = r'C:\\Users\\teenspirit\\Desktop\\Behavior\\Tilda\\Behavior data\\Data\\Mouse name text files\\mouse_name.txt'
    try:
        with open(file_path, "w") as file:
            file.write(mouse_name)
        print(f"Mouse name '{mouse_name}' saved successfully.")
    except Exception as e:
        print(f"Error saving mouse name: {e}")


def run_notebook():
    mouse_name = mouse_name_entry.get().strip()
    if not mouse_name:
        messagebox.showerror("Error", "Please enter a mouse name.")
        return
    
    notebook_command = f'jupyter nbconvert --execute --inplace "Behaviour analysis.ipynb"'

    try:
            subprocess.run(notebook_command, check=True, shell=True)
            messagebox.showinfo("Success", "Notebook executed successfully!")
    except subprocess.CalledProcessError:
            messagebox.showerror("Error", "Failed to execute the notebook.")
        

# Create the main Tkinter window
root = tk.Tk()
root.title("Behavior Analysis Tool")

# Create and place the widgets
tk.Label(root, text="Enter Mouse Name:").pack(padx=20, pady=10)
mouse_name_entry = tk.Entry(root, width=40)
mouse_name_entry.pack(padx=20, pady=10)

run_button = tk.Button(root, text="Run Analysis", command=run_notebook)
run_button.pack(padx=20, pady=20)

# Start the Tkinter event loop
root.mainloop()
