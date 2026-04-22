import multiprocessing
import hashlib
import time

def mine_worker(stop_event):
    """Simulate crypto mining by brute-forcing SHA-256 hashes."""
    target = '00000' # Moderate difficulty for CPU
    base_string = "LANForge_Burnin_Payload_"
    nonce = 0
    
    while not stop_event.is_set():
        # Do hashes in batches to minimize the overhead of checking the stop_event
        for _ in range(20000):
            text = f"{base_string}{nonce}".encode('utf-8')
            hash_result = hashlib.sha256(text).hexdigest()
            if hash_result.startswith(target):
                # Simulated block found, just keep going to stress the CPU
                pass
            nonce += 1

class CryptoPayload:
    def __init__(self):
        self.processes = []
        self.stop_event = multiprocessing.Event()
        self.is_running = False
        
    def start(self):
        if self.is_running:
            return
            
        self.stop_event.clear()
        
        # Max out all CPU cores with mining threads
        num_cores = multiprocessing.cpu_count()
        for _ in range(num_cores):
            p = multiprocessing.Process(target=mine_worker, args=(self.stop_event,))
            p.daemon = True
            p.start()
            self.processes.append(p)
            
        self.is_running = True
        
    def stop(self):
        self.stop_event.set()
        for p in self.processes:
            p.terminate()
            p.join(timeout=1.0)
        self.processes = []
        self.is_running = False
