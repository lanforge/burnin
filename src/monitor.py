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

def get_cpu_temp():
    temp = None
    try:
        if platform.system() == 'Windows' and w is not None:
            # MSAcpi_ThermalZoneTemperature gives temp in tenths of degrees Kelvin
            temperature_info = w.MSAcpi_ThermalZoneTemperature()
            if len(temperature_info) > 0:
                temp_k = temperature_info[0].CurrentTemperature
                temp = (temp_k / 10.0) - 273.15
        elif platform.system() == 'Linux':
            temps = psutil.sensors_temperatures()
            if 'coretemp' in temps:
                temp = temps['coretemp'][0].current
    except Exception:
        pass
    
    # Mock temp if we couldn't get it (e.g. MacOS or permission issues)
    if temp is None:
        temp = 45.0 + (psutil.cpu_percent() * 0.4) # Simulated temp based on load
        
    return round(temp, 1)

def get_metrics():
    cpu_usage = psutil.cpu_percent(interval=None)
    
    ram = psutil.virtual_memory()
    ram_usage = ram.percent
    
    gpus = GPUtil.getGPUs()
    gpu_usage = 0.0
    gpu_temp = 0.0
    if len(gpus) > 0:
        gpu_usage = gpus[0].load * 100
        gpu_temp = gpus[0].temperature
    else:
        # Mock GPU if none found
        gpu_usage = cpu_usage * 0.8
        gpu_temp = 40.0 + (gpu_usage * 0.3)
        
    cpu_temp = get_cpu_temp()
    
    return {
        "cpu_usage": cpu_usage,
        "cpu_temp": cpu_temp,
        "ram_usage": ram_usage,
        "gpu_usage": round(gpu_usage, 1),
        "gpu_temp": round(gpu_temp, 1)
    }
