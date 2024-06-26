import tkinter as tk
import subprocess
import os
import json
import time
import win32api
import win32con



    
def run_script(task_version, mouse_number):
    
    conda_env = "DynamicRoutingTaskDev"  # Hardcoded Conda environment
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
    activate_cmd = f'conda activate {conda_env} && '
    
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

def duplicate_displays(display_index):
    # Get display device name for the specified index
    device_name = win32api.EnumDisplayDevices(None, display_index)

    # Get current display settings for the specified device
    devmode = win32api.EnumDisplaySettings(device_name.DeviceName, win32con.ENUM_CURRENT_SETTINGS)

    try:
        # Set display mode to duplicate
        result = win32api.ChangeDisplaySettingsEx(device_name.DeviceName, devmode)
        if result == win32con.DISP_CHANGE_SUCCESSFUL:
            print(f"Display {display_index} duplicated successfully")
        else:
            print(f"Failed to duplicate display {display_index}. Error code: {result}")
    except Exception as e:
        print(f"An error occurred: {e}")



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


# Create a button to duplicate displays
duplicate_button = tk.Button(root, text="Duplicate Displays", command=lambda: duplicate_displays(0))
duplicate_button.grid()

# Start the GUI event loop
root.mainloop()
