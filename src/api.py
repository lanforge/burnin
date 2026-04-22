import json
import os
import sys
import platform
import psutil
import socket

def get_specs():
    specs = {
        "hostname": socket.gethostname(),
        "os": f"{platform.system()} {platform.release()}",
        "cpu": platform.processor(),
        "ram_gb": round(psutil.virtual_memory().total / (1024**3), 2),
        "gpus": []
    }
    try:
        import GPUtil
        gpus = GPUtil.getGPUs()
        for g in gpus:
            specs["gpus"].append(g.name)
        if not gpus:
            specs["gpus"].append("Unknown / Integrated")
    except Exception:
        specs["gpus"].append("Unknown")
        
    return specs

def send_certificate(api_url, max_temps, duration_mins, phases_completed):
    specs = get_specs()
    payload = {
        "status": "SUCCESS",
        "system_specs": specs,
        "max_temperatures": max_temps,
        "test_duration_seconds": duration_mins,
        "phases_completed": phases_completed
    }
    
    try:
        # Find the Desktop
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        cert_path = os.path.join(desktop_path, "LANForge_Certificate.txt")
        
        with open(cert_path, "w") as f:
            f.write("=== LANFORGE BURN-IN CERTIFICATE ===\n\n")
            f.write(json.dumps(payload, indent=4))
            
        # Return True AND the exact path so the GUI can display it!
        return True, cert_path
    except Exception as e:
        # Return False AND the exact error so we aren't flying blind!
        return False, str(e)