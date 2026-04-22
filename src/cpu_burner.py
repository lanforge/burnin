import multiprocessing
import time
import gc
import numpy as np

def burn_cpu(stop_event):
    """Heavy math using NumPy to trigger AVX/SIMD instructions for max wattage."""
    while not stop_event.is_set():
        # Large matrix multiplication heavily utilizes AVX instructions 
        # generating significantly more physical heat/wattage than pure Python math.
        a = np.random.rand(500, 500)
        b = np.random.rand(500, 500)
        for _ in range(10):
            if stop_event.is_set():
                break
            _ = np.dot(a, b)

def burn_ram(stop_event, target_mb):
    """Allocate memory to stress RAM and keep it active."""
    data = []
    try:
        # Allocate bytes in chunks to prevent immediate MemoryError crash
        for _ in range(target_mb // 10):
            if stop_event.is_set():
                break
            data.append(bytearray(10 * 1024 * 1024))
            
        while not stop_event.is_set():
            # Periodically write to memory to prevent paging
            if len(data) > 0:
                data[0][0] = 1
                data[-1][-1] = 1
            time.sleep(0.1)
    except MemoryError:
        pass
    finally:
        del data
        gc.collect()

class CPUBurner:
    def __init__(self):
        self.processes = []
        self.stop_event = multiprocessing.Event()
        self.is_running = False
        
    def start(self, stress_ram=True):
        if self.is_running:
            return
            
        self.stop_event.clear()
        
        # Start CPU burners (one per logical core)
        num_cores = multiprocessing.cpu_count()
        for _ in range(num_cores):
            p = multiprocessing.Process(target=burn_cpu, args=(self.stop_event,))
            p.daemon = True
            p.start()
            self.processes.append(p)
            
        # Start RAM burner (allocate roughly 30% of remaining RAM)
        if stress_ram:
            import psutil
            mem = psutil.virtual_memory()
            target_mb = int((mem.available / (1024 * 1024)) * 0.3)
            p_ram = multiprocessing.Process(target=burn_ram, args=(self.stop_event, target_mb))
            p_ram.daemon = True
            p_ram.start()
            self.processes.append(p_ram)
            
        self.is_running = True
            
    def stop(self):
        self.stop_event.set()
        for p in self.processes:
            p.terminate()
            p.join(timeout=1.0)
        self.processes = []
        self.is_running = False
