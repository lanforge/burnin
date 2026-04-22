import customtkinter as ctk
import threading
import time
from src.monitor import get_metrics
from src.cpu_burner import CPUBurner
from src.gpu_burner import GPUBurner
from src.crypto_payload import CryptoPayload
from src.api import send_certificate

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class BurnInApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("LANForge Burn-In Tester")
        self.geometry("800x600")

        self.cpu_burner = CPUBurner()
        self.gpu_burner = GPUBurner()
        self.crypto_payload = CryptoPayload()

        self.is_monitoring = False
        self.max_temps = {"cpu_temp": 0.0, "gpu_temp": 0.0}
        self.start_time = None
        
        self.phases_completed = {
            "CPU_Burner": False,
            "GPU_Burner": False,
            "Crypto_Payload": False
        }

        self.setup_ui()

    def setup_ui(self):
        # Grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left Frame - Controls
        self.control_frame = ctk.CTkFrame(self)
        self.control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(self.control_frame, text="Burn-In Phases", font=("Arial", 20, "bold")).pack(pady=10)

        self.btn_cpu = ctk.CTkButton(self.control_frame, text="Phase 2: CPU/RAM Burner (START)", command=self.toggle_cpu)
        self.btn_cpu.pack(pady=10, fill="x", padx=20)

        self.btn_gpu = ctk.CTkButton(self.control_frame, text="Phase 3: GPU Burner (START)", command=self.toggle_gpu)
        self.btn_gpu.pack(pady=10, fill="x", padx=20)

        self.btn_crypto = ctk.CTkButton(self.control_frame, text="Phase 4: Crypto Payload (START)", command=self.toggle_crypto)
        self.btn_crypto.pack(pady=10, fill="x", padx=20)

        self.duration_frame = ctk.CTkFrame(self.control_frame)
        self.duration_frame.pack(pady=10, fill="x", padx=20)
        ctk.CTkLabel(self.duration_frame, text="Auto Burn-In Duration (Mins):").pack(side="left", padx=5)
        self.duration_entry = ctk.CTkEntry(self.duration_frame, width=50)
        self.duration_entry.insert(0, "30")
        self.duration_entry.pack(side="left", padx=5)

        self.btn_all = ctk.CTkButton(self.control_frame, text="RUN AUTOMATED BURN-IN", fg_color="red", command=self.start_automated_test)
        self.btn_all.pack(pady=20, fill="x", padx=20)
        
        self.lbl_timer = ctk.CTkLabel(self.control_frame, text="", font=("Arial", 16), text_color="orange")
        self.lbl_timer.pack(pady=5)

        # Right Frame - Monitoring
        self.monitor_frame = ctk.CTkFrame(self)
        self.monitor_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(self.monitor_frame, text="Phase 1: Core & Temp Monitor", font=("Arial", 20, "bold")).pack(pady=10)

        self.lbl_cpu = ctk.CTkLabel(self.monitor_frame, text="CPU Usage: 0%", font=("Arial", 16))
        self.lbl_cpu.pack(pady=5)

        self.lbl_cpu_temp = ctk.CTkLabel(self.monitor_frame, text="CPU Temp: 0°C", font=("Arial", 16))
        self.lbl_cpu_temp.pack(pady=5)

        self.lbl_ram = ctk.CTkLabel(self.monitor_frame, text="RAM Usage: 0%", font=("Arial", 16))
        self.lbl_ram.pack(pady=5)

        self.lbl_gpu = ctk.CTkLabel(self.monitor_frame, text="GPU Usage: 0%", font=("Arial", 16))
        self.lbl_gpu.pack(pady=5)

        self.lbl_gpu_temp = ctk.CTkLabel(self.monitor_frame, text="GPU Temp: 0°C", font=("Arial", 16))
        self.lbl_gpu_temp.pack(pady=5)
        
        self.lbl_max_temps = ctk.CTkLabel(self.monitor_frame, text="Max Temps - CPU: 0°C | GPU: 0°C", font=("Arial", 14), text_color="orange")
        self.lbl_max_temps.pack(pady=20)

        # API Section
        self.api_frame = ctk.CTkFrame(self.monitor_frame)
        self.api_frame.pack(pady=20, fill="x", padx=10)
        
        ctk.CTkLabel(self.api_frame, text="API Database URL:").pack(pady=5)
        self.api_entry = ctk.CTkEntry(self.api_frame, width=300)
        self.api_entry.insert(0, "http://example-api.com/api/certificate")
        self.api_entry.pack(pady=5)

        self.btn_cert = ctk.CTkButton(self.api_frame, text="Generate & Send Certificate", command=self.send_cert)
        self.btn_cert.pack(pady=10)
        
        self.lbl_status = ctk.CTkLabel(self.api_frame, text="", text_color="green")
        self.lbl_status.pack(pady=5)

        # Start monitoring loop using tkinter's .after() for thread safety
        self.start_time = time.time()
        self.is_monitoring = True
        self.update_metrics()

    def update_metrics(self):
        if not self.is_monitoring:
            return
            
        try:
            # We run the blocking get_metrics in a separate thread so the GUI doesn't freeze
            threading.Thread(target=self.fetch_and_update, daemon=True).start()
        except Exception as e:
            print(f"Monitor loop error: {e}")
            
        self.after(1000, self.update_metrics)
        
    def fetch_and_update(self):
        try:
            metrics = get_metrics()
            # Schedule the UI update back on the main thread
            self.after(0, lambda: self.apply_metrics_to_ui(metrics))
        except Exception as e:
            print(f"Monitor fetch error: {e}")
            
    def apply_metrics_to_ui(self, metrics):
        try:
            if metrics["cpu_temp"] > self.max_temps["cpu_temp"]:
                self.max_temps["cpu_temp"] = metrics["cpu_temp"]
            if metrics["gpu_temp"] > self.max_temps["gpu_temp"]:
                self.max_temps["gpu_temp"] = metrics["gpu_temp"]
                
            self.lbl_cpu.configure(text=f"CPU Usage: {metrics['cpu_usage']}%")
            self.lbl_cpu_temp.configure(text=f"CPU Temp: {metrics['cpu_temp']}°C")
            self.lbl_ram.configure(text=f"RAM Usage: {metrics['ram_usage']}%")
            self.lbl_gpu.configure(text=f"GPU Usage: {metrics['gpu_usage']}%")
            self.lbl_gpu_temp.configure(text=f"GPU Temp: {metrics['gpu_temp']}°C")
            self.lbl_max_temps.configure(text=f"Max Temps - CPU: {self.max_temps['cpu_temp']}°C | GPU: {self.max_temps['gpu_temp']}°C")
        except Exception as e:
            print(f"Monitor UI update error: {e}")

    def toggle_cpu(self):
        if self.cpu_burner.is_running:
            self.cpu_burner.stop()
            self.btn_cpu.configure(text="Phase 2: CPU/RAM Burner (START)", fg_color=["#3B8ED0", "#1F6AA5"])
        else:
            self.cpu_burner.start()
            self.phases_completed["CPU_Burner"] = True
            self.btn_cpu.configure(text="Phase 2: CPU/RAM Burner (STOP)", fg_color="red")

    def toggle_gpu(self):
        if self.gpu_burner.is_running:
            self.gpu_burner.stop()
            self.btn_gpu.configure(text="Phase 3: GPU Burner (START)", fg_color=["#3B8ED0", "#1F6AA5"])
        else:
            self.gpu_burner.start()
            self.phases_completed["GPU_Burner"] = True
            self.btn_gpu.configure(text="Phase 3: GPU Burner (STOP)", fg_color="red")

    def toggle_crypto(self):
        if self.crypto_payload.is_running:
            self.crypto_payload.stop()
            self.btn_crypto.configure(text="Phase 4: Crypto Payload (START)", fg_color=["#3B8ED0", "#1F6AA5"])
        else:
            self.crypto_payload.start()
            self.phases_completed["Crypto_Payload"] = True
            self.btn_crypto.configure(text="Phase 4: Crypto Payload (STOP)", fg_color="red")

    def start_automated_test(self):
        try:
            mins = float(self.duration_entry.get())
        except ValueError:
            mins = 30.0
            self.duration_entry.delete(0, "end")
            self.duration_entry.insert(0, "30")
            
        self.btn_all.configure(text="STOP AUTOMATED BURN-IN", command=self.stop_automated_test)
        
        if not self.cpu_burner.is_running: self.toggle_cpu()
        if not self.gpu_burner.is_running: self.toggle_gpu()
        if not self.crypto_payload.is_running: self.toggle_crypto()
        
        self.auto_end_time = time.time() + (mins * 60)
        self.auto_running = True
        self.update_timer()

    def stop_automated_test(self):
        self.auto_running = False
        self.lbl_timer.configure(text="")
        self.btn_all.configure(text="RUN AUTOMATED BURN-IN", command=self.start_automated_test)
        
        if self.cpu_burner.is_running: self.toggle_cpu()
        if self.gpu_burner.is_running: self.toggle_gpu()
        if self.crypto_payload.is_running: self.toggle_crypto()

    def update_timer(self):
        if not getattr(self, 'auto_running', False):
            return
            
        remaining = int(self.auto_end_time - time.time())
        if remaining <= 0:
            self.stop_automated_test()
            self.send_cert()
        else:
            mins, secs = divmod(remaining, 60)
            self.lbl_timer.configure(text=f"Time Remaining: {mins:02d}:{secs:02d}")
            self.after(1000, self.update_timer)

    def send_cert(self):
        duration_mins = round((time.time() - self.start_time) / 60.0, 2)
        url = self.api_entry.get()
        completed = [k for k, v in self.phases_completed.items() if v]
        
        success = send_certificate(url, self.max_temps, duration_mins, completed)
        if success:
            self.lbl_status.configure(text="Certificate sent successfully!", text_color="green")
        else:
            self.lbl_status.configure(text="Failed to send certificate.", text_color="red")
