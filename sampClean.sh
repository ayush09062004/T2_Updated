#!/bin/bash
#SBATCH --job-name=DemoTest2_sim
#SBATCH --output=logs/DemoTest2_%j.out
#SBATCH --error=logs/DemoTest2_%j.err
#SBATCH --ntasks=2
#SBATCH --time=48:00:00
#SBATCH --mem=40G
#SBATCH --cpus-per-task=10

module load openmpi
# Or activate your env if not using modules:
source ~/projects/WorkT2/.venv/bin/activate

# Run your script
mpirun -np 2 python run_orientation_closed.py nest 2 param/defaults Demo_Try2

