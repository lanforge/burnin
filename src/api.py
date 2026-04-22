import requests
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

import json
import os

def send_certificate(api_url, max_temps, duration_mins, phases_completed):
    """
    Generate the burn-in certificate as a text file instead of deploying an API.
    """
    specs = get_specs()
    payload = {
        "status": "SUCCESS",
        "system_specs": specs,
        "max_temperatures": max_temps,
        "test_duration_seconds": duration_mins, # Repurposed to seconds for quick testing
        "phases_completed": phases_completed
    }
    
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cert_path = os.path.join(base_dir, "burn_in_certificate.txt")
        
        with open(cert_path, "w") as f:
            f.write("=== LANFORGE BURN-IN CERTIFICATE ===\n\n")
            f.write(json.dumps(payload, indent=4))
            
        print(f"Certificate generated at {cert_path}")
        return True
    except Exception as e:
        print(f"File generation error: {e}")
        return False
