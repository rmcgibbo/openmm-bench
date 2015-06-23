from . import create_benchmark

@create_benchmark(test='gbsa', platform='OpenCL', steps=500, cutoff=0.9, heavy=False, device='0', precision='mixed')
def time_opencl(): pass
@create_benchmark(test='gbsa', platform='CUDA', steps=500, cutoff=0.9, heavy=False, device='0', precision='mixed')
def time_cuda(): pass
@create_benchmark(test='gbsa', platform='CPU', steps=100, cutoff=0.9, heavy=False, device='0', precision='mixed')
def time_cpu(): pass
