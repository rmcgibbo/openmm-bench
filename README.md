OpenMM Continuous Benchmarking with Airspeed Velocity

The idea is to continuously track the performance of OpenMM
on each commit, on a couple different machines/platforms.

Currently deployed at http://rmcgibbo.github.io/openmm-bench/



## Installation on a new benchmarking machine

1. Install airspeed velocity from http://github.com/rmcgibbo/asv
2. If you have OpenCL or CUDA installed in a nonstandard location,
   make a file inside the `conda-recipes/` directory called
   build_<your-hostname>.sh, and customize the flags that get
   passed to cmake
3. Make sure you have `conda` installed and available. Then, install
   `conda-build`, and `jinja2` int othe root conda environment
```
$ conda install conda-build jinja2
```
4. Install `ccache` through your package manager to speed up compilation
```
$ sudo apt-get install ccache
```
5. Make sure you have the omnia binstar channel installed
   (`$ conda config --add channels omnia`)
6. Run `$ asv run` with different options to try it out.
7. Acquire commit rights on https://github.com/rmcgibbo/openmm-bench
   so that you can push up new results

Set up a cron tab to run the `run.sh` script periodically, which
will benchmark new commits and push the results/visualization up
to the web.