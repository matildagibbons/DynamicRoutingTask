import tkinter as tk
from tkinter import messagebox
import json
import os
from datetime import datetime
from pathlib import Path
from RFMapping import RFMapping
import time

class TaskGUI(tk.Tk):
    def __init__(self, params):
        super().__init__()
        
        self.title("RF Mapping Task")
        self.geometry("400x350")
        
        self.params = params

        # Create form fields to edit parameters
        self.create_widgets()
    
    def create_widgets(self):
        # Label for Subject Name
        self.subject_name_label = tk.Label(self, text="Subject Name:")
        self.subject_name_label.pack(pady=5)
        
        self.subject_name_var = tk.StringVar(value="Subject001")  # Default subject name
        self.subject_name_entry = tk.Entry(self, textvariable=self.subject_name_var)
        self.subject_name_entry.pack(pady=5)

        # Label for Task Version
        self.task_version_label = tk.Label(self, text="Task Version:")
        self.task_version_label.pack(pady=5)
        
        self.task_version_var = tk.StringVar(value=self.params.get('taskVersion', 'vis only'))
        self.task_version_entry = tk.Entry(self, textvariable=self.task_version_var)
        self.task_version_entry.pack(pady=5)

        # Max Frames input
        self.max_frames_label = tk.Label(self, text="Max Frames:")
        self.max_frames_label.pack(pady=5)
        
        self.max_frames_var = tk.IntVar(value=self.params.get('maxFrames', 300))
        self.max_frames_entry = tk.Entry(self, textvariable=self.max_frames_var)
        self.max_frames_entry.pack(pady=5)

        # Max Trials input
        self.max_trials_label = tk.Label(self, text="Max Trials:")
        self.max_trials_label.pack(pady=5)
        
        self.max_trials_var = tk.IntVar(value=self.params.get('maxTrials', 100))
        self.max_trials_entry = tk.Entry(self, textvariable=self.max_trials_var)
        self.max_trials_entry.pack(pady=5)

        # Max Blocks input
        self.max_blocks_label = tk.Label(self, text="Max Blocks:")
        self.max_blocks_label.pack(pady=5)
        
        self.max_blocks_var = tk.IntVar(value=self.params.get('maxBlocks', 6))
        self.max_blocks_entry = tk.Entry(self, textvariable=self.max_blocks_var)
        self.max_blocks_entry.pack(pady=5)

        # Button to Start Task
        self.start_button = tk.Button(self, text="Start Task", command=self.start_task)
        self.start_button.pack(pady=20)

    def start_task(self):
        # Update parameters from the user input fields
        self.params['taskVersion'] = self.task_version_var.get()
        self.params['maxFrames'] = self.max_frames_var.get()
        self.params['maxTrials'] = self.max_trials_var.get()
        self.params['maxBlocks'] = self.max_blocks_var.get()

        # Get subject name from the entry field
        subject_name = self.subject_name_var.get()

        # Generate save path based on subject name and current date
        current_date = datetime.now().strftime("%Y-%m-%d")
        save_path = f"C:\\Users\\teenspirit\\Desktop\\Behavior\\Tilda\\Behavior data\\Data\\{subject_name}"

        # Ensure the directory exists
        os.makedirs(save_path, exist_ok=True)

        # Update the params with the dynamic save path
        start_time = time.strftime('%Y%m%d_%H%M%S', time.localtime())
        self.params['subjectName'] = subject_name
        self.params['savePath'] = os.path.join(save_path, subject_name + '_' + start_time + '.hdf5')
        

        # Save parameters to the file (if needed)
        params_path = Path("taskParams.json")
        with open(params_path, 'w') as f:
            json.dump(self.params, f, indent=4)

        # Start the task
        try:
            # Assuming the RFMapping class is correctly imported and available
            task = RFMapping(self.params)
            task.start(self.params['subjectName'])
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while starting the task: {e}")

if __name__ == "__main__":
    # Load parameters from a file
    params_path = "C:\\Users\\teenspirit\\Desktop\\Behavior\\Tilda\\Stimuli\\Behaviour\\DynamicRoutingTask\\taskParams.json"
    try:
        with open(params_path, 'r') as f:
            params = json.load(f)
    except FileNotFoundError:
        messagebox.showerror("Error", "Parameters file not found.")
        exit()

    # Create and run the GUI
    app = TaskGUI(params)
    app.mainloop()
