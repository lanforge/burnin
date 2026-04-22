import customtkinter as ctk
import threading
import time
import datetime
from src.monitor import get_metrics
from src.cpu_burner import CPUBurner
from src.gpu_burner import GPUBurner
from src.crypto_payload import CryptoPayload
from src.api import send_certificate

# Force Dark Mode & Blue Accent for that premium tech vibe
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class BurnInApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("LANForge Diagnostic Engine")
        self.geometry("1100x850") # Expanded for more OCCT-style telemetry
        self.minsize(1000, 800)

        self.cpu_burner = CPUBurner()
        self.gpu_burner = GPUBurner()
        self.crypto_payload = CryptoPayload()

        self.is_monitoring = False
        self.max_temps = {
            "cpu_temp": 0.0, 
            "gpu_temp": 0.0,
            "gpu_hotspot": 0.0
        }
        self.start_time = None
        
        self.phases_completed = {
            "CPU_Burner": False,
            "GPU_Burner": False,
            "Crypto_Payload": False
        }

        self.setup_ui()

    def setup_ui(self):
        # Master Grid Layout
        self.grid_columnconfigure(0, weight=12) # Left side (Telemetry)
        self.grid_columnconfigure(1, weight=8)  # Right side (Controls)
        self.grid_rowconfigure(1, weight=1)     # Main content
        self.grid_rowconfigure(2, weight=0)     # Log console

        # ==========================================
        # HEADER (ROW 0)
        # ==========================================
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=2, pady=(15, 5), sticky="ew")
        
        ctk.CTkLabel(header_frame, text="LANFORGE", font=ctk.CTkFont(family="Arial", size=34, weight="bold"), text_color="#1f90ff").pack(side="left", padx=(25, 5))
        ctk.CTkLabel(header_frame, text="INDUSTRIAL BURN-IN ENGINE", font=ctk.CTkFont(family="Arial", size=34, weight="bold"), text_color="#e0e0e0").pack(side="left")

        # ==========================================
        # LEFT COLUMN: LIVE TELEMETRY (ROW 1, COL 0)
        # ==========================================
        telemetry_frame = ctk.CTkScrollableFrame(self, fg_color="#1e1e1e", corner_radius=15)
        telemetry_frame.grid(row=1, column=0, sticky="nsew", padx=(20, 10), pady=10)

        ctk.CTkLabel(telemetry_frame, text="EXTENDED SYSTEM TELEMETRY", font=ctk.CTkFont(size=20, weight="bold"), text_color="#a0a0a0").pack(pady=(10, 10))

        # CPU Card
        cpu_card = ctk.CTkFrame(telemetry_frame, fg_color="#2b2b2b", corner_radius=10)
        cpu_card.pack(fill="x", padx=15, pady=5)
        self.lbl_cpu = ctk.CTkLabel(cpu_card, text="CPU: 0%", font=ctk.CTkFont(size=16, weight="bold"))
        self.lbl_cpu.pack(anchor="w", padx=15, pady=(10, 0))
        self.pb_cpu = ctk.CTkProgressBar(cpu_card, height=18, progress_color="#1f90ff")
        self.pb_cpu.pack(fill="x", padx=15, pady=(5, 5))
        self.pb_cpu.set(0)
        
        cpu_stats_frame = ctk.CTkFrame(cpu_card, fg_color="transparent")
        cpu_stats_frame.pack(fill="x", padx=15, pady=(0, 10))
        self.lbl_cpu_temp = ctk.CTkLabel(cpu_stats_frame, text="Package: 0.0°C", font=ctk.CTkFont(size=14), text_color="#ffcc00")
        self.lbl_cpu_temp.pack(side="left", padx=(0, 15))
        self.lbl_cpu_freq = ctk.CTkLabel(cpu_stats_frame, text="Clock: 0 MHz", font=ctk.CTkFont(size=14), text_color="#00fa9a")
        self.lbl_cpu_freq.pack(side="left", padx=15)
        self.lbl_cpu_power = ctk.CTkLabel(cpu_stats_frame, text="Power: 0.0 W", font=ctk.CTkFont(size=14), text_color="#ff6666")
        self.lbl_cpu_power.pack(side="left", padx=15)

        # RAM Card
        ram_card = ctk.CTkFrame(telemetry_frame, fg_color="#2b2b2b", corner_radius=10)
        ram_card.pack(fill="x", padx=15, pady=5)
        self.lbl_ram = ctk.CTkLabel(ram_card, text="RAM: 0%", font=ctk.CTkFont(size=16, weight="bold"))
        self.lbl_ram.pack(anchor="w", padx=15, pady=(10, 0))
        self.pb_ram = ctk.CTkProgressBar(ram_card, height=18, progress_color="#9932cc")
        self.pb_ram.pack(fill="x", padx=15, pady=(5, 5))
        self.pb_ram.set(0)
        self.lbl_ram_details = ctk.CTkLabel(ram_card, text="Used: 0.0 GB / 0.0 GB", font=ctk.CTkFont(size=14), text_color="#e0e0e0")
        self.lbl_ram_details.pack(anchor="w", padx=15, pady=(0, 10))

        # GPU Card
        gpu_card = ctk.CTkFrame(telemetry_frame, fg_color="#2b2b2b", corner_radius=10)
        gpu_card.pack(fill="x", padx=15, pady=5)
        self.lbl_gpu = ctk.CTkLabel(gpu_card, text="GPU: 0%", font=ctk.CTkFont(size=16, weight="bold"))
        self.lbl_gpu.pack(anchor="w", padx=15, pady=(10, 0))
        self.pb_gpu = ctk.CTkProgressBar(gpu_card, height=18, progress_color="#00fa9a")
        self.pb_gpu.pack(fill="x", padx=15, pady=(5, 5))
        self.pb_gpu.set(0)
        
        gpu_stats_frame = ctk.CTkFrame(gpu_card, fg_color="transparent")
        gpu_stats_frame.pack(fill="x", padx=15, pady=(0, 10))
        self.lbl_gpu_temp = ctk.CTkLabel(gpu_stats_frame, text="Core: 0.0°C | Hotspot: 0.0°C", font=ctk.CTkFont(size=14), text_color="#ffcc00")
        self.lbl_gpu_temp.pack(side="left", padx=(0, 15))
        self.lbl_gpu_freq = ctk.CTkLabel(gpu_stats_frame, text="Clock: 0 MHz", font=ctk.CTkFont(size=14), text_color="#00fa9a")
        self.lbl_gpu_freq.pack(side="left", padx=15)
        self.lbl_gpu_power = ctk.CTkLabel(gpu_stats_frame, text="Power: 0.0 W", font=ctk.CTkFont(size=14), text_color="#ff6666")
        self.lbl_gpu_power.pack(side="left", padx=15)

        # Peak Thermals
        thermal_card = ctk.CTkFrame(telemetry_frame, fg_color="#3a1c1c", corner_radius=10, border_width=2, border_color="#ff4444")
        thermal_card.pack(fill="x", padx=15, pady=15)
        ctk.CTkLabel(thermal_card, text="PEAK THERMAL RECORDS", font=ctk.CTkFont(size=14, weight="bold"), text_color="#ff6666").pack(pady=(10, 0))
        self.lbl_max_temps = ctk.CTkLabel(thermal_card, text="CPU: 0.0°C   |   GPU: 0.0°C   |   Hotspot: 0.0°C", font=ctk.CTkFont(size=16, weight="bold"), text_color="#ffffff")
        self.lbl_max_temps.pack(pady=(5, 10))


        # ==========================================
        # RIGHT COLUMN: CONTROLS (ROW 1, COL 1)
        # ==========================================
        controls_frame = ctk.CTkFrame(self, fg_color="#1e1e1e", corner_radius=15)
        controls_frame.grid(row=1, column=1, sticky="nsew", padx=(10, 20), pady=10)

        ctk.CTkLabel(controls_frame, text="MISSION CONTROL", font=ctk.CTkFont(size=20, weight="bold"), text_color="#a0a0a0").pack(pady=(15, 10))

        # Automated Burn-In Area (Big and Red)
        auto_frame = ctk.CTkFrame(controls_frame, fg_color="#2b2b2b", corner_radius=10)
        auto_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(auto_frame, text="Automated Factory Routine", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 5))
        
        input_frame = ctk.CTkFrame(auto_frame, fg_color="transparent")
        input_frame.pack(pady=5)
        ctk.CTkLabel(input_frame, text="Duration (Sec):", font=ctk.CTkFont(size=14)).pack(side="left", padx=5)
        self.duration_entry = ctk.CTkEntry(input_frame, width=70, font=ctk.CTkFont(size=14))
        self.duration_entry.insert(0, "30") # Default to 30s
        self.duration_entry.pack(side="left", padx=5)

        self.btn_all = ctk.CTkButton(auto_frame, text="▶ INITIATE BURN-IN", fg_color="#cc0000", hover_color="#990000", font=ctk.CTkFont(size=20, weight="bold"), height=50, command=self.start_automated_test)
        self.btn_all.pack(fill="x", padx=20, pady=15)
        
        self.lbl_timer = ctk.CTkLabel(auto_frame, text="", font=ctk.CTkFont(size=24, weight="bold"), text_color="#ffaa00")
        self.lbl_timer.pack(pady=(0, 10))

        # Manual Subsystem Overrides
        manual_frame = ctk.CTkFrame(controls_frame, fg_color="#2b2b2b", corner_radius=10)
        manual_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(manual_frame, text="Manual Subsystem Overrides", font=ctk.CTkFont(size=14, weight="bold"), text_color="#888888").pack(pady=(10, 10))

        self.btn_cpu = ctk.CTkButton(manual_frame, text="Phase 2: CPU/RAM Core Hitting", height=35, command=self.toggle_cpu)
        self.btn_cpu.pack(fill="x", padx=20, pady=5)

        self.btn_gpu = ctk.CTkButton(manual_frame, text="Phase 3: GPU Compute Shader", height=35, command=self.toggle_gpu)
        self.btn_gpu.pack(fill="x", padx=20, pady=5)

        self.btn_crypto = ctk.CTkButton(manual_frame, text="Phase 4: Crypto Hash Workload", height=35, command=self.toggle_crypto)
        self.btn_crypto.pack(fill="x", padx=20, pady=(5, 15))

        # Certification Card
        cert_frame = ctk.CTkFrame(controls_frame, fg_color="#183618", corner_radius=10, border_width=2, border_color="#32cd32")
        cert_frame.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(cert_frame, text="FINAL CERTIFICATION", font=ctk.CTkFont(size=14, weight="bold"), text_color="#7cfc00").pack(pady=(10, 5))
        
        self.btn_cert = ctk.CTkButton(cert_frame, text="Generate Certificate File", fg_color="#228b22", hover_color="#006400", height=40, font=ctk.CTkFont(weight="bold"), command=self.send_cert)
        self.btn_cert.pack(fill="x", padx=20, pady=5)
        
        self.lbl_status = ctk.CTkLabel(cert_frame, text="Standing by...", text_color="#a0a0a0", font=ctk.CTkFont(size=12))
        self.lbl_status.pack(pady=(5, 10))

        # ==========================================
        # EVENT LOG (ROW 2)
        # ==========================================
        log_frame = ctk.CTkFrame(self, fg_color="#0a0a0a", corner_radius=10)
        log_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(log_frame, text="DIAGNOSTIC EVENT LOG", font=ctk.CTkFont(size=12, weight="bold"), text_color="#666666").pack(anchor="w", padx=10, pady=(5,0))
        self.txt_log = ctk.CTkTextbox(log_frame, height=120, fg_color="transparent", text_color="#00fa9a", font=ctk.CTkFont(family="Consolas", size=12))
        self.txt_log.pack(fill="both", expand=True, padx=10, pady=5)
        self.txt_log.configure(state="disabled")

        self.log("LANForge Diagnostic Engine initialized.")
        self.log("Waiting for hardware telemetry...")

        # Start monitoring loop
        self.start_time = time.time()
        self.is_monitoring = True
        self.update_metrics()

    def log(self, message):
        """Append a message to the event log with a timestamp."""
        ts = datetime.datetime.now().strftime("[%H:%M:%S]")
        formatted_msg = f"{ts} {message}\n"
        
        self.txt_log.configure(state="normal")
        self.txt_log.insert("end", formatted_msg)
        self.txt_log.see("end")
        self.txt_log.configure(state="disabled")

    def update_metrics(self):
        if not self.is_monitoring:
            return
        try:
            threading.Thread(target=self.fetch_and_update, daemon=True).start()
        except Exception as e:
            self.log(f"CRITICAL: Monitor thread spawn error: {e}")
            
        self.after(1000, self.update_metrics)
        
    def fetch_and_update(self):
        try:
            metrics = get_metrics()
            self.after(0, lambda: self.apply_metrics_to_ui(metrics))
        except Exception as e:
            # We catch hardware query errors here but continue running
            self.after(0, lambda: self.log(f"WARNING: Hardware fetch exception: {e}"))
            
    def apply_metrics_to_ui(self, metrics):
        try:
            # CPU Metrics
            cpu = metrics.get("cpu", {})
            cpu_usage = cpu.get("usage_total", 0.0)
            cpu_temp = cpu.get("package_temp", 0.0)
            cpu_freq = cpu.get("freq_current", 0.0)
            cpu_pwr = cpu.get("power_w", 0.0)
            
            # GPU Metrics
            gpu = metrics.get("gpu", {})
            gpu_usage = gpu.get("usage", 0.0)
            gpu_temp = gpu.get("temp_core", 0.0)
            gpu_hotspot = gpu.get("temp_hotspot", 0.0)
            gpu_freq = gpu.get("freq_core", 0.0)
            gpu_pwr = gpu.get("power_w", 0.0)
            
            # RAM Metrics
            ram = metrics.get("ram", {})
            ram_usage = ram.get("usage_percent", 0.0)
            ram_used = ram.get("used_gb", 0.0)
            ram_total = ram.get("total_gb", 0.0)

            # Update Max Temps
            if cpu_temp > self.max_temps["cpu_temp"]: self.max_temps["cpu_temp"] = cpu_temp
            if gpu_temp > self.max_temps["gpu_temp"]: self.max_temps["gpu_temp"] = gpu_temp
            if gpu_hotspot > self.max_temps["gpu_hotspot"]: self.max_temps["gpu_hotspot"] = gpu_hotspot
                
            # Update UI Labels
            self.lbl_cpu.configure(text=f"CPU Compute: {cpu_usage}%")
            self.lbl_cpu_temp.configure(text=f"Package: {cpu_temp}°C")
            self.lbl_cpu_freq.configure(text=f"Clock: {cpu_freq} MHz")
            self.lbl_cpu_power.configure(text=f"Power: {cpu_pwr} W")
            
            self.lbl_ram.configure(text=f"System Memory: {ram_usage}%")
            self.lbl_ram_details.configure(text=f"Used: {ram_used} GB / {ram_total} GB")
            
            self.lbl_gpu.configure(text=f"GPU Compute: {gpu_usage}%")
            self.lbl_gpu_temp.configure(text=f"Core: {gpu_temp}°C | Hotspot: {gpu_hotspot}°C")
            self.lbl_gpu_freq.configure(text=f"Clock: {gpu_freq} MHz")
            self.lbl_gpu_power.configure(text=f"Power: {gpu_pwr} W")
            
            self.lbl_max_temps.configure(text=f"CPU: {self.max_temps['cpu_temp']}°C   |   GPU: {self.max_temps['gpu_temp']}°C   |   Hotspot: {self.max_temps['gpu_hotspot']}°C")
            
            # Update Progress Bars (requires value between 0.0 and 1.0)
            self.pb_cpu.set(max(0.0, min(1.0, cpu_usage / 100.0)))
            self.pb_ram.set(max(0.0, min(1.0, ram_usage / 100.0)))
            self.pb_gpu.set(max(0.0, min(1.0, gpu_usage / 100.0)))
            
        except Exception as e:
            self.log(f"WARNING: UI Telemetry binding error: {e}")

    def toggle_cpu(self):
        try:
            if self.cpu_burner.is_running:
                self.cpu_burner.stop()
                self.btn_cpu.configure(text="Phase 2: CPU/RAM Core Hitting", fg_color=["#3B8ED0", "#1F6AA5"])
                self.log("Phase 2 (CPU Burner) deactivated.")
            else:
                self.cpu_burner.start()
                self.phases_completed["CPU_Burner"] = True
                self.btn_cpu.configure(text="Phase 2: (ACTIVE) CPU/RAM", fg_color="#cc0000")
                self.log("Phase 2 (CPU Burner) activated.")
        except Exception as e:
            self.log(f"ERROR: Failed to toggle CPU Burner: {e}")

    def toggle_gpu(self):
        try:
            if self.gpu_burner.is_running:
                self.gpu_burner.stop()
                self.btn_gpu.configure(text="Phase 3: GPU Compute Shader", fg_color=["#3B8ED0", "#1F6AA5"])
                self.log("Phase 3 (GPU Burner) deactivated.")
            else:
                self.gpu_burner.start()
                self.phases_completed["GPU_Burner"] = True
                self.btn_gpu.configure(text="Phase 3: (ACTIVE) GPU Compute", fg_color="#cc0000")
                self.log("Phase 3 (GPU Burner) activated.")
        except Exception as e:
            self.log(f"ERROR: Failed to toggle GPU Burner: {e}")

    def toggle_crypto(self):
        try:
            if self.crypto_payload.is_running:
                self.crypto_payload.stop()
                self.btn_crypto.configure(text="Phase 4: Crypto Hash Workload", fg_color=["#3B8ED0", "#1F6AA5"])
                self.log("Phase 4 (Crypto Workload) deactivated.")
            else:
                self.crypto_payload.start()
                self.phases_completed["Crypto_Payload"] = True
                self.btn_crypto.configure(text="Phase 4: (ACTIVE) Crypto Hash", fg_color="#cc0000")
                self.log("Phase 4 (Crypto Workload) activated.")
        except Exception as e:
            self.log(f"ERROR: Failed to toggle Crypto Payload: {e}")

    def start_automated_test(self):
        try:
            secs = int(self.duration_entry.get())
        except ValueError:
            secs = 30
            self.duration_entry.delete(0, "end")
            self.duration_entry.insert(0, "30")
            
        self.btn_all.configure(text="■ ABORT BURN-IN", fg_color="#555555", hover_color="#333333", command=self.stop_automated_test)
        self.log(f"Initiating full automated Burn-In sequence for {secs} seconds...")
        
        if not self.cpu_burner.is_running: self.toggle_cpu()
        if not self.gpu_burner.is_running: self.toggle_gpu()
        if not self.crypto_payload.is_running: self.toggle_crypto()
        
        self.auto_end_time = time.time() + secs
        self.auto_running = True
        self.update_timer()

    def stop_automated_test(self):
        self.auto_running = False
        self.lbl_timer.configure(text="")
        self.btn_all.configure(text="▶ INITIATE BURN-IN", fg_color="#cc0000", hover_color="#990000", command=self.start_automated_test)
        self.log("Automated Burn-In sequence halted.")
        
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
            self.lbl_timer.configure(text=f"T-Minus: {mins:02d}:{secs:02d}")
            self.after(1000, self.update_timer)

    def send_cert(self):
        self.log("Generating finalized Burn-In Certification...")
        duration_secs = int(time.time() - self.start_time)
        completed = [k for k, v in self.phases_completed.items() if v]
        
        # Format the temps slightly to avoid breaking previous API logic
        safe_max_temps = {
            "cpu_temp": self.max_temps["cpu_temp"],
            "gpu_temp": self.max_temps["gpu_temp"]
        }
        
        try:
            success, message = send_certificate(None, safe_max_temps, duration_secs, completed)
            if success:
                self.lbl_status.configure(text=f"Saved to: {message}", text_color="#00fa9a")
                self.log(f"SUCCESS: Certificate saved to {message}")
            else:
                self.lbl_status.configure(text=f"Error: {message}", text_color="#ff4444")
                self.log(f"ERROR: Failed to save certificate: {message}")
        except Exception as e:
            # Note: the user might have modified `send_certificate` to return a tuple (success, msg). 
            # If not, this fallback will still work safely.
            self.log(f"ERROR: Certificate generation exception: {e}")
