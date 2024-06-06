import tkinter as tk
import subprocess

def run_script():
    conda_env = entry_env.get()  # Get Conda environment from input field
    script_path = entry_script.get()  # Get script path from input field
    params_file = entry_params.get()  # Get parameters file path from input field
    
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

# Create input fields for parameters
label_env = tk.Label(root, text="Conda Environment:")
label_env.grid(row=0, column=0)
entry_env = tk.Entry(root)
entry_env.grid(row=0, column=1)

label_script = tk.Label(root, text="Script Path:")
label_script.grid(row=1, column=0)
entry_script = tk.Entry(root)
entry_script.grid(row=1, column=1)

label_params = tk.Label(root, text="Parameters File Path:")
label_params.grid(row=2, column=0)
entry_params = tk.Entry(root)
entry_params.grid(row=2, column=1)

# Create a button to run the script
run_button = tk.Button(root, text="Run Script", command=run_script)
run_button.grid(row=3, columnspan=2)

# Start the GUI event loop
root.mainloop()
