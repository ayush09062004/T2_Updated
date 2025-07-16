# T2_updated

This repository contains the **updated codebase of the T2 model**, originally developed in [T2 by dguarino](https://github.com/dguarino/T2). The updates improve compatibility, reproducibility, and integration with a customized version of the Mozaik framework for running large-scale spiking neural network simulations.

---

## 📦 Dependencies

The model depends on a customized version of Mozaik:

👉 [mozaik_4_T2 branch](https://github.com/ayush09062004/mozaik/tree/mozaik_4_T2)

---

## Installation Instructions

To install the dependencies and set up the environment for the **T2 model**, follow these steps:

> ⚠️ Make sure Anaconda is **not in your `$PATH`**.

```bash
# Set up directory and unload modules
cd ~/projects/T2
module purge

# Create virtual environment
python3.9 -m venv --prompt T2 .venv
source .venv/bin/activate

# Load MPI and basic Python packages
module load openmpi/4.1.6
pip install --upgrade pip
pip install "numpy<2"
pip install "cython<3"
pip install --no-cache-dir mpi4py
pip install scipy matplotlib quantities lazyarray interval Pillow param==1.5.1 parameters neo==0.12.0 psutil future requests elephant pytest-xdist pytest-timeout junitparser numba numpyencoder sphinx imageio

# Install libtool
mkdir -p ~/src
cd ~/src
wget https://ftpmirror.gnu.org/libtool/libtool-2.5.4.tar.gz
tar xzf libtool-2.5.4.tar.gz
cd libtool-2.5.4/
./configure --prefix=$HOME
make
make install

# Build and install NEST 3.4
mkdir -p $VIRTUAL_ENV/_build/nest-3.4
cd $VIRTUAL_ENV/_build/nest-3.4/
cmake -Dwith-mpi=ON -DCMAKE_INSTALL_PREFIX:PATH=$VIRTUAL_ENV -Dwith-optimize='-O3' -Dwith-ltdl=$HOME ~/src/nest-simulator-3.4
make -j8
make install

# Install nest-step-current-module
cd ~/src
git clone https://github.com/CSNG-MFF/nest-step-current-module.git
cd nest-step-current-module/
cmake -Dwith-mpi=ON -Dwith-optimize='-O3' -Dwith-nest=$VIRTUAL_ENV/bin/nest-config
make
make install

# Install PyNN (custom fork for Mozaik)
cd ~/src
git clone https://github.com/CSNG-MFF/PyNN.git
mv PyNN PyNN-4-mozaik
cd PyNN-4-mozaik
git checkout PyNNStepCurrentModule
pip install .

# Install imagen
cd ~/src
git clone https://github.com/antolikjan/imagen.git
cd imagen/
python setup.py install

# Install Mozaik (T2-compatible version)
cd ~/src
https://github.com/ayush09062004/mozaik.git
cd mozaik
git checkout mozaik_4_T2
python setup.py install
