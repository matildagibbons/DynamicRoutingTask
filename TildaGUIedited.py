import tkinter as tk
import subprocess
import os
import json
import time
from PyDAQmx import Task
import numpy as np  # Import numpy to create arrays

def administer_water():
    """Function to administer water to the mouse via NI-DAQ."""
    task = Task()

    # Create a digital output channel on 'Dev1/port0/line1'
    task.CreateDOChan('Dev1/port0/line1', "WaterValve", 0)  # 0 indicates a digital output channel
    
    # Prepare the signal data to write (1 for high signal, 0 for low)
    data = np.zeros((1,), dtype=np.uint8)  # This will be a 1-element array for a single line
    
    # First, write a high signal (1) to output the water (turn on water valve)
    data[0] = 1  # Set the value to 1 to send a high signal
    task.WriteDigitalLines(1, 1, 10.0, None, data, None, None)  # Write the signal for 1 line
    print("Water administered.")
    
    time.sleep(1)  # Keep the valve open for 1 second
    
    # Now write a low signal (0) to stop the water (turn off water valve)
    data[0] = 0  # Set the value to 0 to stop the water
    task.WriteDigitalLines(1, 1, 10.0, None, data, None, None)  # Write the signal for 1 line
    
    task.StopTask()  # Stop the task to free resources
    task.ClearTask()  # Clear the task

def on_spacebar_press(event):
    """Triggered when the space bar is pressed."""
    administer_water()

def run_script(task_version, mouse_number):
    conda_env = "c:\\Users\\teenspirit\\Desktop\\Behavior\\Tilda\\Stimuli\\Behaviour\\DynamicRoutingTask\\.conda" # Hardcoded Conda environment
    script_path = "C:\\Users\\teenspirit\\Desktop\\Behavior\\Tilda\\Stimuli\\Behaviour\\DynamicRoutingTask\\DynamicRouting1.py"  # Hardcoded script path
    params_file = f"C:\\Users\\teenspirit\\Desktop\\Behavior\\Tilda\\Stimuli\\Behaviour\\DynamicRoutingTask\\{task_version.lower()}"  # Construct parameters file path
    save_dir = f"C:\\Users\\teenspirit\\Desktop\\Behavior\\Tilda\\Behavior data\\Data\\{mouse_number}"

    # Create the directory if it doesn't exist
    os.makedirs(save_dir, exist_ok=True)
    
    with open(params_file, 'r') as f:
        params = json.load(f)
    mouse_id = mouse_number
    start_time = time.strftime('%Y%m%d_%H%M%S', time.localtime()) # add this to file name so you don't accidentally overwrite something
    stage = task_version.split('_')[3]  # Corrected index to extract the stage number
    task_type = task_version.split('_')[-1].split('.')[0].capitalize()
    params['subjectName'] = mouse_id
    params['savePath'] = os.path.join(save_dir, mouse_id + '_' + task_type + '_' + stage  + '_' + start_time + '.hdf5')
    with open(params_file, 'w') as f:
        json.dump(params, f)
    
    params_file = f"C:\\Users\\teenspirit\\Desktop\\Behavior\\Tilda\\Stimuli\\Behaviour\\DynamicRoutingTask\\{task_version.lower()}"  # Construct parameters file path

    # Activate Conda environment
    activate_cmd = f'conda activate {conda_env} &&'
    
    # Command to execute the Python script with parameters
    python_cmd = f'python "{script_path}" "{params_file}" "{save_dir}"'  # Include save_dir as a parameter
    
    # Combine activation and script execution commands
    full_cmd = activate_cmd + python_cmd
    
    # Execute the command in a subprocess
    subprocess.run(full_cmd, shell=True)
    

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
        stage = task_version.split('_')[3]  # Corrected index to extract the stage number
        task_type = task_version.split('_')[-1].split('.')[0].capitalize()
        button_text = f"{task_type} - Stage {stage}" 
        button = tk.Button(root, text=button_text, command=lambda version=task_version: run_script(version, entry_mouse.get()))
        button.grid(row=row+i, column=0, columnspan=2)

# Create buttons for selecting task type
visual_button = tk.Button(root, text="Visual", command=lambda: create_task_buttons(root, 1, 'vis'))
visual_button.grid(row=0, column=0, columnspan=2)

auditory_button = tk.Button(root, text="Auditory", command=lambda: create_task_buttons(root, 1, 'aud'))
auditory_button.grid(row=0, column=2, columnspan=2)

# Bind the spacebar to the administer_water function
root.bind("<space>", on_spacebar_press)

# Start the GUI event loop
root.mainloop()
