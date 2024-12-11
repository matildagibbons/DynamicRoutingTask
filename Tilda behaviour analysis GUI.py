import tkinter as tk
from tkinter import messagebox
import os
import subprocess

def get_newest_file(mouse_name):
    base_directory = r'C:\\Users\\teenspirit\\Desktop\\Behavior\\Tilda\\Behavior data\\Data'  
    mouse_folder = os.path.join(base_directory, mouse_name)

    # Check if the mouse folder exists
    if not os.path.exists(mouse_folder):
        messagebox.showerror("Error", f"Folder for mouse '{mouse_name}' not found!")
        return None

    # List all files in the directory and get the newest one
    try:
        files = [os.path.join(mouse_folder, f) for f in os.listdir(mouse_folder)]
        newest_file = max(files, key=os.path.getctime)
        return newest_file
    except ValueError:
        messagebox.showerror("Error", f"No files found for mouse '{mouse_name}'.")
        return None


def run_notebook():
    mouse_name = mouse_name_entry.get().strip()
    if not mouse_name:
        messagebox.showerror("Error", "Please enter a mouse name.")
        return

    # Get the newest file based on the mouse name
    newest_file = get_newest_file(mouse_name)
    if newest_file:
        # Save the newest file path as a text file
        text_file_path = 'newest_file.txt'
        with open(text_file_path, 'w') as file:
            file.write(newest_file)
        
        # Run the Jupyter notebook
        notebook_command = f'jupyter nbconvert --execute --inplace "Tilda behaviour analysis noyebook.ipynb" --output "{text_file_path}"'
        
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
