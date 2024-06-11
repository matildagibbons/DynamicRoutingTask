import tkinter as tk
import subprocess
import os
import json
import time

def run_script(task_version, mouse_number, save_dir):
    conda_env = "DynamicRoutingTaskDev"  # Hardcoded Conda environment
    script_path = "C:\\Users\\teenspirit\\Desktop\\Behavior\\Tilda\\Stimuli\\Behaviour\\DynamicRoutingTask\\DynamicRouting1.py"  # Hardcoded script path
    params_file = os.path.join(save_dir, task_version.lower())  # Construct parameters file path

    # Activate Conda environment
    activate_cmd = f'conda activate {conda_env} && '
    
    # Command to execute the Python script with parameters
    python_cmd = f'python "{script_path}" "{params_file}"'  # Include save_dir as a parameter
    
    # Combine activation and script execution commands
    full_cmd = activate_cmd + python_cmd
    
    # Execute the command in a subprocess
    subprocess.run(full_cmd, shell=True)

def create_and_save_params(task_version, mouse_id, save_dir):
    params_file = os.path.join(save_dir, task_version.lower())
    with open(params_file, 'r') as f:
        params = json.load(f)
    
    start_time = time.strftime('%Y%m%d_%H%M%S', time.localtime())
    params['subjectName'] = mouse_id
    params['taskVersion'] = task_version
    file_name = f"{mouse_id}_{start_time}.hdf5"
    file_path = os.path.join(save_dir, file_name)
    params['savePath'] = file_path
    
    with open(params_file, 'w') as f:
        json.dump(params, f)

def get_task_versions(task_type):
    task_versions = []
    for file_name in os.listdir("C:\\Users\\teenspirit\\Desktop\\Behavior\\Tilda\\Stimuli\\Behaviour\\DynamicRoutingTask"):
        if task_type in file_name.lower():
            task_versions.append(file_name)
    return task_versions

def start_task(task_version, mouse_id, save_dir):
    create_and_save_params(task_version, mouse_id, save_dir)
    run_script(task_version, mouse_id, save_dir)

def create_task_buttons(root, row, task_type, save_dir):
    task_versions = get_task_versions(task_type)
    for i, task_version in enumerate(task_versions):
        stage = task_version.split('_')[3]
        task_type = task_version.split('_')[-1].split('.')[0].capitalize()
        button_text = f"{task_type} - Stage {stage}"
        button = tk.Button(root, text=button_text, command=lambda version=task_version: start_task(version, entry_mouse.get(), save_dir))
        button.grid(row=row+i, column=0, columnspan=2)

# Create the main window
root = tk.Tk()
root.title("Behavioral Task Runner")

# Create entry field for typing in mouse number
label_mouse = tk.Label(root, text="Mouse Number:")
label_mouse.grid(row=0, column=4)
entry_mouse = tk.Entry(root)
entry_mouse.grid(row=0, column=5)

# Define save directory
save_dir = "C:\\Users\\teenspirit\\Desktop\\Behavior\\Tilda\\Stimuli\\Behaviour\\DynamicRoutingTask"

# Create buttons for selecting task type
visual_button = tk.Button(root, text="Visual", command=lambda: create_task_buttons(root, 1, 'vis', save_dir))
visual_button.grid(row=0, column=0, columnspan=2)

auditory_button = tk.Button(root, text="Auditory", command=lambda: create_task_buttons(root, 1, 'aud', save_dir))
auditory_button.grid(row=0, column=2, columnspan=2)

# Start the GUI event loop
root.mainloop()
