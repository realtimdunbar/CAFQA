#!/bin/bash

# Define variables
ENV_NAME="mycondaenv"
PYTHON_SCRIPT="wrapper.py"  # Name of the Python script to run

# Create the conda environment
conda env create -f environment.yml

# Activate the conda environment
source activate $ENV_NAME

# Run the Python script
cd example/wrapper/
python $PYTHON_SCRIPT

# Optional: Deactivate the conda environment after running
conda deactivate