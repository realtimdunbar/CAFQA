#!/bin/bash
#SBATCH -Jexperiment1
#SBATCH --account=gts-mqureshi4-rg
#SBATCH -N1 --ntasks-per-node=1
#SBATCH --mem-per-cpu=192G
#SBATCH -t90:00:00
#SBATCH -qinferno
#SBATCH -oReport-%j.out
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=tdunbar8@gatech.edu

module load anaconda3/2022.05.0.1

# Create the conda environment
conda env create -f environment.yml

# Activate the conda environment
source activate mycondaenv1

# Run the script
cd /storage/home/hcoda1/2/tdunbar8/p-mqureshi4-0/CAFQA/example/wrapper/
python wrapper.py

# Deactivate the conda environment after running
conda deactivate