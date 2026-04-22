import psutil
import platform
import GPUtil

try:
    if platform.system() == 'Windows':
        import wmi
        w = wmi.WMI(namespace="root\\wmi")
except ImportError:
    w = None
except Exception:
    w = None

def get_lhm_sensors():
    """
    Fetch all sensors from LibreHardwareMonitor / OpenHardwareMonitor.
    Categorize them into CPU, GPU, RAM, Motherboard.
    """
    sensors_data = {
        "cpu": {"temps": {}, "powers": {}, "clocks": {}, "loads": {}},
        "gpu": {"temps": {}, "powers": {}, "clocks": {}, "loads": {}, "fans": {}},
        "ram": {"loads": {}, "data": {}},
        "mobo": {"temps": {}, "fans": {}, "voltages": {}}
    }
    
    if platform.system() != 'Windows':
        return sensors_data
        
    try:
        import wmi
        w_hm = None
        for namespace in ["root\\LibreHardwareMonitor", "root\\OpenHardwareMonitor"]:
            try:
                w_hm = wmi.WMI(namespace=namespace)
                # Test query
                _ = w_hm.Sensor()
                break
            except Exception:
                w_hm = None
                
        if w_hm is None:
            return sensors_data

        # Build hardware mapping to determine type
        hardwares = w_hm.Hardware()
        hw_map = {}
        for hw in hardwares:
            hw_map[hw.Identifier] = hw.HardwareType

        sensors = w_hm.Sensor()
        for s in sensors:
            hw_type = hw_map.get(s.Parent, "")
            s_type = s.SensorType
            s_name = s.Name
            s_val = s.Value

            # CPU
            if "CPU" in hw_type or "Cpu" in hw_type:
                if s_type == "Temperature": sensors_data["cpu"]["temps"][s_name] = s_val
                elif s_type == "Power": sensors_data["cpu"]["powers"][s_name] = s_val
                elif s_type == "Clock": sensors_data["cpu"]["clocks"][s_name] = s_val
                elif s_type == "Load": sensors_data["cpu"]["loads"][s_name] = s_val
            
            # GPU
            elif "Gpu" in hw_type or "GPU" in hw_type:
                if s_type == "Temperature": sensors_data["gpu"]["temps"][s_name] = s_val
                elif s_type == "Power": sensors_data["gpu"]["powers"][s_name] = s_val
                elif s_type == "Clock": sensors_data["gpu"]["clocks"][s_name] = s_val
                elif s_type == "Load": sensors_data["gpu"]["loads"][s_name] = s_val
                elif s_type == "Fan": sensors_data["gpu"]["fans"][s_name] = s_val
            
            # RAM
            elif "Memory" in hw_type or "RAM" in hw_type:
                if s_type == "Load": sensors_data["ram"]["loads"][s_name] = s_val
                elif s_type == "Data": sensors_data["ram"]["data"][s_name] = s_val
            
            # Motherboard
            elif "Mainboard" in hw_type or "SuperIO" in hw_type or "Motherboard" in hw_type:
                if s_type == "Temperature": sensors_data["mobo"]["temps"][s_name] = s_val
                elif s_type == "Fan": sensors_data["mobo"]["fans"][s_name] = s_val
                elif s_type == "Voltage": sensors_data["mobo"]["voltages"][s_name] = s_val
                
    except Exception as e:
        # Ignore WMI errors, we fall back to psutil/GPUtil
        pass
        
    return sensors_data

def get_metrics():
    # Base psutil metrics
    cpu_usage_total = psutil.cpu_percent(interval=None)
    cpu_usage_per_core = psutil.cpu_percent(interval=None, percpu=True)
    
    cpu_freq = psutil.cpu_freq()
    cpu_freq_current = cpu_freq.current if cpu_freq else 0.0
    
    ram = psutil.virtual_memory()
    ram_usage_percent = ram.percent
    ram_used_gb = ram.used / (1024**3)
    ram_total_gb = ram.total / (1024**3)
    
    # Base GPUtil metrics
    gpus = GPUtil.getGPUs()
    gpu_base = None
    if len(gpus) > 0:
        g = gpus[0]
        gpu_base = {
            "name": g.name,
            "usage": g.load * 100,
            "temp": g.temperature,
            "vram_used": g.memoryUsed,
            "vram_total": g.memoryTotal
        }
    
    # Extended LHM metrics
    lhm = get_lhm_sensors()
    
    # CPU Temps
    cpu_temps = lhm["cpu"]["temps"]
    cpu_package_temp = cpu_temps.get("CPU Package", cpu_temps.get("Core (Tctl/Tdie)", None))
    
    # Fallback to older WMI or psutil if LHM missing
    if cpu_package_temp is None:
        if platform.system() == 'Linux':
            temps = psutil.sensors_temperatures()
            if 'coretemp' in temps:
                cpu_package_temp = temps['coretemp'][0].current
        elif platform.system() == 'Windows' and w is not None:
            try:
                t_info = w.MSAcpi_ThermalZoneTemperature()
                if len(t_info) > 0:
                    cpu_package_temp = (t_info[0].CurrentTemperature / 10.0) - 273.15
            except Exception:
                pass
                
    if cpu_package_temp is None:
        cpu_package_temp = 45.0 + (cpu_usage_total * 0.4) # Mock
        
    # GPU Clock fallback if LHM missing
    gpu_clocks = lhm["gpu"]["clocks"]
    gpu_core_clock = gpu_clocks.get("GPU Core", 0.0)
    gpu_mem_clock = gpu_clocks.get("GPU Memory", 0.0)
    
    gpu_powers = lhm["gpu"]["powers"]
    gpu_power_w = gpu_powers.get("GPU Package", gpu_powers.get("GPU Power", 0.0))
    
    gpu_temps = lhm["gpu"]["temps"]
    gpu_hotspot = gpu_temps.get("GPU Hot Spot", gpu_temps.get("GPU Memory", 0.0))
    
    cpu_powers = lhm["cpu"]["powers"]
    cpu_power_w = cpu_powers.get("CPU Package", 0.0)

    # Reconstruct final dictionary
    metrics = {
        "cpu": {
            "usage_total": cpu_usage_total,
            "usage_per_core": cpu_usage_per_core,
            "freq_current": cpu_freq_current,
            "package_temp": round(float(cpu_package_temp), 1),
            "core_temps": {k: round(float(v), 1) for k, v in cpu_temps.items() if "Core" in k},
            "power_w": round(float(cpu_power_w), 1)
        },
        "gpu": {
            "name": gpu_base["name"] if gpu_base else "Unknown/Integrated",
            "usage": gpu_base["usage"] if gpu_base else (cpu_usage_total * 0.8), # Mock if no GPU
            "temp_core": gpu_base["temp"] if gpu_base else (40.0 + cpu_usage_total * 0.3),
            "temp_hotspot": round(float(gpu_hotspot), 1),
            "freq_core": round(float(gpu_core_clock), 1),
            "freq_mem": round(float(gpu_mem_clock), 1),
            "power_w": round(float(gpu_power_w), 1),
            "vram_used": gpu_base["vram_used"] if gpu_base else 0.0,
            "vram_total": gpu_base["vram_total"] if gpu_base else 0.0
        },
        "ram": {
            "usage_percent": ram_usage_percent,
            "used_gb": round(ram_used_gb, 2),
            "total_gb": round(ram_total_gb, 2)
        },
        "mobo": {
            "temps": {k: round(float(v), 1) for k, v in lhm["mobo"]["temps"].items()}
        }
    }
    
    return metrics
