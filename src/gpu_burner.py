import multiprocessing
import time
import numpy as np

try:
    import pyopencl as cl
    HAS_OPENCL = True
except ImportError:
    HAS_OPENCL = False

def burn_gpu_worker(stop_event):
    if not HAS_OPENCL:
        # Fallback to heavy numpy matrix multiplication on CPU if OpenCL is not available
        while not stop_event.is_set():
            a = np.random.rand(1000, 1000)
            b = np.random.rand(1000, 1000)
            _ = np.dot(a, b)
            time.sleep(0.01)
        return

    try:
        # Get all platforms and pick the first one with a GPU
        platforms = cl.get_platforms()
        gpu_devices = []
        for p in platforms:
            gpu_devices.extend(p.get_devices(device_type=cl.device_type.GPU))
            
        if not gpu_devices:
            # Fallback to CPU platform if no GPU
            for p in platforms:
                gpu_devices.extend(p.get_devices())
                
        if not gpu_devices:
            return

        device = gpu_devices[0]
        ctx = cl.Context([device])
        queue = cl.CommandQueue(ctx)

        # Create large arrays
        size = 1024 * 1024 * 5 # 5 million floats
        a_np = np.random.rand(size).astype(np.float32)
        b_np = np.random.rand(size).astype(np.float32)

        mf = cl.mem_flags
        a_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=a_np)
        b_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=b_np)
        res_g = cl.Buffer(ctx, mf.WRITE_ONLY, a_np.nbytes)

        # Heavy kernel
        prg = cl.Program(ctx, """
        __kernel void stress(__global const float *a_g, __global const float *b_g, __global float *res_g)
        {
          int gid = get_global_id(0);
          float sum = 0.0f;
          for(int i = 0; i < 5000; i++){
              sum += sin(a_g[gid]) * cos(b_g[gid]) * tan((float)i);
          }
          res_g[gid] = sum;
        }
        """).build()

        while not stop_event.is_set():
            prg.stress(queue, a_np.shape, None, a_g, b_g, res_g)
            queue.finish()
            time.sleep(0.01)
            
    except Exception as e:
        # If OpenCL fails, just loop to keep process alive (or use numpy fallback)
        while not stop_event.is_set():
            time.sleep(1)

class GPUBurner:
    def __init__(self):
        self.process = None
        self.stop_event = multiprocessing.Event()
        self.is_running = False

    def start(self):
        if self.is_running:
            return
        self.stop_event.clear()
        self.process = multiprocessing.Process(target=burn_gpu_worker, args=(self.stop_event,))
        self.process.daemon = True
        self.process.start()
        self.is_running = True

    def stop(self):
        self.stop_event.set()
        if self.process:
            self.process.terminate()
            self.process.join(timeout=1.0)
            self.process = None
        self.is_running = False
