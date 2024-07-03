import tkinter as tk
import subprocess
import os
import json
import time

# Global variables to store selected task version and mouse number
selected_task_version = ""
selected_mouse_number = ""

# Define the run_script function to execute the task
def run_script(task_version, mouse_number):
    if task_version and mouse_number:
        conda_env = "c:\\Users\\teenspirit\\Desktop\\Behavior\\Tilda\\Stimuli\\Behaviour\\DynamicRoutingTask\\.conda"
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
        params['savePath'] = os.path.join(save_dir, f"{mouse_id}_{task_type}_{stage}_{start_time}.hdf5")
        with open(params_file, 'w') as f:
            json.dump(params, f)

        # Activate Conda environment
        activate_cmd = f'conda activate {conda_env} &&'

        # Command to execute the Python script with parameters
        python_cmd = f'python "{script_path}" "{params_file}" "{save_dir}"'

        # Combine activation and script execution commands
        full_cmd = activate_cmd + python_cmd

        # Display a black screen before starting the task
        black_screen = tk.Toplevel()
        black_screen.attributes('-fullscreen', True)
        black_screen.configure(background='black')
        black_screen.title("Black Screen")

        # Function to handle key press event
        def on_key_press(event):
            black_screen.destroy()  # Destroy black screen immediately
            root.update()  # Update GUI to reflect immediate destruction

            # Start the task without waiting
            subprocess.Popen(full_cmd, shell=True)

        # Bind key press event to the black screen window
        black_screen.bind('<KeyPress>', on_key_press)
        black_screen.focus_force()

        black_screen.mainloop()
    else:
        print("Please select a task stage and enter a mouse number first.")

# Function to set the selected task version
def set_selected_task_version(task_version):
    global selected_task_version
    selected_task_version = task_version

# Function to set the selected mouse number
def set_selected_mouse_number(mouse_number):
    global selected_mouse_number
    selected_mouse_number = mouse_number

def get_task_versions(task_type):
    task_versions = []
    for file_name in os.listdir("C:\\Users\\teenspirit\\Desktop\\Behavior\\Tilda\\Stimuli\\Behaviour\\DynamicRoutingTask"):
        if task_type in file_name.lower():
            task_versions.append(file_name)
    return task_versions

# Create the main window
root = tk.Tk()
root.title("Behavioral Task Runner")

# Create entry field for typing in mouse number
label_mouse = tk.Label(root, text="Mouse Number:")
label_mouse.grid(row=0, column=4)
entry_mouse = tk.Entry(root)
entry_mouse.grid(row=0, column=5)

def create_task_buttons(root, row, task_type):
    task_versions = get_task_versions(task_type)
    for i, task_version in enumerate(task_versions):
        stage = task_version.split('_')[3]
        task_type = task_version.split('_')[-1].split('.')[0].capitalize()
        button_text = f"{task_type} - Stage {stage}"
        button = tk.Button(root, text=button_text, command=lambda version=task_version: set_selected_task_version(version))
        button.grid(row=row+i, column=0, columnspan=2)

# Create buttons for selecting task type
visual_button = tk.Button(root, text="Visual", command=lambda: create_task_buttons(root, 1, 'vis'))
visual_button.grid(row=0, column=0, columnspan=2)

auditory_button = tk.Button(root, text="Auditory", command=lambda: create_task_buttons(root, 1, 'aud'))
auditory_button.grid(row=0, column=2, columnspan=2)

# Function to execute the selected task
def execute_selected_task():
    global selected_task_version, selected_mouse_number
    set_selected_mouse_number(entry_mouse.get())
    if selected_task_version and selected_mouse_number:
        run_script(selected_task_version, selected_mouse_number)
    else:
        print("Please select a task stage and enter a mouse number first.")

# Add a run button
run_button = tk.Button(root, text="Run Task", command=execute_selected_task)
run_button.grid(row=2, column=0, columnspan=4)

# Start the GUI event loop
root.mainloop()
