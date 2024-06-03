@echo off
REM Activate Conda environment
call conda activate DynamicRoutingTaskDev

REM Run Python script
python "DynamicRouting1.py" "taskParams.json"

REM Deactivate Conda environment (optional)
call conda deactivate
