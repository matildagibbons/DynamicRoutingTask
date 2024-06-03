@echo off
REM Activate Conda environment
call conda activate DynamicRoutingTaskDev

REM Run Python script with provided arguments
python "matildagibbons/DynamicRoutingTask/DynamicRouting1.py" "matildagibbons/DynamicRoutingTask/taskParams.json"

REM Deactivate Conda environment (optional)
call conda deactivate