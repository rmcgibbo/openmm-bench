from . import create_benchmark

@create_benchmark(test='pme', platform='OpenCL', cutoff=0.9, heavy=False, device='0', precision='mixed')
def track_opencl(): pass
@create_benchmark(test='pme', platform='CUDA', cutoff=0.9, heavy=False, device='0', precision='mixed')
def track_cuda(): pass
@create_benchmark(test='pme', platform='CPU', cutoff=0.9, heavy=False, device='0', precision='mixed')
def track_cpu(): pass
