import tkinter as tk
import subprocess

def run_script(task_version):
    conda_env = "DynamicRoutingTaskDev"  # Hardcoded Conda environment
    script_path = "C:\\Users\\teenspirit\\Desktop\\Behavior\\Tilda\\Stimuli\\Behaviour\\DynamicRoutingTask\\DynamicRouting1.py"  # Hardcoded script path
    params_file = f"C:\\Users\\teenspirit\\Desktop\\Behavior\\Tilda\\Stimuli\\Behaviour\\DynamicRoutingTask\\taskParams_{task_version.lower().replace(' ', '_')}.json"  # Construct parameters file path
    
    # Activate Conda environment
    activate_cmd = f'conda activate {conda_env} && '
    
    # Command to execute the Python script with parameters
    python_cmd = f'python "{script_path}" "{params_file}"'
    
    # Combine activation and script execution commands
    full_cmd = activate_cmd + python_cmd
    
    # Execute the command in a subprocess
    subprocess.run(full_cmd, shell=True)

# Create the main window
root = tk.Tk()
root.title("Behavioral Task Runner")

# Create buttons for selecting task version
task_versions = [
    "Templeton Stage 0 Aud",
    "Templeton Stage 1 Aud",
    "Templeton Stage 2 Aud",
    "Templeton Stage 0 Vis",
    "Templeton Stage 1 Vis",
    "Templeton Stage 2 Vis"
]

for i, task_version in enumerate(task_versions):
    button = tk.Button(root, text=task_version, command=lambda version=task_version: run_script(version))
    button.grid(row=i, column=0, columnspan=2)

# Start the GUI event loop
root.mainloop()
