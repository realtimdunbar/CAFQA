#!/bin/bash
#SBATCH -test
#SBATCH --account=gts-gburdell3
#SBATCH –N2 --ntasks-per-node=2
#SBATCH --mem-per-cpu=16G
#SBATCH -t1:00:00
#SBATCH -qembers
#SBATCH -oReport-%j.out
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=tdunbar8@gatech.edu

module load anaconda3/2022.05.0.1

# Create the conda environment
conda env create -f environment.yml

# Activate the conda environment
source activate $ENV_NAME

# Run the script
cd /storage/home/hcoda1/2/tdunbar8/p-mqureshi4-0/CAFQA/example/wrapper/
python wrapper.py

# Deactivate the conda environment after running
conda deactivate