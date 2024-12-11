import tkinter as tk
import subprocess
import os
import json
import time
import nidaqmx  # Assuming you're using nidaqmx to control the NIDAQ card

# Global variable to track task running state
is_task_running = False

# Function to administer water
def administer_water():
    with nidaqmx.Task() as task:
        task.do_channels.add_do_chan("Dev1/port0/line1")  # Replace with your NIDAQ channel
        task.write(True)  # Trigger the water valve (open it)
        time.sleep(0.10)  # Keep it open for 1 second
        task.write(False)  # Close the valve

# Function to run the script for the behavioral task
def run_script(task_version, mouse_number):
    global is_task_running
    is_task_running = True  # Mark the task as running

    conda_env = "c:\\Users\\teenspirit\\.conda\\envs\\newerenv"
    script_path = "C:\\Users\\teenspirit\\Desktop\\Behavior\\Tilda\\Stimuli\\Behaviour\\DynamicRoutingTask\\DynamicRouting1.py"
    params_file = f"C:\\Users\\teenspirit\\Desktop\\Behavior\\Tilda\\Stimuli\\Behaviour\\DynamicRoutingTask\\{task_version.lower()}"
    save_dir = f"C:\\Users\\teenspirit\\Desktop\\Behavior\\Tilda\\Behavior data\\Data\\{mouse_number}"

    os.makedirs(save_dir, exist_ok=True)

    with open(params_file, 'r') as f:
        params = json.load(f)
    mouse_id = mouse_number
    start_time = time.strftime('%Y%m%d_%H%M%S', time.localtime())
    stage = task_version.split('_')[3]
    task_type = task_version.split('_')[-1].split('.')[0].capitalize()
    params['subjectName'] = mouse_id
    params['savePath'] = os.path.join(save_dir, mouse_id + '_' + task_type + '_' + stage + '_' + start_time + '.hdf5')
    with open(params_file, 'w') as f:
        json.dump(params, f)

    activate_cmd = f'conda activate {conda_env} &&'
    python_cmd = f'python "{script_path}" "{params_file}" "{save_dir}"'
    full_cmd = activate_cmd + python_cmd

    subprocess.run(full_cmd, shell=True)

    is_task_running = False  # Mark the task as not running once it's finished

# Function to get task versions
def get_task_versions(task_type):
    task_versions = []
    for file_name in os.listdir("C:\\Users\\teenspirit\\Desktop\\Behavior\\Tilda\\Stimuli\\Behaviour\\DynamicRoutingTask"):
        if task_type in file_name.lower():
            task_versions.append(file_name)
    return task_versions

# Create the main window
root = tk.Tk()
root.title("Behavioral Task Runner")

# Set the window size (width x height)
root.geometry("1400x800")  # Adjust the size as needed


# Set the background color of the main window to dark green
root.config(bg="darkolivegreen4")

# Create entry field for typing in mouse number
label_mouse = tk.Label(root, text="Mouse Number:", font=("Arial", 25), bg="darkolivegreen4", fg="gray10")
label_mouse.grid(row=2, column=3, padx=0, pady=(0,0))
entry_mouse = tk.Entry(root, font=("Arial", 14), bg="white", fg="black")  # Light background for text entry
entry_mouse.grid(row=2, column=3, padx=0, pady=(60,0))

def create_task_buttons(root, row, task_type):
    task_versions = get_task_versions(task_type)
    for i, task_version in enumerate(task_versions):
        stage = task_version.split('_')[3]  # Corrected index to extract the stage number
        task_type = task_version.split('_')[-1].split('.')[0].capitalize()
        button_text = f"{task_type} - Stage {stage}"
        
        # Create a button with larger font, size, and padding
        button = tk.Button(
            root,
            text=button_text,
            command=lambda version=task_version: run_script(version, entry_mouse.get()),
            width=20,  # Set a width (number of characters in the button)
            height=2,  # Set the height (rows of text in the button)
            font=("Arial", 14),  # Set a larger font
            padx=10, pady=10,  # Add padding inside the button
            bg="black", fg="white",  # Dark green background and white text
            borderwidth=8,  # Set the border width
            relief="raised" 
        )
        button.grid(row=row+i, column=3, padx=0, pady=(0,0))

# Create buttons for selecting task type with larger spacing and font
visual_button = tk.Button(
    root,
    text="Visual",
    command=lambda: create_task_buttons(root, 1, 'vis'),
    width=20,
    height=5,
    font=("Loma", 25),  # Larger font for the task type button
    padx=20, pady=20,
    bg="orchid2", fg="gray10",
    borderwidth=8,  # Set the border width
    relief="groove" # Dark green background and white text
)
visual_button.grid(row=2, column=2, padx=20, pady=40)
auditory_button = tk.Button(
    root,
    text="Auditory",
    command=lambda: create_task_buttons(root, 1, 'aud'),
    width=20,
    height=5,
    font=("Arial", 25),  # Larger font for the task type button
    padx=20, pady=20,
    bg="darkorange2", fg="gray10",
    borderwidth=8,  # Set the border width
    relief="groove"# Dark green background and white text
)
auditory_button.grid(row=2, column=4, padx=20, pady=40)

# Create the "Water Reward" button
water_button = tk.Button(
    root,
    text="Give water droplet",
    command=administer_water,  # Call the water administration function when clicked
    width=20,
    height=5,
    font=("Arial", 25),  # Larger font for visibility
    padx=20, pady=20,
    bg="deeppink3", fg="gray10",
    borderwidth=8,  # Set the border width
    relief="raised"# Dark green background and white text
)
water_button.grid(row=3, column=3, pady=100)  # Position it in a new row

# Start the GUI event loop
root.mainloop()
