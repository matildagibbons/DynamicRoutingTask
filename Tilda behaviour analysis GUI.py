import tkinter as tk
from tkinter import messagebox
from tkinter import PhotoImage
import os
import glob
import subprocess
from PIL import Image, ImageTk


import tkinter as tk
from PIL import Image, ImageTk
import os

# Function to get the path where the image will be saved
def get_image_path(mouse_name, plot_number):
    base_path = "C:\Users\teenspirit\Desktop\Behavior\Tilda\Behavior data\Data\Saved graphs" 
    mouse_folder = os.path.join(base_path, mouse_name)  # Create a folder for each mouse
    os.makedirs(mouse_folder, exist_ok=True)  # Create the folder if it doesn't exist

    # Construct the full path for the plot
    plot_path = os.path.join(mouse_folder, f"plot{plot_number}.png")
    return plot_path

# Function to display both plots in the GUI
def display_plots_in_gui(mouse_name):
    # Get the paths for both plots
    output_path1 = get_image_path(mouse_name, 1)  # Path for the first plot
    output_path2 = get_image_path(mouse_name, 2)  # Path for the second plot

    # Load and display the first plot
    img1 = Image.open(output_path1)
    img1 = img1.resize((400, 300), Image.Resampling.LANCZOS)
    tk_img1 = ImageTk.PhotoImage(img1)

    label1 = tk.Label(root, image=tk_img1)
    label1.image = tk_img1  # Keep reference to the image
    label1.pack(padx=10, pady=10)

    # Load and display the second plot
    img2 = Image.open(output_path2)
    img2 = img2.resize((400, 300), Image.Resampling.LANCZOS)
    tk_img2 = ImageTk.PhotoImage(img2)

    label2 = tk.Label(root, image=tk_img2)
    label2.image = tk_img2  # Keep reference to the image
    label2.pack(padx=10, pady=10)
    
# Function to be called when the button is clicked
def on_generate_button_click():
    mouse_name = mouse_name_entry.get()  # Get the mouse name from the entry field
    display_plots_in_gui(mouse_name)

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
    directory = r'C:\\Users\\teenspirit\\Desktop\\Behavior\\Tilda\\Behavior data\\Data\\Mouse name text files\\'
    file_path = os.path.join(directory, 'mouse_name.txt')
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

    # Save the mouse name to a text file
    save_mouse_name_to_file(mouse_name)
    
    # Get the newest file path and save it
    newest_file = get_newest_file(mouse_name)
    if newest_file:
        print(f"Newest file: {newest_file}")
    else:
        messagebox.showerror("Error", "No .hdf5 files found for the specified mouse.")
        return
    
    # Command to execute the notebook
    notebook_command = f'jupyter nbconvert --execute --inplace "Behaviour analysis.ipynb"'

    try:
        subprocess.run(notebook_command, check=True, shell=True)
        messagebox.showinfo("Success", "Notebook executed successfully!")
    except subprocess.CalledProcessError:
        messagebox.showerror("Error", "Failed to execute the notebook.")
        

# Create the Tkinter window
root = tk.Tk()
root.title("Behavior Analysis Tool")

# Add an entry widget to input the mouse name
mouse_name_label = tk.Label(root, text="Enter Mouse Name:")
mouse_name_label.pack(padx=10, pady=10)

mouse_name_entry = tk.Entry(root)
mouse_name_entry.pack(padx=10, pady=10)

# Add a button to generate and display the plots
generate_button = tk.Button(root, text="Display Plots", command=on_generate_button_click)
generate_button.pack(padx=20, pady=20)

# Create and place the widgets
tk.Label(root, text="Enter Mouse Name:").pack(padx=20, pady=10)
mouse_name_entry = tk.Entry(root, width=40)
mouse_name_entry.pack(padx=20, pady=10)

run_button = tk.Button(root, text="Run Analysis", command=run_notebook)
run_button.pack(padx=20, pady=20)

# Start the Tkinter event loop
root.mainloop()
